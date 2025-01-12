# fraud_model.py
import joblib
import pandas as pd

# Load the fraud detection model
model_path = 'fraud_detection_model.pkl'
fraud_model = joblib.load(model_path)

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
        fraud_status = "Error"
    
    return fraud_status
