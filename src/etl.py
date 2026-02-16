import pandas as pd
import sqlite3
from pathlib import Path

def load_raw_data(filepath='data/raw/telco_churn.csv'):
    """Load raw CSV data"""
    df = pd.read_csv(str(Path(filepath)))
    return df


def clean_data(df):
    """Clean and transform data"""
    df = df.copy()
    
    # Handle TotalCharges (has spaces for missing values)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'].fillna(0, inplace=True)
    
    # Convert target to binary
    df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
    
    # Convert SeniorCitizen to string for consistency
    df['SeniorCitizen'] = df['SeniorCitizen'].map({0: 'No', 1: 'Yes'})
    
    return df

def create_sql_schema(db_path='data/churn.db'):
    """Create SQLite database and tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customerID TEXT PRIMARY KEY,
            gender TEXT,
            SeniorCitizen TEXT,
            Partner TEXT,
            Dependents TEXT,
            tenure INTEGER,
            PhoneService TEXT,
            MultipleLines TEXT,
            InternetService TEXT,
            OnlineSecurity TEXT,
            OnlineBackup TEXT,
            DeviceProtection TEXT,
            TechSupport TEXT,
            StreamingTV TEXT,
            StreamingMovies TEXT,
            Contract TEXT,
            PaperlessBilling TEXT,
            PaymentMethod TEXT,
            MonthlyCharges REAL,
            TotalCharges REAL,
            Churn INTEGER
        )
    ''')
    
    # Create KPI aggregates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kpi_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_customers INTEGER,
            churned_customers INTEGER,
            churn_rate REAL,
            avg_monthly_charges REAL,
            avg_tenure REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def load_to_sql(df, db_path='data/churn.db'):
    """Load cleaned data into SQLite"""
    conn = sqlite3.connect(db_path)
    
    # Load main data
    df.to_sql('customers', conn, if_exists='replace', index=False)
    
    # Calculate and insert KPIs
    kpi_data = {
        'total_customers': len(df),
        'churned_customers': int(df['Churn'].sum()),
        'churn_rate': float(df['Churn'].mean() * 100),
        'avg_monthly_charges': float(df['MonthlyCharges'].mean()),
        'avg_tenure': float(df['tenure'].mean())
    }
    
    pd.DataFrame([kpi_data]).to_sql('kpi_summary', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"✅ Loaded {len(df)} records to database")

def run_etl():
    """Run complete ETL pipeline"""
    print("🔄 Starting ETL pipeline...")
    
    # Extract
    df = load_raw_data()
    print(f"📥 Loaded {len(df)} raw records")
    
    # Transform
    df_clean = clean_data(df)
    print(f"✨ Cleaned data")
    
    # Save processed CSV
    df_clean.to_csv('data/processed/telco_churn_clean.csv', index=False)
    
    # Load to SQL
    create_sql_schema()
    load_to_sql(df_clean)
    
    print("✅ ETL complete!")
    return df_clean

if __name__ == '__main__':
    run_etl()
