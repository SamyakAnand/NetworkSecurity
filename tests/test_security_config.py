import unittest

from networksecurity.utils.security_config import parse_cors_origins


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


if __name__ == "__main__":
    unittest.main()
