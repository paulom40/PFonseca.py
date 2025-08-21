import streamlit as st
import pandas as pd
import io

# -------------------------------
# 🔐 Login na Sidebar
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
st.title("📂 Filtro por Mês e Ano + Totais Médios")

# 📥 Carregar ficheiro Excel do GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
try:
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('\n', '', regex=True)
    df.columns = df.columns.str.replace('\r', '', regex=True)
    df.columns = df.columns.str.replace('\t', '', regex=True)
except Exception as e:
    st.error("❌ Erro ao carregar o ficheiro.")
    st.stop()

# ✅ Verificar colunas obrigatórias
required_cols = {"Mes", "Ano"}
actual_cols = set(df.columns)
missing = required_cols - actual_cols

if missing:
    st.error(f"❌ O ficheiro precisa conter as colunas: {missing}")
    st.stop()

# 📋 Mostrar colunas disponíveis
st.sidebar.subheader("📋 Colunas disponíveis")
st.sidebar.write(df.columns.tolist())

# 📅 Filtros
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

# 📊 Calcular médias por Mês
categoria_cols = [col for col in df.columns if col not in ["Cliente", "Mes", "Ano"]]
media_por_mes = (
    filtered_df.groupby("Mes")[categoria_cols]
    .mean()
    .round(2)
    .sort_index()
)

st.subheader("📊 Médias por Mês (%)")
st.dataframe(media_por_mes)

# 📈 Gráfico de barras
st.bar_chart(media_por_mes)

# 📤 Exportar médias para Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    media_por_mes.to_excel(writer, sheet_name='MediasPorMes')
processed_data = output.getvalue()

st.download_button(
    label="📥 Download das médias por Mês (.xlsx)",
    data=processed_data,
    file_name="medias_por_mes.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
