from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Date, Boolean
from sqlalchemy.orm import relationship
from finance_app.database import Base
import enum


class PayRate(str, enum.Enum):
    weekly = "weekly"
    biweekly = "bi-weekly"
    monthly = "monthly"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column("password_hash", String, nullable=False)

    finances = relationship("UserFinances", back_populates="user", uselist=False)


class UserFinances(Base):
    __tablename__ = "user_finances"

    id = Column(Integer, primary_key=True, index=True)
    income = Column(Float, nullable=False, default=0.0)
    pay_rate = Column(Enum(PayRate), nullable=False)
    bank_balance = Column(Float, nullable=False, default=0.0)
    goal_budget = Column(Float, nullable=False, default=0.0)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="finances")

    expenses = relationship("Expense", back_populates="finances", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="finances", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="finances", cascade="all, delete-orphan")


class ExpenseCategory(str, enum.Enum):
    basic = "basic"
    luxury = "luxury"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    cost = Column(Float, nullable=False)

    # Tracking fields from PDF
    totalWeekly = Column(Float, nullable=True)
    totalMonth = Column(Float, nullable=True)
    monthlyAverage = Column(Float, nullable=True)
    weeklyAverage = Column(Float, nullable=True)
    priority = Column(Integer, nullable=True)  # 1–5, optional

    finances_id = Column(Integer, ForeignKey("user_finances.id"), nullable=False)
    finances = relationship("UserFinances", back_populates="expenses")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount_owed = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    monthly_pay = Column(Float, nullable=False)

    finances_id = Column(Integer, ForeignKey("user_finances.id"), nullable=False)
    finances = relationship("UserFinances", back_populates="loans")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=True)
    # You can later add fields like expected_return, etc.

    finances_id = Column(Integer, ForeignKey("user_finances.id"), nullable=False)
    finances = relationship("UserFinances", back_populates="investments")
