# Import libraries
import pandas as pd

# Pandas settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ======================================================================================
# Define columns

columns = [
    'province',
    'centre',
    'zone',
    'neighbourhood',
    'dwelling_type',
    'structure_size',
    'bachelor_units',
    'one_bu',
    'two_bu',
    'three_plus_bu',
    'total_units'
]

# ======================================================================================
# Read the dataset

u = pd.read_excel(
    '../../data/input/urban-rental-market-survey-data-number-units-building-size-2023-en.xlsx',
    sheet_name='Neighbourhood',
    skiprows=4,
    header=None,
    names=columns,
    usecols='A:K'
)

# ======================================================================================
# Clean text columns

text_cols = [
    'province',
    'centre',
    'zone',
    'neighbourhood',
    'dwelling_type',
    'structure_size'
]

for col in text_cols:
    u[col] = (
        u[col]
        .astype('string')
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )

# ======================================================================================
# Clean unit counts

unit_cols = [
    'bachelor_units',
    'one_bu',
    'two_bu',
    'three_plus_bu',
    'total_units'
]

for col in unit_cols:
    u[col] = (
        u[col]
        .astype('string')
        .str.replace(',', '', regex=False)
        .str.strip()
    )

    u[col] = pd.to_numeric(
        u[col],
        errors='coerce'
    ).astype('float64')

# ======================================================================================
# Filter only for Metro Vancouver

bc = u[
    (u['province'] == 'B.C.') &
    (u['centre'] == 'Vancouver') &
    (u['neighbourhood'] != 'Total')
].copy()

# Remove rows where all unit counts are missing
bc = bc.dropna(
    subset=unit_cols,
    how='all'
)

# ======================================================================================
# Preserve rental housing universe data

bc_clean = bc[
    [
        'province',
        'centre',
        'zone',
        'neighbourhood',
        'dwelling_type',
        'structure_size'
    ] + unit_cols
].copy()

# ======================================================================================
# Display data


print(bc_clean.to_string(index=False, na_rep='NaN'))

# ======================================================================================
# Export data

bc_clean.to_csv('rental_universe.csv', index=False, na_rep='NaN')