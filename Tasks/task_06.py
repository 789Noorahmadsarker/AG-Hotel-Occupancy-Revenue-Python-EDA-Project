# %% [markdown]
# # Task 6: Where Does the Money Come From? Realized Revenue by City, Month and Hotel Type
#
# **Problem statement:** How much revenue was actually earned ("realized"), and how does it
# split across cities, months and hotel categories (Luxury vs Business)? Realized revenue
# is the money actually received, so cancelled bookings only count for what was kept.
#
# **Run Task 2 first**: it creates the clean bookings file used here.

# %%
# Tools: pandas works with tables, matplotlib draws charts.
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---- Folder settings (usually nothing to change) ----
# These lines tell Python where your project folders are. Each name is a folder inside the
# main project folder, and the code must be run from that main folder.
# You only need to edit a name if you renamed the folder in your own copy of the project.
# (In Google Colab, use the notebooks: their first cell connects to your Google Drive folder for you.)
DATA_DIR = Path("data")             # folder holding the 6 ORIGINAL csv files (never changed)
CLEAN_DIR = Path("cleaned_data")    # folder for the cleaned files that the tasks create and reuse
OUT_DIR = Path("outputs")           # folder where the charts (PNG pictures) are saved
OUT_DIR.mkdir(exist_ok=True)        # create the outputs folder if it does not exist yet

# %% [markdown]
# ## Step 1: Load the clean bookings and add hotel details

# %%
bookings = pd.read_csv(
    CLEAN_DIR / "clean_bookings.csv",
    parse_dates=["booking_date", "check_in_date", "checkout_date"],
)
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")

# Add hotel name, hotel category and city to every booking.
data = bookings.merge(hotels, on="property_id", how="left", validate="many_to_one")

# Safety checks: no bookings lost, every booking matched to a hotel.
assert len(data) == len(bookings)
assert data["city"].notna().all()

# Label each booking with the month of check-in (sorts in true calendar order).
data["month"] = data["check_in_date"].dt.to_period("M")
print("Bookings:", len(data), "| Total realized revenue:", f"{data['revenue_realized'].sum():,}")

# %% [markdown]
# ## Step 2: Revenue by city

# %%
# Total realized revenue per city, highest first.
by_city = data.groupby("city")["revenue_realized"].sum().sort_values(ascending=False)
print(by_city.map("{:,}".format).to_string())

# %% [markdown]
# ## Step 3: Revenue by month

# %%
# Total realized revenue per check-in month, in calendar order.
by_month = data.groupby("month")["revenue_realized"].sum().sort_index()
print(by_month.map("{:,}".format).to_string())

# %% [markdown]
# ## Step 4: Revenue by hotel category and by individual hotel

# %%
# By hotel category (Luxury versus Business).
by_category = data.groupby("category")["revenue_realized"].sum().sort_values(ascending=False)
print(by_category.map("{:,}".format).to_string())

# %%
# By individual hotel. Hotel names repeat across cities (for example there is an
# "Atliq Grands" in four cities), and even name + city is not unique in the hotel list
# (property IDs 16559 and 17559 are both "Atliq Exotica, Mumbai"). Grouping by property ID
# keeps every hotel separate.
by_hotel = (
    data.groupby(["property_id", "property_name", "city"])["revenue_realized"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
by_hotel["revenue_realized"] = by_hotel["revenue_realized"].map("{:,}".format)
print(by_hotel.to_string(index=False))

# %% [markdown]
# ## Step 5: Chart the three views

# %%
# Show money in millions on the vertical axis, for example "250M".
millions = FuncFormatter(lambda value, _: f"{value / 1e6:,.0f}M")

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
panels = [
    (axes[0], by_city, "By city"),
    (axes[1], by_month.rename(index=lambda m: m.strftime("%b %y")), "By month"),
    (axes[2], by_category, "By hotel category"),
]
for ax, series, title in panels:
    bars = ax.bar(series.index.astype(str), series.values, color="#2a77b0")
    ax.bar_label(bars, labels=[f"{v / 1e6:,.0f}M" for v in series.values], padding=2)
    ax.set_title(title)
    ax.yaxis.set_major_formatter(millions)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Realized revenue")
fig.suptitle("Realized Revenue, May to July 2022")
fig.tight_layout()
fig.savefig(OUT_DIR / "task6_revenue.png", dpi=150)
plt.show()
