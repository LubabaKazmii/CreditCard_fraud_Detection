import sqlite3
import pandas as pd
import streamlit as st
import random
import pickle
import numpy as np
import os

# Load the fraud detection model
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'fraud_detection_model.pkl')

# Using joblib to load the model (since it's saved using pickle or joblib)
import joblib
fraud_model = joblib.load(model_path)

# Database creation and management functions
def create_table():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            tx_datetime TEXT,
            customer_id INTEGER,
            terminal_id INTEGER,
            tx_amount REAL,
            tx_time_seconds INTEGER,
            tx_time_days INTEGER,
            location TEXT,
            fraud_status TEXT,
            stop_transaction TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

def create_connection():
    return sqlite3.connect('my_database.db')

def insert_transaction(transaction):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (
            transaction_id, tx_datetime, customer_id, terminal_id, 
            tx_amount, tx_time_seconds, tx_time_days, location, 
            fraud_status, stop_transaction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, transaction)
    conn.commit()
    conn.close()

def fetch_transactions():
    conn = create_connection()
    transactions = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return transactions

# Fraud prediction function (now only returns fraud status)
def predict_fraud_status(tx_amount, tx_time_seconds, tx_time_days, customer_id, terminal_id):
    input_data = pd.DataFrame([{
        'TX_AMOUNT': tx_amount,
        'TX_TIME_SECONDS': tx_time_seconds,
        'TX_TIME_DAYS': tx_time_days,
        'CUSTOMER_ID': customer_id,
        'TERMINAL_ID': terminal_id
    }])
    
    try:
        # Predicting fraud class: 0 = Legitimate, 1 = Fraud
        prediction = fraud_model.predict(input_data)
        # Assign fraud status based on prediction
        fraud_status = "Fraud" if prediction[0] == 1 else "Legitimate"
    except Exception as e:
        st.error(f"Error predicting fraud status: {str(e)}")
        fraud_status = "Error"
    
    return fraud_status

# --- User Panel ---
st.title("Fraud Detection System - User Panel")
st.write("## Submit Your Transaction")

with st.form("transaction_form"):
    tx_amount = st.number_input("Transaction Amount", min_value=1.0, step=0.01)
    customer_id = st.number_input("Customer ID", min_value=1000, max_value=99999, step=1)
    terminal_id = st.number_input("Terminal ID", min_value=1000, max_value=99999, step=1)
    tx_time_seconds = st.number_input("Transaction Time (seconds)", min_value=0, max_value=86400, step=1)
    tx_time_days = st.number_input("Transaction Day", min_value=1, max_value=30, step=1)
    location = st.selectbox("Location", ['New York', 'Los Angeles', 'Chicago', 'San Francisco', 'Miami'])

    submit_button = st.form_submit_button("Submit Transaction")

    if submit_button:
        fraud_status = predict_fraud_status(tx_amount, tx_time_seconds, tx_time_days, customer_id, terminal_id)
        transaction_id = f"TX{random.randint(10000, 999999)}"
        tx_datetime = f"4/{random.randint(1, 30)}/2018 {random.randint(0, 23)}:{random.randint(0, 59)}"

        insert_transaction((
            transaction_id, tx_datetime, customer_id, terminal_id, 
            tx_amount, tx_time_seconds, tx_time_days, location, 
            fraud_status, 'Proceed'
        ))

        st.success(f"Transaction {transaction_id} submitted successfully!")
        st.write(f"**Fraud Status:** {fraud_status}")

# --- Admin Panel ---
st.title("Fraud Detection System - Admin Panel")
st.write("## Transactions Overview")

transactions_df = fetch_transactions()
if not transactions_df.empty:
    st.write(transactions_df)

    st.write("### Stop Fraudulent Transaction")
    transaction_to_stop = st.selectbox("Select a Transaction to Stop", transactions_df['transaction_id'].tolist())

    if st.button("Stop Selected Transaction"):
        transaction = transactions_df[transactions_df['transaction_id'] == transaction_to_stop]
        if not transaction.empty and transaction['fraud_status'].values[0] == "Fraud":
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions
                SET stop_transaction = 'Stop'
                WHERE transaction_id = ?
            """, (transaction_to_stop,))
            conn.commit()
            conn.close()

            st.success(f"Transaction {transaction_to_stop} has been stopped due to fraud!")
        else:
            st.error("Transaction is legitimate or already stopped!")
else:
    st.write("No transactions found.")