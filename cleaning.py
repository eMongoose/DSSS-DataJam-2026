import pandas as pd


def prepare_listing_dataset(data):
    """
    Anything not listed here will be discarded.
    This is so we know what to keep for when we're going to train our model.
    """
    columns_to_keep = {
        "id": "listing_id",
        "source": "source",
        "last_scraped": "last_scraped",
        "neighbourhood_cleansed": "neighbourhood",
        "property_category": "property_category",
        "room_type": "room_type",
        "hosts_time_as_host_months": "hosts_time_as_host_months",
        "host_listings_count": "host_listings_count",
        "host_is_superhost": "host_is_superhost",
        "host_identity_verified": "host_identity_verified",
        "accommodates": "accommodates",
        "bathrooms": "bathrooms",
        "bedrooms": "bedrooms",
        "beds": "beds",
        "price": "price",
        "minimum_nights_avg_ntm": "minimum_nights_avg_ntm",
        "maximum_nights_avg_ntm": "maximum_nights_avg_ntm",
        "has_availability": "has_availability",
        "availability_30": "availability_30",
        "availability_90": "availability_90",
        "availability_365": "availability_365",
        "total_available_count": "calendar_nights_observed",
        "available_true_count": "calendar_nights_available",
        "review_count": "review_count",
        "review_count_30d": "review_count_30d",
        "review_count_90d": "review_count_90d",
        "review_count_365d": "review_count_365d",
        "latest_review_date": "latest_review_date",
        "review_scores_rating": "review_scores_rating",
        "review_scores_accuracy": "review_scores_accuracy",
        "review_scores_cleanliness": "review_scores_cleanliness",
        "review_scores_checkin": "review_scores_checkin",
        "review_scores_communication": "review_scores_communication",
        "review_scores_location": "review_scores_location",
        "review_scores_value": "review_scores_value",
        "license_status": "license_status",
        "estimated_occupancy_l365d": "estimated_occupancy_l365d",
        "estimated_revenue_l365d": "estimated_revenue_l365d",
    }

    missing = sorted(set(columns_to_keep).difference(data.columns))
    if missing:
        raise ValueError(
            "cannot prepare listing dataset; missing columns: " + ", ".join(missing)
        )

    prepared = data.loc[:, list(columns_to_keep)].rename(columns=columns_to_keep)

    if prepared["listing_id"].isna().any():
        raise ValueError("prepared listing dataset contains missing listing IDs")
    if prepared["listing_id"].duplicated().any():
        raise ValueError("prepared listing dataset contains duplicate listing IDs")
    if not pd.api.types.is_datetime64_any_dtype(prepared["last_scraped"]):
        raise TypeError("last_scraped must be converted to datetime before preparation")

    return prepared


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
