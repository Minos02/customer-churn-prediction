from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.predict import predict_churn
import pandas as pd
import sqlite3

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

# Load data for KPIs
def load_data():
    try:
        df = pd.read_csv('data/processed/telco_churn_clean.csv')
    except:
        df = pd.read_csv('data/raw/telco_churn.csv')
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(0, inplace=True)
        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
    return df

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/kpis')
def get_kpis():
    try:
        df = load_data()
        return jsonify({
            'total_customers': int(len(df)),
            'churned_customers': int(df['Churn'].sum()),
            'churn_rate': float(df['Churn'].mean() * 100),
            'avg_monthly_charges': float(df['MonthlyCharges'].mean())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        result = predict_churn(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
