import requests

API_URL = "http://localhost:8000/"

# Create a test user
payload = {
    "username": "testuser",
    "password": "testpass"
}
response = requests.post(f"{API_URL}users/", json=payload)
if response.status_code == 200:
    print("Test user created successfully.")
else:
    print(f"Error: {response.text}")

# Add some test transactions
headers = {"Authorization": "Bearer " + requests.post(f"{API_URL}token", data={"username": "testuser", "password": "testpass"}).json()["access_token"]}

transactions = [
    {"name": "Salary", "amount": 5000, "type": "Credit", "category": "Salary", "date": "2023-10-01", "description": "Monthly salary"},
    {"name": "Rent", "amount": 1000, "type": "Debit", "category": "Rent", "date": "2023-10-05", "description": "Monthly rent"},
    {"name": "Groceries", "amount": 200, "type": "Debit", "category": "Groceries", "date": "2023-10-10", "description": "Weekly groceries"},
    {"name": "Salary", "amount": 5000, "type": "Credit", "category": "Salary", "date": "2023-11-01", "description": "Monthly salary"},
    {"name": "Utilities", "amount": 300, "type": "Debit", "category": "Utilities", "date": "2023-11-15", "description": "Electricity bill"},
]

for t in transactions:
    response = requests.post(f"{API_URL}transactions/", json=t, headers=headers)
    if response.status_code == 200:
        print(f"Transaction {t['name']} added.")
    else:
        print(f"Error adding {t['name']}: {response.text}")
