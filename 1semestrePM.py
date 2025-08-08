import streamlit as st
import pandas as pd
import io

# 🚀 Page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# 🖼️ Display logo in top-left corner
col_logo, _ = st.columns([1, 5])
with col_logo:
    st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=150)

# 📥 Load data from Excel file hosted on GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/1semestrePM.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data()

# 🎛️ Sidebar filters
st.sidebar.header("🧩 Filtros")

ano_options = sorted(df['ano'].unique())
selected_ano = st.sidebar.multiselect("Ano", ano_options, default=ano_options)

mes_options = sorted(df['mês'].unique())
selected_mes = st.sidebar.multiselect("Mês", mes_options, default=mes_options)

artigo_options = sorted(df['artigo'].unique())
selected_artigo = st.sidebar.multiselect("Artigo", artigo_options, default=artigo_options)

# 🔍 Filter data based on selections
filtered_df = df[
    (df['ano'].isin(selected_ano)) &
    (df['mês'].isin(selected_mes)) &
    (df['artigo'].isin(selected_artigo))
]

# 📊 KPIs section
st.header("📊 KPIs")
col1, col2, col3 = st.columns(3)

avg_pm = filtered_df['pm'].mean() if not filtered_df.empty else 0
avg_quantidade = filtered_df['quantidade'].mean() if not filtered_df.empty else 0
avg_valor_liquido = filtered_df['valor_liquido'].mean() if not filtered_df.empty else 0

with col1:
    st.metric("🧮 Média PM", f"{avg_pm:.2f}")
with col2:
    st.metric("📦 Média Quantidade", f"{avg_quantidade:.2f}")
with col3:
    st.metric("💰 Média Valor Liquido", f"{avg_valor_liquido:.2f}")

# 📋 Display filtered data
st.header("📋 Dados Filtrados")
st.dataframe(filtered_df)

# 📤 Export filtered data to Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    return output.getvalue()

excel_data = to_excel(filtered_df)

st.download_button(
    label="📥 Exportar para Excel",
    data=excel_data,
    file_name="dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
