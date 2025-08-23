import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Sample DataFrame structure
# Replace this with your actual data loading logic
df = pd.DataFrame({
    'Entidade': ['Empresa A', 'Empresa B', 'Empresa C'],
    'Data Venc': [datetime.today() + timedelta(days=i*10) for i in range(3)],
    'Valor': [1000, 1500, 2000]
})

# 🎨 Custom UI Styling
st.set_page_config(page_title="Gestão de Fornecedores", layout="wide")

st.markdown("""
    <style>
    .sidebar .sidebar-content { background-color: #f0f4f8; }
    .stSlider > div { background-color: #e0f7fa; border-radius: 10px; padding: 10px; }
    .stSelectbox > div { border-radius: 10px; }
    .stButton > button { border-radius: 20px; background-color: #0077b6; color: white; }
    </style>
""", unsafe_allow_html=True)

# 🧭 Sidebar 1: Entidade
with st.sidebar:
    st.header("🔍 Filtrar por Entidade")
    entidade_selected = st.selectbox("Escolha a Entidade", df['Entidade'].unique())

# 🗓️ Sidebar 2: Calendar based on Data Venc
with st.sidebar:
    st.header("📅 Filtrar por Data de Vencimento")
    min_date = df['Data Venc'].min()
    max_date = df['Data Venc'].max()
    date_range = st.slider("Selecione o intervalo de datas", min_value=min_date, max_value=max_date,
                           value=(min_date, max_date), format="DD/MM/YYYY")

# 📊 Dias Range
dias_range = st.slider("📈 Filtrar por Dias até Vencimento", 0, 90, (0, 30))

# 🔎 Filter Logic
filtered_df = df[
    (df['Entidade'] == entidade_selected) &
    (df['Data Venc'] >= date_range[0]) &
    (df['Data Venc'] <= date_range[1]) &
    (df['Data Venc'] <= datetime.today() + timedelta(days=dias_range[1])) &
    (df['Data Venc'] >= datetime.today() + timedelta(days=dias_range[0]))
]

# 📋 Display Results
st.title("📁 Resultados Filtrados")
st.dataframe(filtered_df.style.highlight_max(axis=0, color='lightgreen'))

# 🎯 Summary
st.metric(label="Total de Registros", value=len(filtered_df))
st.metric(label="Valor Total", value=f"€ {filtered_df['Valor'].sum():,.2f}")
