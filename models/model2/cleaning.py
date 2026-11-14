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
NEIGHBOURHOOD_PURCHASE_PRICE_CAD: dict[str, dict[str, int]] = {
    "Arbutus Ridge": {
        PropertyCategory.ENTIRE_HOUSES.value: 3_110_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_654_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 1_028_000,
    },
    "Cambie Corridor": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_620_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_600_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 1_020_000,
    },
    "Downtown": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_930_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_080_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 605_000,
    },
    "Downtown-Eastside": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_700_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 990_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 624_500,
    },
    "Dunbar-Southlands": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_860_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_553_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 965_000,
    },
    "Fairview": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_249_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_110_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 797_000,
    },
    "Grandview-Woodland": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_640_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_220_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 589_000,
    },
    "Hastings-Sunrise": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_560_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 820_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 493_000,
    },
    "Kensington-Cedar Cottage": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_580_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_250_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 659_000,
    },
    "Kerrisdale": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_960_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_520_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 979_000,
    },
    "Killarney": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_690_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 826_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 526_000,
    },
    "Kitsilano": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_610_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_180_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 714_000,
    },
    "Marpole": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_890_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_440_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 683_000,
    },
    "Mount Pleasant": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_670_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_060_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 648_000,
    },
    "Oakridge": {
        PropertyCategory.ENTIRE_HOUSES.value: 3_410_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_500_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 993_000,
    },
    "Renfrew-Collingwood": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_490_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 856_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 501_000,
    },
    "Riley Park": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_990_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_090_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 948_000,
    },
    "Shaughnessy": {
        PropertyCategory.ENTIRE_HOUSES.value: 4_820_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_680_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 991_000,
    },
    "South Cambie": {
        PropertyCategory.ENTIRE_HOUSES.value: 4_050_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_410_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 1_030_000,
    },
    "Strathcona": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_470_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 900_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 644_000,
    },
    "Sunset": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_580_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 855_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 530_000,
    },
    "UBC": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_120_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_560_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 996_000,
    },
    "Victoria-Fraserview": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_990_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_058_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 658_000,
    },
    "West End": {
        PropertyCategory.ENTIRE_HOUSES.value: 1_971_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_130_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 601_000,
    },
    "West Point Grey": {
        PropertyCategory.ENTIRE_HOUSES.value: 2_690_000,
        PropertyCategory.ENTIRE_TOWNHOUSES.value: 1_240_000,
        PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value: 736_000,
    },
}


ADU_PRIVATE_ROOM_PRICES_CAD = {
    "Arbutus Ridge": (834_000, 313_000),
    "Cambie Corridor": (None, None),
    "Downtown": (562_000, 193_000),
    "Downtown-Eastside": (500_000, 391_000),
    "Dunbar-Southlands": (765_000, 279_000),
    "Fairview": (581_000, 251_000),
    "Grandview-Woodland": (520_000, 187_000),
    "Hastings-Sunrise": (418_000, 153_000),
    "Kensington-Cedar Cottage": (481_000, 194_000),
    "Kerrisdale": (791_000, 296_000),
    "Killarney": (437_000, 161_000),
    "Kitsilano": (652_000, 228_000),
    "Marpole": (581_000, 214_000),
    "Mount Pleasant": (520_000, 205_000),
    "Oakridge": (890_000, 317_000),
    "Renfrew-Collingwood": (404_000, 154_000),
    "Riley Park": (537_000, 250_000),
    "Shaughnessy": (1_261_000, 421_000),
    "South Cambie": (1_011_000, 340_000),
    "Strathcona": (437_000, 198_000),
    "Sunset": (426_000, 153_000),
    "UBC": (None, None),
    "Victoria-Fraserview": (534_000, 200_000),
    "West End": (576_000, 191_000),
    "West Point Grey": (715_000, 247_000),
}

for neighbourhood, (adu_price, room_price) in (
    ADU_PRIVATE_ROOM_PRICES_CAD.items()
):
    prices = NEIGHBOURHOOD_PURCHASE_PRICE_CAD[neighbourhood]

    if adu_price is not None:
        prices[
            PropertyCategory.SECONDARY_SUITES_GUEST_UNITS.value
        ] = adu_price

    if room_price is not None:
        prices[
            PropertyCategory.PRIVATE_ROOMS.value
        ] = room_price
        
        

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
