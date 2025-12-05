import streamlit as st
import pandas as pd
from database import add_expense, update_expense, delete_expense, load_users
from sections.common import BaseSection, format_currency


class ExpenseSection(BaseSection):
    def render(self):
        user = self.user
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
                    name_norm = expense_name.strip()
                    category_norm = expense_category.strip().lower()
                    existing = [
                        exp for exp in user.get('expenses', [])
                        if exp.get('name', '').strip().lower() == name_norm.lower()
                        and exp.get('category', '').strip().lower() == category_norm
                    ]

                    if not name_norm:
                        st.error("Please enter an expense name")
                    elif expense_cost <= 0:
                        st.error("Please enter a valid cost")
                    elif existing:
                        st.error("That expense already exists in this category")
                    else:
                        expense_data = {
                            'name': name_norm,
                            'category': expense_category,
                            'cost': expense_cost
                        }

                        success, message = add_expense(self.user_email, expense_data, st.session_state.users_db)
                        if success:
                            st.success("Expense added successfully!")
                            st.balloons()
                            st.session_state.users_db = load_users()
                            st.rerun()
                        else:
                            st.error(message or "Failed to add expense")

        with col2:
            st.subheader("Expense Summary")
            expenses = user.get('expenses', [])
            total_expenses = sum(exp['cost'] for exp in expenses)
            st.metric("Total Expenses", f"${total_expenses:,.2f}")

        st.write("")
        st.subheader("Your Expenses")

        expenses = user.get('expenses', [])
        if expenses:
            display_rows = [
                {
                    "Name": exp["name"],
                    "Category": exp["category"],
                    "Cost": format_currency(exp["cost"]),
                }
                for exp in expenses
            ]
            expenses_df = pd.DataFrame(display_rows)
            st.dataframe(expenses_df, width="stretch", hide_index=True)

            with st.form("edit_expense_form"):
                st.markdown("**Edit or Delete Expense**")
                options = {f"{e['name']} ({e['category']}) - ${e['cost']:.2f}": e for e in expenses}
                selected_label = st.selectbox("Select expense", list(options.keys()))
                selected = options[selected_label]

                new_name = st.text_input("Name", value=selected["name"])
                new_category = st.selectbox("Category", ["groceries", "rent", "utilities", "transportation", "entertainment", "healthcare", "dining out", "shopping", "subscriptions", "other"], index=0)
                new_cost = st.number_input("Cost ($)", min_value=0.01, value=float(selected["cost"]), step=0.01, format="%.2f")

                col_a, col_b = st.columns(2)
                with col_a:
                    update_btn = st.form_submit_button("Update", type="primary")
                with col_b:
                    delete_btn = st.form_submit_button("Delete", type="secondary")

                if update_btn:
                    updated = {
                        "name": new_name.strip(),
                        "category": new_category,
                        "cost": new_cost
                    }
                    ok, msg = update_expense(self.user_email, selected["id"], updated)
                    if ok:
                        st.success("Expense updated")
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error(msg or "Update failed")
                elif delete_btn:
                    ok, msg = delete_expense(self.user_email, selected["id"])
                    if ok:
                        st.success("Expense deleted")
                        st.session_state.users_db = load_users()
                        st.rerun()
                    else:
                        st.error(msg or "Delete failed")
        else:
            st.info("No expenses added yet. Add your first expense above!")
