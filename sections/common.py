import os
import streamlit as st
from database import load_users

# Default categories/budget to keep UI predictable
DEFAULT_BUDGET = {
    'groceries': 400.0,
    'rent': 1200.0,
    'utilities': 200.0,
    'transportation': 300.0,
    'entertainment': 150.0,
    'healthcare': 100.0,
    'dining out': 200.0,
    'shopping': 150.0,
    'subscriptions': 50.0,
    'other': 100.0,
}


def normalize_category(category: str) -> str:
    return category.strip().lower() if isinstance(category, str) else ''


def format_currency(value: float, decimals: int = 2) -> str:
    """Format a numeric value as currency with a dollar prefix."""
    return f"${float(value):,.{decimals}f}"


def aggregate_expenses(expenses):
    totals_by_category = {}
    for expense in expenses:
        category = normalize_category(expense.get('category', ''))
        if not category:
            continue
        totals_by_category[category] = totals_by_category.get(category, 0.0) + float(expense.get('cost', 0.0))
    return totals_by_category


def collapse_small_slices(totals_by_category, threshold_ratio=0.03):
    total_amount = sum(totals_by_category.values())
    if total_amount == 0:
        return totals_by_category
    main_categories = {name: amount for name, amount in totals_by_category.items() if amount / total_amount >= threshold_ratio}
    other_total = sum(amount for name, amount in totals_by_category.items() if name not in main_categories)
    if other_total > 0:
        main_categories["other"] = main_categories.get("other", 0) + other_total
    return main_categories


def get_budget(user):
    # Always return a full set of categories to avoid KeyErrors/empty charts
    budget = user.get('budget') or {}
    merged = {**DEFAULT_BUDGET, **budget}
    return {k: float(v) for k, v in merged.items()}


class BaseSection:
    """Shared helpers for dashboard sub-sections."""

    def __init__(self, user_email: str):
        self.user_email = user_email

    @property
    def user(self):
        return st.session_state.users_db[self.user_email]

    def refresh_users(self):
        st.session_state.users_db = load_users()
