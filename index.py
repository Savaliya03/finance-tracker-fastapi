# .\venv\Scripts\activate
#  streamlit run index.py

import streamlit as st
import requests
from datetime import date
import pandas as pd

API_URL = "https://pft-fastapi.onrender.com/"

# Function for Login
def login():
    st.title("Login")
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        payload = {
            "username": username,
            "password": password
        }
        try:
            # Send POST request to the backend for login
            response = requests.post(f"{API_URL}token", data=payload)
            if response.status_code == 200:
                token = response.json().get("access_token")
                # Store token in session state for later use
                st.session_state.token = token
                st.success("Login successful!")
                st.rerun()  # Force a page refresh to show the updated state
            else:
                st.error(f"Login failed: {response.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

# Function for Sign Up
def sign_up():
    st.title("Sign Up")
    with st.form(key="signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Sign Up")

    if submit_button:
        payload = {
            "username": username,
            "password": password
        }
        try:
            # Send POST request to the backend to create a new user
            response = requests.post(f"{API_URL}users/", json=payload)
            if response.status_code == 200:
                st.success("User created successfully! You can now log in.")
            else:
                st.error(f"Error: {response.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

# Function for Logging Out
def log_out():
    if "token" in st.session_state:
        del st.session_state.token
        st.success("Logged out successfully.")
        st.rerun()  # Trigger a page refresh to clear session state

# Function to show the sidebar with login or app options
def show_sidebar():
    if "token" in st.session_state:
        # User is logged in, show app options
        with st.sidebar:
            st.header("Welcome to the Personal Finance Tracker")
            option = st.radio(
                "Choose an option:",
                ("New Transaction", "List Transactions", "Analysis", "Log Out")
            )
        return option
    else:
        # User is not logged in, show login/signup form
        option = st.sidebar.radio(
            "Choose an option:",
            ("Login", "Sign Up")
        )
        return option

# Main Logic
option = show_sidebar()

if option == "Login":
    login()

elif option == "Sign Up":
    sign_up()

elif option == "Log Out":
    log_out()

# Handle the different page options if user is logged in
if "token" in st.session_state:
    # Show New Transaction form
    if option == "New Transaction":
        st.title("New Transaction")

        # Display success message if exists
        if "transaction_success" in st.session_state:
            st.success(st.session_state.transaction_success)
            del st.session_state.transaction_success

        with st.form(key="transaction_form", clear_on_submit=True):
            amount = st.number_input("Amount", min_value=0.01, format="%.2f", step=0.01)
            type = st.radio("Type", ("Credit", "Debit"), horizontal= True)
            to_from = st.text_input("To/From(name)")
            CATEGORIES = ['Rent', 'Salary', 'Utilities', 'Food', 'Transportation', 'Entertainment', 'Study', 'Groceries','Other']
            category = st.selectbox("Category", CATEGORIES)
            transaction_date = st.date_input("Transaction Date", value=date.today())
            description = st.text_input("Description")
            submit_button = st.form_submit_button("Submit Transaction")

        if submit_button:
            # Validate required fields
            if not to_from or to_from.strip() == "":
                st.error("Please enter To/From name")
            elif amount <= 0:
                st.error("Please enter a valid amount")
            else:
                payload = {
                    "name": to_from,
                    "amount": amount,
                    "type": type,
                    "category": category,
                    "date": str(transaction_date),
                    "description" : str(description),
                }

                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                try:
                    response = requests.post(f"{API_URL}transactions/", json=payload, headers=headers)
                    if response.status_code == 200:
                        # Store success message in session state
                        st.session_state.transaction_success = "Transaction completed successfully!"
                        st.rerun()
                    else:
                        st.error(f"Error: {response.status_code}, {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")

    # Show List of Transactions
    elif option == "List Transactions":
        st.title("Transactions List")

        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}transactions/", headers=headers)
        if response.status_code == 200:
            transactions = response.json()
            df = pd.DataFrame(transactions)
            st.write(df)
        else:
            st.error(f"Error: {response.status_code}, {response.text}")

    # Show Analysis Content
    elif option == "Analysis":
        st.header("Analysis")
        st.write("Analyze your transactions with the following insights:")

        # Input Form for Date Range
        with st.form(key="transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start date")
            with col2:
                end_date = st.date_input("End date")
            submit_button = st.form_submit_button("Submit")

        # If dates are submitted
        if submit_button:
            st.write(start_date, end_date)
            payload = {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            }

            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            try:
                # Get summary data
                response = requests.get(f"{API_URL}transactions/summary/", params=payload, headers=headers)
                
                # Get all transactions in date range
                transactions_response = requests.get(f"{API_URL}transactions/", headers=headers)
                
                if response.status_code == 200 and transactions_response.status_code == 200:
                    data = response.json()
                    
                    # Display the Income vs Expense Summary
                    st.subheader("Income vs Expense Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Income", f"₹{data['total_income']:.2f}")
                    with col2:
                        st.metric("Total Expense", f"₹{data['total_expense']:.2f}")
                    with col3:
                        st.metric("Net Balance", f"₹{data['net_balance']:.2f}")

                    # Display Detailed Transactions Table
                    st.subheader("Detailed Transactions")
                    all_transactions = transactions_response.json()
                    
                    # Filter transactions by date range
                    filtered_transactions = [
                        t for t in all_transactions 
                        if start_date.strftime('%Y-%m-%d') <= t['date'] <= end_date.strftime('%Y-%m-%d')
                    ]
                    
                    if filtered_transactions:
                        # Create DataFrame with all transaction details
                        df = pd.DataFrame(filtered_transactions)
                        
                        # Add Credit and Debit columns
                        df['Credit'] = df.apply(lambda row: row['amount'] if row['type'] == 'Credit' else 0, axis=1)
                        df['Debit'] = df.apply(lambda row: row['amount'] if row['type'] == 'Debit' else 0, axis=1)
                        
                        # Calculate running balance
                        df['Balance'] = (df['Credit'] - df['Debit']).cumsum()
                        
                        # Reorder columns for better display
                        display_df = df[['date', 'name', 'description', 'category', 'type', 'Credit', 'Debit', 'Balance']]
                        
                        # Format currency columns
                        display_df['Credit'] = display_df['Credit'].apply(lambda x: f"₹{x:.2f}" if x > 0 else "-")
                        display_df['Debit'] = display_df['Debit'].apply(lambda x: f"₹{x:.2f}" if x > 0 else "-")
                        display_df['Balance'] = display_df['Balance'].apply(lambda x: f"₹{x:.2f}")
                        
                        # Rename columns for better readability
                        display_df.columns = ['Date', 'Name', 'Description', 'Category', 'Type', 'Credit (₹)', 'Debit (₹)', 'Balance (₹)']
                        
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.info("No transactions found in the selected date range.")

                    # Display the Category-Wise Breakdown
                    st.subheader("Category-Wise Expense Breakdown")
                    category_data = data["category_breakdown"]
                    
                    if category_data:
                        # Convert category_data to a DataFrame for better visualization
                        category_df = pd.DataFrame(category_data)
                        st.write(category_df)
                        
                        # Create a bar chart for Category-Wise Breakdown
                        st.bar_chart(category_df.set_index("category")["amount"])
                    else:
                        st.info("No expense data available for categories.")

                    # Display the Monthly Trends
                    st.subheader("Monthly Trends")
                    monthly_data = pd.DataFrame(data["monthly_trends"])

                    if not monthly_data.empty:
                        # Ensure the 'month' column is a string for better chart display
                        monthly_data["month"] = monthly_data["month"].astype(str)
                        st.line_chart(monthly_data.set_index("month"))
                    else:
                        st.info("No monthly trend data available.")

                    # Display the Top Transactions
                    st.subheader("Highest Transactions")
                    top_transactions = pd.DataFrame(data["top_transactions"])
                    if not top_transactions.empty:
                        st.table(top_transactions)
                    else:
                        st.info("No top transactions available.")
                else:
                    st.error(f"Error: {response.status_code}, {response.text}")

            except Exception as e:
                    st.error(f"An error occurred: {e}")

