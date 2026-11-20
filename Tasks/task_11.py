# %% [markdown]
# # Task 11: Booking Channel Mix and Dependency
#
# **Problem statement:** Hotels pay commission on bookings from travel agencies, so the mix of
# booking channels matters. Which channels bring the money, how dependent is each city on a few
# of them, is the mix shifting over time, and do some channels bring better guests than others?
#
# **Channel groups used here**
# - **Direct:** direct online and direct offline (no agency commission).
# - **Travel agency (OTA):** makeyourtrip, logtrip, tripster, journey.
# - **Unclassified:** the catch-all "others" label, which hides the real source of those bookings.
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
GROUP_COLOURS = {"Direct": BLUE, "Travel agency (OTA)": ORANGE, "Unclassified": GRAY}
sns.set_theme(style="white", rc={
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": GRID,
    "axes.labelcolor": SOFT, "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlelocation": "left"})

# %% [markdown]
# ## Step 1: Load the data and group the channels

# %%
bookings = pd.read_csv(
    CLEAN_DIR / "clean_bookings.csv", parse_dates=["booking_date", "check_in_date", "checkout_date"]
)
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")
data = bookings.merge(hotels, on="property_id", how="left", validate="many_to_one")

CHANNEL_GROUP = {
    "direct online": "Direct", "direct offline": "Direct",
    "makeyourtrip": "Travel agency (OTA)", "logtrip": "Travel agency (OTA)",
    "tripster": "Travel agency (OTA)", "journey": "Travel agency (OTA)",
    "others": "Unclassified",
}
data["channel_group"] = data["booking_platform"].map(CHANNEL_GROUP)
assert data["channel_group"].notna().all()          # every channel must belong to a group

data["cancelled"] = (data["booking_status"] == "Cancelled").astype(int)
data["lead_days"] = (data["check_in_date"] - data["booking_date"]).dt.days
print("Bookings:", len(data), "| Channels:", data["booking_platform"].nunique())

# %% [markdown]
# ## Step 2: Channel scorecard

# %%
def scorecard(by):
    """Volume, money and guest quality for each channel (or channel group)."""
    t = data.groupby(by).agg(
        bookings=("booking_id", "size"),
        money_kept=("revenue_realized", "sum"),
        money_per_booking=("revenue_realized", "mean"),
        cancel_rate_pct=("cancelled", lambda s: s.mean() * 100),
        avg_rating=("ratings_given", "mean"),
        avg_lead_days=("lead_days", "mean"),
    )
    t.insert(1, "booking_share_pct", t["bookings"] / t["bookings"].sum() * 100)
    t.insert(3, "money_share_pct", t["money_kept"] / t["money_kept"].sum() * 100)
    return t.sort_values("money_kept", ascending=False)


by_channel = scorecard("booking_platform")
by_group = scorecard("channel_group")
print("By channel")
print(by_channel.drop(columns="money_kept").round(2))
print("\nBy channel group")
print(by_group.drop(columns="money_kept").round(2))

# %% [markdown]
# ## Step 3: How dependent is each city on a few channels?
#
# We use the **Herfindahl-Hirschman Index (HHI)**: square each channel's share of the money and
# add them up, then scale to 10,000. Higher means more dependence on a single channel.
# Dividing 10,000 by the HHI gives an easy-to-picture number: the **effective number of channels**
# (if four channels were exactly equal, that number would be 4).
#
# "Others" is left out here because it mixes many unknown sources, which would distort the result.

# %%
def concentration(money):
    """HHI and effective number of channels for rows of money-per-channel."""
    shares = money.div(money.sum(axis=1), axis=0)
    hhi = (shares ** 2).sum(axis=1) * 10_000
    return pd.DataFrame({"hhi": hhi, "effective_channels": 10_000 / hhi})


named = data[data["booking_platform"] != "others"]
chain_money = named.groupby("booking_platform")["revenue_realized"].sum().to_frame().T
city_money = named.pivot_table(index="city", columns="booking_platform",
                               values="revenue_realized", aggfunc="sum")
category_money = named.pivot_table(index="category", columns="booking_platform",
                                   values="revenue_realized", aggfunc="sum")
result = pd.concat([concentration(chain_money).rename(index={"revenue_realized": "Whole chain"}),
                    concentration(city_money), concentration(category_money)])
print(result.round(1))

# %% [markdown]
# ## Step 4: Is the mix shifting over time?

# %%
# Week by week share of money from each channel group, using calendar weeks starting on Monday.
data["week_start"] = data["check_in_date"] - pd.to_timedelta(data["check_in_date"].dt.dayofweek, unit="D")
weekly = data.pivot_table(index="week_start", columns="channel_group",
                          values="revenue_realized", aggfunc="sum")
weekly = weekly.div(weekly.sum(axis=1), axis=0) * 100
weekly = weekly.iloc[1:]            # the first week holds a single day (1 May), so we skip it
print(f"Weeks analysed: {len(weekly)}  ({weekly.index.min():%d %b} to {weekly.index.max():%d %b})")

# Trend = average change in share per week, from a straight-line fit.
weeks = np.arange(len(weekly))
trend = pd.Series({group: np.polyfit(weeks, weekly[group], 1)[0] for group in weekly.columns})
print("\nChange in share per week (percentage points):")
print(trend.round(3).to_string())

# %% [markdown]
# ## Step 5: Do channels bring different quality? (permutation test)
#
# For each measure we take the gap between the best and worst channel. Then we shuffle the
# channel labels at random 1,000 times to see how big a gap pure chance produces. If the real gap
# is no bigger than the shuffled gaps, the channels are not truly different.

# %%
rng = np.random.default_rng(42)                      # fixed seed so results repeat exactly
codes, names = pd.factorize(data["booking_platform"])


def gap_test(values, n_shuffles=1000):
    """Return the real best-minus-worst gap and the share of shuffles that beat it (p-value)."""
    values = np.asarray(values, dtype=float)
    keep = ~np.isnan(values)
    v, c = values[keep], codes[keep]

    def gap(labels):
        means = np.bincount(labels, weights=v, minlength=len(names)) / np.bincount(labels, minlength=len(names))
        return means.max() - means.min()

    real = gap(c)
    shuffled = np.array([gap(rng.permutation(c)) for _ in range(n_shuffles)])
    return real, (1 + (shuffled >= real).sum()) / (n_shuffles + 1)


tests = {"Cancellation rate (points)": data["cancelled"] * 100,
         "Money kept per booking": data["revenue_realized"],
         "Guest rating (1 to 5)": data["ratings_given"],
         "Lead time (days)": data["lead_days"]}
rows = []
for label, series in tests.items():
    real, p_value = gap_test(series)
    rows.append({"measure": label, "best_minus_worst": real, "p_value": p_value,
                 "real_difference": "Yes" if p_value < 0.05 else "No (chance)"})
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% [markdown]
# ## Step 6: Charts

# %%
# Chart 1: left, share of money by channel. Right, how each city and hotel category splits.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1, 1.15]})

chart = by_channel.reset_index()
chart["group"] = chart["booking_platform"].map(CHANNEL_GROUP)
sns.barplot(data=chart, y="booking_platform", x="money_share_pct", hue="group", palette=GROUP_COLOURS,
            dodge=False, saturation=1, ax=ax1)
for bar in [p for p in ax1.patches if p.get_width() > 0]:
    ax1.text(bar.get_width() + 0.6, bar.get_y() + bar.get_height() / 2, f"{bar.get_width():.1f}%",
             va="center", fontsize=9.5)
ax1.set_xlim(0, chart["money_share_pct"].max() * 1.15)
ax1.set_xlabel("% of money kept")
ax1.set_ylabel("")
ax1.set_title("Share of money kept, by channel")
ax1.legend(frameon=False, loc="lower right", title="")

city_mix = data.pivot_table(index="city", columns="channel_group", values="revenue_realized", aggfunc="sum")
cat_mix = data.pivot_table(index="category", columns="channel_group", values="revenue_realized", aggfunc="sum")
mix = pd.concat([city_mix, cat_mix])
mix = mix.div(mix.sum(axis=1), axis=0) * 100
mix = mix[["Direct", "Travel agency (OTA)", "Unclassified"]]
left = np.zeros(len(mix))
for group in mix.columns:
    ax2.barh(mix.index, mix[group], left=left, color=GROUP_COLOURS[group], label=group,
             edgecolor="#fcfcfb", linewidth=2, height=0.62)
    for i, (start, value) in enumerate(zip(left, mix[group])):
        ax2.text(start + value / 2, i, f"{value:.0f}%", ha="center", va="center", fontsize=9,
                 color=INK if group == "Unclassified" else "white")
    left += mix[group].to_numpy()
ax2.axhline(3.5, color=GRID, linewidth=1)
ax2.invert_yaxis()
ax2.set_xlim(0, 100)
ax2.set_xlabel("% of money kept")
ax2.set_title("Channel group mix by city and hotel category", pad=28)
ax2.legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=9)
fig.tight_layout()
fig.savefig(OUT_DIR / "task11_channel_mix.png", dpi=150)
plt.show()

# %%
# Chart 2: weekly share of money by channel group. Flat lines mean a stable mix.
fig, ax = plt.subplots(figsize=(10, 4.4))
for group in ["Unclassified", "Travel agency (OTA)", "Direct"]:
    ax.plot(weekly.index, weekly[group], color=GROUP_COLOURS[group], linewidth=2, marker="o", markersize=4)
    ax.annotate(group, (weekly.index[-1], weekly[group].iloc[-1]), xytext=(8, 0),
                textcoords="offset points", va="center", fontsize=9.5, annotation_clip=False)
ax.set_ylim(0, 60)
ax.set_xticks(weekly.index[::2], [f"{d:%d %b}" for d in weekly.index[::2]])
ax.set_xlabel("Week starting (Monday)")
ax.set_ylabel("% of money kept")
ax.set_title("Channel mix is steady from week to week")
ax.yaxis.grid(True, color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
fig.tight_layout(rect=[0, 0, 0.85, 1])
fig.savefig(OUT_DIR / "task11_channel_mix_trend.png", dpi=150)
plt.show()
