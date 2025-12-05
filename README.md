# FinanceTracker (Streamlit)

FinanceTracker is a Streamlit-based personal finance dashboard. It supports signup/login, tracks balances and transactions, and lets you manage expenses, debts, investments, and budgets with clear charts (including a donut breakdown).

---

## Features
- Streamlit UI with sidebar navigation
- Signup/Login with hashed passwords (Werkzeug) via SQLAlchemy
- PostgreSQL support via `DATABASE_URL` (falls back to local SQLite if unset)
- Transactions (credit/debit) update balances
- Expenses, Debts, Investments: add, edit, delete; duplicate expense guard
- Budgets with budget vs. actual charts and donut breakdown (tiny slices collapsed to “Other”)
- Default budget categories for predictable charts

---

## Tech Stack
- Python 3.12+
- Streamlit, pandas, matplotlib
- SQLAlchemy ORM (PostgreSQL or SQLite fallback)
- psycopg2-binary (Postgres), python-dotenv (env vars), werkzeug (password hashing)

---

## Setup & Run
1) Clone and enter the project  
```bash
git clone https://github.com/XavierCarty95/FinanceTracker.git
cd FinanceTracker
```

2) Create & activate a venv  
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

3) Install deps  
```bash
pip install -r requirements.txt
```

4) Configure database  
- Preferred: set `DATABASE_URL` in `.env` (e.g., `postgresql://user:pass@host/dbname`)  
- If not set, the app uses a local SQLite DB at `financetracker.db`.

5) Run the app  
```bash
streamlit run app.py
```

---

## Project Structure (key parts)
- `app.py` – Streamlit entrypoint, routing login/signup/dashboard
- `models.py` – SQLAlchemy models and engine (`create_tables`)
- `database.py` – DB helpers (signup/login, CRUD for transactions/expenses/debts/investments, budgets)
- `dashboard_page.py` – Sidebar/router to sections
- `sections/` – Feature UIs:
  - `home.py`, `transactions.py`, `analysis.py`, `expenses.py`, `debts.py`, `investments.py`, `budget.py`, `common.py`
- `login_page.py`, `signup_page.py` – Auth flows
- `users_database.json` – Legacy sample data (now primarily DB-backed)

---

## Notes
- Default budget categories are pre-filled to keep charts stable.
- Expenses are deduped by name+category per user.
- Donut chart collapses very small slices into “Other” to keep labels readable.

---

## Contributors
- Xavier Carty, Shree Shingre, Nikhil
