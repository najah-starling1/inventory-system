"""Tests for the CLI functions. We fake the API responses with mock."""
import unittest
from unittest.mock import patch, MagicMock
import requests
import cli


def fake_response(status, data):
    response = MagicMock()
    response.status_code = status
    response.json.return_value = data
    return response


ITEM = {"id": 1, "product_name": "Corn Flakes", "brands": "Kellogg's",
        "price": 4.25, "stock": 60, "barcode": "123", "ingredients_text": "Maize"}


class TestCLI(unittest.TestCase):
    @patch("cli.requests.get")
    def test_view_all(self, mock_get):
        mock_get.return_value = fake_response(200, [ITEM])
        with patch("builtins.print") as mock_print:
            cli.view_all()
        self.assertTrue(mock_print.called)

    @patch("cli.requests.get")
    def test_view_one_not_found(self, mock_get):
        mock_get.return_value = fake_response(404, {"error": "Item not found"})
        with patch("builtins.print") as mock_print:
            cli.view_one("99")
        mock_print.assert_called_with("Item not found.")

    @patch("cli.requests.post")
    def test_add_item(self, mock_post):
        mock_post.return_value = fake_response(201, ITEM)
        cli.add_item("Corn Flakes", "Kellogg's", "123", "4.25", "60")
        mock_post.assert_called_once()

    @patch("cli.requests.post")
    def test_add_item_bad_price(self, mock_post):
        with patch("builtins.print") as mock_print:
            cli.add_item("Corn Flakes", "Kellogg's", "123", "abc", "60")
        mock_post.assert_not_called()  # should stop before calling the API
        mock_print.assert_called_with(
            "Price must be a number and stock must be a whole number.")

    @patch("cli.requests.patch")
    def test_update_item(self, mock_patch):
        mock_patch.return_value = fake_response(200, ITEM)
        cli.update_item("1", "5.00", "")
        mock_patch.assert_called_with(f"{cli.API_URL}/inventory/1", json={"price": 5.0})

    @patch("cli.requests.delete")
    def test_delete_item(self, mock_delete):
        mock_delete.return_value = fake_response(200, {"message": "Item deleted"})
        with patch("builtins.print") as mock_print:
            cli.delete_item("1")
        mock_print.assert_called_with("Item deleted.")

    @patch("cli.requests.get")
    def test_api_down(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with patch("builtins.print") as mock_print:
            cli.view_all()
        mock_print.assert_called_with("Cannot reach the API. Is app.py running?")

    @patch("cli.requests.get")
    def test_find_on_api(self, mock_get):
        mock_get.return_value = fake_response(
            200, {"name": "Nutella", "brand": "Ferrero", "ingredients": "Sugar"})
        cli.find_on_api("2", "nutella")
        mock_get.assert_called_with(f"{cli.API_URL}/lookup", params={"name": "nutella"})

    @patch("cli.requests.post")
    def test_add_from_api(self, mock_post):
        mock_post.return_value = fake_response(201, ITEM)
        found = {"name": "Nutella", "brand": "Ferrero", "ingredients": "Sugar"}
        cli.add_from_api(found, "3017620422003", "5.99", "10")
        mock_post.assert_called_with(f"{cli.API_URL}/inventory", json={
            "product_name": "Nutella", "brands": "Ferrero",
            "ingredients_text": "Sugar", "barcode": "3017620422003",
            "price": 5.99, "stock": 10})

    @patch("cli.requests.get")
    def test_find_returns_result(self, mock_get):
        found = {"name": "Nutella", "brand": "Ferrero", "ingredients": "Sugar"}
        mock_get.return_value = fake_response(200, found)
        self.assertEqual(cli.find_on_api("2", "nutella"), found)


if __name__ == "__main__":
    unittest.main()
