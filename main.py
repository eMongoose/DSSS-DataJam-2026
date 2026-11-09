# =============================================================================
# Import libraries

import pandas as pd 
import geopandas as gpd

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


# Calendar
calendar.drop_duplicates(inplace=True)

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
reviews = reviews.drop(columns=['id', 'reviewer_id'])


# Neighbourhoods
neighbourhoods.drop_duplicates(inplace=True)
neighbourhoods = neighbourhoods.drop(columns=['neighbourhood_group']) 