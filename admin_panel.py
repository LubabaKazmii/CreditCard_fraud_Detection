# admin_panel.py
import streamlit as st
from database import fetch_transactions
import sqlite3

def admin_panel():
# Admin Panel
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
            conn = sqlite3.connect('my_database.db')
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
