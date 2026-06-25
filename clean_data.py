"""
clean_data.py
--------------
Purpose: Take the raw Delhi AQI data (one row per pollutant per station)
and turn it into a clean, analysis-ready table (one row per station per
timestamp, with each pollutant as its own column).
"""

import pandas as pd

# ---- STEP 1: Load the raw data ----
df = pd.read_csv("data/delhi_aqi_raw.csv")
print("Loaded shape:", df.shape)

# ---- STEP 2: Look BEFORE we touch anything ----
# Always inspect raw data before cleaning it - you can't fix what you
# haven't measured.
print("\nUnique stations:", df["station"].nunique())
print("Unique pollutants measured:", df["pollutant_id"].unique())

# How many missing values are already hiding in avg_value?
# NOTE: pandas automatically converts common "missing data" text (like
# "NA", "N/A", "null") into real NaN values the moment we load the CSV
# with read_csv() - so by this point, the text "NA" doesn't exist
# anymore, it's already a proper missing value. That's why we check
# with .isna() here, not by comparing to the string "NA".
na_count = df["avg_value"].isna().sum()
print(f"Rows where avg_value is missing: {na_count} out of {len(df)}")

# ---- STEP 3: Convert text columns to real numbers ----
# pd.to_numeric() converts a text column into actual numbers.
# errors="coerce" means: if something can't be converted (like the
# text 'NA'), turn it into NaN (pandas' official "missing number" marker)
# instead of crashing the whole program.
for col in ["min_value", "max_value", "avg_value"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Sanity check: after conversion, how many real missing values (NaN) do we have?
# This should roughly match the na_count we counted above.
print("\nMissing avg_value after conversion:", df["avg_value"].isna().sum())

# ---- STEP 4: Decide what to do with missing values ----
# We drop rows where avg_value is missing, because avg_value is the
# core number we need for forecasting - a row without it isn't useful
# to us. (min/max being missing is less critical, we keep those as NaN.)
before = len(df)
df = df.dropna(subset=["avg_value"])
print(f"\nDropped {before - len(df)} rows with missing avg_value")
print("Remaining shape:", df.shape)

# ---- STEP 5: Fix the timestamp column ----
# last_update currently looks like text: "24-06-2026 18:00:00"
# pd.to_datetime() converts it into a real datetime object, which lets
# us later do things like "sort by time" or "filter last 7 days" properly.
# dayfirst=True tells pandas the format is DD-MM-YYYY, not MM-DD-YYYY,
# since Indian government data uses the day-first convention.
df["last_update"] = pd.to_datetime(df["last_update"], dayfirst=True)

# ---- STEP 6: Reshape from "long" to "wide" format ----
# Right now: one row = one pollutant at one station at one time.
# We want: one row = one station at one time, with separate columns
# for PM2.5, PM10, NO2, etc.
#
# pivot_table does exactly this kind of reshaping.
# - index: what defines a unique ROW in our new table
# - columns: which column's VALUES become new column headers
# - values: which column's data fills in those new columns
# - aggfunc="mean": if there happen to be duplicate entries for the
#   same station+time+pollutant, average them instead of crashing
wide_df = df.pivot_table(
    index=["station", "latitude", "longitude", "last_update"],
    columns="pollutant_id",
    values="avg_value",
    aggfunc="mean"
).reset_index()

print("\nReshaped (wide) data:")
print("Shape:", wide_df.shape)
print(wide_df.head())

# ---- STEP 7: Save the cleaned, reshaped data ----
wide_df.to_csv("data/delhi_aqi_clean.csv", index=False)
print("\nSaved to data/delhi_aqi_clean.csv")