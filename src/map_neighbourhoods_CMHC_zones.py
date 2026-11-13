
import pandas as pd

pd.set_option('display.max_columns', None)

# Load datasets
airbnb_df = pd.read_csv(
    "../data/output/listings_cleaned.csv.gz"
)

cmhc_df = pd.read_csv(
    "output/merged_cmhc_market_data.csv"
)

# Filter for only vancouver
vancouver_zones = [
    "West End/Stanley Park",
    "English Bay",
    "Downtown",
    "South Granville/Oak",
    "Kitsilano/Point Grey",
    "Westside/Kerrisdale",
    "Marpole",
    "Mount Pleasant/Renfrew Heights",
    "East Hastings",
    "Southeast Vancouver"
]

cmhc_df = cmhc_df[
    cmhc_df["Neighbourhood"].isin(vancouver_zones)
].copy()

print("Remaining CMHC zones:", len(cmhc_df))

# Standardize names for comparison

airbnb_df["neighbourhood_clean"] = (
    airbnb_df["neighbourhood"]
    .astype("string")
    .str.strip()
    .str.lower()
)

cmhc_df["neighbourhood_clean"] = (
    cmhc_df["Neighbourhood"]
    .astype("string")
    .str.strip()
    .str.lower()
)

# Compare neighbourhoods

airbnb_zones = set(
    airbnb_df["neighbourhood_clean"].dropna()
)

cmhc_zones = set(
    cmhc_df["neighbourhood_clean"].dropna()
)

print("Unique Airbnb neighbourhoods:", len(airbnb_zones))
print("Unique CMHC zones:", len(cmhc_zones))
print("Exact matches:", len(airbnb_zones & cmhc_zones))

print("\nUnmatched Airbnb neighbourhoods:")

for neighbourhood in sorted(airbnb_zones - cmhc_zones):
    print(neighbourhood)


#



# Airbnb neighbourhood -> CMHC rental market zone
zone_mapping = {
    "Arbutus Ridge": "Westside/Kerrisdale",
    "Downtown": "Downtown",
    "Downtown Eastside": "East Hastings",
    "Dunbar Southlands": "Westside/Kerrisdale",
    "Fairview": "South Granville/Oak",
    "Grandview-Woodland": "East Hastings",
    "Hastings-Sunrise": "East Hastings",
    "Kensington-Cedar Cottage": "Mount Pleasant/Renfrew Heights",
    "Kerrisdale": "Westside/Kerrisdale",
    "Killarney": "Southeast Vancouver",
    "Kitsilano": "Kitsilano/Point Grey",
    "Marpole": "Marpole",
    "Mount Pleasant": "Mount Pleasant/Renfrew Heights",
    "Oakridge": "Westside/Kerrisdale",
    "Renfrew-Collingwood": "Southeast Vancouver",
    "Riley Park": "South Granville/Oak",
    "Shaughnessy": "Westside/Kerrisdale",
    "South Cambie": "South Granville/Oak",
    "Strathcona": "East Hastings",
    "Sunset": "Southeast Vancouver",
    "Victoria-Fraserview": "Southeast Vancouver",
    "West End": "West End/Stanley Park",
    "West Point Grey": "Kitsilano/Point Grey"
}

# Map Airbnb neighbourhoods to CMHC zones
airbnb_df["cmhc_zone"] = airbnb_df[
    "neighbourhood"
].map(zone_mapping)

# Check for unmatched Airbnb neighbourhoods
print("Unmapped Airbnb listings:")
print(airbnb_df["cmhc_zone"].isna().sum())

# Rename CMHC join key
cmhc_df = cmhc_df.rename(columns={
    "Neighbourhood": "cmhc_zone"
})

# Merge market data into Airbnb listings
df_final = airbnb_df.merge(
    cmhc_df,
    on="cmhc_zone",
    how="left",
    validate="many_to_one",
    indicator=True
)

# Verify results
print("\nMerge results:")
print(df_final["_merge"].value_counts())

print("\nOriginal Airbnb rows:", len(airbnb_df))
print("Final merged rows:", len(df_final))

assert len(df_final) == len(airbnb_df)

# Remove merge indicator
df_final = df_final.drop(columns="_merge")


# Remove temporary columns
df_final = df_final.drop(
    columns=["neighbourhood_clean"],
    errors="ignore"
)

# Check unique listing IDs
print("Unique listings:", df_final["listing_id"].nunique())

print("Total rows:", len(df_final))

# Check missing values
missing = (
    df_final.isna()
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\nMissing values (%):")
print(missing[missing > 0])

# Check CMHC zone assignments
print("\nListings by CMHC zone:")
print(df_final["cmhc_zone"].value_counts())

# Check scraped dates
print("\nAirbnb scraping dates:")
print(
    pd.to_datetime(
        df_final["last_scraped"],
        errors="coerce"
    ).agg(["min", "max"])
)

print(df_final)

# Save
df_final.to_csv(
    "output/airbnb_cmhc_merged.csv",

    index=False,
)

