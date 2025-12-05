import streamlit as st
import pandas as pd
from database import add_debt, update_debt, delete_debt, load_users
from sections.common import BaseSection, format_currency


class DebtSection(BaseSection):
    def render(self):
        user = self.user
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

                        if add_debt(self.user_email, debt_data, st.session_state.users_db):
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

        debts = user.get('debts', [])
        if debts:
            display_rows = [
                {
                    "Name": debt["name"],
                    "Amount Owed": format_currency(debt["amount_owed"]),
                    "Interest Rate (%)": f"{float(debt['interest_rate']):.2f}%",
                    "Monthly Pay": format_currency(debt["monthly_pay"]),
                }
                for debt in debts
            ]
            debts_df = pd.DataFrame(display_rows)
            st.dataframe(debts_df, width="stretch", hide_index=True)

            with st.form("edit_debt_form"):
                st.markdown("**Edit or Delete Debt**")
                options = {f"{d['name']} - ${d['amount_owed']:.2f}": d for d in debts}
                selected_label = st.selectbox("Select debt", list(options.keys()))
                selected = options[selected_label]

                new_name = st.text_input("Name", value=selected["name"])
                new_amount = st.number_input("Amount Owed ($)", min_value=0.01, value=float(selected["amount_owed"]), step=0.01, format="%.2f")
                new_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=float(selected["interest_rate"]), step=0.01, format="%.2f")
                new_monthly = st.number_input("Monthly Payment ($)", min_value=0.01, value=float(selected["monthly_pay"]), step=0.01, format="%.2f")

                col_a, col_b = st.columns(2)
                with col_a:
                    update_btn = st.form_submit_button("Update", type="primary")
                with col_b:
                    delete_btn = st.form_submit_button("Delete", type="secondary")

                if update_btn:
                    updated = {
                        "name": new_name.strip(),
                        "amount_owed": new_amount,
                        "interest_rate": new_rate,
                        "monthly_pay": new_monthly
                    }
                    ok, msg = update_debt(self.user_email, selected["id"], updated)
                    if ok:
                        st.success("Debt updated")
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error(msg or "Update failed")
                elif delete_btn:
                    ok, msg = delete_debt(self.user_email, selected["id"])
                    if ok:
                        st.success("Debt deleted")
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error(msg or "Delete failed")
        else:
            st.info("No debts added yet. Add your first debt above!")
