"""Tests for the external API functions. We fake the internet with mock."""
import unittest
from unittest.mock import patch, MagicMock
import openfoodfacts


class TestOpenFoodFacts(unittest.TestCase):
    @patch("openfoodfacts.requests.get")
    def test_barcode_found(self, mock_get):
        fake = MagicMock()
        fake.json.return_value = {"status": 1, "product": {
            "product_name": "Corn Flakes", "brands": "Kellogg's",
            "ingredients_text": "Maize, sugar"}}
        mock_get.return_value = fake

        result = openfoodfacts.get_product_by_barcode("123")
        self.assertEqual(result["brand"], "Kellogg's")

    @patch("openfoodfacts.requests.get")
    def test_barcode_not_found(self, mock_get):
        fake = MagicMock()
        fake.json.return_value = {"status": 0}
        mock_get.return_value = fake
        self.assertIsNone(openfoodfacts.get_product_by_barcode("000"))

    @patch("openfoodfacts.requests.get")
    def test_api_failure(self, mock_get):
        mock_get.side_effect = Exception("No internet")
        self.assertIsNone(openfoodfacts.get_product_by_barcode("123"))

    @patch("openfoodfacts.requests.get")
    def test_search_by_name(self, mock_get):
        fake = MagicMock()
        fake.json.return_value = {"products": [{
            "product_name": "Tomato Ketchup", "brands": "Heinz",
            "ingredients_text": "Tomatoes"}]}
        mock_get.return_value = fake
        result = openfoodfacts.search_product_by_name("ketchup")
        self.assertEqual(result["name"], "Tomato Ketchup")

    @patch("openfoodfacts.requests.get")
    def test_search_no_results(self, mock_get):
        fake = MagicMock()
        fake.json.return_value = {"products": []}
        mock_get.return_value = fake
        self.assertIsNone(openfoodfacts.search_product_by_name("zzzz"))


if __name__ == "__main__":
    unittest.main()
