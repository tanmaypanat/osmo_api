import requests

url = "http://localhost:8080/formulas"


formula_1 = {
    "name": "Ocean Breeze",
    "materials": [
        {"name": "Ethanol", "concentration": 11.23},
        {"name": "vanilla Oil", "concentration": 5.00},
        {"name": "sea salt", "concentration": 13.7},
    ],
}

response = requests.post(url, json=formula_1)
print("\nStatus Code:", response.status_code)
print("Response Body:", response.json())
