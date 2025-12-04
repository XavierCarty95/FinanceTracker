import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import add_transaction

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = 'login'

def show_dashboard_page():
    user = st.session_state.users_db[st.session_state.current_user]
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🏦 MyBank")
        st.write(f"Welcome, **{user['full_name'].split()[0]}**!")
        st.write("")
        
        menu = st.radio("Navigation", ["🏠 Home", "💳 Add Transaction", "📊 Analysis"], label_visibility="collapsed")
        
        st.write("")
        st.write("")
        st.markdown("---")
        
        if st.button("🚪 Logout", width="stretch"):
            logout()
            st.rerun()
    
    # Main Content Area
    if menu == "🏠 Home":
        home_section(user)
    elif menu == "💳 Add Transaction":
        add_transaction_section(user)
    elif menu == "📊 Analysis":
        analysis_section(user)

def home_section(user):
    st.title("🏠 Dashboard")
    st.write(f"Welcome back, **{user['full_name']}**!")
    st.write("")
    
    # Account Balance Card
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; color: white;'>
            <h3 style='margin: 0; font-weight: 300;'>Available Balance</h3>
            <h1 style='margin: 10px 0; font-size: 48px;'>${user['balance']:,.2f}</h1>
            <p style='margin: 0; opacity: 0.9;'>Account: ****{user['account_number'][-4:]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Account Type", user['account_type'], delta=None)
    
    with col3:
        st.metric("Bank", user['bank_name'][:15], delta=None)
    
    st.write("")
    st.write("")
    
    # Account Details Section
    st.subheader("📋 Account Information")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("##### Personal Details")
        st.write(f"**Full Name:** {user['full_name']}")
        st.write(f"**Email:** {st.session_state.current_user}")
        st.write(f"**Phone:** {user['phone']}")
        st.write(f"**Date of Birth:** {user['birth_date']}")
        st.write(f"**Gender:** {user['gender']}")
    
    with col_b:
        st.markdown("##### Banking Details")
        st.write(f"**Bank Name:** {user['bank_name']}")
        st.write(f"**Account Number:** ****{user['account_number'][-4:]}")
        st.write(f"**Routing Number:** {user['routing_number']}")
        st.write(f"**Account Type:** {user['account_type']}")
        st.write(f"**Current Balance:** ${user['balance']:,.2f}")

def add_transaction_section(user):
    st.title("💳 Add Transaction")
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
                    # Determine transaction amount (negative for debit, positive for credit)
                    final_amount = amount if "Credit" in transaction_type else -amount
                    
                    transaction_data = {
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'description': description,
                        'amount': final_amount,
                        'type': 'credit' if "Credit" in transaction_type else 'debit',
                        'notes': notes if notes else ''
                    }
                    
                    if add_transaction(st.session_state.current_user, transaction_data, st.session_state.users_db):
                        st.success("✅ Transaction added successfully!")
                        st.balloons()
                        
                        # Reload user data
                        st.session_state.users_db = st.session_state.users_db
                        
                        st.info(f"New balance: ${st.session_state.users_db[st.session_state.current_user]['balance']:,.2f}")
                    else:
                        st.error("Failed to add transaction")
    
    with col2:
        st.subheader("Current Balance")
        st.metric("Balance", f"${user['balance']:,.2f}")
        st.write("")
        
        st.info("💡 **Tips:**\n\n• Credit: Money coming in (salary, refunds)\n\n• Debit: Money going out (bills, purchases)")

def analysis_section(user):
    st.title("📊 Financial Analysis")
    st.write(f"Account analytics for **{user['full_name']}**")
    st.write("")
    
    # Summary Metrics
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
    
    # Charts Section
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Balance Trend")
        # Sample data for visualization
        
        dates = pd.date_range(end=datetime.now(), periods=6, freq='ME')
        balances = [10000, 11500, 13200, 14800, 15200, user['balance']]
        
        chart_data = pd.DataFrame({
            'Month': dates.strftime('%b %Y'),
            'Balance': balances
        })
        
        st.line_chart(chart_data.set_index('Month'))
    
    with col_chart2:
        st.subheader("💳 Spending Categories")
        
        categories = pd.DataFrame({
            'Category': ['Groceries', 'Utilities', 'Entertainment', 'Transport', 'Others'],
            'Amount': [450, 200, 150, 180, 320]
        })
        
        st.bar_chart(categories.set_index('Category'))
    
    st.write("")
    st.write("")
    
    # Recent Activity
    st.subheader("🕐 Recent Transactions")
    
    # Get transactions from user data
    if 'transactions' in user and user['transactions']:
        transactions_list = user['transactions'][:10]  # Show last 10 transactions
        
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
            running_balance -= trans['amount']  # Subtract to get previous balance
        
        transactions = pd.DataFrame(transactions_data)
        st.dataframe(transactions, width="stretch", hide_index=True)
    else:
        st.info("No transactions yet. Add your first transaction using the 'Add Transaction' page!")