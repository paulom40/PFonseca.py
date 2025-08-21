import streamlit as st
import pandas as pd

# --- USER AUTHENTICATION ---
def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    # Replace with your own credentials
    valid_users = {
        "paulojt": "braga2025",
        "admin": "12345"
    }

    if login_btn:
        if username in valid_users and password == valid_users[username]:
            st.session_state["authenticated"] = True
            st.success(f"✅ Welcome, {username}!")
        else:
            st.error("❌ Invalid username or password")

# --- INITIALIZE SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN GATE ---
if not st.session_state["authenticated"]:
    login()
    st.stop()

# --- LOAD DATA ---
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("📊 Perc2025 Commercial Dashboard")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")
cliente = st.sidebar.multiselect("Cliente", options=df["Cliente"].dropna().unique())
comercial = st.sidebar.multiselect("Comercial", options=df["Comercial"].dropna().unique())
mes = st.sidebar.multiselect("Mes", options=df["Mes"].dropna().unique())

update = st.sidebar.button("🔄 Update")
refresh = st.sidebar.button("♻️ Refresh")

# --- FILTER FUNCTION ---
def filter_data():
    filtered = df.copy()
    if cliente:
        filtered = filtered[filtered["Cliente"].isin(cliente)]
    if comercial:
        filtered = filtered[filtered["Comercial"].isin(comercial)]
    if mes:
        filtered = filtered[filtered["Mes"].isin(mes)]
    return filtered

if update:
    filtered_df = filter_data()
elif refresh:
    cliente = comercial = mes = []
    filtered_df = df.copy()
else:
    filtered_df = df.copy()

# --- FORMAT NUMERIC COLUMNS ---
numeric_cols = ["Congelados", "Frescos", "Leitão", "Peixe", "Transf"]
for col in numeric_cols:
    if col in filtered_df.columns:
        filtered_df[col] = filtered_df[col].map(lambda x: f"{x:.2%}")

# --- DISPLAY TABLE ---
st.subheader("📈 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

# --- ALERT FOR MISSING MONTHS ---
if cliente:
    all_months = set(df["Mes"].dropna().unique())
    missing_clients = []
    for c in cliente:
        client_months = set(df[df["Cliente"] == c]["Mes"].dropna().unique())
        if client_months != all_months:
            missing_clients.append(c)
    if missing_clients:
        st.warning(f"⚠️ These clients did not buy in every month: {', '.join(missing_clients)}")
