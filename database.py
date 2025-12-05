import json
import os

# Database file path
DB_FILE = 'users_database.json'

# Load users from file
def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return get_default_users()
    else:
        return get_default_users()

# Save users to file
def save_users(users_db):
    with open(DB_FILE, 'w') as f:
        json.dump(users_db, f, indent=4)

# Default users (includes demo account)
def get_default_users():
    return {
        'demo@example.com': {
            'password': 'demo123',
            'full_name': 'John Doe',
            'birth_date': '1990-01-15',
            'gender': 'Male',
            'phone': '+1 (555) 123-4567',
            'bank_name': 'First National Bank',
            'account_number': '1234567890',
            'routing_number': '021000021',
            'account_type': 'Checking',
            'balance': 15750.50,
            'transactions': [
                {'date': '2024-12-01', 'description': 'Salary Deposit', 'amount': 3500.00, 'type': 'credit'},
                {'date': '2024-11-28', 'description': 'Grocery Store', 'amount': -125.50, 'type': 'debit'},
                {'date': '2024-11-25', 'description': 'Electric Bill', 'amount': -89.00, 'type': 'debit'},
                {'date': '2024-11-22', 'description': 'Gas Station', 'amount': -45.00, 'type': 'debit'},
                {'date': '2024-11-20', 'description': 'Restaurant', 'amount': -67.80, 'type': 'debit'}
            ]
        }
    }

# Validate email format
def validate_email(email):
    import re
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

# Login user
def login_user(email, password, users_db):
    if email in users_db:
        if users_db[email]['password'] == password:
            return True
    return False

# Signup user
def signup_user(user_data, users_db):
    users_db[user_data['email']] = user_data
    save_users(users_db)
    return True

# Add transaction to user account
def add_transaction(email, transaction_data, users_db):
    if email in users_db:
        if 'transactions' not in users_db[email]:
            users_db[email]['transactions'] = []
        
        # Add transaction to beginning of list (most recent first)
        users_db[email]['transactions'].insert(0, transaction_data)
        
        # Update balance
        users_db[email]['balance'] += transaction_data['amount']
        
        save_users(users_db)
        return True
    return False