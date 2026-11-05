# %% [markdown]
# # Task 2: Clean the Individual Booking Records
#
# **Problem statement:** The booking transactions table holds one row per guest booking.
# It contains typing errors that would distort revenue and guest statistics: negative guest
# counts, absurdly large revenue amounts, and dates written in two different styles.
# Detect and correct these problems so revenue analysis can be trusted.
#
# **What this task does**
# 1. Removes bookings with zero or negative guests.
# 2. Detects and removes extreme revenue values (outliers).
# 3. Converts the three date columns into proper dates.
# 4. Saves a clean file for the next tasks.

# %%
# pandas is the library used to work with tables of data.
from pathlib import Path
import pandas as pd

# Folder where the original CSV files live, and a folder where cleaned files will be saved.
# If you run this in Google Colab, change DATA_DIR to your Google Drive folder path.
DATA_DIR = Path("data")
CLEAN_DIR = Path("cleaned_data")
CLEAN_DIR.mkdir(exist_ok=True)

# %% [markdown]
# ## Step 1: Load the data

# %%
# Read the bookings file. Each row is a single booking.
bookings = pd.read_csv(DATA_DIR / "fact_bookings.csv")
print("Rows, columns:", bookings.shape)
bookings.head()

# %% [markdown]
# ## Step 2: Remove bookings with an invalid number of guests

# %%
# A booking must have at least one guest. Rows with zero or negative guests are errors.
invalid_guests = bookings[bookings["no_guests"] <= 0]
print("Bookings with invalid guest counts:", len(invalid_guests))
invalid_guests[["booking_id", "property_id", "no_guests", "booking_status"]]

# %%
# Keep only bookings with one or more guests.
bookings = bookings[bookings["no_guests"] > 0].copy()
print("Rows after removing invalid guest counts:", len(bookings))

# %% [markdown]
# ## Step 3: Detect and remove extreme revenue values

# %%
# Statistical rule of thumb: in normally behaved data, almost every value falls within
# 3 "standard deviations" (a measure of spread) of the average. Values beyond that are
# treated as outliers, meaning likely typing errors.
average = bookings["revenue_generated"].mean()
spread = bookings["revenue_generated"].std()
upper_limit = average + 3 * spread
lower_limit = average - 3 * spread
print(f"Average revenue per booking: {average:,.0f}")
print(f"Acceptable range: {lower_limit:,.0f} to {upper_limit:,.0f}")

# %%
# Revenue can never be negative, so the lower limit does not matter in practice.
assert (bookings["revenue_generated"] >= 0).all()

# Show the bookings above the upper limit. Note how the 'revenue_realized' column shows
# the real amount (for example 9,100 versus a recorded 9,100,000), which confirms these
# are typing errors with extra digits.
outliers = bookings[bookings["revenue_generated"] > upper_limit]
print("Outlier bookings:", len(outliers))
outliers[["booking_id", "booking_status", "revenue_generated", "revenue_realized"]]

# %%
# Keep only bookings within the acceptable range.
bookings = bookings[bookings["revenue_generated"] <= upper_limit].copy()
print("Rows after removing revenue outliers:", len(bookings))
print("Largest remaining revenue value:", f"{bookings['revenue_generated'].max():,}")

# %% [markdown]
# ## Step 4: Convert date columns into proper dates
#
# The date columns mix two text styles, for example `1/5/2022` and `13-05-22`. If they are
# not converted, sorting by month and matching with the calendar table will not work.

# %%
def parse_mixed_dates(text_dates):
    """Turn dates written as 'day/month/year' OR 'day-month-year' into real dates."""
    # Try the first style (for example 1/5/2022); cells that don't fit become blank.
    style_slash = pd.to_datetime(text_dates, format="%d/%m/%Y", errors="coerce")
    # Try the second style (for example 13-05-22).
    style_dash = pd.to_datetime(text_dates, format="%d-%m-%y", errors="coerce")
    # Use the first style where it worked, otherwise the second.
    result = style_slash.fillna(style_dash)
    # Safety check: every single date must have been understood.
    assert result.notna().all(), "Some dates could not be read"
    return result


for column in ["booking_date", "check_in_date", "checkout_date"]:
    bookings[column] = parse_mixed_dates(bookings[column])

# Check-out can never be before check-in.
assert (bookings["checkout_date"] >= bookings["check_in_date"]).all()

# Confirm all three columns are now real dates.
date_columns = ["booking_date", "check_in_date", "checkout_date"]
assert all(pd.api.types.is_datetime64_any_dtype(bookings[c]) for c in date_columns)
print("All three date columns converted to dates.")
print("Check-in dates run from", bookings["check_in_date"].min().date(),
      "to", bookings["check_in_date"].max().date())

# %% [markdown]
# ## Step 5: Summary and save

# %%
# Statistical summary of the numeric columns after cleaning.
# (ratings_given has fewer values because many guests do not leave a rating. That is normal.)
print(bookings.select_dtypes("number").describe().round(2).T)

# Save the cleaned table. Dates are stored in the standard YYYY-MM-DD style.
bookings.to_csv(CLEAN_DIR / "clean_bookings.csv", index=False)
print("Saved:", CLEAN_DIR / "clean_bookings.csv", "| rows:", len(bookings))
