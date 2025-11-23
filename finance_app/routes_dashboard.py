from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from datetime import date, timedelta
from sqlalchemy import select, func
from finance_app.database import SessionLocal
from finance_app.models import User, UserFinances, Expense, Loan, Investment

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def _get_db():
    return SessionLocal()


def _current_user_and_finances():
    user_id = session.get("user_id")
    if not user_id:
        return None, None

    db = _get_db()
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        db.close()
        return None, None
    finances = db.execute(
        select(UserFinances).where(UserFinances.user_id == user_id)
    ).scalar_one_or_none()
    return (user, finances, db)


@dashboard_bp.route("/")
def home():
    """
    Existing user dashboard, with:
      - Bank balance
      - Loans summary
      - Monthly report
      - Goal budget progress bar
      - Investments summary
      - Money spent current month/week
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("onboarding.new_account"))

    db = _get_db()

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    finances = db.execute(
        select(UserFinances).where(UserFinances.user_id == user_id)
    ).scalar_one_or_none()

    if not user or not finances:
        db.close()
        return redirect(url_for("onboarding.new_account"))

    # Loans
    loans = db.execute(
        select(Loan).where(Loan.finances_id == finances.id)
    ).scalars().all()
    total_loans_owed = sum(l.amount_owed for l in loans)

    # Investments
    investments = db.execute(
        select(Investment).where(Investment.finances_id == finances.id)
    ).scalars().all()
    total_investments = sum(i.amount for i in investments)

    # Monthly report (current month)
    today = date.today()
    month_start = today.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)

    # Filter expenses in current month
    # Here we assume we add date columns to Expense in real app;
    monthly_spent = db.execute(
        select(func.sum(Expense.cost)).where(
            Expense.finances_id == finances.id
        )
    ).scalar() or 0.0

    # Weekly spent (last 7 days)
    weekly_spent = monthly_spent  # placeholder behavior

    # Goal budget progress
    goal_budget = finances.goal_budget or 0.0
    goal_progress = 0.0
    if goal_budget > 0:
        goal_progress = min(100.0, (monthly_spent / goal_budget) * 100.0)

    context = {
        "user": user,
        "finances": finances,
        "total_loans_owed": total_loans_owed,
        "loans": loans,
        "investments": investments,
        "total_investments": total_investments,
        "monthly_spent": monthly_spent,
        "weekly_spent": weekly_spent,
        "goal_progress": goal_progress,
    }

    db.close()
    return render_template("dashboard.html", **context)


@dashboard_bp.route("/edit", methods=["GET", "POST"])
def edit():
    """
    Edit profile financial info:
      - income (salary)
      - pay_rate
      - goal_budget
      - bank_balance
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("onboarding.new_account"))

    db = _get_db()
    finances = db.execute(
        select(UserFinances).where(UserFinances.user_id == user_id)
    ).scalar_one_or_none()

    if not finances:
        db.close()
        flash("No finances record found.", "error")
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        income_str = request.form.get("income", "").strip()
        pay_rate_str = request.form.get("pay_rate", "").strip()
        goal_budget_str = request.form.get("goal_budget", "").strip()
        bank_balance_str = request.form.get("bank_balance", "").strip()

        try:
            income = float(income_str)
            goal_budget = float(goal_budget_str)
            bank_balance = float(bank_balance_str)
        except ValueError:
            flash("Income, goal budget, and bank balance must be numeric.", "error")
            db.close()
            return render_template("edit_profile.html", finances=finances)

        from .models import PayRate
        finances.income = income
        finances.goal_budget = goal_budget
        finances.bank_balance = bank_balance
        if pay_rate_str:
            finances.pay_rate = PayRate(pay_rate_str)

        db.commit()
        db.close()
        flash("Financial profile updated.", "success")
        return redirect(url_for("dashboard.home"))

    db.close()
    return render_template("edit_profile.html", finances=finances)
