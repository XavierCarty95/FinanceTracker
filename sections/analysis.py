import streamlit as st
import pandas as pd
from datetime import datetime
from sections.common import get_budget, aggregate_expenses, BaseSection


class AnalysisSection(BaseSection):
    def __init__(self, user_email: str):
        super().__init__(user_email)

    def render(self):
        user = self.user
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

        budget = get_budget(user)
        expenses = user.get('expenses', [])
        expense_totals = aggregate_expenses(expenses)

        categories = sorted(set(list(budget.keys()) + list(expense_totals.keys())))
        actual_by_cat = {cat: expense_totals.get(cat, 0.0) for cat in categories}

        budget_actual_data = []
        for cat in categories:
            budget_actual_data.append({'Category': f"{cat.capitalize()} Budget", 'Amount': budget.get(cat, 0.0)})
            budget_actual_data.append({'Category': f"{cat.capitalize()} Actual", 'Amount': actual_by_cat[cat]})

        if budget_actual_data:
            budget_actual_df = pd.DataFrame(budget_actual_data)
            st.bar_chart(budget_actual_df.set_index('Category'))
        else:
            st.info("No budget or expenses available yet.")

        st.write("")
        st.write("")

        actual_by_cat = {cat: expense_totals.get(cat, 0.0) for cat in categories}

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
