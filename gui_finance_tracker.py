import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash
from finance_app.database import SessionLocal
from finance_app.models import (
    User,
    UserFinances,
    Expense,
    Loan,
    Investment,
    PayRate,
    ExpenseCategory,
)


class FinanceTrackerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finance Tracker")
        self.geometry("900x600")

        self.current_user_id = None
        self.current_finances_id = None
        self._main_view_shown = False

        # --------- TOP BAR (for Logout when logged in) -------------- #
        self.top_bar = ttk.Frame(self)
        self.logout_button = ttk.Button(self.top_bar, text="Logout", command=self.logout)
        self.logout_button.pack(side="right", padx=10, pady=10)

        # --------- AUTH SCREENS (first show login) ----- #
        self.login_frame = ttk.Frame(self)
        self.account_frame = ttk.Frame(self)

        # Start on login page
        self.login_frame.pack(fill="both", expand=True)

        # --------- MAIN NOTEBOOK (hidden at start) ----- #
        self.notebook = ttk.Notebook(self)

        self.frame_expenses = ttk.Frame(self.notebook)
        self.frame_debts = ttk.Frame(self.notebook)
        self.frame_investments = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_expenses, text="Expenses")
        self.notebook.add(self.frame_debts, text="Debts")
        self.notebook.add(self.frame_investments, text="Investments")

        # Build UI
        self._build_login_page()
        self._build_account_tab()
        self._build_expenses_tab()
        self._build_debts_tab()
        self._build_investments_tab()


    def _build_login_page(self):
        frame = self.login_frame

        row = 0
        ttk.Label(frame, text="Login", font=("TkDefaultFont", 14, "bold")).grid(
            row=row, column=0, columnspan=2, pady=(20, 10)
        )

        row += 1
        ttk.Label(frame, text="Email:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.login_email_entry = ttk.Entry(frame, width=30)
        self.login_email_entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Password:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.login_password_entry = ttk.Entry(frame, width=30, show="*")
        self.login_password_entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        btn_login = ttk.Button(frame, text="Login", command=self.login_account)
        btn_login.grid(row=row, column=0, columnspan=2, pady=15)

        row += 1
        btn_go_to_create = ttk.Button(frame, text="Create New Account", command=self.go_to_create_account)
        btn_go_to_create.grid(row=row, column=0, columnspan=2)

        row += 1
        self.login_status_label = ttk.Label(frame, text="", foreground="grey")
        self.login_status_label.grid(row=row, column=0, columnspan=2, pady=5)

    def go_to_create_account(self):
        self.login_frame.pack_forget()
        self.account_frame.pack(fill="both", expand=True)

    def go_to_login(self):
        self.account_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    # ---------- helper to switch from account → main tabs ---------- #
    def show_main_view(self):
        if self._main_view_shown:
            return
        self._main_view_shown = True

        # Hide the login and account forms
        self.login_frame.pack_forget()
        self.account_frame.pack_forget()

        # Show top bar (logout) and the notebook with the money stuff
        self.top_bar.pack(fill="x")
        self.notebook.pack(fill="both", expand=True)

    def logout(self):
        """Log out the current user and return to the login screen."""
        # Clear current user state
        self.current_user_id = None
        self.current_finances_id = None
        self._main_view_shown = False

        # Hide main app views
        self.notebook.pack_forget()
        self.top_bar.pack_forget()

        # Clear tables
        for item in self.tree_expenses.get_children():
            self.tree_expenses.delete(item)
        for item in self.tree_debts.get_children():
            self.tree_debts.delete(item)
        for item in self.tree_investments.get_children():
            self.tree_investments.delete(item)

        # Clear login and account fields
        self.login_email_entry.delete(0, tk.END)
        self.login_password_entry.delete(0, tk.END)

        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_income.delete(0, tk.END)
        self.entry_goal_budget.delete(0, tk.END)
        self.entry_bank_balance.delete(0, tk.END)

        self.label_status.config(text="No account loaded.")
        self.login_status_label.config(text="")

        # Return to login screen
        self.login_frame.pack(fill="both", expand=True)

    # ---------- Account page (now a separate screen, not a tab) ---- #
    def _build_account_tab(self):
        frame = self.account_frame

        row = 0
        ttk.Label(frame, text="Name:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_name = ttk.Entry(frame, width=30)
        self.entry_name.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Email:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_email = ttk.Entry(frame, width=30)
        self.entry_email.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Password:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_password = ttk.Entry(frame, width=30, show="*")
        self.entry_password.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Income:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_income = ttk.Entry(frame, width=20)
        self.entry_income.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Pay Rate:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.combo_pay_rate = ttk.Combobox(
            frame,
            values=["weekly", "bi-weekly", "monthly"],
            state="readonly",
            width=18,
        )
        self.combo_pay_rate.set("monthly")
        self.combo_pay_rate.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Goal Budget:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_goal_budget = ttk.Entry(frame, width=20)
        self.entry_goal_budget.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Bank Balance:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_bank_balance = ttk.Entry(frame, width=20)
        self.entry_bank_balance.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        btn_create = ttk.Button(frame, text="Create New Account", command=self.create_account)
        btn_create.grid(row=row, column=0, padx=5, pady=15, sticky="e")

        btn_load = ttk.Button(frame, text="Load Existing By Email", command=self.load_account)
        btn_load.grid(row=row, column=1, padx=5, pady=15, sticky="w")

        row += 1
        self.label_status = ttk.Label(frame, text="No account loaded.", foreground="grey")
        self.label_status.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    # ---------- Expenses tab --------------------------------------- #
    def _build_expenses_tab(self):
        frame = self.frame_expenses

        row = 0
        ttk.Label(frame, text="Expense Name:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_expense_name = ttk.Entry(frame, width=30)
        self.entry_expense_name.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Category:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.combo_expense_cat = ttk.Combobox(
            frame,
            values=["basic", "luxury"],
            state="readonly",
            width=18,
        )
        self.combo_expense_cat.set("basic")
        self.combo_expense_cat.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Cost:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_expense_cost = ttk.Entry(frame, width=20)
        self.entry_expense_cost.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        btn_add_expense = ttk.Button(frame, text="Add Expense", command=self.add_expense)
        btn_add_expense.grid(row=row, column=0, columnspan=2, padx=5, pady=15)

        row += 1
        self.tree_expenses = ttk.Treeview(
            frame,
            columns=("name", "category", "cost"),
            show="headings",
            height=12,
        )
        self.tree_expenses.heading("name", text="Name")
        self.tree_expenses.heading("category", text="Category")
        self.tree_expenses.heading("cost", text="Cost")
        self.tree_expenses.column("name", anchor="center", width=200)
        self.tree_expenses.column("category", anchor="center", width=100)
        self.tree_expenses.column("cost", anchor="center", width=100)

        self.tree_expenses.heading("name", anchor="center")
        self.tree_expenses.heading("category", anchor="center")
        self.tree_expenses.heading("cost", anchor="center")
        self.tree_expenses.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        frame.rowconfigure(row, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    # ---------- Debts tab ------------------------------------------ #
    def _build_debts_tab(self):
        frame = self.frame_debts

        row = 0
        ttk.Label(frame, text="Debt Name:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_debt_name = ttk.Entry(frame, width=30)
        self.entry_debt_name.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Amount Owed:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_debt_amount = ttk.Entry(frame, width=20)
        self.entry_debt_amount.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Interest Rate (%):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_debt_rate = ttk.Entry(frame, width=20)
        self.entry_debt_rate.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Monthly Payment:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_debt_monthly = ttk.Entry(frame, width=20)
        self.entry_debt_monthly.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        btn_add_debt = ttk.Button(frame, text="Add Debt", command=self.add_debt)
        btn_add_debt.grid(row=row, column=0, columnspan=2, padx=5, pady=15)

        row += 1
        self.tree_debts = ttk.Treeview(
            frame,
            columns=("name", "amount", "rate", "monthly"),
            show="headings",
            height=12,
        )
        self.tree_debts.heading("name", text="Name")
        self.tree_debts.heading("amount", text="Amount Owed")
        self.tree_debts.heading("rate", text="Interest Rate")
        self.tree_debts.heading("monthly", text="Monthly Pay")
        self.tree_debts.column("name", anchor="center", width=200)
        self.tree_debts.column("amount", anchor="center", width=120)
        self.tree_debts.column("rate", anchor="center", width=100)
        self.tree_debts.column("monthly", anchor="center", width=120)
        self.tree_debts.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        frame.rowconfigure(row, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    # ---------- Investments tab ------------------------------------ #
    def _build_investments_tab(self):
        frame = self.frame_investments

        row = 0
        ttk.Label(frame, text="Investment Name:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_inv_name = ttk.Entry(frame, width=30)
        self.entry_inv_name.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Amount:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_inv_amount = ttk.Entry(frame, width=20)
        self.entry_inv_amount.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        ttk.Label(frame, text="Risk Level:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.entry_inv_risk = ttk.Entry(frame, width=20)
        self.entry_inv_risk.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        row += 1
        btn_add_inv = ttk.Button(frame, text="Add Investment", command=self.add_investment)
        btn_add_inv.grid(row=row, column=0, columnspan=2, padx=5, pady=15)

        row += 1
        self.tree_investments = ttk.Treeview(
            frame,
            columns=("name", "amount", "risk"),
            show="headings",
            height=12,
        )
        self.tree_investments.heading("name", text="Name")
        self.tree_investments.heading("amount", text="Amount")
        self.tree_investments.heading("risk", text="Risk Level")
        self.tree_investments.column("name", anchor="center", width=200)
        self.tree_investments.column("amount", anchor="center", width=120)
        self.tree_investments.column("risk", anchor="center", width=120)
        self.tree_investments.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        frame.rowconfigure(row, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    # ---------- Create account / login ------------------------------ #
    def login_account(self):
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Email and password are required.")
            return

        db = SessionLocal()
        try:
            user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if not user:
                messagebox.showerror("Error", "User not found.")
                return

            if not check_password_hash(user.hashed_password, password):
                messagebox.showerror("Error", "Incorrect password.")
                return

            finances = db.execute(
                select(UserFinances).where(UserFinances.user_id == user.id)
            ).scalar_one_or_none()
            if not finances:
                messagebox.showerror("Error", "No finances record found for this user.")
                return

            self.current_user_id = user.id
            self.current_finances_id = finances.id

            messagebox.showinfo("Success", "Logged in successfully.")
            self.reload_all_lists()
            self.show_main_view()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def create_account(self):
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        income_str = self.entry_income.get().strip() or "0"
        goal_str = self.entry_goal_budget.get().strip() or "0"
        bank_str = self.entry_bank_balance.get().strip() or "0"
        pay_rate_str = self.combo_pay_rate.get().strip()

        if not (name and email and password):
            messagebox.showerror("Error", "Name, email, and password are required.")
            return

        try:
            income = float(income_str)
            goal_budget = float(goal_str)
            bank_balance = float(bank_str)
        except ValueError:
            messagebox.showerror("Error", "Income, goal budget, and bank balance must be numbers.")
            return

        try:
            pay_rate = PayRate(pay_rate_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid pay rate selected.")
            return

        db = SessionLocal()
        try:
            existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if existing:
                messagebox.showerror("Error", "Email already registered. Use 'Load Existing By Email'.")
                return

            user = User(
                name=name,
                email=email,
                hashed_password=generate_password_hash(password),
            )
            db.add(user)
            db.flush()

            finances = UserFinances(
                income=income,
                pay_rate=pay_rate,
                bank_balance=bank_balance,
                goal_budget=goal_budget,
                user_id=user.id,
            )
            db.add(finances)
            db.commit()

            self.current_user_id = user.id
            self.current_finances_id = finances.id
            self.label_status.config(text=f"Loaded user: {name} ({email})")
            messagebox.showinfo("Success", "Account created successfully.")
            self.reload_all_lists()
            self.show_main_view()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def load_account(self):
        email = self.entry_email.get().strip()
        if not email:
            messagebox.showerror("Error", "Enter an email to load.")
            return

        db = SessionLocal()
        try:
            user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if not user:
                messagebox.showerror("Error", "User not found.")
                return

            finances = db.execute(
                select(UserFinances).where(UserFinances.user_id == user.id)
            ).scalar_one_or_none()
            if not finances:
                messagebox.showerror("Error", "No finances record found for this user.")
                return

            self.current_user_id = user.id
            self.current_finances_id = finances.id

            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, user.name)

            self.label_status.config(text=f"Loaded user: {user.name} ({user.email})")
            messagebox.showinfo("Success", "Account loaded.")
            self.reload_all_lists()
            self.show_main_view()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    # ---------- Guards & CRUD for expenses/debts/investments ------- #
    def ensure_finances_loaded(self):
        if not self.current_finances_id:
            messagebox.showerror("Error", "No account loaded. Create or load an account first.")
            return False
        return True

    def add_expense(self):
        if not self.ensure_finances_loaded():
            return

        name = self.entry_expense_name.get().strip()
        cat_str = self.combo_expense_cat.get().strip()
        cost_str = self.entry_expense_cost.get().strip() or "0"

        if not name:
            messagebox.showerror("Error", "Expense name is required.")
            return

        try:
            cost = float(cost_str)
        except ValueError:
            messagebox.showerror("Error", "Cost must be a number.")
            return

        try:
            category = ExpenseCategory(cat_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid category.")
            return

        db = SessionLocal()
        try:
            exp = Expense(
                name=name,
                category=category,
                cost=cost,
                finances_id=self.current_finances_id,
            )
            db.add(exp)
            db.commit()
            messagebox.showinfo("Success", "Expense added.")
            self.entry_expense_name.delete(0, tk.END)
            self.entry_expense_cost.delete(0, tk.END)
            self.reload_expenses()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def add_debt(self):
        if not self.ensure_finances_loaded():
            return

        name = self.entry_debt_name.get().strip()
        owed_str = self.entry_debt_amount.get().strip() or "0"
        rate_str = self.entry_debt_rate.get().strip() or "0"
        monthly_str = self.entry_debt_monthly.get().strip() or "0"

        if not name:
            messagebox.showerror("Error", "Debt name is required.")
            return

        try:
            amount_owed = float(owed_str)
            interest_rate = float(rate_str)
            monthly_pay = float(monthly_str)
        except ValueError:
            messagebox.showerror("Error", "Debt values must be numeric.")
            return

        db = SessionLocal()
        try:
            loan = Loan(
                name=name,
                amount_owed=amount_owed,
                interest_rate=interest_rate,
                monthly_pay=monthly_pay,
                finances_id=self.current_finances_id,
            )
            db.add(loan)
            db.commit()
            messagebox.showinfo("Success", "Loan added.")
            self.entry_debt_name.delete(0, tk.END)
            self.entry_debt_amount.delete(0, tk.END)
            self.entry_debt_rate.delete(0, tk.END)
            self.entry_debt_monthly.delete(0, tk.END)
            self.reload_debts()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def add_investment(self):
        if not self.ensure_finances_loaded():
            return

        name = self.entry_inv_name.get().strip()
        amount_str = self.entry_inv_amount.get().strip() or "0"
        risk = self.entry_inv_risk.get().strip()

        if not name:
            messagebox.showerror("Error", "Investment name is required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be numeric.")
            return

        db = SessionLocal()
        try:
            inv = Investment(
                name=name,
                amount=amount,
                risk_level=risk,
                finances_id=self.current_finances_id,
            )
            db.add(inv)
            db.commit()
            messagebox.showinfo("Success", "Investment added.")
            self.entry_inv_name.delete(0, tk.END)
            self.entry_inv_amount.delete(0, tk.END)
            self.entry_inv_risk.delete(0, tk.END)
            self.reload_investments()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def reload_all_lists(self):
        self.reload_expenses()
        self.reload_debts()
        self.reload_investments()

    def reload_expenses(self):
        for item in self.tree_expenses.get_children():
            self.tree_expenses.delete(item)

        if not self.current_finances_id:
            return

        db = SessionLocal()
        try:
            result = db.execute(
                select(Expense).where(Expense.finances_id == self.current_finances_id)
            ).scalars().all()
            for exp in result:
                self.tree_expenses.insert("", tk.END, values=(exp.name, exp.category.value, exp.cost))
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def reload_debts(self):
        for item in self.tree_debts.get_children():
            self.tree_debts.delete(item)

        if not self.current_finances_id:
            return

        db = SessionLocal()
        try:
            result = db.execute(
                select(Loan).where(Loan.finances_id == self.current_finances_id)
            ).scalars().all()
            for loan in result:
                self.tree_debts.insert(
                    "",
                    tk.END,
                    values=(loan.name, loan.amount_owed, loan.interest_rate, loan.monthly_pay),
                )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()

    def reload_investments(self):
        for item in self.tree_investments.get_children():
            self.tree_investments.delete(item)

        if not self.current_finances_id:
            return

        db = SessionLocal()
        try:
            result = db.execute(
                select(Investment).where(Investment.finances_id == self.current_finances_id)
            ).scalars().all()
            for inv in result:
                self.tree_investments.insert(
                    "",
                    tk.END,
                    values=(inv.name, inv.amount, inv.risk_level),
                )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            db.close()


if __name__ == "__main__":
    app = FinanceTrackerGUI()
    app.mainloop()