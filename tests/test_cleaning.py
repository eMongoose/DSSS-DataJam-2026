import unittest

import pandas as pd

from cleaning import (
    aggregate_trailing_review_counts,
    categorize_properties,
    clean_currency,
    convert_tf_to_boolean,
    convert_to_datetime,
    derive_license_status,
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
    def test_each_property_category_and_fallback(self):
        examples = {
            "Entire condo": "Entire Apartment / Condos",
            "Entire townhouse": "Entire Houses / Townhouses",
            "Entire guesthouse": "Secondary Suites / Guest Units",
            "Private room in condo": "Private Rooms",
            "Shared room in home": "Shared Rooms",
            "Room in hotel": "Commercial / Hospitality",
            "Tiny home": "Niche / Unconventional Accommodations",
            "Castle": "Other",
        }

        for property_type, expected_category in examples.items():
            with self.subTest(property_type=property_type):
                self.assertEqual(
                    categorize_properties(property_type),
                    expected_category,
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


if __name__ == "__main__":
    unittest.main()
