# =============================================================================
# Import libraries

import pandas as pd
import geopandas as gpd

from cleaning import (
    clean_currency,
    convert_tf_to_boolean,
    convert_to_datetime,
    derive_license_status,
    categorize_properties,
    encode_property_category,
)

# =============================================================================
# Read input files

listings = pd.read_csv('data/input/listings.csv.gz') 
calendar = pd.read_csv('data/input/calendar.csv.gz')
reviews = pd.read_csv('data/input/reviews.csv.gz')
neighbourhoods = gpd.read_file('data/input/neighbourhoods.geojson')

# =============================================================================
# Cleaning Data
# =============================================================================

# Listings

#listings.drop_duplicates(inplace=True)
listings = listings.drop(columns=[
    'listing_url',#irrelevant
    'scrape_id', #irrelevant
    'name', #irrelevant
    'description', #irrelevant
    'neighborhood_overview', #nan
    'neighbourhood', #nan
    'picture_url', #irrelevant
    'host_location', #irrelevant
    'host_response_time', #nan
    'host_response_rate', #nan
    'host_url', #irrelevant
    'host_profile_id', #irrelevant
    'host_profile_url', #irrelevant
    'host_acceptance_rate', #nan
    'host_neighbourhood', #nan
    'host_total_listings_count', #nan
    'neighbourhood_group_cleansed', #nan
    'host_about', #irrelevant
    'host_thumbnail_url', #irrelevant
    'host_picture_url', #irrelevant
    'host_has_profile_pic', #irrelevant
    'host_verifications', #nan
    'host_since', #nan
    'host_name', #irrelevant
    'calendar_updated', #nan
    'calendar_last_scraped', #irrelevant
    'instant_bookable' #nan
    ])        

# Keep the useful license status without retaining license identifiers.
listings['license_status'] = derive_license_status(listings['license'])
listings.drop(columns=['license'], inplace=True)

# Convert currency-formatted prices and verify populated values were preserved.
original_price = listings['price'].copy()
listings['price'] = clean_currency(listings['price'])
failed_price_conversion = original_price.notna() & listings['price'].isna()

# Convert Airbnb t/f indicators to nullable Boolean values.
listing_boolean_columns = [
    'host_is_superhost',
    'host_identity_verified',
    'has_availability',
]

for column in listing_boolean_columns:
    listings[column] = convert_tf_to_boolean(listings[column])

# Convert listing dates to datetime values.
listing_date_columns = [
    'last_scraped',
    'price_quote_checkin_date',
    'price_quote_checkout_date',
]

for column in listing_date_columns:
    listings[column] = convert_to_datetime(listings[column])

print('Price dtype:', listings['price'].dtype)
print('Failed populated price conversions:', failed_price_conversion.sum())

# Calendar
calendar.drop_duplicates(inplace=True)
calendar['date'] = convert_to_datetime(calendar['date'])

# aggregate calendar dataframe: count num trues and num falses (idk why jeff wants this)
calendar_tf = calendar.groupby('listing_id').agg(
    true_count=('available', lambda x: (x == 't').sum()),
    false_count=('available', lambda x: (x == 'f').sum())
).reset_index() 

print(calendar_tf)

# aggregate calendar dataframe: group by listings_id, drop date, group by available, avg on minimum nights and maximum nights
#calendar_aggregated = calendar.groupby(['listing_id','available']).agg({'minimum_nights':'mean', 'maximum_nights' :'mean'}).reset_index() 

# aggregate calendar dataframe: group by listings_id, counts available days, avg on minimum nights and maximum nights
calendar_aggregated = calendar.groupby(['listing_id']).agg(
    total_available_count=('available', 'count'),
    available_true_count=('available', lambda x: (x == 't').sum()),
    minimum_nights=('minimum_nights', 'mean'),
    maximum_nights=('maximum_nights', 'mean')
).reset_index()

print(calendar_aggregated)

# Reviews
reviews.drop_duplicates(inplace=True)
reviews['date'] = convert_to_datetime(reviews['date'])
reviews = reviews.drop(columns=['id', 'reviewer_id'])

reviews_aggregated = reviews.groupby('listing_id').agg(
    review_count=("comments", "count"),
    latest_review_date=("date", "max")).reset_index()

print(reviews_aggregated)

# Neighbourhoods
neighbourhoods = neighbourhoods.drop(columns=['neighbourhood_group'])
neighbourhoods = neighbourhoods.dissolve(
    by='neighbourhood',
    as_index=False,
)

final_df = pd.merge(listings, calendar_aggregated, how='left', left_on='id', right_on='listing_id')
final_df = pd.merge(final_df, reviews_aggregated, how='left', left_on='id', right_on='listing_id')
final_df = pd.merge(
    final_df,
    neighbourhoods,
    how='left',
    left_on='neighbourhood_cleansed',
    right_on='neighbourhood',
    validate='many_to_one',
)

print(final_df)

# =============================================================================
# Data Validation
# =============================================================================

assert neighbourhoods['neighbourhood'].is_unique
assert final_df['neighbourhood'].notna().all()
assert len(final_df) == len(listings)
assert final_df['id'].is_unique
assert pd.api.types.is_numeric_dtype(listings['price'])
assert failed_price_conversion.sum() == 0
assert all(
    pd.api.types.is_bool_dtype(listings[column])
    for column in listing_boolean_columns
)
assert all(
    pd.api.types.is_datetime64_any_dtype(listings[column])
    for column in listing_date_columns
)
assert pd.api.types.is_datetime64_any_dtype(calendar['date'])
assert pd.api.types.is_datetime64_any_dtype(reviews['date'])
assert 'license' not in listings.columns
assert 'license' not in final_df.columns
assert listings['license_status'].notna().all()
assert set(listings['license_status'].unique()) == {
    'licensed',
    'exempt',
    '30_day_minimum',
    'missing',
    'unknown',
}

print(final_df.columns)

### ROI BRANCH

final_df["property_category"] = final_df["property_type"].apply(categorize_properties)
final_df["property_category_code"] = final_df["property_category"].apply(
    encode_property_category
)

assert pd.api.types.is_numeric_dtype(final_df["property_category_code"])
assert set(final_df["property_category_code"].unique()).issubset(set(range(8)))

print(final_df["property_category_code"].value_counts().sort_index())
