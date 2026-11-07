# %% [markdown]
# # Task 3: Where Are Our Rooms Filling Up? Occupancy by Room Class and City
#
# **Problem statement:** Management wants to know which room classes (Standard, Elite,
# Premium, Presidential) and which cities have the best average occupancy, so that
# pricing and marketing effort can be focused where rooms are emptiest.
#
# **Run Task 1 first**: it creates the clean occupancy file used here.

# %%
# Tools: pandas works with tables, matplotlib draws charts.
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("data")
CLEAN_DIR = Path("cleaned_data")
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

# %% [markdown]
# ## Step 1: Load the data and add readable names

# %%
# Clean occupancy table from Task 1, plus the two lookup tables (room types and hotels).
agg = pd.read_csv(CLEAN_DIR / "clean_aggregated_bookings.csv", parse_dates=["check_in_date"])
rooms = pd.read_csv(DATA_DIR / "dim_rooms.csv")
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")

# Replace the codes RT1..RT4 with readable names (Standard, Elite, ...).
# "validate" makes pandas stop with an error if the lookup would duplicate any row.
occupancy = agg.merge(
    rooms, left_on="room_category", right_on="room_id", how="left", validate="many_to_one"
).drop(columns="room_id")

# Add hotel name, hotel category (Luxury / Business) and city.
occupancy = occupancy.merge(hotels, on="property_id", how="left", validate="many_to_one")

# Safety checks: no rows lost, no names missing.
assert len(occupancy) == len(agg)
assert occupancy[["room_class", "city"]].notna().all().all()
occupancy.head()

# %% [markdown]
# ## Step 2: Average occupancy by room class

# %%
# Average the daily occupancy % for each room class, highest first.
by_room_class = (
    occupancy.groupby("room_class")["occ_pct"].mean().round(2).sort_values(ascending=False)
)
print("Average occupancy % by room class")
print(by_room_class)

# %% [markdown]
# ## Step 3: Average occupancy by city

# %%
# Same calculation for each city.
by_city = occupancy.groupby("city")["occ_pct"].mean().round(2).sort_values(ascending=False)
print("Average occupancy % by city")
print(by_city)

# %% [markdown]
# ## Step 4: Chart both results side by side

# %%
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)

for ax, series, title in [
    (axes[0], by_room_class, "By room class"),
    (axes[1], by_city, "By city"),
]:
    bars = ax.bar(series.index, series.values, color="#2a77b0")
    ax.bar_label(bars, fmt="%.1f%%", padding=2)   # print the value above each bar
    ax.set_title(title)
    ax.set_ylim(0, 75)                            # same scale on both charts
    ax.spines[["top", "right"]].set_visible(False)

axes[0].set_ylabel("Average occupancy (%)")
fig.suptitle("Average Occupancy (May to July 2022)")
fig.tight_layout()
fig.savefig(Visual_Outputs / "task3_occupancy_room_class_city.png", dpi=150)
plt.show()
