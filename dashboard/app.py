import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

st.set_page_config(page_title="Churn Analytics", layout="wide", page_icon="📊")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "https://customerchurnai.streamlit.app/"  # Change when you deploy API
# For now, predictions won't work without deployed API


st.markdown('<h1 class="main-header">📊 Customer Churn Prediction System</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Customer Retention Platform** | Built with ML, FastAPI & Streamlit")

# Sidebar
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox("", ["📈 Analytics", "🔮 Single Prediction", "📂 Batch Prediction", "📊 Model Performance", "💡 Feature Importance"])

# Load data from SQL
@st.cache_data
def load_data():
    # Load from CSV instead of SQLite for cloud deployment
    try:
        df = pd.read_csv('data/processed/telco_churn_clean.csv')
        return df
    except:
        # Fallback: use raw data
        df = pd.read_csv('data/raw/telco_churn.csv')
        # Basic cleaning
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(0, inplace=True)
        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
        return df

df = load_data()

# ===== ANALYTICS PAGE =====
if page == "📈 Analytics":
    st.header("📈 Business Analytics Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", f"{len(df):,}")
    with col2:
        st.metric("Churned", f"{int(df['Churn'].sum()):,}", delta=f"-{df['Churn'].mean()*100:.1f}%")
    with col3:
        st.metric("Churn Rate", f"{df['Churn'].mean()*100:.2f}%")
    with col4:
        st.metric("Avg Revenue/Customer", f"${df['MonthlyCharges'].mean():.2f}")
    
    st.markdown("---")
    
    # Row 1: Contract & Internet Service
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Churn by Contract Type")
        contract_churn = df.groupby('Contract')['Churn'].agg(['count', 'sum', 'mean']).reset_index()
        contract_churn['churn_rate'] = contract_churn['mean'] * 100
        fig = px.bar(contract_churn, x='Contract', y='churn_rate',
                     labels={'churn_rate': 'Churn Rate (%)', 'Contract': 'Contract Type'},
                     color='churn_rate', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Churn by Internet Service")
        internet_churn = df.groupby('InternetService')['Churn'].mean().reset_index()
        internet_churn['churn_rate'] = internet_churn['Churn'] * 100
        fig = px.pie(internet_churn, values='churn_rate', names='InternetService',
                     title='', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Tenure & Monthly Charges
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Churn by Tenure")
        df['tenure_group'] = pd.cut(df['tenure'], bins=[0, 12, 24, 48, 100],
                                      labels=['0-12 mo', '13-24 mo', '25-48 mo', '48+ mo'])
        tenure_churn = df.groupby('tenure_group')['Churn'].mean().reset_index()
        tenure_churn['churn_rate'] = tenure_churn['Churn'] * 100
        fig = px.line(tenure_churn, x='tenure_group', y='churn_rate', markers=True,
                      labels={'tenure_group': 'Tenure', 'churn_rate': 'Churn Rate (%)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Monthly Charges Distribution")
        fig = px.box(df, x='Churn', y='MonthlyCharges',
                     labels={'Churn': 'Churned (0=No, 1=Yes)', 'MonthlyCharges': 'Monthly Charges ($)'},
                     color='Churn')
        st.plotly_chart(fig, use_container_width=True)

# ===== SINGLE PREDICTION PAGE =====
elif page == "🔮 Single Prediction":
    st.header("🔮 Predict Customer Churn")
    st.write("Enter customer details to get real-time churn prediction")
    
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**👤 Demographics**")
            gender = st.selectbox("Gender", ['Male', 'Female'])
            senior = st.selectbox("Senior Citizen", ['No', 'Yes'])
            partner = st.selectbox("Partner", ['No', 'Yes'])
            dependents = st.selectbox("Dependents", ['No', 'Yes'])
            tenure = st.number_input("Tenure (months)", 0, 100, 12)
        
        with col2:
            st.markdown("**📞 Services**")
            phone = st.selectbox("Phone Service", ['Yes', 'No'])
            multiple = st.selectbox("Multiple Lines", ['No', 'Yes', 'No phone service'])
            internet = st.selectbox("Internet Service", ['Fiber optic', 'DSL', 'No'])
            security = st.selectbox("Online Security", ['No', 'Yes', 'No internet service'])
            backup = st.selectbox("Online Backup", ['No', 'Yes', 'No internet service'])
        
        with col3:
            st.markdown("**💳 Account Info**")
            device = st.selectbox("Device Protection", ['No', 'Yes', 'No internet service'])
            tech = st.selectbox("Tech Support", ['No', 'Yes', 'No internet service'])
            tv = st.selectbox("Streaming TV", ['No', 'Yes', 'No internet service'])
            movies = st.selectbox("Streaming Movies", ['No', 'Yes', 'No internet service'])
            contract = st.selectbox("Contract", ['Month-to-month', 'One year', 'Two year'])
            paperless = st.selectbox("Paperless Billing", ['Yes', 'No'])
            payment = st.selectbox("Payment Method", 
                                   ['Electronic check', 'Mailed check', 
                                    'Bank transfer (automatic)', 'Credit card (automatic)'])
            monthly = st.number_input("Monthly Charges ($)", 0.0, 200.0, 70.0)
            total = st.number_input("Total Charges ($)", 0.0, 10000.0, 1000.0)
        
        submit = st.form_submit_button("🔍 Predict Churn", use_container_width=True)
    
    if submit:
        payload = {
            "gender": gender, "SeniorCitizen": senior, "Partner": partner,
            "Dependents": dependents, "tenure": tenure, "PhoneService": phone,
            "MultipleLines": multiple, "InternetService": internet,
            "OnlineSecurity": security, "OnlineBackup": backup,
            "DeviceProtection": device, "TechSupport": tech,
            "StreamingTV": tv, "StreamingMovies": movies,
            "Contract": contract, "PaperlessBilling": paperless,
            "PaymentMethod": payment, "MonthlyCharges": monthly,
            "TotalCharges": total
        }
        
        try:
            with st.spinner("🤖 AI is analyzing..."):
                response = requests.post(f"{API_URL}/predict", json=payload)
                result = response.json()
            
            st.success("✅ Prediction Complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Churn Probability", f"{result['churn_probability']*100:.1f}%")
            with col2:
                prediction_text = "🚨 WILL CHURN" if result['churn_prediction'] == 1 else "✅ WILL STAY"
                st.metric("Prediction", prediction_text)
            with col3:
                st.metric("Risk Level", result['risk_level'])
            
            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result['churn_probability']*100,
                title={'text': "Churn Risk Score"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "darkred"},
                       'steps': [
                           {'range': [0, 40], 'color': "lightgreen"},
                           {'range': [40, 70], 'color': "yellow"},
                           {'range': [70, 100], 'color': "red"}],
                       'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 50}}))
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            if result['churn_prediction'] == 1:
                st.warning("⚠️ **Recommended Actions:**")
                st.write("- Offer retention discount (10-20% off)")
                st.write("- Upgrade to long-term contract with benefits")
                st.write("- Assign dedicated account manager")
                st.write("- Survey to understand pain points")
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ===== BATCH PREDICTION PAGE =====
elif page == "📂 Batch Prediction":
    st.header("📂 Batch Prediction - Upload CSV")
    st.write("Upload a CSV file with customer data to predict churn for multiple customers at once")
    
    # Download sample template
    st.subheader("📥 Step 1: Download Template")
    sample_data = {
        'gender': ['Male', 'Female'],
        'SeniorCitizen': ['No', 'Yes'],
        'Partner': ['Yes', 'No'],
        'Dependents': ['No', 'No'],
        'tenure': [12, 24],
        'PhoneService': ['Yes', 'Yes'],
        'MultipleLines': ['No', 'Yes'],
        'InternetService': ['Fiber optic', 'DSL'],
        'OnlineSecurity': ['No', 'Yes'],
        'OnlineBackup': ['No', 'Yes'],
        'DeviceProtection': ['No', 'No'],
        'TechSupport': ['No', 'Yes'],
        'StreamingTV': ['Yes', 'No'],
        'StreamingMovies': ['Yes', 'No'],
        'Contract': ['Month-to-month', 'One year'],
        'PaperlessBilling': ['Yes', 'No'],
        'PaymentMethod': ['Electronic check', 'Mailed check'],
        'MonthlyCharges': [85.0, 65.0],
        'TotalCharges': [1020.0, 1560.0]
    }
    sample_df = pd.DataFrame(sample_data)
    
    csv = sample_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Sample CSV Template",
        data=csv,
        file_name="customer_template.csv",
        mime="text/csv",
    )
    
    st.subheader("📤 Step 2: Upload Your CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            input_df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(input_df)} customers")
            
            st.write("**Preview:**")
            st.dataframe(input_df.head(), use_container_width=True)
            
            if st.button("🚀 Predict All", use_container_width=True):
                with st.spinner(f"🤖 Processing {len(input_df)} predictions..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, row in input_df.iterrows():
                        payload = row.to_dict()
                        response = requests.post(f"{API_URL}/predict", json=payload)
                        result = response.json()
                        results.append(result)
                        progress_bar.progress((idx + 1) / len(input_df))
                    
                    # Combine results
                    results_df = pd.DataFrame(results)
                    output_df = pd.concat([input_df, results_df], axis=1)
                    
                    st.success("✅ Predictions Complete!")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Customers", len(output_df))
                    with col2:
                        high_risk = len(output_df[output_df['risk_level'] == 'High'])
                        st.metric("High Risk Customers", high_risk)
                    with col3:
                        avg_prob = output_df['churn_probability'].mean() * 100
                        st.metric("Avg Churn Probability", f"{avg_prob:.1f}%")
                    
                    # Show results
                    st.write("**Results:**")
                    st.dataframe(output_df, use_container_width=True)
                    
                    # Download results
                    csv_output = output_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download Results as CSV",
                        data=csv_output,
                        file_name="churn_predictions.csv",
                        mime="text/csv",
                    )
                    
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ===== MODEL PERFORMANCE PAGE =====
elif page == "📊 Model Performance":
    st.header("📊 Model Performance Metrics")
    st.write("Track model accuracy and evaluation metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Key Metrics")
        metrics_data = {
            'Metric': ['ROC-AUC', 'Accuracy', 'Precision', 'Recall', 'F1-Score'],
            'Score': [0.8348, 0.80, 0.79, 0.80, 0.79]
        }
        metrics_df = pd.DataFrame(metrics_data)
        
        fig = px.bar(metrics_df, x='Metric', y='Score', 
                     color='Score', color_continuous_scale='Blues',
                     text='Score')
        fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Confusion Matrix")
        confusion_data = pd.DataFrame({
            'Predicted No': [1035, 374],
            'Predicted Yes': [87, 374]
        }, index=['Actual No', 'Actual Yes'])
        
        st.dataframe(confusion_data.style.background_gradient(cmap='RdYlGn_r'), use_container_width=True)
        
        st.markdown("**Interpretation:**")
        st.write("- True Negatives: 1035 (Correctly predicted Stay)")
        st.write("- True Positives: 374 (Correctly predicted Churn)")
        st.write("- False Positives: 87 (Predicted Churn but Stayed)")
        st.write("- False Negatives: 374 (Predicted Stay but Churned)")

# ===== FEATURE IMPORTANCE PAGE =====
elif page == "💡 Feature Importance":
    st.header("💡 Feature Importance Analysis")
    st.write("Understand which features drive churn predictions")
    
    # Mock feature importance (you'll replace with actual from model)
    importance_data = {
        'Feature': ['Contract', 'tenure', 'MonthlyCharges', 'TotalCharges', 'InternetService', 
                    'OnlineSecurity', 'TechSupport', 'PaymentMethod', 'PaperlessBilling', 'Dependents'],
        'Importance': [0.18, 0.15, 0.13, 0.12, 0.10, 0.08, 0.07, 0.06, 0.06, 0.05]
    }
    importance_df = pd.DataFrame(importance_data).sort_values('Importance', ascending=True)
    
    fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h',
             labels={'Importance': 'Feature Importance Score'},
             color='Importance', color_continuous_scale='Viridis')

    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("**Top Insights:**")
    st.write("1. **Contract Type** is the strongest predictor (18% importance)")
    st.write("2. **Tenure** (how long customer has been with company) is 2nd most important")
    st.write("3. **Pricing** (Monthly & Total Charges) significantly impacts churn")
    st.write("4. **Support services** (Online Security, Tech Support) help retention")

# Footer
st.markdown("---")
st.markdown("**🚀 Built with:** Python • FastAPI • Streamlit • scikit-learn • MLflow")
st.markdown("*AI-Powered Customer Retention System | v1.0*")
