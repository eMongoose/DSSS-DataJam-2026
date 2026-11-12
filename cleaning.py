from dataclasses import dataclass
from enum import Enum

import pandas as pd


PROPERTY_CATEGORY_CODES = {
    "Entire Apartments / Condos": 0,
    "Entire Houses": 1,
    "Entire Townhouses": 2,
    "Secondary Suites / Guest Units": 3,
    "Private Rooms": 4,
    "Commercial / Hospitality": 5,
    "Other": 6,
}


class PropertyCategory(str, Enum):
    ENTIRE_APARTMENTS_CONDOS     = "Entire Apartments / Condos"
    ENTIRE_HOUSES                = "Entire Houses"
    ENTIRE_TOWNHOUSES            = "Entire Townhouses"
    SECONDARY_SUITES_GUEST_UNITS = "Secondary Suites / Guest Units"
    PRIVATE_ROOMS                = "Private Rooms"
    COMMERCIAL_HOSPITALITY       = "Commercial / Hospitality"
    
# Source: user-supplied market research, November 2026.
MARKET_PURCHASE_PRICE: dict[str, float] = {
    PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value:        708_250.0,
    PropertyCategory.ENTIRE_HOUSES.value:                   2_350_750.0,
    PropertyCategory.ENTIRE_TOWNHOUSES.value:               1_203_250.0,
    PropertyCategory.SECONDARY_SUITES_GUEST_UNITS.value:    627_871.0,
    PropertyCategory.PRIVATE_ROOMS.value:                   225_156.0,
    PropertyCategory.COMMERCIAL_HOSPITALITY.value:          762_040.0,
}

@dataclass(frozen=True)
class NeighbourhoodComposite:
    multiplier: float
    price_cad: int

COMPOSITE_BASELINE = NeighbourhoodComposite(multiplier=1.00, price_cad=1_099_100)

NEIGHBOURHOOD_COMPOSITE: dict[str, NeighbourhoodComposite] = {
    "Shaughnessy":              NeighbourhoodComposite(3.58, 3_930_000),
    "Arbutus Ridge":            NeighbourhoodComposite(2.78, 3_050_000),
    "Dunbar-Southlands":        NeighbourhoodComposite(2.40, 2_640_000),
    "West Point Grey":          NeighbourhoodComposite(2.06, 2_260_000),
    "Victoria-Fraserview":      NeighbourhoodComposite(1.82, 2_000_000),
    "Kerrisdale":               NeighbourhoodComposite(1.78, 1_960_000),
    "Riley Park":               NeighbourhoodComposite(1.44, 1_580_000),
    "Killarney":                NeighbourhoodComposite(1.37, 1_510_000),
    "Sunset":                   NeighbourhoodComposite(1.35, 1_480_000),
    "Oakridge":                 NeighbourhoodComposite(1.30, 1_430_000),
    "South Cambie":             NeighbourhoodComposite(1.28, 1_410_000),
    "Kensington-Cedar Cottage": NeighbourhoodComposite(1.28, 1_410_000),
    "Hastings-Sunrise":         NeighbourhoodComposite(1.23, 1_350_000),
    "Grandview-Woodland":       NeighbourhoodComposite(1.19, 1_310_000),
    "Kitsilano":                NeighbourhoodComposite(1.18, 1_300_000),
    "Marpole":                  NeighbourhoodComposite(0.98, 1_080_000),
    "Fairview":                 NeighbourhoodComposite(0.81,   893_000),
    "Renfrew-Collingwood":      NeighbourhoodComposite(0.76,   834_000),
    "Mount Pleasant":           NeighbourhoodComposite(0.74,   808_000),
    "Strathcona":               NeighbourhoodComposite(0.72,   795_000),
    "Downtown":                 NeighbourhoodComposite(0.56,   613_000),
    "West End":                 NeighbourhoodComposite(0.55,   610_000),
}

# Future scenario scaffold. Do not apply during the preprocessing phase.
PROPERTY_NEIGHBOURHOOD_PERCENTAGES = {
    # "Downtown": {
    #     "Entire Apartments / Condos": 0.08,
    #     "Entire Houses": 0.05,
    # },
}


def clean_currency(series):
    """Convert currency-formatted values to numeric values."""
    return pd.to_numeric(
        series.astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce",
    )


def derive_license_status(series):
    """
    Convert raw license text into more anonymous analyse categories. 
    License compliance is an investment risk especially for short-term rentals in Vancouver.
    This allows us to also compare estimated compliance patterns across neighbourhoods :D

    Output:
    A pandas Series of the same length as the input series, with values in
    {"missing", "exempt", "licensed", "30_day_minimum", "unknown"}.

    Example: 
    - missing -> no value provided / value is empty
    - "License 1234" -> licensed
    - 30 day minimum -> 30_day_minimum
    - "abcdef jeff" -> unknown
    """

    # Convert to pandas strings and remove surrounding whitespace
    # Remove the "30 day minimum" text to avoid misclassifying licenses that contain a number
    license_text = series.astype("string").str.strip()
    license_without_minimum = license_text.str.replace(
        r"30\s*day\s*minimum", "", case=False, regex=True
    )

    status = pd.Series("unknown", index=series.index, dtype="string")
    status[license_text.isna() | license_text.eq("")] = "missing"
    status[license_text.str.contains("exempt", case=False, na=False)] = "exempt"
    status[license_without_minimum.str.contains(r"\d", na=False)] = "licensed"
    status[
        license_text.str.contains(
            r"30\s*day\s*minimum", case=False, regex=True, na=False
        )
    ] = "30_day_minimum"
    return status


def convert_tf_to_boolean(series):
    """Convert Airbnb t/f values to nullable Boolean values."""
    return series.map({"t": True, "f": False}).astype("boolean")


def convert_to_datetime(series):
    """Convert values to datetime; invalid values become NaT."""
    return pd.to_datetime(series, errors="coerce")


def aggregate_trailing_review_counts(reviews, as_of_date):
    """Aggregate privacy-safe review-event counts through an inclusive cutoff."""
    required_columns = {"listing_id", "date"}
    missing_columns = sorted(required_columns.difference(reviews.columns))
    if missing_columns:
        raise ValueError(
            "reviews missing required columns: " + ", ".join(missing_columns)
        )

    cutoff = pd.to_datetime(as_of_date, errors="coerce")
    if pd.isna(cutoff):
        raise ValueError("review cutoff must be a valid date")
    cutoff = cutoff.normalize()

    review_events = reviews.loc[:, ["listing_id", "date"]].copy()
    if review_events["listing_id"].isna().any():
        raise ValueError("reviews contain missing listing IDs")

    review_events["date"] = convert_to_datetime(review_events["date"])
    if review_events["date"].isna().any():
        raise ValueError("reviews contain invalid dates")
    review_events["date"] = review_events["date"].dt.normalize()
    review_events = review_events.loc[review_events["date"] <= cutoff]

    output_columns = [
        "listing_id",
        "review_count",
        "review_count_30d",
        "review_count_90d",
        "review_count_365d",
        "latest_review_date",
    ]
    if review_events.empty:
        return pd.DataFrame(columns=output_columns)

    days_before_cutoff = (cutoff - review_events["date"]).dt.days
    review_events["in_30d"] = days_before_cutoff < 30
    review_events["in_90d"] = days_before_cutoff < 90
    review_events["in_365d"] = days_before_cutoff < 365

    aggregated = (
        review_events.groupby("listing_id", as_index=False)
        .agg(
            review_count=("date", "size"),
            review_count_30d=("in_30d", "sum"),
            review_count_90d=("in_90d", "sum"),
            review_count_365d=("in_365d", "sum"),
            latest_review_date=("date", "max"),
        )
    )
    return aggregated.loc[:, output_columns]


def categorize_properties(property_type):
    pt = str(property_type).strip()
    if pt in [
        "Entire rental unit", "Entire condo", "Entire loft", "Entire serviced apartment",
    ]:
        return "Entire Apartments / Condos"
    elif pt in [
        "Entire home", "Entire villa", "Entire bungalow", "Entire cottage",
        "Entire vacation home", "Entire place", "Entire house",
        "Entire residential home",
    ]:
        return "Entire Houses"
    elif pt in [
        "Entire townhouse", "Townhouse", "Entire residential townhouse",
    ]:
        return "Entire Townhouses"
    elif pt in [
        "Entire guest suite", "Entire guesthouse",
    ]:
        return "Secondary Suites / Guest Units"
    elif pt.startswith("Private room"):
        return "Private Rooms"
    elif pt in [
        "Room in hotel", "Room in aparthotel", "Room in boutique hotel", "Entire bed and breakfast", "Room in bed and breakfast",
    ]:
        return "Commercial / Hospitality"
    return "Other"

    

def encode_property_category(property_category):
    """Return the non-ordinal numeric code for a property category."""
    try:
        return PROPERTY_CATEGORY_CODES[property_category]
    except KeyError as exc:
        raise ValueError(
            f"Unexpected property category: {property_category!r}"
        ) from exc


def get_property_neighbourhood_percentage(
    neighbourhood,
    property_category,
    percentages=None,
):
    """Return the configured row-level percentage, or 0.0 when absent."""
    if percentages is None:
        percentages = PROPERTY_NEIGHBOURHOOD_PERCENTAGES

    neighbourhood_percentages = percentages.get(neighbourhood, {})
    return float(neighbourhood_percentages.get(property_category, 0.0))
