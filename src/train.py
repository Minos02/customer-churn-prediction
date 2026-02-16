import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib

def load_data(filepath='data/processed/telco_churn_clean.csv'):
    return pd.read_csv(filepath)

def preprocess_features(df):
    df = df.copy()
    
    # Drop customerID
    df = df.drop('customerID', axis=1, errors='ignore')
    
    # Separate target
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    
    # Encode categoricals
    categorical_cols = X.select_dtypes(include=['object']).columns
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
    
    # Create interaction features (KEY for 90%+)
    X['tenure_contract'] = X['tenure'] * X['Contract']
    X['charges_tenure'] = X['MonthlyCharges'] * X['tenure']
    X['internet_security'] = X['InternetService'] * X['OnlineSecurity']
    X['support_backup'] = X['TechSupport'] * X['OnlineBackup']
    
    # Scale
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    
    return X_scaled, y, label_encoders, scaler

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Gradient Boosting with optimized params for churn
    model = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        min_samples_split=20,
        min_samples_leaf=10,
        subsample=0.8,
        random_state=42
    )
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\n📊 Model Performance:")
    print(f"ROC-AUC: {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
    print(f"\n5-Fold CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    return model, X_train, X_test, y_train, y_test

def save_artifacts(model, label_encoders, scaler):
    artifacts = {'model': model, 'label_encoders': label_encoders, 'scaler': scaler}
    joblib.dump(artifacts, 'models/churn_model.pkl')
    print("✅ Model saved!")

def main():
    print("🚀 Training optimized model...")
    df = load_data()
    X, y, label_encoders, scaler = preprocess_features(df)
    model, _, _, _, _ = train_model(X, y)
    save_artifacts(model, label_encoders, scaler)
    print("✅ Complete!")

if __name__ == '__main__':
    main()
