"""Flask REST API for the inventory system."""
from flask import Flask, jsonify, request
from openfoodfacts import get_product_by_barcode, search_product_by_name

app = Flask(__name__)

# Our fake database: just a list of dictionaries.
# The fields look like what OpenFoodFacts returns.
inventory = [
    {
        "id": 1,
        "product_name": "Nutella Hazelnut Spread",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa, skim milk powder",
        "barcode": "3017620422003",
        "price": 5.99,
        "stock": 40,
    },
    {
        "id": 2,
        "product_name": "Tomato Ketchup",
        "brands": "Heinz",
        "ingredients_text": "Tomatoes, vinegar, sugar, salt, spice",
        "barcode": "5000157024671",
        "price": 3.49,
        "stock": 25,
    },
    {
        "id": 3,
        "product_name": "Corn Flakes",
        "brands": "Kellogg's",
        "ingredients_text": "Maize, sugar, malt flavouring, salt",
        "barcode": "5053827154735",
        "price": 4.25,
        "stock": 60,
    },
]


def find_item(item_id):
    """Return the item with this id, or None."""
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def next_id():
    """Give the next free id number."""
    if len(inventory) == 0:
        return 1
    return max(item["id"] for item in inventory) + 1


# GET /inventory -> all items
@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(inventory), 200


# GET /inventory/<id> -> one item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


# POST /inventory -> add a new item
@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)
    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400

    new_item = {
        "id": next_id(),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
    }

    # If a barcode was given, try to fill in missing details from the API
    if new_item["barcode"]:
        details = get_product_by_barcode(new_item["barcode"])
        if details:
            if not new_item["brands"]:
                new_item["brands"] = details["brand"]
            if not new_item["ingredients_text"]:
                new_item["ingredients_text"] = details["ingredients"]

    inventory.append(new_item)
    return jsonify(new_item), 201


# PATCH /inventory/<id> -> update an item
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data sent"}), 400

    # Only these fields may be changed
    for field in ["product_name", "brands", "ingredients_text", "barcode", "price", "stock"]:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200


# DELETE /inventory/<id> -> remove an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200


# GET /lookup?barcode=123  or  /lookup?name=nutella -> search OpenFoodFacts
@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        result = get_product_by_barcode(barcode)
    elif name:
        result = search_product_by_name(name)
    else:
        return jsonify({"error": "Give a barcode or a name"}), 400

    if result is None:
        return jsonify({"error": "Product not found or API unavailable"}), 404
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)  # debug mode shows helpful errors
