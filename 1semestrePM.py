import streamlit as st
import pandas as pd

# Load data from GitHub
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
    df = pd.read_excel(url)
    return df

df = load_data()

st.title("📊 Perc2025 Commercial Dashboard")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    cliente = st.multiselect("Cliente", options=df["Cliente"].unique())
    comercial = st.multiselect("Comercial", options=df["Comercial"].unique())
    categoria = st.multiselect("Categoria", options=df["Categoria"].unique())
    mes = st.multiselect("Mes", options=df["Mes"].unique())
    
    update = st.button("🔄 Update")
    refresh = st.button("♻️ Refresh")

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

# Convert numeric columns to percentage format
numeric_cols = filtered_df.select_dtypes(include="number").columns
filtered_df[numeric_cols] = filtered_df[numeric_cols].applymap(lambda x: f"{x:.2%}")

# Display filtered table
st.subheader("📈 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

# Alert for clients missing purchases in any month
if cliente:
    missing_clients = []
    for c in cliente:
        client_data = df[df["Cliente"] == c]
        all_months = set(df["Mes"].unique())
        client_months = set(client_data["Mes"].unique())
        if client_months != all_months:
            missing_clients.append(c)
    if missing_clients:
        st.warning(f"⚠️ These clients did not buy in every month: {', '.join(missing_clients)}")
