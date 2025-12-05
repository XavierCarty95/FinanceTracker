import streamlit as st
import pandas as pd
from database import add_investment, update_investment, delete_investment, load_users
from sections.common import BaseSection, format_currency


class InvestmentSection(BaseSection):
    def render(self):
        user = self.user
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

                        if add_investment(self.user_email, investment_data, st.session_state.users_db):
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

        investments = user.get('investments', [])
        if investments:
            display_rows = [
                {
                    "Name": inv["name"],
                    "Amount": format_currency(inv["amount"]),
                    "Risk Level": inv["risk_level"],
                }
                for inv in investments
            ]
            investments_df = pd.DataFrame(display_rows)
            st.dataframe(investments_df, width="stretch", hide_index=True)

            with st.form("edit_investment_form"):
                st.markdown("**Edit or Delete Investment**")
                options = {f"{i['name']} - ${i['amount']:.2f}": i for i in investments}
                selected_label = st.selectbox("Select investment", list(options.keys()))
                selected = options[selected_label]

                new_name = st.text_input("Name", value=selected["name"])
                new_amount = st.number_input("Amount ($)", min_value=0.01, value=float(selected["amount"]), step=0.01, format="%.2f")
                new_risk = st.text_input("Risk Level", value=selected["risk_level"])

                col_a, col_b = st.columns(2)
                with col_a:
                    update_btn = st.form_submit_button("Update", type="primary")
                with col_b:
                    delete_btn = st.form_submit_button("Delete", type="secondary")

                if update_btn:
                    updated = {
                        "name": new_name.strip(),
                        "amount": new_amount,
                        "risk_level": new_risk.strip()
                    }
                    ok, msg = update_investment(self.user_email, selected["id"], updated)
                    if ok:
                        st.success("Investment updated")
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error(msg or "Update failed")
                elif delete_btn:
                    ok, msg = delete_investment(self.user_email, selected["id"])
                    if ok:
                        st.success("Investment deleted")
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error(msg or "Delete failed")
        else:
            st.info("No investments added yet. Add your first investment above!")
