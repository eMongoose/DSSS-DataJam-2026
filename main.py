# =============================================================================
# Import libraries

import pandas as pd
import geopandas as gpd

from cleaning import (
    clean_currency,
    convert_tf_to_boolean,
    convert_to_datetime,
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
    'source', #metadata
    'last_scraped', #irrelevant
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
    'license', #nan
    'instant_bookable' #nan
    ])        

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

# Convert listing quote dates to datetime values.
listing_date_columns = [
    'price_quote_checkin_date',
    'price_quote_checkout_date',
]

for column in listing_date_columns:
    listings[column] = convert_to_datetime(listings[column])

print('Price dtype:', listings['price'].dtype)
print('Failed populated price conversions:', failed_price_conversion.sum())

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


# Calendar
calendar.drop_duplicates(inplace=True)
calendar['date'] = convert_to_datetime(calendar['date'])

assert pd.api.types.is_datetime64_any_dtype(calendar['date'])

# aggregate calendar dataframe: count num trues and num falses (idk why jeff wants this)
calendar_tf = calendar.groupby('listing_id').agg(
    true_count=('available', lambda x: (x == 't').sum()),
    false_count=('available', lambda x: (x == 'f').sum())
).reset_index()

print(calendar_tf)

# aggregate calendar dataframe: group by listings_id, drop date, group by available, avg on minimum nights and maximum nights
calendar_aggregated = calendar.groupby(['listing_id','available']).agg({'minimum_nights':'mean', 'maximum_nights' :'mean'})

print(calendar_aggregated)

# Reviews
reviews.drop_duplicates(inplace=True)
reviews['date'] = convert_to_datetime(reviews['date'])
reviews = reviews.drop(columns=['id', 'reviewer_id'])

<<<<<<< HEAD
reviews_tf = reviews.groupby('listing_id').agg(
    review_count=("comments", "count"),
    latest_review_date=("date", "max")).reset_index()

print(reviews_tf)
=======
assert pd.api.types.is_datetime64_any_dtype(reviews['date'])

>>>>>>> 1fac0673667082e78fb052cd52b281a3f0d204a7

# Neighbourhoods
neighbourhoods.drop_duplicates(inplace=True)
neighbourhoods = neighbourhoods.drop(columns=['neighbourhood_group'])
