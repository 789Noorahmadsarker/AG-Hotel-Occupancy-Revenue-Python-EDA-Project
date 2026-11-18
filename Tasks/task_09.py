# %% [markdown]
# # Task 9: Booking Behaviour: How Far Ahead Do Guests Book and How Long Do They Stay?
#
# **Problem statement:** Two numbers shape how a hotel plans staff, prices and promotions:
# the **lead time** (days between booking and arrival) and the **length of stay** (nights).
# Measure both, and find out how they differ between Luxury and Business hotels and between
# solo travellers, couples and groups.
#
# **Run Task 2 first.**

# %%
# Tools: pandas works with tables, numpy sets up the groups, matplotlib and seaborn draw charts.
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
STEPS = ["#86b6ef", "#3987e5", "#1c5cab", "#104281"]   # one blue, light to dark = short to long
sns.set_theme(style="white", rc={
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": GRID,
    "axes.labelcolor": SOFT, "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlelocation": "left"})

# %% [markdown]
# ## Step 1: Load the data and measure lead time and nights

# %%
bookings = pd.read_csv(
    CLEAN_DIR / "clean_bookings.csv", parse_dates=["booking_date", "check_in_date", "checkout_date"]
)
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")
data = bookings.merge(hotels, on="property_id", how="left", validate="many_to_one")

# Lead time = days from booking to arrival. Nights = days from arrival to departure.
data["lead_days"] = (data["check_in_date"] - data["booking_date"]).dt.days
data["nights"] = (data["checkout_date"] - data["check_in_date"]).dt.days

# Safety checks: nobody arrives before booking, and every stay lasts at least one night.
assert (data["lead_days"] >= 0).all() and (data["nights"] >= 1).all()
print("Bookings:", len(data))
print("Lead time (days): average", round(data["lead_days"].mean(), 2),
      "| median", data["lead_days"].median(), "| longest", data["lead_days"].max())
print("Average length of stay (ALOS):", round(data["nights"].mean(), 2), "nights")

# %%
# How are lead times spread? Count bookings for each number of days ahead.
print(data["lead_days"].value_counts().sort_index().to_string())

# Interesting gap: nobody books between 8 and 19 days ahead. Bookings are either made within
# a week of arrival, or about three weeks ahead. We group them to match this pattern.
print("\nBookings made 8 to 19 days ahead:", int(data["lead_days"].between(8, 19).sum()))

# %% [markdown]
# ## Step 2: Group the bookings into easy-to-read segments

# %%
# Lead time groups (right = True means the number on the right edge belongs to that group).
data["lead_group"] = pd.cut(
    data["lead_days"], bins=[-1, 0, 3, 7, np.inf],
    labels=["Same day", "1-3 days", "4-7 days", "20-24 days"],
)
# Length of stay groups.
data["stay_group"] = pd.cut(
    data["nights"], bins=[0, 1, 2, 4, 6],
    labels=["1 night", "2 nights", "3-4 nights", "5-6 nights"],
)
# Party size groups.
data["party_group"] = pd.cut(
    data["no_guests"], bins=[0, 1, 2, 4, 6],
    labels=["Solo", "Couple", "3-4 guests", "5-6 guests"],
)
for column in ["lead_group", "stay_group", "party_group"]:
    print((data[column].value_counts(normalize=True, sort=False) * 100).round(1).to_string(), "\n")

# %% [markdown]
# ## Step 3: Compare guest profiles

# %%
def profile(by):
    """Average behaviour for each group: size, lead time, length of stay, spend."""
    t = data.groupby(by, observed=True).agg(
        bookings=("booking_id", "size"),
        avg_lead_days=("lead_days", "mean"),
        avg_nights=("nights", "mean"),
        avg_booking_value=("revenue_generated", "mean"),
    )
    t["share_pct"] = t["bookings"] / t["bookings"].sum() * 100
    return t.round(2)


print("By hotel category")
print(profile("category"))
print("\nBy party size")
print(profile("party_group"))
print("\nBy city")
print(profile("city"))

# %%
# Do guests who book far ahead stay longer? Share of each stay length within each lead group.
lead_vs_stay = pd.crosstab(data["lead_group"], data["stay_group"], normalize="index") * 100
print("Length of stay mix (%) within each lead-time group")
print(lead_vs_stay.round(1))

# %% [markdown]
# ## Step 4: Charts
#
# Each bar shows 100% of a group's bookings, split into lead-time (left) or stay-length (right)
# groups, from short (light) to long (dark). Percentages are written inside segments of 7% or more.

# %%
def share_bars(ax, groups, column, labels, title):
    """Draw one 100% stacked horizontal bar per group, with % labels inside big segments."""
    table = pd.crosstab(data[groups], data[column], normalize="index") * 100
    left = np.zeros(len(table))
    for i, name in enumerate(labels):
        values = table[name].to_numpy()
        ax.barh(table.index.astype(str), values, left=left, color=STEPS[i], label=name,
                edgecolor="#fcfcfb", linewidth=2, height=0.62)
        for y, (start, v) in enumerate(zip(left, values)):
            if v >= 7:
                ax.text(start + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color=INK if i == 0 else "white")
        left += values
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel("% of bookings")
    ax.legend(frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0),
              fontsize=8.5, handlelength=1, columnspacing=1)


lead_labels = ["Same day", "1-3 days", "4-7 days", "20-24 days"]
stay_labels = ["1 night", "2 nights", "3-4 nights", "5-6 nights"]
fig, axes = plt.subplots(2, 2, figsize=(13, 7), gridspec_kw={"height_ratios": [2, 4]})
share_bars(axes[0, 0], "category", "lead_group", lead_labels, "")
share_bars(axes[0, 1], "category", "stay_group", stay_labels, "")
share_bars(axes[1, 0], "party_group", "lead_group", lead_labels, "")
share_bars(axes[1, 1], "party_group", "stay_group", stay_labels, "")
axes[0, 0].set_title("How far ahead guests book", pad=34)
axes[0, 1].set_title("How long guests stay", pad=34)
for ax in axes[0]:
    ax.set_xlabel("")
fig.suptitle("Luxury guests plan ahead and stay longer than Business guests",
             x=0.01, ha="left", fontweight="bold", fontsize=13)
fig.tight_layout()
fig.savefig(OUT_DIR / "task9_lead_time_and_stay.png", dpi=150)
plt.show()
