import unittest

from networksecurity.utils.security_config import (
    parse_cors_origins,
    resolve_mongo_db_url,
)


class ParseCorsOriginsTests(unittest.TestCase):
    def test_empty_configuration_disables_cross_origin_access(self):
        self.assertEqual(parse_cors_origins(None), [])
        self.assertEqual(parse_cors_origins("  ,  "), [])

    def test_parses_and_deduplicates_explicit_origins(self):
        self.assertEqual(
            parse_cors_origins(
                " https://EXAMPLE.com/, http://localhost:3000, https://example.com "
            ),
            ["https://example.com", "http://localhost:3000"],
        )

    def test_rejects_wildcard_origins(self):
        with self.assertRaisesRegex(ValueError, "explicit origins"):
            parse_cors_origins("*")

    def test_rejects_non_origin_urls(self):
        invalid_values = (
            "ftp://example.com",
            "https://example.com/app",
            "https://example.com?token=value",
            "https://example.com#section",
            "https://user:password@example.com",
            "https://example.com:99999",
        )
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_cors_origins(value)


class ResolveMongoDbUrlTests(unittest.TestCase):
    def test_prefers_current_variable(self):
        self.assertEqual(
            resolve_mongo_db_url(
                {
                    "MONGO_DB_URL": " mongodb://primary ",
                    "MONGODB_URL_KEY": "mongodb://legacy",
                }
            ),
            "mongodb://primary",
        )

    def test_accepts_legacy_variable_when_current_one_is_missing(self):
        self.assertEqual(
            resolve_mongo_db_url({"MONGODB_URL_KEY": " mongodb://legacy "}),
            "mongodb://legacy",
        )

    def test_uses_legacy_variable_when_current_one_is_blank(self):
        self.assertEqual(
            resolve_mongo_db_url(
                {
                    "MONGO_DB_URL": "  ",
                    "MONGODB_URL_KEY": "mongodb://legacy",
                }
            ),
            "mongodb://legacy",
        )

    def test_requires_a_non_blank_url(self):
        for values in ({}, {"MONGO_DB_URL": " "}, {"MONGODB_URL_KEY": ""}):
            with self.subTest(values=values):
                with self.assertRaisesRegex(RuntimeError, "Set MONGO_DB_URL"):
                    resolve_mongo_db_url(values)


if __name__ == "__main__":
    unittest.main()
