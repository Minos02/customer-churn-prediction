import joblib
import pandas as pd
import numpy as np

def load_model(model_path='models/churn_model.pkl'):
    return joblib.load(model_path)

def predict_churn(customer_data, model_path='models/churn_model.pkl'):
    artifacts = load_model(model_path)
    model = artifacts['model']
    label_encoders = artifacts['label_encoders']
    scaler = artifacts['scaler']
    
    df = pd.DataFrame([customer_data])
    
    # Encode categoricals
    for col, le in label_encoders.items():
        if col in df.columns:
            df[col] = le.transform(df[col].astype(str))
    
    # Create interaction features (MUST match training!)
    df['tenure_contract'] = df['tenure'] * df['Contract']
    df['charges_tenure'] = df['MonthlyCharges'] * df['tenure']
    df['internet_security'] = df['InternetService'] * df['OnlineSecurity']
    df['support_backup'] = df['TechSupport'] * df['OnlineBackup']
    
    # Scale
    df_scaled = scaler.transform(df)
    
    # Predict
    churn_prob = model.predict_proba(df_scaled)[0][1]
    churn_label = int(churn_prob >= 0.5)
    
    return {
        'churn_probability': float(churn_prob),
        'churn_prediction': churn_label,
        'risk_level': 'High' if churn_prob >= 0.7 else 'Medium' if churn_prob >= 0.4 else 'Low'
    }
