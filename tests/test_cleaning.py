import unittest

import pandas as pd

from cleaning import (
    NEIGHBOURHOOD_PURCHASE_PRICE_CAD,
    PropertyCategory,
    aggregate_trailing_review_counts,
    categorize_properties,
    clean_currency,
    convert_tf_to_boolean,
    convert_to_datetime,
    derive_license_status,
    encode_property_category,
)


class BasicConversionTests(unittest.TestCase):
    def test_clean_currency(self):
        values = pd.Series(["$1,234.50", "$0", "not a price", None])

        result = clean_currency(values)

        self.assertEqual(result.iloc[0], 1234.50)
        self.assertEqual(result.iloc[1], 0)
        self.assertTrue(result.iloc[2:].isna().all())

    def test_convert_tf_to_boolean(self):
        values = pd.Series(["t", "f", "unknown", None])

        result = convert_tf_to_boolean(values)

        self.assertEqual(str(result.dtype), "boolean")
        self.assertTrue(result.iloc[0])
        self.assertFalse(result.iloc[1])
        self.assertTrue(result.iloc[2:].isna().all())

    def test_convert_to_datetime(self):
        values = pd.Series(["2026-06-15", "not a date", None])

        result = convert_to_datetime(values)

        self.assertEqual(result.iloc[0], pd.Timestamp("2026-06-15"))
        self.assertTrue(result.iloc[1:].isna().all())


class LicenseStatusTests(unittest.TestCase):
    def test_derives_anonymous_license_categories(self):
        licenses = pd.Series(
            [
                None,
                "  ",
                "Exempt",
                "Licence 1234",
                "30 day minimum",
                "unrecognized text",
            ]
        )

        result = derive_license_status(licenses)

        self.assertEqual(
            result.tolist(),
            [
                "missing",
                "missing",
                "exempt",
                "licensed",
                "30_day_minimum",
                "unknown",
            ],
        )


class PropertyCategoryTests(unittest.TestCase):
    def test_supported_property_categories_and_fallback(self):
        examples = {
            "Entire condo": "Entire Apartments / Condos",
            "Entire home": "Entire Houses",
            "Entire townhouse": "Entire Townhouses",
            "Entire guesthouse": "Secondary Suites / Guest Units",
            "Private room in condo": "Private Rooms",
            "Room in hotel": "Commercial / Hospitality",
            "Shared room in home": "Other",
            "Tiny home": "Other",
            "Castle": "Other",
        }

        for property_type, expected_category in examples.items():
            with self.subTest(property_type=property_type):
                self.assertEqual(
                    categorize_properties(property_type),
                    expected_category,
                )

    def test_encodes_each_property_category_as_a_numeric_identifier(self):
        expected_codes = {
            "Entire Apartments / Condos": 0,
            "Entire Houses": 1,
            "Entire Townhouses": 2,
            "Secondary Suites / Guest Units": 3,
            "Private Rooms": 4,
            "Commercial / Hospitality": 5,
        }

        for category, expected_code in expected_codes.items():
            with self.subTest(category=category):
                self.assertEqual(
                    encode_property_category(category),
                    expected_code,
                )

    def test_rejects_unexpected_property_category(self):
        with self.assertRaisesRegex(ValueError, "Unexpected property category"):
            encode_property_category("Unknown category")


class NeighbourhoodPurchasePriceTests(unittest.TestCase):
    def test_contains_all_supplied_neighbourhood_and_category_prices(self):
        expected_neighbourhoods = {
            "Arbutus Ridge", "Cambie Corridor", "Downtown",
            "Dunbar-Southlands", "Fairview", "Grandview-Woodland",
            "Hastings-Sunrise", "Kensington-Cedar Cottage", "Kerrisdale",
            "Killarney", "Kitsilano", "Marpole", "Mount Pleasant",
            "Oakridge", "Renfrew-Collingwood", "Riley Park", "Shaughnessy",
            "South Cambie", "Strathcona", "Sunset", "UBC",
            "Victoria-Fraserview", "West End", "West Point Grey",
        }
        expected_categories = {
            PropertyCategory.ENTIRE_HOUSES.value,
            PropertyCategory.ENTIRE_TOWNHOUSES.value,
            PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value,
        }

        self.assertEqual(
            set(NEIGHBOURHOOD_PURCHASE_PRICE_CAD),
            expected_neighbourhoods,
        )
        self.assertEqual(len(NEIGHBOURHOOD_PURCHASE_PRICE_CAD), 24)
        for neighbourhood, prices in NEIGHBOURHOOD_PURCHASE_PRICE_CAD.items():
            with self.subTest(neighbourhood=neighbourhood):
                self.assertEqual(set(prices), expected_categories)
                self.assertTrue(
                    all(type(price) is int and price > 0 for price in prices.values())
                )

    def test_stores_supplied_million_cad_values_as_whole_cad(self):
        houses = PropertyCategory.ENTIRE_HOUSES.value
        townhouses = PropertyCategory.ENTIRE_TOWNHOUSES.value
        apartments = PropertyCategory.ENTIRE_APARTMENTS_CONDOS.value

        self.assertEqual(
            NEIGHBOURHOOD_PURCHASE_PRICE_CAD["Arbutus Ridge"],
            {houses: 3_110_000, townhouses: 1_654_000, apartments: 1_028_000},
        )
        self.assertEqual(
            NEIGHBOURHOOD_PURCHASE_PRICE_CAD["Downtown"],
            {houses: 1_930_000, townhouses: 1_080_000, apartments: 605_000},
        )
        self.assertEqual(
            NEIGHBOURHOOD_PURCHASE_PRICE_CAD["Shaughnessy"],
            {houses: 4_820_000, townhouses: 1_680_000, apartments: 991_000},
        )

    def test_does_not_impute_an_unsupplied_downtown_eastside_price(self):
        self.assertNotIn(
            "Downtown Eastside",
            NEIGHBOURHOOD_PURCHASE_PRICE_CAD,
        )

class AggregateTrailingReviewCountsTests(unittest.TestCase):
    def test_counts_inclusive_windows_and_excludes_future_reviews(self):
        reviews = pd.DataFrame(
            {
                "listing_id": [1, 1, 1, 1, 1, 1, 1, 2],
                "date": [
                    "2025-06-15",  # Before the 365-day window.
                    "2025-06-16",  # First day of the 365-day window.
                    "2026-03-18",  # First day of the 90-day window.
                    "2026-05-17",  # First day of the 30-day window.
                    "2026-06-15",
                    "2026-06-15",  # A separate same-day review event.
                    "2026-06-16",  # After the snapshot cutoff.
                    "2026-06-16",  # Future-only listing is excluded.
                ],
            }
        )

        result = aggregate_trailing_review_counts(
            reviews,
            as_of_date="2026-06-15",
        )

        self.assertEqual(result["listing_id"].tolist(), [1])
        row = result.iloc[0]
        self.assertEqual(row["review_count"], 6)
        self.assertEqual(row["review_count_30d"], 3)
        self.assertEqual(row["review_count_90d"], 4)
        self.assertEqual(row["review_count_365d"], 5)
        self.assertEqual(row["latest_review_date"], pd.Timestamp("2026-06-15"))

    def test_output_contains_no_review_level_fields(self):
        reviews = pd.DataFrame(
            {"listing_id": [1], "date": ["2026-06-15"]}
        )

        result = aggregate_trailing_review_counts(
            reviews,
            as_of_date="2026-06-15",
        )

        sensitive_columns = {
            "review_id",
            "reviewer_id",
            "reviewer_name",
            "comments",
        }
        self.assertTrue(sensitive_columns.isdisjoint(result.columns))

    def test_rejects_missing_listing_id(self):
        reviews = pd.DataFrame(
            {"listing_id": [None], "date": ["2026-06-15"]}
        )

        with self.assertRaisesRegex(ValueError, "listing IDs"):
            aggregate_trailing_review_counts(reviews, "2026-06-15")

    def test_rejects_invalid_date(self):
        reviews = pd.DataFrame(
            {"listing_id": [1], "date": ["not-a-date"]}
        )

        with self.assertRaisesRegex(ValueError, "dates"):
            aggregate_trailing_review_counts(reviews, "2026-06-15")

    def test_rejects_missing_required_column(self):
        reviews = pd.DataFrame({"listing_id": [1]})

        with self.assertRaisesRegex(ValueError, "missing required columns: date"):
            aggregate_trailing_review_counts(reviews, "2026-06-15")

    def test_rejects_invalid_cutoff(self):
        reviews = pd.DataFrame(
            {"listing_id": [1], "date": ["2026-06-15"]}
        )

        with self.assertRaisesRegex(ValueError, "cutoff"):
            aggregate_trailing_review_counts(reviews, "not-a-date")

    def test_returns_empty_summary_when_all_reviews_are_after_cutoff(self):
        reviews = pd.DataFrame(
            {"listing_id": [1], "date": ["2026-06-16"]}
        )

        result = aggregate_trailing_review_counts(reviews, "2026-06-15")

        self.assertTrue(result.empty)
        self.assertEqual(
            result.columns.tolist(),
            [
                "listing_id",
                "review_count",
                "review_count_30d",
                "review_count_90d",
                "review_count_365d",
                "latest_review_date",
            ],
        )


class PrepareListingDatasetTests(unittest.TestCase):
    def make_listing(self):
        columns = [
            "id", "source", "last_scraped", "neighbourhood_cleansed",
            "property_category", "room_type", "hosts_time_as_host_months",
            "host_listings_count", "host_is_superhost",
            "host_identity_verified", "accommodates", "bathrooms", "bedrooms",
            "beds", "price", "minimum_nights_avg_ntm",
            "maximum_nights_avg_ntm", "has_availability", "availability_30",
            "availability_90", "availability_365", "total_available_count",
            "available_true_count", "review_count", "review_count_30d",
            "review_count_90d", "review_count_365d", "latest_review_date",
            "review_scores_rating", "review_scores_accuracy",
            "review_scores_cleanliness", "review_scores_checkin",
            "review_scores_communication", "review_scores_location",
            "review_scores_value", "license_status",
            "estimated_occupancy_l365d", "estimated_revenue_l365d",
        ]
        listing = {column: 1 for column in columns}
        listing["last_scraped"] = pd.Timestamp("2026-06-15")
        listing["host_name"] = "must be discarded"
        listing["listing_url"] = "must be discarded"
        listing["license"] = "must be discarded"
        return listing

    def test_keeps_only_explicit_privacy_safe_columns(self):
        result = prepare_listing_dataset(pd.DataFrame([self.make_listing()]))

        self.assertEqual(result.columns[0], "listing_id")
        self.assertIn("neighbourhood", result.columns)
        self.assertIn("calendar_nights_observed", result.columns)
        self.assertNotIn("id", result.columns)
        self.assertNotIn("host_name", result.columns)
        self.assertNotIn("listing_url", result.columns)
        self.assertNotIn("license", result.columns)

    def test_rejects_missing_required_column(self):
        listing = self.make_listing()
        del listing["source"]

        with self.assertRaisesRegex(ValueError, "missing columns: source"):
            prepare_listing_dataset(pd.DataFrame([listing]))

    def test_rejects_duplicate_listing_ids(self):
        listing = self.make_listing()

        with self.assertRaisesRegex(ValueError, "duplicate listing IDs"):
            prepare_listing_dataset(pd.DataFrame([listing, listing]))


if __name__ == "__main__":
    unittest.main()
