from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.predict import predict_churn
import sqlite3
import pandas as pd

app = FastAPI(
    title="Churn Prediction API",
    description="ML-powered customer churn prediction system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CustomerInput(BaseModel):
    gender: Literal['Male', 'Female']
    SeniorCitizen: Literal['Yes', 'No']
    Partner: Literal['Yes', 'No']
    Dependents: Literal['Yes', 'No']
    tenure: int = Field(ge=0, le=100)
    PhoneService: Literal['Yes', 'No']
    MultipleLines: Literal['Yes', 'No', 'No phone service']
    InternetService: Literal['DSL', 'Fiber optic', 'No']
    OnlineSecurity: Literal['Yes', 'No', 'No internet service']
    OnlineBackup: Literal['Yes', 'No', 'No internet service']
    DeviceProtection: Literal['Yes', 'No', 'No internet service']
    TechSupport: Literal['Yes', 'No', 'No internet service']
    StreamingTV: Literal['Yes', 'No', 'No internet service']
    StreamingMovies: Literal['Yes', 'No', 'No internet service']
    Contract: Literal['Month-to-month', 'One year', 'Two year']
    PaperlessBilling: Literal['Yes', 'No']
    PaymentMethod: Literal['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)']
    MonthlyCharges: float = Field(gt=0)
    TotalCharges: float = Field(ge=0)

class PredictionResponse(BaseModel):
    churn_probability: float
    churn_prediction: int
    risk_level: str

@app.get("/")
def root():
    return {"message": "Churn Prediction API", "status": "active"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "loaded"}

@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerInput):
    """Predict churn for a customer"""
    try:
        customer_dict = customer.dict()
        result = predict_churn(customer_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis")
def get_kpis():
    """Get business KPIs from database"""
    try:
        conn = sqlite3.connect('data/churn.db')
        kpi = pd.read_sql_query("SELECT * FROM kpi_summary", conn)
        conn.close()
        return kpi.to_dict(orient='records')[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
