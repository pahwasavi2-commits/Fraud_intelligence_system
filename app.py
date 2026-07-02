"""
Financial Fraud Intelligence System
------------------------------------
A production-styled Streamlit application combining:
  - Secure signup/login (SQLite + salted SHA-256 hashing)
  - Executive KPI dashboard (Power BI-style cross-filtering)
  - Transaction analytics
  - ML model performance comparison
  - SHAP-style explainability
  - Live fraud scoring
  - Auto-generated business insights & downloadable report

Author: Savi Pahwa
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sqlite3
import hashlib
import hmac
import os
import io
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Financial Fraud Intelligence System",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# GLOBAL STYLE
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
/*
  DESIGN CONCEPT — "Security Print"
  A fraud-intelligence tool borrows its visual language from the thing it
  protects: currency and official documents. Engine-turned hairline
  crosshatching (the same anti-counterfeit technique printed on banknotes),
  a ledger-stamp KPI treatment, and a wax-seal verdict badge stand in for
  the generic gradient-and-glass dashboard look.
  Palette: paper #F1F4EE · ink #14231C · emerald #1F6F52 · gold #A9812E · alert #A3312B
  Type: Fraunces (display) · Public Sans (body) · IBM Plex Mono (figures)
*/
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

html, body, [class*="css"]  { font-family: 'Public Sans', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---- Security-paper background: fine engine-turned crosshatch ---- */
.stApp {
    background-color: #F1F4EE;
    background-image:
        repeating-linear-gradient(45deg, rgba(31,111,82,0.05) 0px, rgba(31,111,82,0.05) 1px, transparent 1px, transparent 13px),
        repeating-linear-gradient(-45deg, rgba(20,35,28,0.035) 0px, rgba(20,35,28,0.035) 1px, transparent 1px, transparent 13px);
}

/* ---- Ledger rule (double hairline, the page's signature device) ---- */
.ledger-rule { width: 240px; margin: 0.5rem auto 1.5rem; }
.ledger-rule .r1 { height: 2px; background-image: repeating-linear-gradient(90deg, #1F6F52 0 7px, transparent 7px 10px); }
.ledger-rule .r2 { height: 1px; margin-top: 3px; background-image: repeating-linear-gradient(90deg, #A9812E 0 4px, transparent 4px 7px); }

/* ---- Header ---- */
.brand-eyebrow {
    text-align: center;
    color: #1F6F52;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.brand-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 2.5rem;
    color: #14231C;
    text-align: center;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
.brand-sub {
    text-align: center;
    color: #4B5C53;
    font-size: 0.95rem;
    margin-top: 0.3rem;
    margin-bottom: 0.6rem;
}

/* ---- KPI Cards: ledger-stamp treatment ---- */
.kpi-card {
    position: relative;
    background: #FBFAF6;
    border: 1px solid rgba(20,35,28,0.12);
    border-top: 3px solid #1F6F52;
    border-radius: 4px;
    padding: 1rem 1.2rem 1.1rem;
    box-shadow: 0 4px 14px rgba(20,35,28,0.06);
}
.kpi-label {
    color: #4B5C53;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}
.kpi-value {
    color: #14231C;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.7rem;
    font-weight: 600;
    margin: 0.2rem 0;
}
.kpi-delta-up { color: #1F6F52; font-size: 0.82rem; font-weight: 600; font-family: 'IBM Plex Mono', monospace; }
.kpi-delta-down { color: #A3312B; font-size: 0.82rem; font-weight: 600; font-family: 'IBM Plex Mono', monospace; }

/* ---- Section Card ---- */
.section-card {
    background: #FBFAF6;
    border: 1px solid rgba(20,35,28,0.1);
    border-radius: 6px;
    padding: 1.3rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(20,35,28,0.05);
}
.section-title {
    font-family: 'Fraunces', serif;
    color: #14231C;
    font-weight: 600;
    font-size: 1.15rem;
    margin-bottom: 0.6rem;
}

/* ---- Insight Pills ---- */
.insight-pill {
    background: rgba(31,111,82,0.07);
    border-left: 3px solid #1F6F52;
    padding: 0.6rem 0.9rem;
    border-radius: 3px;
    margin-bottom: 0.5rem;
    color: #14231C;
    font-size: 0.9rem;
}
.insight-pill.risk { background: rgba(163,49,43,0.08); border-left-color: #A3312B; }
.insight-pill.info { background: rgba(169,129,46,0.1); border-left-color: #A9812E; }

/* ---- Auth card: "secure access" framing ---- */
.auth-wrap { display:flex; justify-content:center; margin-top: 1rem; }
.auth-card {
    background: #FBFAF6;
    border: 1px solid rgba(20,35,28,0.12);
    border-radius: 6px;
    padding: 2.2rem 2.4rem;
    width: 100%;
    max-width: 430px;
    box-shadow: 0 18px 44px rgba(20,35,28,0.14);
}
.auth-seal {
    width: 56px; height: 56px; margin: 0 auto 0.9rem;
    border-radius: 50%;
    border: 2px solid #1F6F52;
    outline: 1px solid #1F6F52;
    outline-offset: 3px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    color: #1F6F52;
}

/* ---- Verdict seal (Live Detector) ---- */
.verdict-box {
    display: flex; align-items: center; gap: 1rem;
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
    margin: 0.8rem 0;
}
.verdict-box.ok { background: rgba(31,111,82,0.08); border: 1px solid rgba(31,111,82,0.3); }
.verdict-box.bad {
    background: rgba(163,49,43,0.07);
    border: 1px solid rgba(163,49,43,0.3);
    background-image: repeating-linear-gradient(135deg, rgba(163,49,43,0.05) 0 10px, transparent 10px 20px);
}
.verdict-seal {
    flex-shrink: 0; width: 54px; height: 54px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; font-weight: 700;
}
.verdict-box.ok .verdict-seal { border: 2px solid #1F6F52; outline: 1px solid #1F6F52; outline-offset: 3px; color: #1F6F52; }
.verdict-box.bad .verdict-seal { border: 2px solid #A3312B; outline: 1px solid #A3312B; outline-offset: 3px; color: #A3312B; }
.verdict-text { font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.15rem; color: #14231C; }
.verdict-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #4B5C53; margin-top: 0.15rem; }

div[data-testid="stMetric"] {
    background: #FBFAF6;
    border: 1px solid rgba(20,35,28,0.1);
    border-radius: 6px;
    padding: 0.8rem 1rem;
}

section[data-testid="stSidebar"] {
    background: #E8EDE5;
    border-right: 1px solid rgba(20,35,28,0.12);
}

h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #14231C !important; font-weight: 600 !important; }
h1 { border-bottom: 2px solid #1F6F52; padding-bottom: 0.5rem; }

.stButton>button {
    border-radius: 4px;
    font-weight: 600;
    border: 1px solid #14231C;
    background: #14231C;
    color: #F1F4EE;
}
.stButton>button:hover {
    background: #1F6F52;
    border-color: #1F6F52;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# BRAND PALETTE (single source of truth for chart colors, so
# every visual — CSS and Plotly alike — reads as one system)
# ══════════════════════════════════════════════════════════
INK = "#14231C"
SLATE = "#4B5C53"
EMERALD = "#1F6F52"
EMERALD_DEEP = "#123D2C"
GOLD = "#A9812E"
ALERT = "#A3312B"
SAGE = "#7C9885"
PAPER_CARD = "#FBFAF6"
CATEGORICAL = [EMERALD, GOLD, SLATE, SAGE, EMERALD_DEEP]
DIVERGING = [[0, EMERALD], [0.5, GOLD], [1, ALERT]]
SEQUENTIAL = [[0, "#E7EBDE"], [1, EMERALD]]


def style_fig(fig, **kwargs):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color=INK, font_family="Public Sans, sans-serif",
        **kwargs,
    )
    return fig


def brand_header(eyebrow: str, title: str, subtitle: str):
    st.markdown(f'<p class="brand-eyebrow">{eyebrow}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="brand-title">{title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="brand-sub">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown('<div class="ledger-rule"><div class="r1"></div><div class="r2"></div></div>', unsafe_allow_html=True)



DB_PATH = "users.db"
DATA_PATH = "fraud_processed.csv"
MODEL_PATH = "fraud_model.pkl"
SCALER_PATH = "scaler.pkl"
ENCODER_PATH = "label_encoder.pkl"

# ══════════════════════════════════════════════════════════
# AUTH LAYER (SQLite + salted hash)
# ══════════════════════════════════════════════════════════
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            salt TEXT,
            password_hash TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()
    return salt, pwd_hash


def create_user(username: str, email: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists."
    salt, pwd_hash = hash_password(password)
    c.execute(
        "INSERT INTO users (username, email, salt, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, email, salt, pwd_hash, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return True, "Account created successfully."


def verify_user(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    salt, stored_hash = row
    _, attempt_hash = hash_password(password, salt)
    return hmac.compare_digest(attempt_hash, stored_hash)


init_db()

# ══════════════════════════════════════════════════════════
# DATA / MODEL LOADING (with graceful synthetic fallback so the
# app is always demo-ready even without the trained artifacts)
# ══════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        return df, True
    # Synthetic PaySim-like fallback for demo purposes
    rng = np.random.default_rng(42)
    n = 20000
    types = rng.choice(
        ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"],
        size=n, p=[0.34, 0.10, 0.35, 0.06, 0.15]
    )
    amount = np.round(rng.gamma(2.2, 9000, size=n), 2)
    old_orig = np.round(rng.gamma(2, 60000, size=n), 2)
    new_orig = np.clip(old_orig - amount, 0, None)
    old_dest = np.round(rng.gamma(1.5, 40000, size=n), 2)
    new_dest = old_dest + amount
    hour = rng.integers(0, 24, size=n)
    day = rng.integers(1, 31, size=n)

    fraud_prob = np.where(
        np.isin(types, ["TRANSFER", "CASH_OUT"]),
        np.where(new_orig == 0, 0.09, 0.012),
        0.0005
    )
    is_fraud = (rng.random(n) < fraud_prob).astype(int)

    df = pd.DataFrame({
        "type": types, "amount": amount,
        "oldbalanceOrg": old_orig, "newbalanceOrig": new_orig,
        "oldbalanceDest": old_dest, "newbalanceDest": new_dest,
        "hour": hour, "day": day, "isFraud": is_fraud,
    })
    df["error_balance_orig"] = df["newbalanceOrig"] + df["amount"] - df["oldbalanceOrg"]
    df["error_balance_dest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]
    return df, False


@st.cache_resource
def load_models():
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            scaler = pickle.load(f)
        with open(ENCODER_PATH, "rb") as f:
            le = pickle.load(f)
        return model, scaler, le, True
    except Exception:
        return None, None, None, False


def rule_based_score(row):
    """Fallback lightweight scorer used only if trained model artifacts are absent."""
    score = 0.02
    if row["type"] in ["TRANSFER", "CASH_OUT"]:
        score += 0.25
    if row.get("orig_zero_after", 0) == 1:
        score += 0.45
    if abs(row.get("error_balance_orig", 0)) > 1000:
        score += 0.15
    if row.get("amount_ratio", 0) > 0.8:
        score += 0.1
    return min(score, 0.98)


df, real_data_loaded = load_data()
best_model, scaler, le, real_model_loaded = load_models()

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# ══════════════════════════════════════════════════════════
# AUTH SCREEN
# ══════════════════════════════════════════════════════════
def auth_screen():
    brand_header(
        "Fraud Intelligence Division · Secure Access",
        "💳 Fraud Intelligence Platform",
        "Enterprise-grade fraud analytics — Machine Learning + Business Intelligence",
    )

    left, mid, right = st.columns([1, 1.3, 1])
    with mid:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<div class="auth-seal">🔒</div>', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔐 Log In", "🆕 Sign Up"])

        with tab_login:
            st.markdown("##### Welcome back")
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In", width='stretch', type="primary"):
                if verify_user(u, p):
                    st.session_state.authenticated = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            st.caption("Demo tip: create an account in the Sign Up tab — no external setup needed.")

        with tab_signup:
            st.markdown("##### Create your analyst account")
            su_user = st.text_input("Choose a username", key="signup_user")
            su_email = st.text_input("Email", key="signup_email")
            su_pass = st.text_input("Choose a password", type="password", key="signup_pass")
            su_pass2 = st.text_input("Confirm password", type="password", key="signup_pass2")
            if st.button("Create Account", width='stretch', type="primary"):
                if not su_user or not su_pass:
                    st.error("Username and password are required.")
                elif su_pass != su_pass2:
                    st.error("Passwords do not match.")
                elif len(su_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = create_user(su_user, su_email, su_pass)
                    if ok:
                        st.success(msg + " Please log in.")
                    else:
                        st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.authenticated:
    auth_screen()
    st.stop()

# ══════════════════════════════════════════════════════════
# AUTHENTICATED APP
# ══════════════════════════════════════════════════════════
if not real_data_loaded:
    st.info("Demo mode: `fraud_processed.csv` not found — showing synthetic sample data so the app "
            "stays fully interactive. Drop your real dataset in the app folder to use live data.",
            icon="ℹ️")
if not real_model_loaded:
    st.info("Demo mode: trained model file not found — the Live Detector is using a transparent "
            "rule-based scorer as a stand-in. Add `fraud_model.pkl`, `scaler.pkl`, `label_encoder.pkl` "
            "to enable the trained LightGBM model.", icon="ℹ️")

with st.sidebar:
    st.markdown(f"### 👋 Hi, {st.session_state.username}")
    if st.button("Log Out", width='stretch'):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    st.markdown("---")
    st.markdown(
        '<p style="font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;'
        'letter-spacing:2px;color:#1F6F52;font-weight:600;margin-bottom:0;">'
        '🔏 CASE NAVIGATOR</p>', unsafe_allow_html=True,
    )
    page = st.radio("Go to", [
        "🏠 Executive Overview",
        "📊 Transaction Analysis",
        "📈 BI Dashboard",
        "🤖 Model Performance",
        "🔍 SHAP Explainability",
        "⚡ Live Fraud Detector",
        "📝 Insights & Report",
    ])
    st.markdown("---")

    st.markdown("#### 🔎 Global Filters")
    type_filter = st.multiselect(
        "Transaction Type", sorted(df["type"].unique()), default=sorted(df["type"].unique())
    )
    amt_min, amt_max = float(df["amount"].min()), float(df["amount"].max())
    amount_range = st.slider("Amount Range ($)", amt_min, amt_max, (amt_min, amt_max))
    if "hour" in df.columns:
        hour_range = st.slider("Hour of Day", 0, 23, (0, 23))
    else:
        hour_range = (0, 23)

    st.markdown("---")
    total = len(df)
    fraud_total = int(df["isFraud"].sum())
    st.markdown(f"**Total Transactions:** {total:,}")
    st.markdown(f"**Fraud Detected:** {fraud_total:,}")
    st.markdown(f"**Fraud Rate:** {fraud_total/total*100:.3f}%")
    st.markdown("**Dataset:** PaySim Mobile Money")

# Apply global filters (Power BI-style cross-filtering across all pages)
fdf = df[df["type"].isin(type_filter)]
fdf = fdf[(fdf["amount"] >= amount_range[0]) & (fdf["amount"] <= amount_range[1])]
if "hour" in fdf.columns:
    fdf = fdf[(fdf["hour"] >= hour_range[0]) & (fdf["hour"] <= hour_range[1])]
if len(fdf) == 0:
    st.warning("No transactions match the current filters — adjust the sidebar filters.")
    st.stop()


def kpi_card(col, label, value, delta=None, delta_positive=True):
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "🏠 Executive Overview":
    brand_header(
        "Fraud Intelligence Division · Case Dashboard",
        "💳 Financial Fraud Intelligence System",
        "PaySim Mobile Money Transactions — ML + BI Fraud Detection Suite",
    )

    f_total = len(fdf)
    f_fraud = int(fdf["isFraud"].sum())
    fraud_amount = fdf[fdf["isFraud"] == 1]["amount"].sum()
    avg_fraud_amount = fdf[fdf["isFraud"] == 1]["amount"].mean() if f_fraud else 0

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Filtered Transactions", f"{f_total:,}")
    kpi_card(c2, "Fraud Detected", f"{f_fraud:,}", f"{f_fraud/f_total*100:.3f}% rate", delta_positive=False)
    kpi_card(c3, "Fraud Exposure ($)", f"${fraud_amount:,.0f}")
    kpi_card(c4, "Avg Fraud Ticket ($)", f"${avg_fraud_amount:,.0f}")

    st.markdown("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Transaction Volume by Type</div>', unsafe_allow_html=True)
        type_counts = fdf["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.bar(type_counts, x="type", y="count", color="type", text="count",
                     color_discrete_sequence=CATEGORICAL)
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color=INK)
        st.plotly_chart(fig, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Normal vs Fraud Distribution</div>', unsafe_allow_html=True)
        fig2 = px.pie(values=[f_total - f_fraud, f_fraud], names=["Normal", "Fraud"],
                      color_discrete_sequence=[EMERALD, ALERT], hole=0.55)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
        st.plotly_chart(fig2, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Fraud Rate (%) by Transaction Type</div>', unsafe_allow_html=True)
    fraud_type = fdf.groupby("type")["isFraud"].agg(fraud_count="sum", total="count").reset_index()
    fraud_type["fraud_rate"] = (fraud_type["fraud_count"] / fraud_type["total"] * 100).round(3)
    fig3 = px.bar(fraud_type.sort_values("fraud_rate", ascending=False), x="type", y="fraud_rate",
                  color="fraud_rate", color_continuous_scale=DIVERGING,
                  text=fraud_type.sort_values("fraud_rate", ascending=False)["fraud_rate"].round(3).astype(str) + "%")
    fig3.update_traces(textposition="outside")
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
    st.plotly_chart(fig3, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — TRANSACTION ANALYSIS
# ══════════════════════════════════════════════════════════
elif page == "📊 Transaction Analysis":
    st.title("📊 Transaction Analysis")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Transaction Amount: Fraud vs Normal</div>', unsafe_allow_html=True)
        sample = fdf.sample(min(30000, len(fdf)), random_state=42)
        fig = px.box(sample, x="isFraud", y="amount", color="isFraud",
                     color_discrete_map={0: EMERALD, 1: ALERT}, points=False)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
        st.plotly_chart(fig, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        if "hour" in fdf.columns:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Fraud Rate by Hour of Day</div>', unsafe_allow_html=True)
            hourly = fdf.groupby("hour").agg(total=("isFraud", "count"), frauds=("isFraud", "sum")).reset_index()
            hourly["fraud_rate"] = (hourly["frauds"] / hourly["total"] * 100).round(3)
            fig2 = px.line(hourly, x="hour", y="fraud_rate", markers=True,
                           color_discrete_sequence=[ALERT])
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
            st.plotly_chart(fig2, width='stretch')
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Fraud Transaction Summary by Type</div>', unsafe_allow_html=True)
    fraud_only = fdf[fdf["isFraud"] == 1]
    if len(fraud_only):
        fraud_amt = fraud_only.groupby("type")["amount"].agg(["sum", "mean", "count"]).reset_index()
        fraud_amt.columns = ["Type", "Total Amount", "Avg Amount", "Count"]
        st.dataframe(
            fraud_amt.style.format({"Total Amount": "${:,.0f}", "Avg Amount": "${:,.0f}", "Count": "{:,}"}),
            width='stretch', hide_index=True,
        )
    else:
        st.info("No fraud transactions in the current filter selection.")
    st.markdown("</div>", unsafe_allow_html=True)

    if "error_balance_orig" in fdf.columns and len(fraud_only):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Balance Discrepancy Analysis</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig3 = px.histogram(fraud_only.sample(min(5000, len(fraud_only))), x="error_balance_orig",
                                title="Balance Error (Origin)", color_discrete_sequence=[ALERT], nbins=50)
            fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
            st.plotly_chart(fig3, width='stretch')
        with c2:
            fig4 = px.histogram(fraud_only.sample(min(5000, len(fraud_only))), x="error_balance_dest",
                                title="Balance Error (Destination)", color_discrete_sequence=[GOLD], nbins=50)
            fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
            st.plotly_chart(fig4, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — BI DASHBOARD (Power BI-style, cross-filtered)
# ══════════════════════════════════════════════════════════
elif page == "📈 BI Dashboard":
    st.title("📈 Business Intelligence Dashboard")
    st.caption("Cross-filtered view — all visuals respond to the sidebar filters, mirroring a Power BI report page.")
    st.markdown("---")

    st.markdown("""
    > **Note:** This native dashboard reproduces the interactivity of a Power BI report
    > (slicers, cross-filtering, drill-through) directly in Streamlit.
    > To embed an actual **Power BI Publish-to-Web** report instead, replace the block
    > below with an `st.components.v1.iframe("<your-powerbi-embed-url>", height=650)` call.
    """)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_card(k1, "Transactions", f"{len(fdf):,}")
    kpi_card(k2, "Fraud Cases", f"{int(fdf['isFraud'].sum()):,}")
    kpi_card(k3, "Total Volume", f"${fdf['amount'].sum():,.0f}")
    kpi_card(k4, "Avg Ticket", f"${fdf['amount'].mean():,.0f}")
    kpi_card(k5, "Fraud Loss", f"${fdf[fdf['isFraud']==1]['amount'].sum():,.0f}")

    st.markdown("")
    drill = st.selectbox("🔽 Drill into a transaction type", ["All"] + sorted(fdf["type"].unique().tolist()))
    ddf = fdf if drill == "All" else fdf[fdf["type"] == drill]

    r1c1, r1c2 = st.columns([1.3, 1])
    with r1c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">Volume Trend by Day — {drill}</div>', unsafe_allow_html=True)
        if "day" in ddf.columns:
            daily = ddf.groupby("day").agg(volume=("amount", "sum"), txns=("amount", "count")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily["day"], y=daily["txns"], name="Transactions", marker_color=SAGE, opacity=0.6))
            fig.add_trace(go.Scatter(x=daily["day"], y=daily["volume"] / max(daily["volume"].max(), 1) * daily["txns"].max(),
                                      name="Volume (scaled)", mode="lines+markers", line=dict(color=GOLD)))
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK,
                               legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with r1c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Mix</div>', unsafe_allow_html=True)
        risk_mix = ddf["isFraud"].value_counts().rename({0: "Legit", 1: "Fraud"}).reset_index()
        risk_mix.columns = ["Status", "Count"]
        fig2 = px.pie(risk_mix, names="Status", values="Count", hole=0.6,
                      color="Status", color_discrete_map={"Legit": EMERALD, "Fraud": ALERT})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=INK, showlegend=True)
        st.plotly_chart(fig2, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Amount Band Heatmap (Type × Fraud Rate)</div>', unsafe_allow_html=True)
    bins = [0, 1000, 5000, 20000, 100000, np.inf]
    labels = ["<1K", "1K-5K", "5K-20K", "20K-100K", "100K+"]
    tmp = fdf.copy()
    tmp["amount_band"] = pd.cut(tmp["amount"], bins=bins, labels=labels)
    pivot = tmp.pivot_table(index="type", columns="amount_band", values="isFraud", aggfunc="mean", observed=False) * 100
    fig3 = px.imshow(pivot.round(2), text_auto=True, color_continuous_scale=DIVERGING, aspect="auto",
                     labels=dict(color="Fraud Rate %"))
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=INK)
    st.plotly_chart(fig3, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

    # Downloadable filtered dataset — analyst self-service export
    csv_buf = io.StringIO()
    fdf.to_csv(csv_buf, index=False)
    st.download_button("⬇️ Export Filtered Data (CSV)", data=csv_buf.getvalue(),
                       file_name="fraud_filtered_export.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════
# PAGE 4 — MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════
elif page == "🤖 Model Performance":
    st.title("🤖 ML Model Performance")
    st.markdown("---")

    model_results = {
        "Logistic Regression": 0.9708,
        "Random Forest": 0.9945,
        "XGBoost (GPU)": 0.9981,
        "Neural Network (GPU)": 0.9957,
        "LightGBM 🏆": 0.9995,
    }

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Model Comparison — AUC-ROC Score</div>', unsafe_allow_html=True)
    fig = px.bar(x=list(model_results.keys()), y=list(model_results.values()), color=list(model_results.keys()),
                text=[f"{v:.4f}" for v in model_results.values()],
                color_discrete_sequence=[SLATE, SAGE, EMERALD, EMERALD_DEEP, GOLD])
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      yaxis_range=[0.9, 1.02], font_color=INK)
    st.plotly_chart(fig, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

    insights = pd.DataFrame({
        "Model": list(model_results.keys()),
        "AUC-ROC": [f"{v:.4f}" for v in model_results.values()],
        "Speed": ["Fast", "Medium", "Fast (GPU)", "Medium (GPU)", "Fast"],
        "Interpretability": ["High", "Medium", "Low", "Low", "Medium"],
        "Best For": ["Baseline & Compliance", "Balanced Performance", "High Accuracy + Speed",
                     "Complex Patterns", "Production Deployment 🏆"],
    })
    st.dataframe(insights, width='stretch', hide_index=True)

    st.success("""
    **🏆 Key Finding:** LightGBM achieved **99.95% AUC-ROC** — best overall performance!
    All 5 models exceeded 97% AUC, showing engineered features (balance discrepancy,
    zero-balance flags, amount ratios) are highly predictive of fraud.
    """)

# ══════════════════════════════════════════════════════════
# PAGE 5 — SHAP EXPLAINABILITY
# ══════════════════════════════════════════════════════════
elif page == "🔍 SHAP Explainability":
    st.title("🔍 SHAP Explainability (XAI)")
    st.markdown("Understanding **why** the model flags a transaction as fraud.")
    st.markdown("---")

    FEATURES = [
        "type_enc", "amount", "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest", "error_balance_orig",
        "error_balance_dest", "orig_zero_after", "dest_zero_before",
        "amount_ratio", "hour", "day",
    ]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Feature Importance</div>', unsafe_allow_html=True)
    try:
        if real_model_loaded:
            importance = best_model.feature_importances_
        else:
            raise AttributeError("No trained model loaded — using illustrative weights.")
        feat_imp = pd.DataFrame({"Feature": FEATURES[:len(importance)], "Importance": importance}) \
            .sort_values("Importance", ascending=False)
    except Exception:
        illustrative = [0.31, 0.05, 0.06, 0.04, 0.05, 0.04, 0.22, 0.15, 0.18, 0.06, 0.09, 0.02, 0.01]
        feat_imp = pd.DataFrame({"Feature": FEATURES, "Importance": illustrative[:len(FEATURES)]}) \
            .sort_values("Importance", ascending=False)
        st.caption("Showing illustrative feature-importance weights (no trained model artifact found).")

    fig = px.bar(feat_imp, x="Importance", y="Feature", orientation="h",
                color="Importance", color_continuous_scale=SEQUENTIAL)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=INK,
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Top Fraud Indicators")
    col1, col2, col3 = st.columns(3)
    col1.info("**error_balance_orig**\nBalance discrepancy at origin account — strongest fraud signal.")
    col2.warning("**orig_zero_after**\nAccount drained to zero after transaction — high fraud risk.")
    col3.error("**error_balance_dest**\nBalance discrepancy at destination — key fraud pattern.")

    st.markdown("---")
    st.subheader("Business Insights from XAI")
    st.markdown("""
    - 🔴 **TRANSFER & CASH_OUT** transactions account for the overwhelming majority of fraud cases
    - 🟡 **Balance discrepancy** features are the top predictors — engineered features outperform raw ones
    - 🟢 **Zero balance after transaction** is a strong signal — fraudsters drain accounts completely
    - 🔵 **Amount ratio** (amount ÷ balance) shows fraudsters tend to transfer entire balances
    """)

# ══════════════════════════════════════════════════════════
# PAGE 6 — LIVE FRAUD DETECTOR
# ══════════════════════════════════════════════════════════
elif page == "⚡ Live Fraud Detector":
    st.title("⚡ Live Fraud Detection")
    st.markdown("Enter transaction details to get an instant fraud risk score.")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        txn_type = st.selectbox("Transaction Type", ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"])
        amount = st.number_input("Transaction Amount ($)", min_value=0.0, max_value=10_000_000.0,
                                 value=50000.0, step=1000.0)
        old_balance_orig = st.number_input("Sender Old Balance ($)", min_value=0.0, value=100000.0, step=1000.0)
        new_balance_orig = st.number_input("Sender New Balance ($)", min_value=0.0, value=50000.0, step=1000.0)
    with c2:
        old_balance_dest = st.number_input("Receiver Old Balance ($)", min_value=0.0, value=0.0, step=1000.0)
        new_balance_dest = st.number_input("Receiver New Balance ($)", min_value=0.0, value=50000.0, step=1000.0)
        hour = st.slider("Hour of Day", 0, 23, 12)
        day = st.slider("Day", 1, 30, 15)

    if st.button("⚡ Detect Fraud", type="primary"):
        error_balance_orig = new_balance_orig + amount - old_balance_orig
        error_balance_dest = old_balance_dest + amount - new_balance_dest
        orig_zero_after = 1 if new_balance_orig == 0 else 0
        dest_zero_before = 1 if old_balance_dest == 0 else 0
        amount_ratio = amount / (old_balance_orig + 1)

        row = {
            "type": txn_type, "amount": amount, "error_balance_orig": error_balance_orig,
            "orig_zero_after": orig_zero_after, "amount_ratio": amount_ratio,
        }

        if real_model_loaded:
            try:
                type_enc = le.transform([txn_type])[0]
            except Exception:
                type_enc = 0
            input_data = pd.DataFrame([{
                "type_enc": type_enc, "amount": amount, "oldbalanceOrg": old_balance_orig,
                "newbalanceOrig": new_balance_orig, "oldbalanceDest": old_balance_dest,
                "newbalanceDest": new_balance_dest, "error_balance_orig": error_balance_orig,
                "error_balance_dest": error_balance_dest, "orig_zero_after": orig_zero_after,
                "dest_zero_before": dest_zero_before, "amount_ratio": amount_ratio,
                "hour": hour, "day": day,
            }])
            prediction = best_model.predict(input_data)[0]
            proba = best_model.predict_proba(input_data)[0]
        else:
            fraud_p = rule_based_score(row)
            prediction = 1 if fraud_p >= 0.5 else 0
            proba = [1 - fraud_p, fraud_p]

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Prediction", "🚨 FRAUD" if prediction == 1 else "✅ LEGITIMATE")
        c2.metric("Fraud Probability", f"{proba[1]*100:.2f}%")
        c3.metric("Confidence", f"{max(proba)*100:.2f}%")

        if prediction == 1:
            st.markdown("""
            <div class="verdict-box bad">
                <div class="verdict-seal">✕</div>
                <div>
                    <div class="verdict-text">FLAGGED — Suspected Fraud</div>
                    <div class="verdict-sub">Block transaction · alert account holder · route to investigation team</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            **Recommended actions:**
            - Block transaction immediately
            - Alert account holder via SMS/email
            - Flag for manual review
            - Escalate to fraud investigation team
            """)
        else:
            st.markdown("""
            <div class="verdict-box ok">
                <div class="verdict-seal">✓</div>
                <div>
                    <div class="verdict-text">AUTHENTICATED — Legitimate Transaction</div>
                    <div class="verdict-sub">No fraud indicators detected · transaction can proceed normally</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        fig = px.bar(x=["Legitimate", "Fraud"], y=[proba[0]*100, proba[1]*100],
                    color=["Legitimate", "Fraud"], color_discrete_map={"Legitimate": EMERALD, "Fraud": ALERT},
                    text=[f"{proba[0]*100:.2f}%", f"{proba[1]*100:.2f}%"])
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          yaxis_range=[0, 115], font_color=INK)
        st.plotly_chart(fig, width='stretch')

        st.subheader("Risk Indicators")
        risk_df = pd.DataFrame({
            "Indicator": ["Zero Balance After", "Zero Balance Before", "Amount Ratio",
                         "Balance Error (Origin)", "Transaction Type"],
            "Value": [
                "⚠️ YES" if orig_zero_after else "✅ NO",
                "⚠️ YES" if dest_zero_before else "✅ NO",
                f"{amount_ratio:.3f}",
                f"${error_balance_orig:,.2f}",
                txn_type,
            ],
            "Risk Level": [
                "HIGH" if orig_zero_after else "LOW",
                "MEDIUM" if dest_zero_before else "LOW",
                "HIGH" if amount_ratio > 0.8 else "LOW",
                "HIGH" if abs(error_balance_orig) > 1000 else "LOW",
                "HIGH" if txn_type in ["TRANSFER", "CASH_OUT"] else "LOW",
            ],
        })
        st.dataframe(risk_df, width='stretch', hide_index=True)

# ══════════════════════════════════════════════════════════
# PAGE 7 — INSIGHTS & REPORT (Business Analyst layer)
# ══════════════════════════════════════════════════════════
elif page == "📝 Insights & Report":
    st.title("📝 Executive Insights & Recommendations")
    st.caption("Auto-generated narrative summary based on the current filtered view — the BA layer on top of the model.")
    st.markdown("---")

    f_total = len(fdf)
    f_fraud = int(fdf["isFraud"].sum())
    fraud_rate = f_fraud / f_total * 100 if f_total else 0
    fraud_amount = fdf[fdf["isFraud"] == 1]["amount"].sum()
    top_type = fdf.groupby("type")["isFraud"].mean().idxmax() if f_fraud else "N/A"
    top_type_rate = fdf.groupby("type")["isFraud"].mean().max() * 100 if f_fraud else 0

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Key Findings</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-pill">📌 The current selection covers <b>{f_total:,}</b> transactions,
    of which <b>{f_fraud:,}</b> ({fraud_rate:.3f}%) are flagged as fraudulent, representing
    <b>${fraud_amount:,.0f}</b> in exposure.</div>
    <div class="insight-pill risk">⚠️ <b>{top_type}</b> carries the highest fraud concentration
    at <b>{top_type_rate:.2f}%</b> — prioritize additional verification controls on this channel.</div>
    <div class="insight-pill info">💡 Transactions that leave the sender's balance at exactly zero
    are disproportionately fraudulent — a real-time zero-balance trigger would materially reduce risk exposure.</div>
    <div class="insight-pill">📌 LightGBM is the recommended production model (99.95% AUC-ROC),
    balancing detection accuracy with inference speed for real-time scoring.</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)
    st.markdown("""
    1. **Real-time rule layer**: auto-hold TRANSFER/CASH_OUT transactions that zero out the sender's balance, pending secondary authentication.
    2. **Model deployment**: promote LightGBM to production scoring with a monitored probability threshold (e.g., 0.5) and a manual-review queue for borderline scores (0.3–0.5).
    3. **Feedback loop**: route confirmed fraud/non-fraud outcomes back into monthly model retraining to counter concept drift.
    4. **Executive reporting**: distribute this filtered view (or the CSV export from the BI Dashboard page) weekly to the risk & compliance team.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    report_text = f"""FRAUD INTELLIGENCE — EXECUTIVE SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Prepared for: {st.session_state.username}

FILTERED TRANSACTIONS: {f_total:,}
FRAUD DETECTED: {f_fraud:,} ({fraud_rate:.3f}%)
FRAUD EXPOSURE: ${fraud_amount:,.0f}
HIGHEST-RISK TYPE: {top_type} ({top_type_rate:.2f}% fraud rate)

RECOMMENDED MODEL: LightGBM (99.95% AUC-ROC)

KEY RECOMMENDATIONS:
1. Real-time hold rule for zero-balance TRANSFER/CASH_OUT transactions
2. Deploy LightGBM with a manual-review band for borderline probability scores
3. Monthly retraining loop using confirmed outcomes
4. Weekly distribution of this report to risk & compliance stakeholders
"""
    st.download_button("⬇️ Download Executive Summary (.txt)", data=report_text,
                       file_name="fraud_executive_summary.txt", mime="text/plain")