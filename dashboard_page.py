import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from database import add_transaction, add_expense, add_debt, add_investment, update_user_budget, load_users

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = 'login'

def show_dashboard_page():
    user = st.session_state.users_db[st.session_state.current_user]
    
    with st.sidebar:
        st.title("MyBank")
        st.write(f"Welcome, **{user['full_name'].split()[0]}**!")
        st.write("")

        menu = st.radio("Navigation", ["Home", "Add Transaction", "Analysis", "Expenses", "Debts", "Investments", "Budget"], label_visibility="collapsed")
        
        st.write("")
        st.write("")
        st.markdown("---")

        if st.button("Logout", width="stretch"):
            logout()
            st.rerun()

    if menu == "Home":
        home_section(user)
    elif menu == "Add Transaction":
        add_transaction_section(user)
    elif menu == "Analysis":
        analysis_section(user)
    elif menu == "Expenses":
        expenses_section(user)
    elif menu == "Debts":
        debts_section(user)
    elif menu == "Investments":
        investments_section(user)
    elif menu == "Budget":
        budget_section(user)

def home_section(user):
    st.title("Dashboard")
    st.write(f"Welcome back, **{user['full_name']}**!")
    st.write("")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; color: white;'>
            <h3 style='margin: 0; font-weight: 300;'>Available Balance</h3>
            <h1 style='margin: 10px 0; font-size: 48px;'>${user['balance']:,.2f}</h1>
            <p style='margin: 0; opacity: 0.9;'>Account: ****{user['account_number'][-4:]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Account Type", user['account_type'], delta=None)
    
    with col3:
        st.metric("Bank", user['bank_name'][:15], delta=None)
    
    st.write("")
    st.write("")
    
    st.subheader("Account Information")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("##### Personal Details")
        st.write(f"**Full Name:** {user['full_name']}")
        st.write(f"**Email:** {st.session_state.current_user}")
        st.write(f"**Phone:** {user['phone']}")
        st.write(f"**Date of Birth:** {user['birth_date']}")
        st.write(f"**Gender:** {user['gender']}")
    
    with col_b:
        st.markdown("##### Banking Details")
        st.write(f"**Bank Name:** {user['bank_name']}")
        st.write(f"**Account Number:** ****{user['account_number'][-4:]}")
        st.write(f"**Routing Number:** {user['routing_number']}")
        st.write(f"**Account Type:** {user['account_type']}")
        st.write(f"**Current Balance:** ${user['balance']:,.2f}")

def add_transaction_section(user):
    st.title("Add Transaction")
    st.write("Record a new transaction for your account")
    st.write("")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("transaction_form"):
            st.subheader("Transaction Details")
            
            transaction_type = st.selectbox(
                "Transaction Type *",
                ["Credit (Money In)", "Debit (Money Out)"]
            )
            
            description = st.text_input(
                "Description *",
                placeholder="e.g., Salary, Groceries, Bill Payment"
            )
            
            amount = st.number_input(
                "Amount ($) *",
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
            
            transaction_date = st.date_input(
                "Date *",
                value=date.today(),
                max_value=date.today()
            )
            
            notes = st.text_area(
                "Notes (Optional)",
                placeholder="Add any additional notes..."
            )
            
            st.write("")
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn2:
                submit_button = st.form_submit_button("Add Transaction", type="primary", width="stretch")
            
            if submit_button:
                if not description.strip():
                    st.error("Please enter a description")
                elif amount <= 0:
                    st.error("Please enter a valid amount")
                else:
                    final_amount = amount if "Credit" in transaction_type else -amount

                    transaction_data = {
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'description': description,
                        'amount': final_amount,
                        'type': 'credit' if "Credit" in transaction_type else 'debit',
                        'notes': notes if notes else ''
                    }

                    if add_transaction(st.session_state.current_user, transaction_data, st.session_state.users_db):
                        st.success("Transaction added successfully!")
                        st.balloons()

                        st.session_state.users_db = load_users()

                        st.info(f"New balance: ${st.session_state.users_db[st.session_state.current_user]['balance']:,.2f}")
                        st.rerun()
                    else:
                        st.error("Failed to add transaction")
    
    with col2:
        st.subheader("Current Balance")
        st.metric("Balance", f"${user['balance']:,.2f}")
        st.write("")
        
        st.info("Tips:\n\n- Credit: Money coming in (salary, refunds)\n\n- Debit: Money going out (bills, purchases)")

def analysis_section(user):
    st.title("Financial Analysis")
    st.write(f"Account analytics for **{user['full_name']}**")
    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Balance", f"${user['balance']:,.2f}")
    with col2:
        st.metric("Account Age", "3 months")
    with col3:
        total_transactions = len(user.get('transactions', []))
        st.metric("Transactions", str(total_transactions))
    with col4:
        st.metric("Avg. Monthly", "$5,250")

    st.write("")
    st.write("")
    st.subheader("Budget Overview")

    budget = user.get('budget', {})
    expenses = user.get('expenses', [])
    actual_by_cat = {}
    for cat in budget.keys():
        actual_by_cat[cat] = sum(exp['cost'] for exp in expenses if exp['category'] == cat)

    budget_actual_data = []
    for cat in budget.keys():
        budget_actual_data.append({'Category': f"{cat.capitalize()} Budget", 'Amount': budget[cat]})
        budget_actual_data.append({'Category': f"{cat.capitalize()} Actual", 'Amount': actual_by_cat[cat]})

    budget_actual_df = pd.DataFrame(budget_actual_data)
    st.bar_chart(budget_actual_df.set_index('Category'))

    st.write("")
    st.write("")

    expenses = user.get('expenses', [])
    actual_by_cat = {}
    categories_list = ['groceries', 'rent', 'utilities', 'transportation', 'entertainment', 'healthcare', 'dining out', 'shopping', 'subscriptions', 'other']
    for cat in categories_list:
        actual_by_cat[cat] = sum(exp['cost'] for exp in expenses if exp['category'] == cat)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Balance Trend")

        dates = pd.date_range(end=datetime.now(), periods=6, freq='ME')
        balances = [10000, 11500, 13200, 14800, 15200, user['balance']]

        chart_data = pd.DataFrame({
            'Month': dates.strftime('%b %Y'),
            'Balance': balances
        })

        st.line_chart(chart_data.set_index('Month'))

    with col_chart2:
        st.subheader("Spending Categories")

        categories_df = pd.DataFrame({
            'Category': [cat.capitalize() for cat in actual_by_cat.keys() if actual_by_cat[cat] > 0],
            'Amount': [actual_by_cat[cat] for cat in actual_by_cat.keys() if actual_by_cat[cat] > 0]
        })

        if not categories_df.empty:
            st.bar_chart(categories_df.set_index('Category'))
        else:
            st.info("No expenses recorded yet.")

    st.write("")
    st.write("")

    st.subheader("Recent Transactions")
    
    # Get transactions from user data
    if 'transactions' in user and user['transactions']:
        transactions_list = user['transactions'][:10]

        transactions_data = []
        running_balance = user['balance']

        for trans in transactions_list:
            amount_str = f"+${abs(trans['amount']):,.2f}" if trans['amount'] > 0 else f"-${abs(trans['amount']):,.2f}"
            transactions_data.append({
                'Date': trans['date'],
                'Description': trans['description'],
                'Amount': amount_str,
                'Balance': f"${running_balance:,.2f}"
            })
            running_balance -= trans['amount']

        transactions = pd.DataFrame(transactions_data)
        st.dataframe(transactions, width="stretch", hide_index=True)
    else:
        st.info("No transactions yet. Add your first transaction using the 'Add Transaction' page!")

def expenses_section(user):
    st.title("Expenses")
    st.write("Track your expenses by category and cost")
    st.write("")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("expense_form"):
            st.subheader("Add Expense")

            expense_name = st.text_input("Expense Name *")
            expense_category = st.selectbox("Category *", ["groceries", "rent", "utilities", "transportation", "entertainment", "healthcare", "dining out", "shopping", "subscriptions", "other"])
            expense_cost = st.number_input("Cost ($) *", min_value=0.01, step=0.01, format="%.2f")

            submitted = st.form_submit_button("Add Expense", type="primary")

            if submitted:
                if not expense_name.strip():
                    st.error("Please enter an expense name")
                elif expense_cost <= 0:
                    st.error("Please enter a valid cost")
                else:
                    expense_data = {
                        'name': expense_name,
                        'category': expense_category,
                        'cost': expense_cost
                    }

                    if add_expense(st.session_state.current_user, expense_data, st.session_state.users_db):
                        st.success("Expense added successfully!")
                        st.balloons()
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error("Failed to add expense")

    with col2:
        st.subheader("Expense Summary")
        expenses = user.get('expenses', [])
        total_expenses = sum(exp['cost'] for exp in expenses)
        st.metric("Total Expenses", f"${total_expenses:,.2f}")

    st.write("")
    st.subheader("Your Expenses")

    if expenses:
        expenses_df = pd.DataFrame(expenses)
        st.dataframe(expenses_df, width="stretch", hide_index=True)
    else:
        st.info("No expenses added yet. Add your first expense above!")

def debts_section(user):
    st.title("Debts")
    st.write("Track your debts and loans")
    st.write("")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("debt_form"):
            st.subheader("Add Debt")

            debt_name = st.text_input("Debt Name *")
            debt_amount = st.number_input("Amount Owed ($) *", min_value=0.01, step=0.01, format="%.2f")
            debt_rate = st.number_input("Interest Rate (%) *", min_value=0.0, step=0.01, format="%.2f")
            debt_monthly = st.number_input("Monthly Payment ($) *", min_value=0.01, step=0.01, format="%.2f")

            submitted = st.form_submit_button("Add Debt", type="primary")

            if submitted:
                if not debt_name.strip():
                    st.error("Please enter a debt name")
                elif debt_amount <= 0 or debt_monthly <= 0:
                    st.error("Please enter valid amounts")
                else:
                    debt_data = {
                        'name': debt_name,
                        'amount_owed': debt_amount,
                        'interest_rate': debt_rate,
                        'monthly_pay': debt_monthly
                    }

                    if add_debt(st.session_state.current_user, debt_data, st.session_state.users_db):
                        st.success("Debt added successfully!")
                        st.balloons()
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error("Failed to add debt")

    with col2:
        st.subheader("Debt Summary")
        debts = user.get('debts', [])
        total_debts = sum(debt['amount_owed'] for debt in debts)
        st.metric("Total Debt", f"${total_debts:,.2f}")

    st.write("")
    st.subheader("Your Debts")

    if debts:
        debts_df = pd.DataFrame(debts)
        st.dataframe(debts_df, width="stretch", hide_index=True)
    else:
        st.info("No debts added yet. Add your first debt above!")

def investments_section(user):
    st.title("Investments")
    st.write("Track your investments and risk levels")
    st.write("")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("investment_form"):
            st.subheader("Add Investment")

            investment_name = st.text_input("Investment Name *")
            investment_amount = st.number_input("Amount ($) *", min_value=0.01, step=0.01, format="%.2f")
            investment_risk = st.text_input("Risk Level *")

            submitted = st.form_submit_button("Add Investment", type="primary")

            if submitted:
                if not investment_name.strip():
                    st.error("Please enter an investment name")
                elif investment_amount <= 0:
                    st.error("Please enter a valid amount")
                elif not investment_risk.strip():
                    st.error("Please enter a risk level")
                else:
                    investment_data = {
                        'name': investment_name,
                        'amount': investment_amount,
                        'risk_level': investment_risk
                    }

                    if add_investment(st.session_state.current_user, investment_data, st.session_state.users_db):
                        st.success("Investment added successfully!")
                        st.balloons()
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error("Failed to add investment")

    with col2:
        st.subheader("Investment Summary")
        investments = user.get('investments', [])
        total_investments = sum(inv['amount'] for inv in investments)
        st.metric("Total Investments", f"${total_investments:,.2f}")

    st.write("")
    st.subheader("Your Investments")

    if investments:
        investments_df = pd.DataFrame(investments)
        st.dataframe(investments_df, width="stretch", hide_index=True)
    else:
        st.info("No investments added yet. Add your first investment above!")

def budget_section(user):
    st.title("Budget Settings")
    st.write("Set your monthly budget goals by category")
    st.write("")

    budget = user.get('budget', {'basic': 1000.0, 'luxury': 500.0})

    col1, col2 = st.columns(2)

    with col1:
        with st.form("budget_form"):
            st.subheader("Set Monthly Budgets")

            categories = ['groceries', 'rent', 'utilities', 'transportation', 'entertainment', 'healthcare', 'dining out', 'shopping', 'subscriptions', 'other']
            budget_inputs = {}

            for cat in categories:
                budget_inputs[cat] = st.number_input(f"{cat.capitalize()} Budget ($)", min_value=0.0, value=budget.get(cat, 0.0), step=10.0)

            submitted = st.form_submit_button("Update Budget", type="primary")

            if submitted:
                st.session_state.users_db[st.session_state.current_user]['budget'] = budget_inputs
                update_user_budget(st.session_state.current_user, budget_inputs)
                st.session_state.users_db = load_users()
                st.success("Budget updated successfully!")
                st.rerun()

    with col2:
        st.subheader("Current Budget Summary")
        total_budget = sum(budget.values())
        st.metric("Total Monthly Budget", f"${total_budget:,.2f}")
        categories = list(budget.keys())
        for cat in categories[:5]:
            st.write(f"**{cat.capitalize()}:** ${budget[cat]:,.2f}")

    st.write("")
    st.subheader("Budget vs Actual")

    expenses = user.get('expenses', [])
    actual_by_cat = {}
    for cat in budget.keys():
        actual_by_cat[cat] = sum(exp['cost'] for exp in expenses if exp['category'] == cat)

    if any(v > 0 for v in actual_by_cat.values()):
        expense_df = pd.DataFrame({
            'Category': [cat.capitalize() for cat in actual_by_cat.keys()],
            'Amount': list(actual_by_cat.values())
        })
        st.bar_chart(expense_df.set_index('Category'))
    else:
        st.info("No expenses recorded yet. Add some expenses to see the chart.")

    st.write("")
    st.write("")

    st.subheader("Expense Breakdown (Donut Chart)")
    if any(v >= 0.01 for v in actual_by_cat.values()):
        labels = [cat.capitalize() for cat in actual_by_cat.keys() if actual_by_cat[cat] >= 0.01]
        values = [actual_by_cat[cat] for cat in actual_by_cat.keys() if actual_by_cat[cat] >= 0.01]
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = plt.cm.Paired.colors[:len(values)] if values else []
        ax.pie(values, labels=labels, autopct='%1.2f%%', startangle=90, wedgeprops={'width': 0.3}, colors=colors)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No expenses recorded yet.")

    st.write("")
    st.write("")

    st.subheader("Budget vs Actual")
    cols = st.columns(2)
    for i, cat in enumerate(budget.keys()):
        with cols[i % 2]:
            budgeted = budget[cat]
            actual = actual_by_cat[cat]
            st.metric(f"{cat.capitalize()} Budget", f"${budgeted:,.2f}", delta=f"{actual - budgeted:,.2f}")