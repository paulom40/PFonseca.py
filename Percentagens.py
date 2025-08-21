import streamlit as st
import pandas as pd
import io

# -------------------------------
# 🔐 Sidebar Login System
# -------------------------------
users = {
    "paulojt": "1234",
    "admin": "adminpass"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.sidebar.success("✅ Login successful!")
        else:
            st.sidebar.error("❌ Invalid credentials")
    st.stop()

# -------------------------------
# 📊 Main App
# -------------------------------
st.title("📂 Filtro e Exportação de Dados")

# Load Excel file from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
try:
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error("❌ Erro ao carregar o ficheiro do GitHub.")
    st.stop()

# Show available columns
st.sidebar.subheader("📋 Colunas disponíveis")
st.sidebar.write(df.columns.tolist())

# Check for required columns
if "Mes" in df.columns and "Ano" in df.columns:
    # Sidebar filters
    selected_mes = st.sidebar.multiselect("📅 Selecione o Mês", options=df["Mes"].dropna().unique())
    selected_ano = st.sidebar.multiselect("📆 Selecione o Ano", options=df["Ano"].dropna().unique())

    # Filter data
    filtered_df = df.copy()
    if selected_mes:
        filtered_df = filtered_df[filtered_df["Mes"].isin(selected_mes)]
    if selected_ano:
        filtered_df = filtered_df[filtered_df["Ano"].isin(selected_ano)]

    # Show filtered data
    st.subheader("📄 Dados Filtrados")
    st.dataframe(filtered_df, use_container_width=True)

    # Export filtered data to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Download dos dados filtrados em Excel",
        data=processed_data,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.error("❌ As colunas 'Mes' e 'Ano' são obrigatórias no ficheiro.")
