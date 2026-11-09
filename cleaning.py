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
    """Replace raw license details with an anonymous status."""
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
