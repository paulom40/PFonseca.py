import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 🧠 Sample DataFrame (replace with your Excel import)
df = pd.DataFrame({
    'Entidade': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa A'],
    'Data Venc': [datetime.today() + timedelta(days=i*15) for i in range(4)],
    'Valor': [1000, 1500, 2000, 1200]
})

# ✅ Ensure datetime format
df['Data Venc'] = pd.to_datetime(df['Data Venc'], errors='coerce')

# 🎨 Page config
st.set_page_config(page_title="Gestão de Fornecedores", layout="wide")

# 🎨 Custom CSS
st.markdown("""
<style>
    .sidebar .sidebar-content { background-color: #f0f4f8; }
    .stSlider > div { background-color: #e0f7fa; border-radius: 10px; padding: 10px; }
    .stSelectbox > div { border-radius: 10px; }
    .stButton > button { border-radius: 20px; background-color: #0077b6; color: white; }
    .metric-box { background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# 🧭 Sidebar 1: Entidade
with st.sidebar:
    st.header("🔍 Filtrar por Entidade")
    entidade_selected = st.selectbox("Escolha a Entidade", df['Entidade'].unique())

# 🗓️ Sidebar 2: Data Vencimento
with st.sidebar:
    st.header("📅 Intervalo de Vencimento")
    min_date = df['Data Venc'].min().to_pydatetime()
    max_date = df['Data Venc'].max().to_pydatetime()
    date_range = st.slider("Selecione o intervalo de datas",
                           min_value=min_date,
                           max_value=max_date,
                           value=(min_date, max_date),
                           format="DD/MM/YYYY")

# 📆 Dias Range
dias_range = st.slider("📈 Dias até vencimento", 0, 90, (0, 30))

# 🔎 Filter Logic
today = datetime.today()
filtered_df = df[
    (df['Entidade'] == entidade_selected) &
    (df['Data Venc'] >= date_range[0]) &
    (df['Data Venc'] <= date_range[1]) &
    (df['Data Venc'] >= today + timedelta(days=dias_range[0])) &
    (df['Data Venc'] <= today + timedelta(days=dias_range[1]))
]

# 📋 Summary Table
st.markdown("### 🎛️ Filtros Ativos")
summary_df = pd.DataFrame({
    "Filtro": ["Entidade", "Data Inicial", "Data Final", "Dias Mínimos", "Dias Máximos"],
    "Selecionado": [
        entidade_selected,
        date_range[0].strftime("%d/%m/%Y"),
        date_range[1].strftime("%d/%m/%Y"),
        dias_range[0],
        dias_range[1]
    ]
})
st.table(summary_df)

# 📊 Resultados
st.markdown("### 📁 Resultados Filtrados")
st.dataframe(filtered_df.style.highlight_max(axis=0, color='lightgreen'))

# 📈 Métricas
st.markdown("### 📊 Métricas")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total de Registros", value=len(filtered_df))
with col2:
    st.metric(label="Valor Total", value=f"€ {filtered_df['Valor'].sum():,.2f}")
