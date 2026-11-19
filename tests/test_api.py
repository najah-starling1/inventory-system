"""Tests for the Flask endpoints."""
import unittest
from unittest.mock import patch
import app as app_module


class TestInventoryAPI(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()
        # Reset the data before each test so tests don't affect each other
        self.original = [dict(i) for i in app_module.inventory]

    def tearDown(self):
        app_module.inventory[:] = self.original

    def test_get_all(self):
        response = self.client.get("/inventory")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 3)

    def test_get_one(self):
        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["brands"], "Ferrero")

    def test_get_one_not_found(self):
        response = self.client.get("/inventory/999")
        self.assertEqual(response.status_code, 404)

    @patch("app.get_product_by_barcode")
    def test_post_adds_item(self, mock_fetch):
        mock_fetch.return_value = None
        response = self.client.post("/inventory", json={
            "product_name": "Peanut Butter", "price": 6.5, "stock": 10})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 4)
        self.assertEqual(len(app_module.inventory), 4)

    def test_post_missing_name(self):
        response = self.client.post("/inventory", json={"price": 2})
        self.assertEqual(response.status_code, 400)

    @patch("app.get_product_by_barcode")
    def test_post_fills_details_from_api(self, mock_fetch):
        mock_fetch.return_value = {"name": "Jam", "brand": "Hartley's",
                                   "ingredients": "Strawberries, sugar"}
        response = self.client.post("/inventory", json={
            "product_name": "Jam", "barcode": "111"})
        self.assertEqual(response.get_json()["brands"], "Hartley's")

    def test_patch_updates_item(self):
        response = self.client.patch("/inventory/2", json={"price": 9.99, "stock": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["price"], 9.99)
        self.assertEqual(response.get_json()["stock"], 5)

    def test_patch_not_found(self):
        response = self.client.patch("/inventory/999", json={"price": 1})
        self.assertEqual(response.status_code, 404)

    def test_delete_item(self):
        response = self.client.delete("/inventory/3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(app_module.inventory), 2)

    def test_delete_not_found(self):
        response = self.client.delete("/inventory/999")
        self.assertEqual(response.status_code, 404)

    @patch("app.get_product_by_barcode")
    def test_lookup_by_barcode(self, mock_fetch):
        mock_fetch.return_value = {"name": "X", "brand": "Y", "ingredients": "Z"}
        response = self.client.get("/lookup?barcode=123")
        self.assertEqual(response.status_code, 200)

    def test_lookup_needs_input(self):
        response = self.client.get("/lookup")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
