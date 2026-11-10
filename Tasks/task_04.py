# %% [markdown]
# # Task 4: Weekday or Weekend? When Do Guests Fill Our Rooms?
#
# **Problem statement:** Do hotels fill up more on weekends than on weekdays, and does
# the pattern hold in every city? The answer guides weekend pricing and promotions.
#
# **Run Task 1 first**: it creates the clean occupancy file used here.

# %%
# Tools: pandas works with tables, matplotlib draws charts.
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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
# ## Step 1: Load the data and attach calendar information

# %%
# Clean occupancy table, hotel lookup, and the calendar table (which says whether each
# date is a weekday or weekend).
agg = pd.read_csv(CLEAN_DIR / "clean_aggregated_bookings.csv", parse_dates=["check_in_date"])
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")
calendar = pd.read_csv(DATA_DIR / "dim_date.csv")

# The calendar dates are text such as "01-May-22". Convert them to real dates so they match
# the occupancy table. (If left as text, "1-May-22" would not match "01-May-22" and every
# date from the 1st to the 9th of each month would silently disappear.)
calendar["date"] = pd.to_datetime(calendar["date"], format="%d-%b-%y")

# The calendar file spells "weekday" as "weekeday". Fix the spelling for clean reports.
calendar["day_type"] = calendar["day_type"].replace({"weekeday": "weekday"})

# Attach city and day type to every occupancy row.
data = agg.merge(hotels, on="property_id", how="left", validate="many_to_one")
data = data.merge(
    calendar[["date", "day_type"]],
    left_on="check_in_date", right_on="date", how="left", validate="many_to_one",
).drop(columns="date")

# Safety checks: no rows lost, every date matched.
assert len(data) == len(agg)
assert data["day_type"].notna().all()
print("Rows:", len(data))

# %% [markdown]
# ## Step 2: Compare weekday and weekend occupancy

# %%
# Average occupancy % for weekdays versus weekends.
by_day_type = data.groupby("day_type")["occ_pct"].mean().round(2)
print("Average occupancy % by day type")
print(by_day_type)

# How many calendar days of each type are in the data (for context).
print("\nNumber of days covered:")
print(calendar[calendar["date"].isin(data["check_in_date"])]["day_type"].value_counts())

# %%
# Does the weekend effect appear in every city? Rows = city, columns = day type.
by_city_day_type = data.pivot_table(
    index="city", columns="day_type", values="occ_pct", aggfunc="mean"
).round(2)
by_city_day_type["weekend_uplift_pts"] = (
    by_city_day_type["weekend"] - by_city_day_type["weekday"]
).round(2)
print("Average occupancy % by city and day type")
print(by_city_day_type)

# %% [markdown]
# ## Step 3: Chart the result

# %%
fig, ax = plt.subplots(figsize=(7, 4.5))
by_city_day_type[["weekday", "weekend"]].plot(
    kind="bar", ax=ax, color=["#9bb7d4", "#2a77b0"], width=0.75
)
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", padding=2)  # show the value above each bar
ax.set_ylabel("Average occupancy (%)")
ax.set_xlabel("")
ax.set_ylim(0, 90)
ax.set_title("Weekday vs Weekend Occupancy by City")
ax.legend(title="")
ax.spines[["top", "right"]].set_visible(False)
plt.xticks(rotation=0)
fig.tight_layout()
fig.savefig(OUT_DIR / "task4_weekday_vs_weekend.png", dpi=150)
plt.show()

# %% [markdown]
# **Reading the result:** compare the "weekend" and "weekday" values above. A large positive
# `weekend_uplift_pts` means that city's rooms fill much more on weekends.
