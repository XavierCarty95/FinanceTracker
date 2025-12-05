from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from models import SessionLocal, User, Transaction, Expense, Debt, Investment, create_tables
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re

def get_db():
    return SessionLocal()

# Validate email format
def validate_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

# Load users (for compatibility, return dict)
def load_users():
    db = get_db()
    try:
        users = db.query(User).all()
        users_by_email = {}
        for user in users:
            users_by_email[user.email] = {
                'password': user.password,
                'full_name': user.full_name,
                'birth_date': user.birth_date.strftime('%Y-%m-%d') if user.birth_date else '',
                'gender': user.gender,
                'phone': user.phone,
                'bank_name': user.bank_name,
                'account_number': user.account_number,
                'routing_number': user.routing_number,
                'account_type': user.account_type,
                'balance': user.balance,
                'budget': user.budget or {},
                'transactions': [
                    {
                        'id': transaction.id,
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description,
                        'amount': transaction.amount,
                        'type': transaction.type,
                        'notes': transaction.notes
                    }
                    for transaction in db.query(Transaction).filter(Transaction.user_id == user.id).all()
                ],
                'expenses': [
                    {
                        'id': expense.id,
                        'name': expense.name,
                        'category': expense.category,
                        'cost': expense.cost
                    }
                    for expense in db.query(Expense).filter(Expense.user_id == user.id).all()
                ],
                'debts': [
                    {
                        'id': debt.id,
                        'name': debt.name,
                        'amount_owed': debt.amount_owed,
                        'interest_rate': debt.interest_rate,
                        'monthly_pay': debt.monthly_pay
                    }
                    for debt in db.query(Debt).filter(Debt.user_id == user.id).all()
                ],
                'investments': [
                    {
                        'id': investment.id,
                        'name': investment.name,
                        'amount': investment.amount,
                        'risk_level': investment.risk_level
                    }
                    for investment in db.query(Investment).filter(Investment.user_id == user.id).all()
                ]
            }
        return users_by_email
    finally:
        db.close()

# Save users (not needed for SQL)
def save_users(users_db):
    pass

# Login user
def login_user(email, password, users_db=None):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and check_password_hash(user.password, password):
            return True
        return False
    finally:
        db.close()

# Signup user
def signup_user(user_data, users_db=None):
    db = get_db()
    try:
        existing = db.query(User).filter(User.email == user_data['email']).first()
        if existing:
            return False
        user = User(
            email=user_data['email'],
            password=generate_password_hash(user_data['password']),
            full_name=user_data['full_name'],
            birth_date=datetime.strptime(user_data['birth_date'], '%Y-%m-%d').date() if user_data.get('birth_date') else None,
            gender=user_data.get('gender'),
            phone=user_data.get('phone'),
            bank_name=user_data.get('bank_name'),
            account_number=user_data.get('account_number'),
            routing_number=user_data.get('routing_number'),
            account_type=user_data.get('account_type'),
            balance=user_data.get('balance', 0.0),
            budget=user_data.get('budget', {})
        )
        db.add(user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

# Add transaction to user account
def add_transaction(email, transaction_data, users_db=None):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        trans = Transaction(
            user_id=user.id,
            date=datetime.strptime(transaction_data['date'], '%Y-%m-%d').date(),
            description=transaction_data['description'],
            amount=transaction_data['amount'],
            type=transaction_data['type'],
            notes=transaction_data.get('notes', '')
        )
        db.add(trans)
        user.balance += transaction_data['amount']
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

# Add expense to user account
def add_expense(email, expense_data, users_db=None):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"

        name = expense_data['name'].strip()
        category = expense_data['category'].strip().lower()
        # Prevent duplicate expense entries for the same user/category/name (case-insensitive)
        existing = db.query(Expense).filter(
            Expense.user_id == user.id,
            func.lower(Expense.name) == func.lower(name),
            func.lower(Expense.category) == func.lower(category)
        ).first()
        if existing:
            return False, "Expense already exists"

        expense = Expense(
            user_id=user.id,
            name=expense_data['name'],
            category=expense_data['category'],
            cost=expense_data['cost']
        )
        db.add(expense)
        db.commit()
        return True, None
    except Exception as e:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

def update_expense(email, expense_id, expense_data):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
        if not expense:
            return False, "Expense not found"
        name = expense_data['name'].strip()
        category = expense_data['category'].strip().lower()
        dup = db.query(Expense).filter(
            Expense.user_id == user.id,
            func.lower(Expense.name) == func.lower(name),
            func.lower(Expense.category) == func.lower(category),
            Expense.id != expense_id
        ).first()
        if dup:
            return False, "Duplicate expense in this category"
        expense.name = name
        expense.category = expense_data['category']
        expense.cost = expense_data['cost']
        db.commit()
        return True, None
    except Exception:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

def delete_expense(email, expense_id):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
        if not expense:
            return False, "Expense not found"
        db.delete(expense)
        db.commit()
        return True, None
    except Exception:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

# Add debt to user account
def add_debt(email, debt_data, users_db=None):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        debt = Debt(
            user_id=user.id,
            name=debt_data['name'],
            amount_owed=debt_data['amount_owed'],
            interest_rate=debt_data['interest_rate'],
            monthly_pay=debt_data['monthly_pay']
        )
        db.add(debt)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def update_debt(email, debt_id, debt_data):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == user.id).first()
        if not debt:
            return False, "Debt not found"
        debt.name = debt_data['name']
        debt.amount_owed = debt_data['amount_owed']
        debt.interest_rate = debt_data['interest_rate']
        debt.monthly_pay = debt_data['monthly_pay']
        db.commit()
        return True, None
    except Exception:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

def delete_debt(email, debt_id):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == user.id).first()
        if not debt:
            return False, "Debt not found"
        db.delete(debt)
        db.commit()
        return True, None
    except Exception:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

# Add investment to user account
def add_investment(email, investment_data, users_db=None):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        inv = Investment(
            user_id=user.id,
            name=investment_data['name'],
            amount=investment_data['amount'],
            risk_level=investment_data['risk_level']
        )
        db.add(inv)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def update_investment(email, investment_id, investment_data):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        investment = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == user.id).first()
        if not investment:
            return False, "Investment not found"
        investment.name = investment_data['name']
        investment.amount = investment_data['amount']
        investment.risk_level = investment_data['risk_level']
        db.commit()
        return True, None
    except Exception:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

def delete_investment(email, investment_id):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found"
        investment = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == user.id).first()
        if not investment:
            return False, "Investment not found"
        db.delete(investment)
        db.commit()
        return True, None
    except Exception:
        db.rollback()
        return False, "Database error"
    finally:
        db.close()

# Update user budget
def update_user_budget(email, budget):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        user.budget = budget
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()
