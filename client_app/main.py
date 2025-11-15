import requests


url = "http://localhost:8080/formulas"


formula_1 = {
    "name": "Ocean Breeze",
    "materials": [
        {"name": "Ethanol", "concentration": 11.23},
        {"name": "vanilla Oil", "concentration": 5.00},
        {"name": "sea salt", "concentration": 13.77},
    ],
}

formula_2 = {
    "name": "Mountain Mist",
    "materials": [
        {"name": "Water", "concentration": 20.00},
        {"name": "Pine Extract", "concentration": 7.50},
        {"name": "Lemon Zest", "concentration": 12.50},
    ],
}

invalid_formula = {
    "name": "Invalid Formula",
    "materials": [
        {"name": "Unknown Substance", "concentration": "high"},
        {"name": "Mystery Ingredient", "concentration": -5},
    ],
}

while True:
    choice = (
        input(
            "\n1.Send formula 1\n2.Send formula 2 \n3.Send invalid formula\n4.Get all formulas\n\n"
        )
        .strip()
        .lower()
    )
    if choice == "1":
        selected_formula = formula_1
        response = requests.post(url, json=selected_formula)
        print("\nStatus Code:", response.status_code)
        print("Response Body:", response.json())
    elif choice == "2":
        selected_formula = formula_2
        response = requests.post(url, json=selected_formula)
        print("\nStatus Code:", response.status_code)
        print("Response Body:", response.json())
    elif choice == "3":
        selected_formula = invalid_formula
        response = requests.post(url, json=selected_formula)
        print("\nStatus Code:", response.status_code)
        print("Response Body:", response.json())
    elif choice == "4":
        response = requests.get(url)
        print("\nStatus Code:", response.status_code)
        print("Response Body:", response.json())
    else:
        print("Invalid choice. Please enter 1 or 2.")
