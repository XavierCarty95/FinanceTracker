import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import update_user_budget, load_users
from sections.common import get_budget, aggregate_expenses, collapse_small_slices, BaseSection


class BudgetSection(BaseSection):
    def render(self):
        user = self.user
        st.title("Budget Settings")
        st.write("Set your monthly budget goals by category")
        st.write("")

        budget = get_budget(user)

        col1, col2 = st.columns(2)

        with col1:
            with st.form("budget_form"):
                st.subheader("Set Monthly Budgets")

                categories = sorted(budget.keys())
                budget_inputs = {}

                for cat in categories:
                    budget_inputs[cat] = st.number_input(f"{cat.capitalize()} Budget ($)", min_value=0.0, value=budget.get(cat, 0.0), step=10.0)

                submitted = st.form_submit_button("Update Budget", type="primary")

                if submitted:
                    st.session_state.users_db[self.user_email]['budget'] = budget_inputs
                    update_user_budget(self.user_email, budget_inputs)
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
        expense_totals = aggregate_expenses(expenses)
        categories = sorted(set(list(budget.keys()) + list(expense_totals.keys())))
        actual_by_cat = {cat: expense_totals.get(cat, 0.0) for cat in categories}

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
        collapsed = collapse_small_slices(expense_totals)
        chart_items = [(cat, total) for cat, total in collapsed.items() if total > 0]
        labels = [cat.capitalize() for cat, _ in chart_items]
        values = [total for _, total in chart_items]

        if values:
            total = sum(values)

            def format_pct(pct):
                if pct < 0.01 and total > 0:
                    return "<0.01%"
                return f"{pct:.2f}%"

            fig, ax = plt.subplots(figsize=(6, 6))
            colors = plt.cm.Paired.colors[:len(values)] if values else []
            ax.pie(
                values,
                labels=labels,
                autopct=format_pct,
                startangle=90,
                wedgeprops={'width': 0.35, 'edgecolor': 'white', 'linewidth': 1},
                colors=colors,
                pctdistance=0.75,
                labeldistance=1.1
            )
            ax.set(aspect='equal')
            st.pyplot(fig)
        else:
            st.info("No expenses recorded yet.")

        st.write("")
        st.write("")

        st.subheader("Budget vs Actual")
        cols = st.columns(2)
        for i, cat in enumerate(categories):
            with cols[i % 2]:
                budgeted = budget.get(cat, 0.0)
                actual = actual_by_cat.get(cat, 0.0)
                st.metric(f"{cat.capitalize()} Budget", f"${budgeted:,.2f}", delta=f"{actual - budgeted:,.2f}")
