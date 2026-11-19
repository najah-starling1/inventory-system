"""Simple command line program that talks to the Flask API.
Start the API first (python app.py), then run: python cli.py"""
import requests

API_URL = "http://127.0.0.1:5000"


def show_item(item):
    """Print one item nicely."""
    print(f"[{item['id']}] {item['product_name']} | Brand: {item['brands']} | "
          f"Price: ${item['price']} | Stock: {item['stock']}")


def view_all():
    try:
        response = requests.get(f"{API_URL}/inventory")
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return
    for item in response.json():
        show_item(item)


def view_one(item_id):
    try:
        response = requests.get(f"{API_URL}/inventory/{item_id}")
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return
    if response.status_code == 404:
        print("Item not found.")
        return
    item = response.json()
    show_item(item)
    print("Barcode:", item["barcode"])
    print("Ingredients:", item["ingredients_text"])


def add_item(name, brand, barcode, price, stock):
    # Check that price and stock are numbers
    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        print("Price must be a number and stock must be a whole number.")
        return
    data = {"product_name": name, "brands": brand, "barcode": barcode,
            "price": price, "stock": stock}
    try:
        response = requests.post(f"{API_URL}/inventory", json=data)
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return
    if response.status_code == 201:
        print("Item added!")
        show_item(response.json())
    else:
        print("Error:", response.json().get("error"))


def update_item(item_id, price, stock):
    data = {}
    try:
        if price != "":
            data["price"] = float(price)
        if stock != "":
            data["stock"] = int(stock)
    except ValueError:
        print("Price must be a number and stock must be a whole number.")
        return
    try:
        response = requests.patch(f"{API_URL}/inventory/{item_id}", json=data)
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return
    if response.status_code == 200:
        print("Item updated!")
        show_item(response.json())
    else:
        print("Error:", response.json().get("error"))


def delete_item(item_id):
    try:
        response = requests.delete(f"{API_URL}/inventory/{item_id}")
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return
    if response.status_code == 200:
        print("Item deleted.")
    else:
        print("Error:", response.json().get("error"))


def find_on_api(search_type, value):
    if search_type == "1":
        params = {"barcode": value}
    else:
        params = {"name": value}
    try:
        response = requests.get(f"{API_URL}/lookup", params=params)
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return None
    if response.status_code == 200:
        result = response.json()
        print("Name:", result["name"])
        print("Brand:", result["brand"])
        print("Ingredients:", result["ingredients"])
        return result  # so the menu can offer to add it
    else:
        print("Error:", response.json().get("error"))
        return None


def add_from_api(result, barcode, price, stock):
    """Save a product found on OpenFoodFacts into our inventory."""
    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        print("Price must be a number and stock must be a whole number.")
        return
    data = {"product_name": result["name"], "brands": result["brand"],
            "ingredients_text": result["ingredients"], "barcode": barcode,
            "price": price, "stock": stock}
    try:
        response = requests.post(f"{API_URL}/inventory", json=data)
    except requests.exceptions.ConnectionError:
        print("Cannot reach the API. Is app.py running?")
        return
    if response.status_code == 201:
        print("Product added to inventory!")
        show_item(response.json())
    else:
        print("Error:", response.json().get("error"))


def menu():
    while True:
        print("\n--- Inventory Menu ---")
        print("1. View all items")
        print("2. View one item")
        print("3. Add item")
        print("4. Update price / stock")
        print("5. Delete item")
        print("6. Find product on OpenFoodFacts")
        print("7. Quit")
        choice = input("Choose (1-7): ")

        if choice == "1":
            view_all()
        elif choice == "2":
            view_one(input("Item id: "))
        elif choice == "3":
            add_item(input("Name: "), input("Brand: "), input("Barcode (optional): "),
                     input("Price: "), input("Stock: "))
        elif choice == "4":
            update_item(input("Item id: "),
                        input("New price (press Enter to skip): "),
                        input("New stock (press Enter to skip): "))
        elif choice == "5":
            delete_item(input("Item id: "))
        elif choice == "6":
            t = input("Search by 1) barcode or 2) name? ")
            value = input("Enter value: ")
            result = find_on_api(t, value)
            if result:
                if input("Add this to inventory? (y/n): ").lower() == "y":
                    barcode = value if t == "1" else ""
                    add_from_api(result, barcode, input("Price: "), input("Stock: "))
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 7.")


if __name__ == "__main__":
    menu()
