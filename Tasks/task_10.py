# %% [markdown]
# # Task 10: Cancellations, No-Shows and Revenue Leakage
#
# **Problem statement:** About one in four bookings is cancelled, and every cancellation costs
# the hotel money. How large is this "revenue leakage"? Is it concentrated in particular cities,
# channels or guest types (so it can be fixed locally), or does it affect the whole chain (so it
# needs a chain-wide policy)? And what would a lower cancellation rate be worth?
#
# **How to read the statistics (plain English)**
# A segment's cancellation rate can differ from the chain average by pure chance, especially when
# it has few bookings. For every segment we therefore measure how many "standard errors"
# (a z-score) it sits away from the chain average.
# - **z between -3 and +3:** the difference is within normal chance.
# - **z beyond 3 in either direction:** very unlikely to be chance (under 0.3%), so we flag it.
#
# **Run Task 2 first.**

# %%
# Tools: pandas works with tables, numpy does the statistics, matplotlib and seaborn draw charts.
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
sns.set_theme(style="white", rc={
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": GRID,
    "axes.labelcolor": SOFT, "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlelocation": "left"})

# %% [markdown]
# ## Step 1: Load the data and prepare guest segments

# %%
bookings = pd.read_csv(
    CLEAN_DIR / "clean_bookings.csv", parse_dates=["booking_date", "check_in_date", "checkout_date"]
)
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")
rooms = pd.read_csv(DATA_DIR / "dim_rooms.csv")
data = bookings.merge(hotels, on="property_id", how="left", validate="many_to_one")
data = data.merge(rooms, left_on="room_category", right_on="room_id", how="left",
                  validate="many_to_one")

# A simple 1/0 flag: 1 if the booking was cancelled.
data["cancelled"] = (data["booking_status"] == "Cancelled").astype(int)

# Segments (same groupings as Task 9, plus weekday/weekend arrival).
lead_days = (data["check_in_date"] - data["booking_date"]).dt.days
nights = (data["checkout_date"] - data["check_in_date"]).dt.days
data["lead_group"] = pd.cut(lead_days, [-1, 0, 3, 7, np.inf],
                            labels=["Same day", "1-3 days", "4-7 days", "20-24 days"])
data["stay_group"] = pd.cut(nights, [0, 1, 2, 4, 6],
                            labels=["1 night", "2 nights", "3-4 nights", "5-6 nights"])
data["party_group"] = pd.cut(data["no_guests"], [0, 1, 2, 4, 6],
                             labels=["Solo", "Couple", "3-4 guests", "5-6 guests"])
data["day_type"] = np.where(data["check_in_date"].dt.dayofweek >= 5, "Weekend", "Weekday")
print("Bookings:", len(data))

# %% [markdown]
# ## Step 2: How many bookings are lost, and how much money?

# %%
# What happened to every 100 bookings?
status_mix = (data["booking_status"].value_counts(normalize=True) * 100).round(1)
print(status_mix.to_string())

# %%
# Money view. "Generated" = the value of all bookings when made.
# "Realized" = what the hotel actually kept (cancelled bookings keep only a 40% fee).
generated = data["revenue_generated"].sum()
realized = data["revenue_realized"].sum()
leakage = generated - realized

cancelled_rows = data[data["cancelled"] == 1]
fee_kept = cancelled_rows["revenue_realized"].sum()
lost_value = cancelled_rows["revenue_generated"].sum() - fee_kept

# Safety check: all the leakage comes from cancellations (no-shows are charged in full).
assert np.isclose(leakage, lost_value)

print(f"Value of all bookings when made : {generated:,.0f}")
print(f"Money actually kept             : {realized:,.0f}")
print(f"Revenue leakage                 : {leakage:,.0f}  ({leakage / generated * 100:.1f}% of booked value)")
print(f"Cancellation fees recovered     : {fee_kept:,.0f}")
print(f"Average money lost per cancelled booking: {lost_value / len(cancelled_rows):,.0f}")

# %% [markdown]
# ## Step 3: Is any segment unusually bad? (Statistical check)

# %%
chain_rate = data["cancelled"].mean()

# Every grouping we want to test. Hotels are tested too, but only listed in the table.
dimensions = {
    "City": "city", "Hotel category": "category", "Room class": "room_class",
    "Booking channel": "booking_platform", "Lead time": "lead_group",
    "Length of stay": "stay_group", "Party size": "party_group",
    "Arrival day": "day_type", "Hotel (property ID)": "property_id",
}

records = []
for label, column in dimensions.items():
    grouped = data.groupby(column, observed=True)["cancelled"].agg(["size", "mean"])
    for segment, row in grouped.iterrows():
        n, rate = row["size"], row["mean"]
        std_error = np.sqrt(chain_rate * (1 - chain_rate) / n)     # spread expected from chance alone
        records.append({
            "dimension": label, "segment": str(segment), "bookings": int(n),
            "cancel_rate_pct": rate * 100,
            "ci_pct": 1.96 * np.sqrt(rate * (1 - rate) / n) * 100,  # 95% margin of error
            "z_score": (rate - chain_rate) / std_error,
        })
segments = pd.DataFrame(records)
segments["flagged"] = segments["z_score"].abs() >= 3

print(f"Chain-wide cancellation rate: {chain_rate * 100:.2f}%")
print(f"Segments tested: {len(segments)} | flagged as unusual: {int(segments['flagged'].sum())}")
print("\nFive segments furthest from the chain average:")
print(segments.reindex(segments["z_score"].abs().sort_values(ascending=False).index)
      .head(5)[["dimension", "segment", "bookings", "cancel_rate_pct", "z_score"]].round(2).to_string(index=False))

# %%
# The spread of cancellation rates inside each grouping (highest minus lowest segment).
spread = segments.groupby("dimension")["cancel_rate_pct"].agg(["min", "max"])
spread["gap_points"] = spread["max"] - spread["min"]
print(spread.round(2).sort_values("gap_points", ascending=False))

# %% [markdown]
# ## Step 4: What is a lower cancellation rate worth? (illustrative)
#
# Assumption: every cancellation we prevent becomes a guest who stays and pays in full, and no
# other bookings change. This is a simple what-if, not a forecast.

# %%
avg_loss = lost_value / len(cancelled_rows)
scenarios = []
for points in [1, 2, 3, 5]:
    saved = len(data) * points / 100
    gain = saved * avg_loss
    scenarios.append({"cancellation_rate_cut_points": points,
                      "bookings_saved": round(saved),
                      "extra_revenue": round(gain),
                      "uplift_pct_of_realized": round(gain / realized * 100, 2)})
what_if = pd.DataFrame(scenarios)
print(what_if.to_string(index=False))

# %% [markdown]
# ## Step 5: Charts

# %%
# Chart 1: left, what happens to 100 bookings. Right, where the booked money goes.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 3.8), gridspec_kw={"width_ratios": [1.1, 1]})

order = [("Checked Out", "Stayed", BLUE), ("Cancelled", "Cancelled", ORANGE), ("No Show", "No-show", GRAY)]
left = 0
for key, name, colour in order:
    value = status_mix[key]
    ax1.barh([0], [value], left=left, color=colour, edgecolor="#fcfcfb", linewidth=2, height=0.5)
    if value >= 8:       # wide segment: write the label inside it
        ax1.text(left + value / 2, 0, f"{name}\n{value:.1f}%", ha="center", va="center",
                 fontsize=10, color="white" if colour != GRAY else INK)
    else:                # narrow segment: write the label just above it
        ax1.text(left + value / 2, 0.3, f"{name} {value:.1f}%", ha="right", va="bottom",
                 fontsize=10, color=INK)
    left += value
ax1.set_ylim(-0.4, 0.75)
ax1.set_xlim(0, 100)
ax1.set_yticks([])
ax1.set_xlabel("% of all bookings")
ax1.set_title("What happens to every 100 bookings")

money = pd.DataFrame({
    "item": ["Value when booked", "Money kept", "Lost to cancellations"],
    "billions": [generated / 1e9, realized / 1e9, leakage / 1e9],
})
sns.barplot(data=money, y="item", x="billions", hue="item", legend=False, ax=ax2, saturation=1,
            palette={"Value when booked": GRAY, "Money kept": BLUE, "Lost to cancellations": ORANGE})
for patch, value in zip(ax2.patches, money["billions"]):
    ax2.text(value + 0.03, patch.get_y() + patch.get_height() / 2, f"{value:.2f} bn", va="center", fontsize=10)
ax2.set_xlim(0, money["billions"].max() * 1.18)
ax2.set_xlabel("Billions")
ax2.set_ylabel("")
ax2.set_title("Where the booked money goes")
fig.tight_layout()
fig.savefig(OUT_DIR / "task10_cancellation_overview.png", dpi=150)
plt.show()

# %%
# Chart 2: cancellation rate of every segment, with its 95% margin of error.
# A segment would be orange if it were unusual. The dotted line is the chain average.
shown = segments[segments["dimension"] != "Hotel (property ID)"]
fig, ax = plt.subplots(figsize=(9, 10))
y, ticks, names, headers = 0, [], [], []
for dimension in [d for d in dimensions if d != "Hotel (property ID)"]:
    ticks.append(y); names.append(dimension); headers.append(dimension)
    y += 1
    for _, row in shown[shown["dimension"] == dimension].iterrows():
        colour = ORANGE if row["flagged"] else BLUE
        ax.errorbar(row["cancel_rate_pct"], y, xerr=row["ci_pct"], fmt="o", color=colour,
                    ecolor=colour, elinewidth=1.4, capsize=3, markersize=6)
        ax.text(row["cancel_rate_pct"] + row["ci_pct"] + 0.12, y, f"{row['cancel_rate_pct']:.1f}%",
                va="center", fontsize=8.5, color=SOFT)
        ticks.append(y); names.append(f"{row['segment']}  (n={row['bookings']:,})")
        y += 1
    y += 0.7
ax.axvline(chain_rate * 100, color=SOFT, linestyle=":", linewidth=1.3)
ax.set_yticks(ticks, names)
for label in ax.get_yticklabels():
    if label.get_text() in headers:
        label.set_fontweight("bold"); label.set_color(INK)
ax.invert_yaxis()
ax.set_xlim(chain_rate * 100 - 3, chain_rate * 100 + 3)
ax.set_xlabel("Cancellation rate (%)")
n_flagged = int(segments["flagged"].sum())
headline = (f"No segment stands out: cancellations sit near {chain_rate * 100:.1f}% everywhere"
            if n_flagged == 0 else f"{n_flagged} segment(s) cancel unusually often or rarely")
ax.set_title(headline)
ax.legend(handles=[plt.Line2D([], [], marker="o", color=BLUE, linestyle="", label="Within normal chance"),
                   plt.Line2D([], [], marker="o", color=ORANGE, linestyle="", label="Unusual (z beyond 3)")],
          frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(OUT_DIR / "task10_cancellation_by_segment.png", dpi=150)
plt.show()
