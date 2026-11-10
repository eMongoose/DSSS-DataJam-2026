import pandas as pd


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


def aggregate_trailing_review_counts(
    reviews, as_of_date, windows=(30, 90, 365)
):
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

    if (
        not windows
        or len(set(windows)) != len(windows)
        or any(
            isinstance(window, bool)
            or not isinstance(window, int)
            or window <= 0
            for window in windows
        )
    ):
        raise ValueError("review windows must be unique positive integers")

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
        *(f"review_count_{window}d" for window in windows),
        "latest_review_date",
    ]
    if review_events.empty:
        return pd.DataFrame(columns=output_columns)

    aggregated = (
        review_events.groupby("listing_id", as_index=False)
        .agg(
            review_count=("date", "size"),
            latest_review_date=("date", "max"),
        )
    )

    for window in windows:
        window_start = cutoff - pd.Timedelta(days=window - 1)
        window_counts = (
            review_events.loc[review_events["date"] >= window_start]
            .groupby("listing_id")
            .size()
        )
        aggregated[f"review_count_{window}d"] = (
            aggregated["listing_id"].map(window_counts).fillna(0).astype("int64")
        )

    return aggregated.loc[:, output_columns]


def categorize_properties(property_type):
    pt = str(property_type).strip()
    if pt in [
        "Entire rental unit", "Entire condo", "Entire loft", "Entire serviced apartment",
    ]:
        return "Entire Apartment / Condos"
    if pt in [
        "Entire home", "Entire townhouse", "Entire villa", "Entire bungalow", "Entire cottage", "Entire vacation home", "Entire place",
    ]:
        return "Entire Houses / Townhouses"
    if pt in [
        "Entire guest suite", "Entire guesthouse",
    ]:
        return "Secondary Suites / Guest Units"
    if pt.startswith("Private room"):
        return "Private Rooms"
    if pt.startswith("Shared room"):
        return "Shared Rooms"
    if pt in [
        "Room in hotel", "Room in aparthotel", "Room in boutique hotel", "Entire bed and breakfast",
    ]:
        return "Commercial / Hospitality"
    if pt in [
        "Tiny home","Camper/RV","Boat","Tower","Cave","Earthen home","Hut",
    ]:
        return "Niche / Unconventional Accommodations"
    return "Other"
