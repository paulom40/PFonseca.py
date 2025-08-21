import streamlit as st
import pandas as pd
import io

# -------------------------------
# 🔐 Sistema de Login na Sidebar
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
            st.sidebar.success("✅ Login bem-sucedido!")
        else:
            st.sidebar.error("❌ Credenciais inválidas")
    st.stop()

# -------------------------------
# 📊 Aplicação Principal
# -------------------------------
st.title("📂 Filtro por Mês e Ano + Exportação")

# 📥 Carregar ficheiro Excel do GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
try:
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error("❌ Erro ao carregar o ficheiro. Verifica o link ou o formato.")
    st.stop()

# 📋 Mostrar colunas disponíveis
st.sidebar.subheader("📋 Colunas disponíveis")
st.sidebar.write(df.columns.tolist())

# ✅ Verificar colunas obrigatórias
if "Mes" in df.columns and "Ano" in df.columns:
    # 📅 Filtros na barra lateral
    selected_mes = st.sidebar.multiselect("📅 Selecione o(s) Mês(es)", sorted(df["Mes"].dropna().unique()))
    selected_ano = st.sidebar.multiselect("📆 Selecione o(s) Ano(s)", sorted(df["Ano"].dropna().unique()))

    # 🔍 Aplicar filtros
    filtered_df = df.copy()
    if selected_mes:
        filtered_df = filtered_df[filtered_df["Mes"].isin(selected_mes)]
    if selected_ano:
        filtered_df = filtered_df[filtered_df["Ano"].isin(selected_ano)]

    # 📄 Mostrar dados filtrados
    st.subheader("📄 Dados Filtrados")
    st.dataframe(filtered_df, use_container_width=True)

    # 📤 Exportar dados filtrados para Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='DadosFiltrados')
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Download dos dados filtrados (.xlsx)",
        data=processed_data,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.error("❌ As colunas 'Mes' e 'Ano' são obrigatórias no ficheiro.")
