# %% [markdown]
# # Task 5: Month-by-Month Occupancy by City, Including the New August Data
#
# **Problem statement:** How has each city's occupancy moved from May to June to July, and
# how do the newly received August figures fit in? The August file uses slightly different
# column names and date styles, so it must be aligned with the existing data before it can
# be combined.
#
# **Run Task 1 first**: it creates the clean occupancy file used here.

# %%
# Tools: pandas works with tables, numpy helps with number checks, matplotlib draws charts.
from pathlib import Path
import numpy as np
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
# ## Step 1: Build the May to July table with hotel and room details

# %%
agg = pd.read_csv(CLEAN_DIR / "clean_aggregated_bookings.csv", parse_dates=["check_in_date"])
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")
rooms = pd.read_csv(DATA_DIR / "dim_rooms.csv")

# Add hotel name, hotel category and city, then the readable room class.
may_jul = agg.merge(hotels, on="property_id", how="left", validate="many_to_one")
may_jul = may_jul.merge(
    rooms, left_on="room_category", right_on="room_id", how="left", validate="many_to_one"
).drop(columns="room_id")
assert len(may_jul) == len(agg)
print("May-July rows:", len(may_jul))

# %% [markdown]
# ## Step 2: Load and align the August data

# %%
august = pd.read_csv(DATA_DIR / "new_data_august.csv")
print("August rows:", len(august))

# The August file calls the column "occ%", while our table calls it "occ_pct". Rename it so
# both tables line up. (If not renamed, pandas would keep two separate columns.)
august = august.rename(columns={"occ%": "occ_pct"})

# Convert the August date text into real dates, like the other tables.
august["check_in_date"] = pd.to_datetime(august["check_in_date"], format="%d-%b-%y")

# Safety check 1: the supplied occupancy % must match rooms sold / capacity.
recomputed = (august["successful_bookings"] / august["capacity"] * 100).round(2)
assert np.allclose(recomputed, august["occ_pct"], atol=0.01)

# Safety check 2: hotel names, categories and cities in the August file must agree with
# the official hotel list.
check = august.merge(hotels, on="property_id", suffixes=("", "_official"), validate="many_to_one")
assert (check["city"] == check["city_official"]).all()
assert (check["property_name"] == check["property_name_official"]).all()
print("August file agrees with the hotel list.")

# %% [markdown]
# ## Step 3: Combine May-July with August

# %%
# Keep the same columns in both tables, then stack August underneath.
# "ignore_index=True" renumbers the rows 0, 1, 2, ... so the row numbers are tidy.
columns = [
    "property_id", "property_name", "category", "city", "room_category", "room_class",
    "check_in_date", "successful_bookings", "capacity", "occ_pct",
]
all_months = pd.concat([may_jul[columns], august[columns]], ignore_index=True)

# Label each row with its month (for example 2022-05), which sorts in true calendar order.
all_months["month"] = all_months["check_in_date"].dt.to_period("M")

# Safety check: no rows lost or duplicated.
assert len(all_months) == len(may_jul) + len(august)
print("Combined rows:", len(all_months))

# %% [markdown]
# ## Step 4: Occupancy by city and month

# %%
# Rows = city, columns = month. Each value is the average occupancy %.
city_by_month = all_months.pivot_table(
    index="city", columns="month", values="occ_pct", aggfunc="mean"
).round(2)
print("Average occupancy % by city and month")
print(city_by_month)

# %%
# IMPORTANT CONTEXT: how much data does each month contain?
# The August file holds a single day (1 Aug) for only a few hotels.
coverage = all_months.groupby("month").agg(
    days=("check_in_date", "nunique"),
    hotels=("property_id", "nunique"),
    rows=("occ_pct", "size"),
)
print("Data coverage per month")
print(coverage)

# %%
# June ranking on its own (cities from highest to lowest occupancy).
june = all_months[all_months["month"] == "2022-06"]
print("June average occupancy % by city")
print(june.groupby("city")["occ_pct"].mean().round(2).sort_values(ascending=False))

# %% [markdown]
# ## Step 5: Chart May to July (full months only)
#
# August is left out of the chart on purpose: it covers one day and two cities, so it
# cannot be compared fairly with full months.

# %%
full_months = city_by_month[[m for m in city_by_month.columns if str(m) != "2022-08"]]
fig, ax = plt.subplots(figsize=(8, 4.5))
full_months.plot(kind="bar", ax=ax, width=0.8)
ax.set_ylabel("Average occupancy (%)")
ax.set_xlabel("")
ax.set_ylim(0, 80)
ax.set_title("Average Occupancy by City, May to July 2022")
ax.legend(title="Month", labels=["May 22", "Jun 22", "Jul 22"])
ax.spines[["top", "right"]].set_visible(False)
plt.xticks(rotation=0)
fig.tight_layout()
fig.savefig(OUT_DIR / "task5_city_occupancy_by_month.png", dpi=150)
plt.show()
