
# Import Libraries
import pandas as pd

# Pandas settings
pd.set_option('display.max_columns', None)
pd.set_option("display.width", 1000)

# ========================================================================================================================================
# Read the input file

p = pd.read_excel(
    '../../data/input/percentile-rents-urban-centres-pooled-small-centre-rental-market-2025-en.xlsx',
    sheet_name=0,
    header=None
)

# ========================================================================================================================================
# Define columns

columns = [
    "province",
    "met_centre",
    "rms_zone",

    "studio_p30",
    "studio_p50",
    "studio_p65",
    "studio_p80",

    "one_bedroom_p30",
    "one_bedroom_p50",
    "one_bedroom_p65",
    "one_bedroom_p80",

    "two_bedroom_p30",
    "two_bedroom_p50",
    "two_bedroom_p65",
    "two_bedroom_p80",

    "three_plus_bedroom_p30",
    "three_plus_bedroom_p50",
    "three_plus_bedroom_p65",
    "three_plus_bedroom_p80"
]

# ========================================================================================================================================
# Locate header row

header_rows = p.index[
    p.iloc[:, 0]
    .astype("string")
    .str.strip()
    .eq("Province")
]

if len(header_rows) == 0:
    raise ValueError("Could not locate the 'Province' header row.")

header_row = header_rows[0]

# ========================================================================================================================================
# Select columns

# Columns A-C contain geographical information.
# From column D onward, rent values alternate with reliability codes.
# Keep rent values only: D, F, H, J, ..., AH.

selected_columns = [0, 1, 2] + list(range(3, 35, 2))

p = p.iloc[
    header_row + 1:,
    selected_columns
].copy()

p.columns = columns

# ========================================================================================================================================
# Clean text columns

text_cols = [
    "province",
    "met_centre",
    "rms_zone"
]

for col in text_cols:
    p[col] = (
        p[col]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

# ========================================================================================================================================
# Clean rent values

rent_cols = columns[3:]

for col in rent_cols:
    p[col] = (
        p[col]
        .astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    p[col] = pd.to_numeric(
        p[col],
        errors="coerce"
    ).astype("float64")

# ========================================================================================================================================
# Filter only for Metro Vancouver

bc = p[
    (p["province"] == "British Columbia") &
    (p["met_centre"].str.upper() == "VANCOUVER") &
    p["rms_zone"].notna() &
    (p["rms_zone"].str.upper() != "TOTAL")
].copy()

# Remove rows where all rent percentiles are missing
bc = bc.dropna(
    subset=rent_cols,
    how="all"
)

# ========================================================================================================================================
# Preserve rent distribution

bc_clean = bc[
    [
        "province",
        "met_centre",
        "rms_zone"
    ] + rent_cols
].copy()

# ========================================================================================================================================
# Display data

print("\nMETRO VANCOUVER 2025 RENT PERCENTILES:")

print(
    bc_clean.to_string(
        index=False,
        na_rep="NaN"
    )
)

print("\nTotal rows:", len(bc_clean))

# ========================================================================================================================================
# Export data

bc_clean.to_csv(
    "mv_rent_percentiles_2025.csv",
    index=False,
    na_rep="NaN"
)
