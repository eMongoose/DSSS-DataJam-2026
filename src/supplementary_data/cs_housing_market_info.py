# Import Libraries
import pandas as pd
import geopandas as gpd
import openpyxl

# Pandas settings
pd.set_option('display.max_columns', None)
pd.set_option("display.width", 1000)

# Read the input file
housing_market_info = pd.read_csv('../../data/input/TableExport.csv')

# ========================================================================================================================================
# Housing Market Information Portal: vacancy, average and median rents, turnover, and universe counts by zone

# drop unnecessary columns
housing_market_info = housing_market_info.drop(columns={
    'Availability Rate (%)', # "Data suppressed to protect confidentiality or data not statistically reliable"
    'Unnamed: 4', 
    '% Change', # Either close to zero, or redacted. Makes rest of values unreliable/can't perform statistic tests on them 
    'Unnamed: 10', # all entries are either NaN or c/d (not very reliable)
})

# rename columns
housing_market_info = housing_market_info.rename(columns={
    'Vacancy Rate (%)' : 'vacancy_rate',
    'Unnamed: 2' : 'vr_conf', # vacancy rate confidence
    'Average Rent ($)' : 'avg_rent',
    'Unnamed: 6' : 'ar_conf', # average rent confidence
    'Median Rent ($)' : 'med_rent',
    'Unnamed: 8' : 'mr_c', # median rent confidence
    # '% Change' : 'avg_percent_change'
    # 'Unnanmed: 10' : 'apc_conf' # average's percent change confidence
})

# change % average's ++ entries into 0.
# housing_market_info['avg_percent_change'] = housing_market_info['avg_percent_change'].replace('++', 0)

print(housing_market_info)
