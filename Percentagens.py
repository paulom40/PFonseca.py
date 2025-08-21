import streamlit as st
import pandas as pd

# Load data from GitHub
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()  # Clean column names
    return df

df = load_data()

st.title("📊 Perc2025 Commercial Dashboard")

# Show available columns for debugging
st.expander("📋 Show Available Columns").write(df.columns.tolist())

# Helper to check column existence
def safe_multiselect(label, col_name):
    if col_name in df.columns:
        return st.sidebar.multiselect(label, options=df[col_name].dropna().unique())
    else:
        st.sidebar.warning(f"⚠️ Column '{col_name}' not found.")
        return []

# Sidebar filters
st.sidebar.header("🔍 Filters")
cliente = safe_multiselect("Cliente", "Cliente")
comercial = safe_multiselect("Comercial", "Comercial")
categoria = safe_multiselect("Categoria", "Categoria")
mes = safe_multiselect("Mes", "Mes")

update = st.sidebar.button("🔄 Update")
refresh = st.sidebar.button("♻️ Refresh")

# Apply filters
def filter_data():
    filtered = df.copy()
    if cliente:
        filtered = filtered[filtered["Cliente"].isin(cliente)]
    if comercial:
        filtered = filtered[filtered["Comercial"].isin(comercial)]
    if categoria:
        filtered = filtered[filtered["Categoria"].isin(categoria)]
    if mes:
        filtered = filtered[filtered["Mes"].isin(mes)]
    return filtered

if update:
    filtered_df = filter_data()
elif refresh:
    cliente = comercial = categoria = mes = []
    filtered_df = df.copy()
else:
    filtered_df = df.copy()

# Format numeric columns as percentages
numeric_cols = filtered_df.select_dtypes(include="number").columns
filtered_df[numeric_cols] = filtered_df[numeric_cols].applymap(lambda x: f"{x:.2%}")

# Display filtered table
st.subheader("📈 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

# Alert for clients missing purchases in any month
if "Cliente" in df.columns and "Mes" in df.columns and cliente:
    all_months = set(df["Mes"].dropna().unique())
    missing_clients = []
    for c in cliente:
        client_months = set(df[df["Cliente"] == c]["Mes"].dropna().unique())
        if client_months != all_months:
            missing_clients.append(c)
    if missing_clients:
        st.warning(f"⚠️ These clients did not buy in every month: {', '.join(missing_clients)}")
