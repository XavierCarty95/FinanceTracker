import streamlit as st
from sections import (
    render_home,
    TransactionSection,
    AnalysisSection,
    ExpenseSection,
    DebtSection,
    InvestmentSection,
    BudgetSection,
)


def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = 'login'


def show_dashboard_page():
    current_user_email = st.session_state.current_user
    user = st.session_state.users_db[current_user_email]

    with st.sidebar:
        st.title("MyBank")
        st.write(f"Welcome, **{user['full_name'].split()[0]}**!")
        st.write("")

        menu = st.radio(
            "Navigation",
            ["Home", "Add Transaction", "Analysis", "Expenses", "Debts", "Investments", "Budget"],
            label_visibility="collapsed",
        )

        st.write("")
        st.write("")
        st.markdown("---")

        if st.button("Logout", width="stretch"):
            logout()
            st.rerun()

    sections = {
        "Home": lambda: render_home(user),
        "Add Transaction": TransactionSection(current_user_email).render,
        "Analysis": AnalysisSection(current_user_email).render,
        "Expenses": ExpenseSection(current_user_email).render,
        "Debts": DebtSection(current_user_email).render,
        "Investments": InvestmentSection(current_user_email).render,
        "Budget": BudgetSection(current_user_email).render,
    }

    if menu in sections:
        sections[menu]()
