
import pandas as pd
import numpy as np
from pathlib import Path

# ===============================================================================
# Configuration
# ===============================================================================

INPUT_PATH = Path('supplementary_data/output/')
OUTPUT_PATH = Path('output/')

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


# ===============================================================================
# 1. Housing Market Information (October 2025)
# ===============================================================================

df1 = pd.read_csv(
    INPUT_PATH / 'housing_market_info.csv'
)

# Drop unnecessary columns
df1 = df1.drop(
    columns=['Unnamed: 0'],
    errors='ignore'
)

# Rename columns to indicate reporting year
df1 = df1.rename(columns={
    'Units': 'total_units_2025'
})

# Convert formatted numeric values
for col in [
    'vacancy_rate',
    'avg_rent',
    'med_rent',
    'total_units_2025'
]:
    df1[col] = pd.to_numeric(
        df1[col]
        .astype('string')
        .str.replace(',', '', regex=False)
        .str.strip(),
        errors='coerce'
    )

# Remove Vancouver aggregate row
df1 = df1[
    df1['Neighbourhood'] != 'Vancouver'
].copy()

# Standardize neighbourhood names
df1['Neighbourhood'] = (
    df1['Neighbourhood'].str.strip()
)


# ===============================================================================
# 2. Rent Percentiles by Rental Market Zone
# ===============================================================================

df2 = pd.read_csv(
    INPUT_PATH / 'percentile_rents_small_centres.csv'
)

df2 = df2.drop(
    columns=['province'],
    errors='ignore'
)

df2 = df2.rename(columns={
    'rms_zone': 'Neighbourhood'
})

df2['Neighbourhood'] = (
    df2['Neighbourhood'].str.strip()
)

# Optional: remove redundant metropolitan centre identifier
df2 = df2.drop(
    columns=['met_centre'],
    errors='ignore'
)


# ===============================================================================
# 3. Merge Housing Market Information + Rent Percentiles
# ===============================================================================

df_merged = pd.merge(
    df1,
    df2,
    on='Neighbourhood',
    how='left',
    validate='one_to_one',
    indicator=True
)

print('\n========== MERGE 1 VALIDATION ==========')
print(df_merged['_merge'].value_counts())

df_merged = df_merged.drop(
    columns=['_merge']
)


# ===============================================================================
# 4. Rent Distribution by Municipality
# ===============================================================================

df3 = pd.read_csv(
    INPUT_PATH / 'rent_distribution.csv'
)

df3 = df3.drop(
    columns=['province', 'centre'],
    errors='ignore'
)

# Keep municipality-wide rental benchmarks
df3_overall = df3[
    (df3['dwelling_type'] == 'Total') &
    (df3['bedroom_type'] == 'Total')
].copy()

df3_overall = df3_overall[
    [
        'census_subdivision',
        'p25_rent',
        'p50_rent',
        'p75_rent'
    ]
].rename(columns={
    'p25_rent': 'municipal_p25_rent',
    'p50_rent': 'municipal_p50_rent',
    'p75_rent': 'municipal_p75_rent'
})

# Keep bedroom-specific rows separately
df3_specific = df3[
    (df3['dwelling_type'] != 'Total') &
    (df3['bedroom_type'] != 'Total')
].copy()

# Note:
# df3 is NOT merged because it uses municipality-level
# geography instead of CMHC rental market zones.


# ===============================================================================
# 5. Housing Supply by Building Size (October 2023)
# ===============================================================================

df4 = pd.read_csv(
    INPUT_PATH / 'num_units_by_building_size.csv'
)

# Keep total dwelling type and total structure size
# to avoid double-counting
df4_totals = df4[
    (df4['dwelling_type'] == 'Total') &
    (df4['structure_size'] == 'Total')
].copy()

# Housing supply variables
unit_cols = [
    'bachelor_units',
    'one_bu',
    'two_bu',
    'three_plus_bu',
    'total_units'
]

# Aggregate subzones into rental market zones
df4_aggregated = (
    df4_totals
    .groupby('zone', as_index=False)[unit_cols]
    .sum(min_count=1)
    .rename(columns={
        'zone': 'Neighbourhood'
    })
)

# Rename housing supply variables by reporting year
df4_aggregated = df4_aggregated.rename(columns={
    'bachelor_units': 'bachelor_units_2023',
    'one_bu': 'one_bu_2023',
    'two_bu': 'two_bu_2023',
    'three_plus_bu': 'three_plus_bu_2023',
    'total_units': 'total_units_2023'
})

df4_aggregated['Neighbourhood'] = (
    df4_aggregated['Neighbourhood'].str.strip()
)


# ===============================================================================
# 6. Merge 2023 Housing Supply
# ===============================================================================

df_merged = pd.merge(
    df_merged,
    df4_aggregated,
    on='Neighbourhood',
    how='left',
    validate='one_to_one',
    indicator=True
)

print('\n========== MERGE 2 VALIDATION ==========')
print(df_merged['_merge'].value_counts())

df_merged = df_merged.drop(
    columns=['_merge']
)


# ===============================================================================
# 7. Feature Engineering: Housing Supply Proportions (2023)
# ===============================================================================

# Prevent division by zero
denominator = df_merged['total_units_2023'].replace(
    0, np.nan
)

df_merged['pct_studio_units_2023'] = (
    df_merged['bachelor_units_2023'] / denominator
)

df_merged['pct_1b_units_2023'] = (
    df_merged['one_bu_2023'] / denominator
)

df_merged['pct_2b_units_2023'] = (
    df_merged['two_bu_2023'] / denominator
)

df_merged['pct_3pb_units_2023'] = (
    df_merged['three_plus_bu_2023'] / denominator
)


# ===============================================================================
# 8. Validation: Dataset Structure
# ===============================================================================

print('\n========== DATASET STRUCTURE ==========')

print('Dataset shape:', df_merged.shape)

print(
    'Duplicate neighbourhoods:',
    df_merged['Neighbourhood'].duplicated().sum()
)

print('\nColumn data types:')
print(df_merged.dtypes)


# ===============================================================================
# 9. Validation: Missing Values
# ===============================================================================

print('\n========== MISSING VALUES ==========')

missing = pd.DataFrame({
    'missing_count': df_merged.isna().sum(),
    'missing_pct': df_merged.isna().mean() * 100
})

print(
    missing[
        missing['missing_count'] > 0
    ].sort_values(
        'missing_pct',
        ascending=False
    )
)


# ===============================================================================
# 10. Validation: Housing Supply Proportions
# ===============================================================================

print('\n========== HOUSING SUPPLY PROPORTIONS ==========')

pct_cols = [
    'pct_studio_units_2023',
    'pct_1b_units_2023',
    'pct_2b_units_2023',
    'pct_3pb_units_2023'
]

df_merged['proportion_sum_2023'] = (
    df_merged[pct_cols]
    .sum(axis=1, min_count=4)
)

print(
    df_merged[
        [
            'Neighbourhood',
            'proportion_sum_2023'
        ]
    ]
)

# Identify neighbourhoods where proportions do not sum to 1
invalid_proportions = df_merged[
    df_merged['proportion_sum_2023'].notna() &
    ~np.isclose(
        df_merged['proportion_sum_2023'].fillna(0),
        1.0,
        atol=0.001
    )
]

print('\nInvalid proportion sums:')
print(invalid_proportions[
    ['Neighbourhood', 'proportion_sum_2023']
])


# ===============================================================================
# 11. Validation: Housing Unit Differences (2023 vs 2025)
# ===============================================================================

print('\n========== HOUSING SUPPLY COMPARISON ==========')

df_merged['units_difference_2025_2023'] = (
    df_merged['total_units_2025'] -
    df_merged['total_units_2023']
)

# 2023 is used as the comparison baseline
df_merged['unit_difference_pct_2025_2023'] = (
    df_merged['units_difference_2025_2023'] /
    df_merged['total_units_2023'].replace(0, np.nan)
    * 100
)

unit_comparison = df_merged[
    [
        'Neighbourhood',
        'total_units_2023',
        'total_units_2025',
        'units_difference_2025_2023',
        'unit_difference_pct_2025_2023'
    ]
].copy()

unit_comparison['abs_difference'] = (
    unit_comparison[
        'unit_difference_pct_2025_2023'
    ].abs()
)

unit_comparison = unit_comparison.sort_values(
    'abs_difference',
    ascending=False
)

print('\nLargest unit count differences:')
print(unit_comparison.head(10))

# Important:
# Differences are not necessarily actual housing supply growth.
# The source tables may differ in coverage or methodology.


# ===============================================================================
# 12. Validate University Endowment Lands
# ===============================================================================

print('\n========== UNIVERSITY ENDOWMENT LANDS ==========')

uel_records = df4[
    (df4['zone'] == 'University Endowment Lands') &
    (df4['dwelling_type'] == 'Total')
][
    [
        'zone',
        'neighbourhood',
        'structure_size',
        'total_units'
    ]
]

print(uel_records)


# ===============================================================================
# 13. Prepare Final Modeling Dataset
# ===============================================================================

# Copy dataframe so validation calculations can be kept separately
df_final = df_merged.copy()

# Remove diagnostic-only variables
df_final = df_final.drop(
    columns=[
        'proportion_sum_2023',
        'units_difference_2025_2023',
        'unit_difference_pct_2025_2023'
    ],
    errors='ignore'
)

# Remove redundant or metadata variables
df_final = df_final.drop(
    columns=[
        'met_centre'
    ],
    errors='ignore'
)

# Confirm final structure
print('\n========== FINAL DATASET ==========')

print('Final dataset shape:', df_final.shape)

print(df_final.head())


# ===============================================================================
# 14. Export Datasets
# ===============================================================================

# Main CMHC modeling dataset
df_final.to_csv(
    OUTPUT_PATH / 'merged_cmhc_market_data.csv',
    index=False
)

# Municipality rental benchmarks kept separately
df3_overall.to_csv(
    OUTPUT_PATH / 'municipal_rent_benchmarks.csv',
    index=False
)

# Bedroom-specific municipality rents kept separately
df3_specific.to_csv(
    OUTPUT_PATH / 'municipal_rent_by_bedroom.csv',
    index=False
)

# Data quality diagnostics
unit_comparison.to_csv(
    OUTPUT_PATH / 'housing_supply_comparison_2023_2025.csv',
    index=False
)

missing.to_csv(
    OUTPUT_PATH / 'cmhc_missing_value_report.csv'
)

print('\n========== EXPORT COMPLETE ==========')
print('Files saved to:', OUTPUT_PATH.resolve())
