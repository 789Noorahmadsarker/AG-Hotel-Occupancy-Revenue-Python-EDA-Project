# %% [markdown]
# # Task 8: Hotel KPI Scorecard (Occupancy, ADR and RevPAR)
#
# **Problem statement:** Hotel managers judge performance with three headline numbers:
# how full the rooms are (occupancy), how much a used room earns (ADR) and how much every
# available room earns, used or not (RevPAR). Calculate them for every city, hotel category,
# room class and individual hotel, and explain why the city with the fullest rooms (Delhi)
# earns the least total money.
#
# **KPI glossary (plain English)**
# - **Booked occupancy** = rooms booked / rooms available. Cancelled and no-show bookings are
#   still counted, exactly as in Tasks 3 to 5.
# - **Net occupancy** = rooms used by guests who actually stayed / rooms available.
# - **ADR (Average Daily Rate)** = money earned from guests who stayed / rooms they used.
# - **RevPAR (Revenue per Available Room)** = all money kept / rooms available. It includes
#   cancellation fees and no-show charges, because the hotel keeps that money.
#
# **Modelling note:** one booking is treated as one room on its check-in date, the same
# convention the aggregated table uses. The booking value in this data does not grow with the
# number of nights, so rates are "per booking", not "per night".
#
# **Why these figures differ slightly from Tasks 3 to 5:** those tasks averaged each day's
# percentage, which treats a small room type and a large one equally. Here we divide the total
# rooms booked by the total rooms available (the standard hotel-industry method), so every room
# counts equally. The gap is about one point (for example Delhi: 61.5% in Task 3, 60.5% here).
#
# **Run Tasks 1 and 2 first.**

# %%
# Tools: pandas works with tables, numpy does safe maths, matplotlib and seaborn draw charts.
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# ---- Folder settings (usually nothing to change) ----
# These lines tell Python where your project folders are. Each name is a folder inside the
# main project folder, and the code must be run from that main folder.
# You only need to edit a name if you renamed the folder in your own copy of the project.
# (In Google Colab, use the notebooks: their first cell connects to your Google Drive folder for you.)
DATA_DIR = Path("data")             # folder holding the 6 ORIGINAL csv files (never changed)
CLEAN_DIR = Path("cleaned_data")    # folder for the cleaned files that the tasks create and reuse
OUT_DIR = Path("outputs")           # folder where the charts (PNG pictures) are saved
OUT_DIR.mkdir(exist_ok=True)        # create the outputs folder if it does not exist yet

# Chart look: one clean, colour-blind-friendly style used by every chart in this project.
INK, SOFT, GRID = "#0b0b0b", "#52514e", "#e3e2de"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#a8a7a1"
HEAT = LinearSegmentedColormap.from_list("blue", ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
sns.set_theme(style="white", rc={
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": GRID,
    "axes.labelcolor": SOFT, "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlelocation": "left"})

# %% [markdown]
# ## Step 1: Load the clean data

# %%
# Clean booking records (Task 2), clean room availability (Task 1) and the lookup tables.
bookings = pd.read_csv(CLEAN_DIR / "clean_bookings.csv", parse_dates=["check_in_date"])
agg = pd.read_csv(CLEAN_DIR / "clean_aggregated_bookings.csv", parse_dates=["check_in_date"])
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")
rooms = pd.read_csv(DATA_DIR / "dim_rooms.csv")
print("Bookings:", len(bookings), "| Availability rows:", len(agg))

# %% [markdown]
# ## Step 2: Build one table with rooms available and what happened to each booking
#
# Every row is one hotel, one day and one room type. We count how many bookings ended as a
# stay, a cancellation or a no-show, and how much money each outcome produced.

# %%
# Turn each booking's outcome into simple 1/0 flags so they can be added up.
bookings["stayed"] = (bookings["booking_status"] == "Checked Out").astype(int)
bookings["cancelled"] = (bookings["booking_status"] == "Cancelled").astype(int)
bookings["no_show"] = (bookings["booking_status"] == "No Show").astype(int)
bookings["stay_revenue"] = bookings["revenue_realized"] * bookings["stayed"]

# Add up the bookings for each hotel, day and room type.
daily = bookings.groupby(["property_id", "check_in_date", "room_category"], as_index=False).agg(
    booked=("booking_id", "size"),
    stayed=("stayed", "sum"),
    cancelled=("cancelled", "sum"),
    no_show=("no_show", "sum"),
    revenue=("revenue_realized", "sum"),
    stay_revenue=("stay_revenue", "sum"),
)

# Attach them to the clean availability table. Days with no bookings become zeros.
# We keep the aggregated table's own "successful_bookings" count (renamed) for a check below.
base = agg[["property_id", "check_in_date", "room_category", "capacity", "successful_bookings"]].rename(
    columns={"successful_bookings": "agg_successful"}
).merge(
    daily, on=["property_id", "check_in_date", "room_category"], how="left", validate="one_to_one"
)
count_columns = ["booked", "stayed", "cancelled", "no_show", "revenue", "stay_revenue"]
base[count_columns] = base[count_columns].fillna(0)

# What does the aggregated table's "successful_bookings" column really count? Despite its name,
# it matches ALL bookings made (including cancellations and no-shows), not only guests who stayed.
all_match = (base["agg_successful"] == base["booked"]).mean() * 100
stay_match = (base["agg_successful"] == base["stayed"]).mean() * 100
print(f"Hotel-days where 'successful_bookings' equals ALL bookings made: {all_match:.1f}%")
print(f"Hotel-days where it equals only guests who stayed:              {stay_match:.1f}%")

# Add hotel details (city, category) and readable room class names.
base = base.merge(hotels, on="property_id", how="left", validate="many_to_one")
base = base.merge(rooms, left_on="room_category", right_on="room_id", how="left",
                  validate="many_to_one").drop(columns="room_id")

# Safety check: how many bookings sit on days removed in Task 1 (impossible availability rows)?
left_out = len(bookings) - int(base["booked"].sum())
print(f"Bookings left out because their day/hotel row was removed in Task 1: {left_out}")
print("Table rows:", len(base))

# %% [markdown]
# ## Step 3: Calculate the KPIs

# %%
def kpi_table(table, by):
    """Add up the raw counts for a group and turn them into the headline KPIs."""
    t = table.groupby(by, observed=True).agg(
        hotels=("property_id", "nunique"),
        rooms_available=("capacity", "sum"),
        booked=("booked", "sum"),
        stayed=("stayed", "sum"),
        cancelled=("cancelled", "sum"),
        revenue=("revenue", "sum"),
        stay_revenue=("stay_revenue", "sum"),
    )
    # np.where avoids dividing by zero: if a group has no stays, ADR is left blank (NaN).
    t["booked_occ_pct"] = t["booked"] / t["rooms_available"] * 100
    t["net_occ_pct"] = t["stayed"] / t["rooms_available"] * 100
    t["adr"] = np.where(t["stayed"] > 0, t["stay_revenue"] / t["stayed"].replace(0, np.nan), np.nan)
    t["revpar"] = t["revenue"] / t["rooms_available"]
    t["cancel_rate_pct"] = t["cancelled"] / t["booked"] * 100
    return t


chain = kpi_table(base.assign(all_hotels="Whole chain"), "all_hotels")
show = ["booked_occ_pct", "net_occ_pct", "adr", "revpar"]
print("Whole chain")
print(chain[show].round(2))

# %%
# KPIs by city, ranked by RevPAR (money per available room).
by_city = kpi_table(base, "city").sort_values("revpar", ascending=False)
print("KPIs by city")
print(by_city[["hotels", "rooms_available"] + show].round(2))

# %%
# KPIs by hotel category and by room class.
by_category = kpi_table(base, "category").sort_values("revpar", ascending=False)
by_room = kpi_table(base, "room_class").sort_values("revpar", ascending=False)
print("KPIs by hotel category")
print(by_category[show].round(2))
print("\nKPIs by room class")
print(by_room[show].round(2))

# %%
# KPIs for each of the 25 hotels. Hotel names repeat, so we keep the property ID visible.
by_hotel = kpi_table(base, ["property_id", "property_name", "city", "category"])
by_hotel = by_hotel.sort_values("revpar", ascending=False)
print("KPIs by hotel (ranked by RevPAR)")
print(by_hotel[show].round(2).to_string())

# %% [markdown]
# ## Step 4: Why does the fullest city earn the least money?
#
# Total revenue depends on how many hotels a city has. RevPAR removes that effect by
# measuring money per available room, so cities of different sizes can be compared fairly.

# %%
# Compare cities on size (hotels), occupancy, price (ADR) and total money kept.
explain = by_city[["hotels", "booked_occ_pct", "adr", "revpar", "revenue"]].copy()
explain["revenue_per_hotel"] = explain["revenue"] / explain["hotels"]
explain["revenue_rank"] = explain["revenue"].rank(ascending=False).astype(int)
explain["revpar_rank"] = explain["revpar"].rank(ascending=False).astype(int)
print(explain.round(2))

# %% [markdown]
# ## Step 5: Charts

# %%
# Chart 1: the three headline KPIs by city.
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
panels = [("net_occ_pct", "Net occupancy (%)", "{:.1f}%"),
          ("adr", "ADR (average rate per used room)", "{:,.0f}"),
          ("revpar", "RevPAR (revenue per available room)", "{:,.0f}")]
for ax, (column, title, label) in zip(axes, panels):
    bars = ax.bar(by_city.index, by_city[column], color=BLUE, width=0.62)
    ax.bar_label(bars, labels=[label.format(v) for v in by_city[column]], padding=2, fontsize=9)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
fig.suptitle("Headline KPIs by city, May to July 2022", x=0.01, ha="left", fontweight="bold")
fig.tight_layout()
fig.savefig(OUT_DIR / "task8_kpis_by_city.png", dpi=150)
plt.show()

# %%
# Chart 2: how many booked rooms really get used, and RevPAR by city and room class.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1, 1.1]})

gap = by_city[["booked_occ_pct", "net_occ_pct"]]
x = np.arange(len(gap))
b1 = ax1.bar(x - 0.2, gap["booked_occ_pct"], width=0.38, color=BLUE, label="Booked occupancy")
b2 = ax1.bar(x + 0.2, gap["net_occ_pct"], width=0.38, color=ORANGE, label="Net occupancy (stayed)")
ax1.bar_label(b1, fmt="%.1f", padding=2, fontsize=9)
ax1.bar_label(b2, fmt="%.1f", padding=2, fontsize=9)
ax1.set_xticks(x, gap.index)
ax1.set_ylabel("% of rooms available")
ax1.set_title("Booked vs net occupancy by city", pad=28)
ax1.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
ax1.yaxis.grid(True, color=GRID, linewidth=0.6)
ax1.set_axisbelow(True)

# RevPAR for every city and room class: money kept divided by rooms available.
cells = base.groupby(["city", "room_class"], observed=True).agg(
    money=("revenue", "sum"), rooms=("capacity", "sum")
)
heat = (cells["money"] / cells["rooms"]).unstack()
heat = heat.loc[by_city.index, ["Standard", "Elite", "Premium", "Presidential"]]
sns.heatmap(heat, annot=True, fmt=",.0f", cmap=HEAT, linewidths=2, linecolor="#fcfcfb",
            cbar_kws={"label": "RevPAR"}, ax=ax2)
ax2.set_title("RevPAR by city and room class", pad=28)
ax2.set_xlabel("")
ax2.set_ylabel("")
ax2.tick_params(axis="y", rotation=0)
fig.tight_layout()
fig.savefig(OUT_DIR / "task8_occupancy_gap_and_revpar_heatmap.png", dpi=150)
plt.show()

# %% [markdown]
# ## Step 6: Save the hotel KPIs for Task 14

# %%
hotel_kpis = by_hotel.reset_index()
hotel_kpis["noshow_rate_pct"] = (
    base.groupby("property_id")["no_show"].sum().div(base.groupby("property_id")["booked"].sum()) * 100
).reindex(hotel_kpis["property_id"]).to_numpy()
hotel_kpis.to_csv(CLEAN_DIR / "hotel_kpis.csv", index=False)
print("Saved:", CLEAN_DIR / "hotel_kpis.csv", "| hotels:", len(hotel_kpis))
