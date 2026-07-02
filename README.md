# 💳 Financial Fraud Intelligence System

> End-to-end financial fraud detection platform on 1.1M+ PaySim mobile money transactions — combining SQL analytics, statistical testing, classical ML, deep learning (PyTorch GPU), and explainable AI (SHAP) — deployed as an interactive Streamlit dashboard.

## 🚀 Live Demo
👉 [Click here to view the live dashboard](https://dkr53ztwslsbappk2nzt5vn.streamlit.app/)

## 📌 Project Overview
- Analyzed **1,146,015 mobile money transactions**
- Built **5 ML/DL models** with best AUC-ROC of **99.95%**
- Detected fraud using **LightGBM, XGBoost (GPU), Neural Network (PyTorch GPU)**
- Implemented **SHAP explainability** for model interpretability
- Built **SQL analytics layer** using DuckDB with window functions & CTEs
- Conducted **statistical hypothesis testing** (T-test, Chi-square)
- Handled **extreme class imbalance** (0.058% fraud rate) using SMOTE

## 📊 Model Performance
| Model | AUC-ROC | Notes |
|-------|---------|-------|
| **LightGBM 🏆** | **0.9995** | Best overall — production deployed |
| XGBoost (GPU) | 0.9981 | GPU accelerated |
| Neural Network (GPU) | 0.9957 | PyTorch — 15 epochs |
| Random Forest | 0.9945 | Balanced class weights |
| Logistic Regression | 0.9708 | Baseline model |

## ✨ Dashboard Features
- **🏠 Executive Overview** — KPIs, fraud distribution, transaction volume by type
- **📊 Transaction Analysis** — Amount patterns, hourly trends, balance discrepancy analysis
- **🤖 Model Performance** — AUC-ROC comparison, model insights table
- **🔍 SHAP Explainability** — Feature importance, XAI business insights for compliance
- **⚡ Live Fraud Detector** — Real-time prediction with risk indicators & recommendations

## 🛠️ Tech Stack
| Category | Tools |
|----------|-------|
| Language | Python |
| Classical ML | LightGBM, XGBoost (GPU), Random Forest, Logistic Regression |
| Deep Learning | PyTorch (MLP Neural Network — T4 GPU) |
| Explainable AI | SHAP (TreeExplainer) |
| SQL Analytics | DuckDB (Window Functions, CTEs, Aggregations) |
| Statistics | SciPy (Welch T-test, Chi-square test) |
| Class Imbalance | SMOTE (imbalanced-learn) |
| Feature Engineering | Balance discrepancy, zero-balance flags, amount ratios |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit (5 pages) |
| Data Processing | Pandas, NumPy |
| Training Environment | Google Colab (T4 GPU) |

## 📁 Dataset
- **Source:** PaySim — Synthetic Mobile Money Transactions (Kaggle)
- **Size:** 1,146,015 transactions × 11 features
- **Fraud Rate:** 0.058% (extreme class imbalance)
- **Transaction Types:** PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN
- **Engineered Features:** 7 new features (balance discrepancy, zero flags, amount ratio, time features)

## 💡 Key Business Insights
- 🔴 **TRANSFER & CASH_OUT** — only transaction types with fraud (100% of fraud cases)
- 🟡 **Balance discrepancy** features are strongest fraud predictors (#1 SHAP feature)
- 🟢 **Zero balance after transaction** = high fraud risk — fraudsters drain accounts completely
- 🔵 **Amount ratio > 0.8** = fraudster transferring entire account balance
- ⚡ All 5 models exceeded **97% AUC** — engineered features are highly predictive

## 📂 Project Structure
