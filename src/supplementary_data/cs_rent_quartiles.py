# Import libraries
import pandas as pd
import numpy as np

# Pandas settings
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# ======================================================================================

columns = [
    "province",
    "centre",
    "census_subdivision",
    "dwelling_type",
    "bedroom_type",
    "p25_rent",
    "p50_rent",
    "p75_rent"
]

# Read the dataset

r = pd.read_excel(
    "../../data/input/urban-rental-market-survey-data-rent-quartiles-2023-en.xlsx",
    sheet_name="CSD",
    skiprows=4,
    header=None,
    names=columns,
    usecols="A:F,H,J"
)


# ======================================================================================
# Clean the columns

text_cols = [
    "province",
    "centre",
    "census_subdivision",
    "dwelling_type",
    "bedroom_type"
]

for col in text_cols:
    r[col] = (
        r[col]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


# ======================================================================================
# Clean rent values

rent_cols = [
    "p25_rent",
    "p50_rent",
    "p75_rent"
]

for col in rent_cols:
    r[col] = (
        r[col]
        .astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    r[col] = pd.to_numeric(
        r[col],
        errors="coerce"
    )

# Remove rows where all rent data is missing
r = r.dropna(
    subset=rent_cols,
    how="all"
)

# ========================================================================================================================================
# Filter only for Metro Vancouver

bc = r[
    (r['province'] == 'B.C.') &
    (r['centre'] == 'Vancouver') &
    (r['census_subdivision'] != 'Total')
].copy()

# ========================================================================================================================================
# Clean rent values

rent_cols = ['p25_rent', 'p50_rent', 'p75_rent']

bc[rent_cols] = bc[rent_cols].apply(
    pd.to_numeric,
    errors='coerce'
)


# ========================================================================================================================================
# Preserve rent distribution

bc_clean = bc[
    [
        'province',
        'centre',
        'census_subdivision',
        'dwelling_type',
        'bedroom_type'
    ] + rent_cols
].copy()

# Replace NA with NaN
bc_clean = bc_clean.replace({pd.NA: np.nan})

# ========================================================================================================================================
# Display data

# print(bc_clean.to_string(index=False, na_rep='NaN'))

# ========================================================================================================================================
# Export data

bc_clean.to_csv(
    'output/rent_distribution.csv',
    index=False,
    na_rep='NaN'
)