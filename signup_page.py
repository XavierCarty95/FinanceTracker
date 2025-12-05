import streamlit as st
from database import validate_email, signup_user, load_users

def show_signup_page():
    st.title("Create New Account")
    st.markdown("Join MyBank today and experience secure banking")
    st.write("")
    
    # Check if signup was successful
    if st.session_state.signup_success:
        st.success("Account created successfully!")
        st.balloons()
        st.info("Please login with your credentials")
        
        if st.button("Go to Login"):
            st.session_state.page = 'login'
            st.session_state.signup_success = False
            st.rerun()
        return
    
    with st.form("signup_form"):
        # Personal Information
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email Address *", placeholder="john.doe@example.com")
            phone = st.text_input("Phone Number *", placeholder="+1 (555) 123-4567")
        
        with col2:
            from datetime import datetime
            birth_date = st.date_input("Date of Birth *", min_value=datetime(1900, 1, 1), max_value=datetime.now())
            gender = st.selectbox("Gender *", ["Male", "Female", "Other", "Prefer not to say"])
            st.write("")
        
        password = st.text_input("Password *", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter your password")
        
        st.write("")
        
        # Bank Account Details
        st.subheader("Bank Account Details")
        col3, col4 = st.columns(2)
        
        with col3:
            bank_name = st.text_input("Bank Name *", placeholder="First National Bank")
            account_number = st.text_input("Account Number *", placeholder="1234567890")
        
        with col4:
            routing_number = st.text_input("Routing Number *", placeholder="021000021")
            account_type = st.selectbox("Account Type *", ["Checking", "Savings"])
        
        st.write("")
        bank_balance = st.number_input("Initial Balance ($)", min_value=0.0, value=1000.0, step=100.0)
        st.write("")
        st.write("")
        
        # Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn1:
            cancel_button = st.form_submit_button("← Back to Login", width="stretch")
        with col_btn3:
            submit_button = st.form_submit_button("Create Account", type="primary", width="stretch")
        
        if cancel_button:
            st.session_state.page = 'login'
            st.rerun()
        
        if submit_button:
            errors = []
            
            # Validation
            if not full_name.strip():
                errors.append("Full name is required")
            if not email.strip():
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Invalid email format")
            elif email in st.session_state.users_db:
                errors.append("Email already registered")
            if not phone.strip():
                errors.append("Phone number is required")
            if not password:
                errors.append("Password is required")
            elif len(password) < 6:
                errors.append("Password must be at least 6 characters")
            if password != confirm_password:
                errors.append("Passwords do not match")
            if not bank_name.strip():
                errors.append("Bank name is required")
            if not account_number.strip():
                errors.append("Account number is required")
            elif not account_number.isdigit():
                errors.append("Account number must contain only digits")
            if not routing_number.strip():
                errors.append("Routing number is required")
            elif not routing_number.isdigit() or len(routing_number) != 9:
                errors.append("Routing number must be 9 digits")
            
            if errors:
                st.error("Please fix the following errors:")
                for error in errors:
                    st.write(f"• {error}")
            else:
                # Create user account
                user_data = {
                    'email': email,
                    'password': password,
                    'full_name': full_name,
                    'birth_date': birth_date.strftime('%Y-%m-%d'),
                    'gender': gender,
                    'phone': phone,
                    'bank_name': bank_name,
                    'account_number': account_number,
                    'routing_number': routing_number,
                    'account_type': account_type,
                    'balance': bank_balance,  # Initial balance
                    'transactions': [],  # Empty transaction list
                    'expenses': [],
                    'debts': [],
                    'investments': [],
                    'budget': {
                        'groceries': 400.0,
                        'rent': 1200.0,
                        'utilities': 200.0,
                        'transportation': 300.0,
                        'entertainment': 150.0,
                        'healthcare': 100.0,
                        'dining out': 200.0,
                        'shopping': 150.0,
                        'subscriptions': 50.0,
                        'other': 100.0
                    }  # Default monthly budget
                }
                
                if signup_user(user_data, st.session_state.users_db):
                    st.session_state.users_db = load_users()
                    st.session_state.signup_success = True
                    st.rerun()
                else:
                    st.error("Unable to create account. Please try again.")
