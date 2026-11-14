# %% [markdown]
# # Task 7: Guest Satisfaction and Booking Channels
#
# **Problem statement:** How satisfied are guests in each city, and which booking channels
# (our own website, travel portals, and so on) bring in the most realized revenue? This
# shows where service quality needs attention and which channels the business depends on.
#
# **Run Task 2 first**: it creates the clean bookings file used here.

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
# ## Step 1: Load the clean bookings and add hotel details

# %%
bookings = pd.read_csv(CLEAN_DIR / "clean_bookings.csv")
hotels = pd.read_csv(DATA_DIR / "dim_hotels.csv")

# Add hotel name, hotel category and city to every booking.
data = bookings.merge(hotels, on="property_id", how="left", validate="many_to_one")
assert len(data) == len(bookings)
assert data["city"].notna().all()

# %% [markdown]
# ## Step 2: Average guest rating by city

# %%
# Many guests do not leave a rating. Those blank cells are ignored automatically when
# averaging, so we also show how many ratings each average is based on.
rating_summary = data.groupby("city")["ratings_given"].agg(
    average_rating="mean", ratings_received="count"
)
rating_summary["average_rating"] = rating_summary["average_rating"].round(2)
rating_summary = rating_summary.sort_values("average_rating", ascending=False)
print("Average rating (1 to 5) by city")
print(rating_summary)

# %% [markdown]
# ## Step 3: Realized revenue by booking channel

# %%
# Total realized revenue per channel, with each channel's share of the total.
by_platform = (
    data.groupby("booking_platform")["revenue_realized"].sum().sort_values(ascending=False)
)
platform_summary = pd.DataFrame(
    {
        "realized_revenue": by_platform,
        "share_pct": (by_platform / by_platform.sum() * 100).round(1),
    }
)
print(platform_summary.assign(realized_revenue=lambda d: d["realized_revenue"].map("{:,}".format)))

# %% [markdown]
# ## Step 4: Chart the results

# %%
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: average rating per city.
bars = axes[0].bar(
    rating_summary.index, rating_summary["average_rating"], color="#2a77b0"
)
axes[0].bar_label(bars, fmt="%.2f", padding=2)
axes[0].set_ylim(0, 5)
axes[0].set_ylabel("Average rating (out of 5)")
axes[0].set_title("Average guest rating by city")
axes[0].spines[["top", "right"]].set_visible(False)

# Right: share of realized revenue per booking channel.
axes[1].pie(
    by_platform.values,
    labels=by_platform.index,
    autopct="%1.1f%%",   # print each channel's percentage on its slice
    startangle=90,
    counterclock=False,
    wedgeprops={"linewidth": 1, "edgecolor": "white"},
)
axes[1].set_title("Share of realized revenue by booking channel")

fig.tight_layout()
fig.savefig(OUT_DIR / "task7_ratings_and_channels.png", dpi=150)
plt.show()
