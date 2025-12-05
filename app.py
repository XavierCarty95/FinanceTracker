import streamlit as st
from database import load_users
from login_page import show_login_page
from signup_page import show_signup_page
from dashboard_page import show_dashboard_page

# Page configuration
st.set_page_config(page_title="MyBank", page_icon="🏦", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'signup_success' not in st.session_state:
    st.session_state.signup_success = False
if 'users_db' not in st.session_state:
    st.session_state.users_db = load_users()

# Page Routing
if not st.session_state.logged_in:
    if st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'signup':
        show_signup_page()
else:
    show_dashboard_page()