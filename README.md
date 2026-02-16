# 🎯 Customer Churn Prediction System

AI-powered customer retention platform using Machine Learning, FastAPI, React, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18-cyan)
![ML](https://img.shields.io/badge/ROC--AUC-83%25-orange)

## 🚀 Features

- ✅ **ML Model**: Random Forest classifier with 83% ROC-AUC
- ✅ **REST API**: FastAPI backend with auto-generated Swagger docs
- ✅ **Modern UI**: React dashboard with Apple dark theme
- ✅ **Analytics Dashboard**: Streamlit-based business intelligence
- ✅ **Batch Predictions**: Upload CSV, predict multiple customers
- ✅ **Real-time Predictions**: Single customer risk assessment
- ✅ **SQL Analytics**: SQLite database with KPI tracking

## 📊 Model Performance

- **ROC-AUC**: 83.48%
- **Accuracy**: 80%
- **Precision**: 79%
- **Recall**: 80%

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- FastAPI
- scikit-learn
- MLflow
- SQLite

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Recharts
- Axios

**Dashboard:**
- Streamlit
- Plotly
- Pandas

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/customer-churn-prediction.git
cd customer-churn-prediction

# Backend setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run ETL
python src/etl.py

# Train model
python src/train.py

# Start API
uvicorn api.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Streamlit (new terminal)
streamlit run dashboard/app.py



churn-prediction-system/
├── data/
│   ├── raw/              # Original dataset
│   ├── processed/        # Cleaned data
│   └── churn.db         # SQLite database
├── src/
│   ├── etl.py           # ETL pipeline
│   ├── train.py         # Model training
│   └── predict.py       # Prediction logic
├── api/
│   └── main.py          # FastAPI backend
├── frontend/
│   └── src/
│       └── App.jsx      # React dashboard
├── dashboard/
│   └── app.py           # Streamlit dashboard
├── models/
│   └── churn_model.pkl  # Trained model
└── notebooks/           # Jupyter notebooks
