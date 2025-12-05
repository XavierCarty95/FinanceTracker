import streamlit as st
from database import login_user

def show_login_page():
    st.markdown("<h1 style='text-align: center;'>MyBank</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Secure Banking at Your Fingertips</h3>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.write("")
            login_button = st.form_submit_button("Login", width="stretch", type="primary")
            
            if login_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                elif login_user(email, password, st.session_state.users_db):
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.session_state.page = 'dashboard'
                    from database import load_users
                    st.session_state.users_db = load_users()
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        
        st.write("")
        st.markdown("---")
        st.write("")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("Don't have an account?")
        with col_b:
            if st.button("Sign Up", width="stretch"):
                st.session_state.page = 'signup'
                st.rerun()
        
        # Demo credentials
        with st.expander("Demo Credentials"):
            st.code("Email: demo@example.com\nPassword: demo123")