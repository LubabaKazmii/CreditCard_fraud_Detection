# database.py
import sqlite3
import pandas as pd

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




import streamlit as st
from user_panel import user_panel
from admin_panel import admin_panel

# Check for user login or role
role = st.sidebar.selectbox("Select Role", ["User", "Admin"])

if role == "User":
    user_panel()  # Calls the user_panel function
else:
    admin_panel()  # Calls the admin_panel function
