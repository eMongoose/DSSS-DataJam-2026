#  Vacancy Rates by Rent Quartile: vacancy by price tier, more useful than a headline rate for anything about market segments.

# Import Libraries
import pandas as pd

# Pandas settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ======================================================================================


columns = [
    'province',
    'centre',
    'census_subdivision',
    'dwelling_type',
    'bedroom_type',
    'q1_vacancy',
    'q1_reliability',
    'q2_vacancy',
    'q2_reliability',
    'q3_vacancy',
    'q3_reliability',
    'q4_vacancy',
    'q4_reliability'
]

# Read the dataset
v = pd.read_excel(
    '../../data/input/urban-rental-market-survey-data-vacancy-rates-rent-quartile-2023-en.xlsx',
    sheet_name='CSD',
    skiprows=5,
    header=None,
    names=columns,
    usecols='A:M'
)

# ======================================================================================

# Clean the columns

text_cols = [
    'province',
    'centre',
    'census_subdivision',
    'dwelling_type',
    'bedroom_type'
]

for col in text_cols:
    v[col] = (
        v[col]
        .astype('string')
        .str.replace('\n', ' ', regex=False)
        .str.strip()
    )
    
# ======================================================================================
# Clean the vacancy values

vacancy_cols = [
    'q1_vacancy',
    'q2_vacancy',
    'q3_vacancy',
    'q4_vacancy'
]

v[vacancy_cols] = v[vacancy_cols].apply(
    pd.to_numeric,
    errors='coerce'
)
# ======================================================================================

# Filter only for BC

bc = v[
    (v['province'] == 'B.C.') &
    (v['centre'] == 'Vancouver') &
    (v['dwelling_type'] == 'Total') &
    (v['bedroom_type'] == 'Total') &
    (v['census_subdivision'] != 'Total')
].copy()

bc = bc.dropna(subset=vacancy_cols, how='all')

# Handle duplicates
duplicates = bc[bc.duplicated(subset=['census_subdivision'], keep=False)].copy()

# print('\nDUPLICATE MUNICIPALITIES:')
# print(duplicates[['census_subdivision'] + vacancy_cols].to_string(index=False))

# Keep duplicates separately for manual review
# duplicates.to_csv('metro_vancouver_duplicates.csv', index=False)

# Temporarily exclude unresolved municipalities
duplicate_names = duplicates['census_subdivision'].unique()

bc_clean = bc[
    ~bc['census_subdivision'].isin(
        duplicate_names
    )
].copy()

# ======================================================================================
# Rank by Q4 vacancy

ranking = (bc_clean.dropna(subset=['q4_vacancy']).sort_values('q4_vacancy').reset_index(drop=True))

ranking['rank'] = ranking.index + 1

# print(ranking[['rank', 'census_subdivision'] + vacancy_cols].to_string(index=False))

# ======================================================================================

# Export data

ranking.to_csv('output/vacancy_ranking.csv', index=False)