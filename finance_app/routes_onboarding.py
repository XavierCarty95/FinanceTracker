from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from sqlalchemy import select
from finance_app.database import SessionLocal
from finance_app.models import User, UserFinances, Expense, Loan, Investment, PayRate, ExpenseCategory

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/onboarding")


def _get_db():
    return SessionLocal()


@onboarding_bp.route("/new-account", methods=["GET", "POST"])
def new_account():
    """
    Creates a new user + basic finances object.
    Here we cover:
      - name, email, password (simple)
      - income
      - pay_rate (weekly, bi-weekly, monthly)
      - goal_budget
      - bank_balance
    After this, user flows to extra pages to enter expenses, debts, investments.
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        income_str = request.form.get("income", "0").strip()
        goal_budget_str = request.form.get("goal_budget", "0").strip()
        bank_balance_str = request.form.get("bank_balance", "0").strip()

        if not (name and email and password):
            flash("Name, email, and password are required.", "error")
            return render_template("onboarding_new_account.html")

        try:
            income = float(income_str)
            goal_budget = float(goal_budget_str)
            bank_balance = float(bank_balance_str)
        except ValueError:
            flash("Income, goal budget, and bank balance must be numbers.", "error")
            return render_template("onboarding_new_account.html")

        pay_rate_key = request.form.get("pay_rate", "monthly").strip().lower()

        PAY_RATE_MAP = {
            "weekly": PayRate.weekly,
            "bi-weekly": PayRate.biweekly,
            "biweekly": PayRate.biweekly,
            "monthly": PayRate.monthly,
        }

        pay_rate = PAY_RATE_MAP.get(pay_rate_key)

        if pay_rate is None:
            flash("Invalid pay rate selected.", "error")
            return render_template("onboarding_new_account.html")

        db = _get_db()
        try:
            # Check if email already exists
            existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if existing:
                flash("Email already registered.", "error")
                return render_template("onboarding_new_account.html")

            user = User(
                name=name,
                email=email,
                hashed_password=generate_password_hash(password),
            )
            db.add(user)
            db.flush()  # get user.id

            finances = UserFinances(
                income=income,
                pay_rate=pay_rate,
                bank_balance=bank_balance,
                goal_budget=goal_budget,
                user_id=user.id,
            )
            db.add(finances)
            db.commit()

            # Save logged in user_id in session
            session["user_id"] = user.id
            flash("Account created. Now add your expenses.", "success")
            return redirect(url_for("onboarding.expenses"))
        finally:
            db.close()

    return render_template("onboarding_new_account.html")


@onboarding_bp.route("/expenses", methods=["GET", "POST"])
def expenses():
    """
    Add initial expenses split into:
      - Basic Needs (rent, groceries, transportation, clothes)
      - Luxury (eating out, gym, vacation, etc.)
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
        flash("No finances record found. Please create an account first.", "error")
        return redirect(url_for("onboarding.new_account"))

    if request.method == "POST":
        # We allow multiple expenses, so we’ll accept dynamic fields
        # For simplicity, treat each row as separate POST sets or accept comma-separated.
        name = request.form.get("name", "").strip()
        cat = request.form.get("category", "basic").strip()
        cost_str = request.form.get("cost", "0").strip()

        if not name:
            flash("Expense name is required.", "error")
        else:
            try:
                cost = float(cost_str)
            except ValueError:
                flash("Cost must be a number.", "error")
                db.close()
                return render_template("onboarding_expenses.html", finances=finances)

            exp = Expense(
                name=name,
                category=ExpenseCategory(cat),
                cost=cost,
                finances_id=finances.id,
            )
            db.add(exp)
            db.commit()
            flash("Expense added.", "success")

    # Fetch existing expenses to display
    expenses = db.execute(
        select(Expense).where(Expense.finances_id == finances.id)
    ).scalars().all()
    db.close()
    return render_template("onboarding_expenses.html", finances=finances, expenses=expenses)


@onboarding_bp.route("/debts", methods=["GET", "POST"])
def debts():
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
        return redirect(url_for("onboarding.new_account"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        owed_str = request.form.get("amount_owed", "0").strip()
        rate_str = request.form.get("interest_rate", "0").strip()
        pay_str = request.form.get("monthly_pay", "0").strip()

        try:
            amount_owed = float(owed_str)
            interest_rate = float(rate_str)
            monthly_pay = float(pay_str)
        except ValueError:
            flash("Debt values must be numeric.", "error")
        else:
            loan = Loan(
                name=name,
                amount_owed=amount_owed,
                interest_rate=interest_rate,
                monthly_pay=monthly_pay,
                finances_id=finances.id,
            )
            db.add(loan)
            db.commit()
            flash("Loan added.", "success")

    loans = db.execute(
        select(Loan).where(Loan.finances_id == finances.id)
    ).scalars().all()
    db.close()
    return render_template("onboarding_debts.html", finances=finances, loans=loans)


@onboarding_bp.route("/investments", methods=["GET", "POST"])
def investments():
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
        return redirect(url_for("onboarding.new_account"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        amount_str = request.form.get("amount", "0").strip()
        risk = request.form.get("risk_level", "").strip()

        try:
            amount = float(amount_str)
        except ValueError:
            flash("Amount must be numeric.", "error")
        else:
            inv = Investment(
                name=name,
                amount=amount,
                risk_level=risk,
                finances_id=finances.id,
            )
            db.add(inv)
            db.commit()
            flash("Investment added.", "success")

    investments = db.execute(
        select(Investment).where(Investment.finances_id == finances.id)
    ).scalars().all()
    db.close()
    return render_template("onboarding_investments.html", finances=finances, investments=investments)
