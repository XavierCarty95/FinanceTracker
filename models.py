from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, Enum as SAEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum
import os

# Prefer DATABASE_URL if provided; otherwise fall back to a local SQLite file for easy setup.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'financetracker.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PayRate(Enum):
    weekly = "weekly"
    bi_weekly = "bi-weekly"
    monthly = "monthly"

class ExpenseCategory(Enum):
    basic = "basic"
    luxury = "luxury"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    birth_date = Column(Date)
    gender = Column(String)
    phone = Column(String)
    bank_name = Column(String)
    account_number = Column(String)
    routing_number = Column(String)
    account_type = Column(String)
    balance = Column(Float, default=0.0)
    pay_rate = Column(SAEnum(PayRate), default=PayRate.monthly)
    goal_budget = Column(Float, default=0.0)
    income = Column(Float, default=0.0)
    budget = Column(JSON, default=dict)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    date = Column(Date)
    description = Column(String)
    amount = Column(Float)
    type = Column(String)
    notes = Column(Text)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    category = Column(String)
    cost = Column(Float)

class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    amount_owed = Column(Float)
    interest_rate = Column(Float)
    monthly_pay = Column(Float)

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    amount = Column(Float)
    risk_level = Column(String)

def create_tables():
    Base.metadata.create_all(bind=engine)
