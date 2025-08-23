import pandas as pd
import requests
from io import BytesIO
import streamlit as st
from datetime import datetime, timedelta

# Function to convert Excel serial date to datetime
def excel_to_datetime(serial_date):
    return pd.to_datetime(serial_date - 2, unit='d', origin='1899-12-30')

st.set_page_config(layout="wide")

# Custom CSS for modern look with round table
st.markdown("""
<style>
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
    }
    .stSlider .css-1aumxhk {
        background-color: #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# Load Excel file from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Fornecedores_Deb.xlsx"

try:
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")

    # Clean and prepare data
    df.columns = df.columns.str.strip()
    df["Entidade (Nome)"] = df["Entidade (Nome)"].astype(str).str.strip()
    df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
    df = df.dropna(subset=["Dias"])
    df["Dias"] = df["Dias"].astype(int)
    df["Valor Pendente"] = pd.to_numeric(df["Valor Pendente"], errors="coerce")
    
    # Convert Data Venc. to datetime
    df["Data Venc."] = df["Data Venc."].apply(excel_to_datetime)
    
    st.success("Dados carregados com sucesso!")

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Sidebar for filters
st.sidebar.header("🔎 Filtros")

# Entidade filter
entidades_unicas = sorted(df["Entidade (Nome)"].dropna().unique())
selected_entidades = st.sidebar.multiselect("Selecione Entidades:", entidades_unicas, default=entidades_unicas)

# Data Venc. calendar mode (date range picker)
st.sidebar.header("📅 Filtro Data Venc.")
min_date = df["Data Venc."].min().date()
max_date = df["Data Venc."].max().date()
start_date, end_date = st.sidebar.date_input("Selecione intervalo de Data Venc.:", [min_date, max_date])

# Dias range slider
st.sidebar.header("⏳ Filtro por Dias")
dias_min_default = int(df["Dias"].min())
dias_max_default = int(df["Dias"].max())
dias_min, dias_max = st.sidebar.slider(
    "Selecione o intervalo de Dias:",
    min_value=dias_min_default,
    max_value=dias_max_default,
    value=(dias_min_default, dias_max_default),
    step=1
)

# Filter the dataframe
df_filtrado = df[
    df["Entidade (Nome)"].isin(selected_entidades) &
    (df["Data Venc."].dt.date >= start_date) &
    (df["Data Venc."].dt.date <= end_date) &
    (df["Dias"] >= dias_min) &
    (df["Dias"] <= dias_max)
]

# Colorful highlighting based on Dias
def color_dias(val):
    if val > 30:
        color = 'red'
    elif val > 0:
        color = 'orange'
    else:
        color = 'green'
    return f'background-color: {color}; color: white;'

# Display results
st.title("📊 Fornecedores Deb")
st.markdown(f"""
Exibindo resultados para:
- **Entidades:** {', '.join(selected_entidades) if selected_entidades else 'Nenhuma'}
- **Data Venc.:** {start_date} – {end_date}
- **Dias:** {dias_min} – {dias_max}
""")

# Styled dataframe
st.dataframe(
    df_filtrado.style
    .applymap(color_dias, subset=["Dias"])
    .format({"Valor Pendente": "{:.2f}", "Data Venc.": "{:%d/%m/%Y}", "Data Doc.": "{:.0f}"}),
    use_container_width=True
)

# Summary metrics
total_registros = len(df_filtrado)
media_dias = df_filtrado["Dias"].mean() if total_registros > 0 else 0
valor_total = df_filtrado["Valor Pendente"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📌 Total de Registros", total_registros)
col2.metric("📆 Dias Médios", f"{media_dias:.1f}")
col3.metric("💰 Valor Pendente Total", f"€ {valor_total:,.2f}")
