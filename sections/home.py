import streamlit as st


def render_home(user):
    st.title("Dashboard")
    st.write(f"Welcome back, **{user['full_name']}**!")
    st.write("")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; color: white;'>
            <h3 style='margin: 0; font-weight: 300;'>Available Balance</h3>
            <h1 style='margin: 10px 0; font-size: 48px;'>${user['balance']:,.2f}</h1>
            <p style='margin: 0; opacity: 0.9;'>Account: ****{user['account_number'][-4:]}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.metric("Account Type", user['account_type'], delta=None)

    with col3:
        st.metric("Bank", user['bank_name'][:15], delta=None)

    st.write("")
    st.write("")

    st.subheader("Account Information")

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
