# Inventory Management System

A small project for a retail company. It has:

- A **Flask API** to add, view, update and delete products
- A link to the **OpenFoodFacts API** to look up real product details
- A **command line menu (CLI)** to use everything easily
- **Tests** to check that it all works

Data is kept in a Python list (a fake database), so it resets every time you restart the API.

## Files

| File | What it does |
|------|--------------|
| `app.py` | The Flask API |
| `openfoodfacts.py` | Gets product info from OpenFoodFacts |
| `cli.py` | The menu you use in the terminal |
| `tests/` | Test files |
| `requirements.txt` | Packages to install |

## Setup

1. Make sure Python 3 is installed.
2. Open a terminal in this folder and run:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## How to Run

You need **two terminals**.

**Terminal 1** - start the API:
```bash
python app.py
```

**Terminal 2** - start the menu:
```bash
python cli.py
```

## API Endpoints

| Method | URL | What it does |
|--------|-----|--------------|
| GET | `/inventory` | Get all items |
| GET | `/inventory/<id>` | Get one item |
| POST | `/inventory` | Add an item |
| PATCH | `/inventory/<id>` | Change an item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/lookup?barcode=...` or `/lookup?name=...` | Search OpenFoodFacts |

Example item:
```json
{
  "id": 1,
  "product_name": "Nutella Hazelnut Spread",
  "brands": "Ferrero",
  "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa, skim milk powder",
  "barcode": "3017620422003",
  "price": 5.99,
  "stock": 40
}
```

Example: add an item (`product_name` is required, the rest is optional). If you give a barcode, missing brand and ingredients are filled in from OpenFoodFacts.
```bash
curl -X POST http://127.0.0.1:5000/inventory -H "Content-Type: application/json" -d '{"product_name": "Peanut Butter", "price": 6.5, "stock": 10}'
```

## Using the CLI

When you run `python cli.py` you see this menu:

```
1. View all items
2. View one item
3. Add item
4. Update price / stock
5. Delete item
6. Find product on OpenFoodFacts (then choose to add it to inventory)
7. Quit
```

Type a number and press Enter. Example - change the price of item 1:
```
Choose (1-7): 4
Item id: 1
New price (press Enter to skip): 6.50
New stock (press Enter to skip):
```

Example - find a product online and add it to your inventory:
```
Choose (1-7): 6
Search by 1) barcode or 2) name? 1
Enter value: 3017620422003
Add this to inventory? (y/n): y
Price: 5.99
Stock: 20
```

## Run the Tests

```bash
pytest
```
(or `python -m unittest discover -s tests -t .`)

The tests use `unittest.mock` to pretend to be OpenFoodFacts and the API, so no internet is needed.

## Error Handling

- Item not found -> the API returns 404
- Missing name when adding -> the API returns 400
- Typing letters for price or stock in the CLI -> a friendly message
- API not running or no internet -> a message instead of a crash
