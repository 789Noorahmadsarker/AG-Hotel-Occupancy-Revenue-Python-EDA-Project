# %% [markdown]
# # Task 1: Prepare the Daily Room-Availability Table
#
# **Problem statement:** The aggregated bookings table records, for every hotel, day and
# room type, how many rooms were sold and how many rooms were available (capacity).
# Before any analysis, can we trust this table? Find the gaps and errors, fix them, and
# add an occupancy percentage that later tasks can rely on.
#
# **What this task does**
# 1. Gets to know the table (hotels, total bookings, largest capacity).
# 2. Fills in missing capacity values.
# 3. Removes impossible records (more rooms sold than rooms available).
# 4. Creates the occupancy percentage (`occ_pct`) column.
# 5. Saves a clean file for the next tasks.

# %%
# Tools we need: pandas is the library used to work with tables of data.
from pathlib import Path
import pandas as pd

# Folder where the original CSV files live, and a folder where cleaned files will be saved.
# If you run this in Google Colab, change DATA_DIR to your Google Drive folder path.
DATA_DIR = Path("data")
CLEAN_DIR = Path("cleaned_data")
CLEAN_DIR.mkdir(exist_ok=True)

# %% [markdown]
# ## Step 1: Load and explore the data

# %%
# Read the aggregated bookings file into a table (called a "DataFrame").
agg = pd.read_csv(DATA_DIR / "fact_aggregated_bookings.csv")

# Show how many rows and columns the table has, then the first five rows.
print("Rows, columns:", agg.shape)
agg.head()

# %%
# List every unique hotel (property) ID that appears in the table.
property_ids = sorted(int(pid) for pid in agg["property_id"].unique())
print(f"Number of hotels: {len(property_ids)}")
print(property_ids)

# %%
# Add up all successful bookings for each hotel and rank from highest to lowest.
bookings_per_property = (
    agg.groupby("property_id")["successful_bookings"].sum().sort_values(ascending=False)
)
print(bookings_per_property)

# %%
# Find the largest capacity in the table, and which hotel / room type has it.
max_capacity = agg["capacity"].max()
print("Highest capacity:", max_capacity)

# Show which hotel and room type reach that capacity (duplicates removed for readability).
print(
    agg.loc[agg["capacity"] == max_capacity, ["property_id", "room_category"]]
    .drop_duplicates()
    .to_string(index=False)
)

# %% [markdown]
# ## Step 2: Fill in missing capacity values

# %%
# Count empty (missing) cells in every column.
print(agg.isna().sum())

# Show the rows where capacity is missing.
agg[agg["capacity"].isna()]

# %%
# Capacity differs a lot between hotels and room types (from 3 to 50), so using one overall
# average would be inaccurate. Instead, we fill each gap with the typical (median) capacity
# of the SAME hotel and SAME room type.
group_median = agg.groupby(["property_id", "room_category"])["capacity"].transform("median")
agg["capacity"] = agg["capacity"].fillna(group_median)

# Safety check: no missing capacity should remain.
assert agg["capacity"].isna().sum() == 0
print("Missing values left:", int(agg.isna().sum().sum()))

# %% [markdown]
# ## Step 3: Remove impossible records

# %%
# A hotel cannot sell more rooms than it has, so these rows must be data-entry errors.
over_capacity = agg[agg["successful_bookings"] > agg["capacity"]]
print("Rows with bookings greater than capacity:", len(over_capacity))
over_capacity

# %%
# Keep only valid rows. ".copy()" makes an independent table so later edits are safe.
agg_clean = agg[agg["successful_bookings"] <= agg["capacity"]].copy()
print("Rows before:", len(agg), "| Rows after:", len(agg_clean))

# %% [markdown]
# ## Step 4: Create the occupancy percentage

# %%
# Convert the date text (for example "1-May-22") into real dates so they can be matched
# with other tables later.
agg_clean["check_in_date"] = pd.to_datetime(agg_clean["check_in_date"], format="%d-%b-%y")

# Occupancy % = rooms sold divided by rooms available, multiplied by 100, rounded to 2 decimals.
agg_clean["occ_pct"] = (
    agg_clean["successful_bookings"] / agg_clean["capacity"] * 100
).round(2)

# Occupancy can now never exceed 100%.
print("Occupancy range:", agg_clean["occ_pct"].min(), "to", agg_clean["occ_pct"].max())
agg_clean.head()

# %% [markdown]
# ## Step 5: Save the clean table for the next tasks

# %%
agg_clean.to_csv(CLEAN_DIR / "clean_aggregated_bookings.csv", index=False)
print("Saved:", CLEAN_DIR / "clean_aggregated_bookings.csv", "| rows:", len(agg_clean))
