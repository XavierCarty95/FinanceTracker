from sqlalchemy.orm import sessionmaker
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
        users_db = {}
        for user in users:
            user_data = {
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
                        'date': t.date.strftime('%Y-%m-%d'),
                        'description': t.description,
                        'amount': t.amount,
                        'type': t.type,
                        'notes': t.notes
                    } for t in db.query(Transaction).filter(Transaction.user_id == user.id).all()
                ],
                'expenses': [
                    {
                        'name': e.name,
                        'category': e.category,
                        'cost': e.cost
                    } for e in db.query(Expense).filter(Expense.user_id == user.id).all()
                ],
                'debts': [
                    {
                        'name': d.name,
                        'amount_owed': d.amount_owed,
                        'interest_rate': d.interest_rate,
                        'monthly_pay': d.monthly_pay
                    } for d in db.query(Debt).filter(Debt.user_id == user.id).all()
                ],
                'investments': [
                    {
                        'name': i.name,
                        'amount': i.amount,
                        'risk_level': i.risk_level
                    } for i in db.query(Investment).filter(Investment.user_id == user.id).all()
                ]
            }
            users_db[user.email] = user_data
        return users_db
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
            return False
        exp = Expense(
            user_id=user.id,
            name=expense_data['name'],
            category=expense_data['category'],
            cost=expense_data['cost']
        )
        db.add(exp)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
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