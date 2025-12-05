import streamlit as st
from datetime import date
from database import add_transaction, load_users
from sections.common import BaseSection


class TransactionSection(BaseSection):
    def render(self):
        user = self.user
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

                        if add_transaction(self.user_email, transaction_data, st.session_state.users_db):
                            st.success("Transaction added successfully!")
                            st.balloons()
                            st.session_state.users_db = load_users()
                            st.info(f"New balance: ${st.session_state.users_db[self.user_email]['balance']:,.2f}")
                            st.rerun()
                        else:
                            st.error("Failed to add transaction")

        with col2:
            st.subheader("Current Balance")
            st.metric("Balance", f"${user['balance']:,.2f}")
            st.write("")
            st.info("Tips:\n\n- Credit: Money coming in (salary, refunds)\n\n- Debit: Money going out (bills, purchases)")
