import pandas as pd
import requests
from io import BytesIO
import streamlit as st
from datetime import datetime, timedelta
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to convert Excel serial date to datetime
def excel_to_datetime(serial_date):
    try:
        return pd.to_datetime(serial_date - 2, unit='d', origin='1899-12-30')
    except Exception as e:
        logger.error(f"Error converting serial date {serial_date}: {e}")
        return None

# Set page config at the very start
st.set_page_config(layout="wide")

# Custom CSS for modern look with rounded table
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

# Display a loading message
st.write("Inicializando o aplicativo...")

# Load Excel file from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Fornecedores_Deb.xlsx"

try:
    logger.debug("Attempting to fetch Excel file from GitHub")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    logger.debug("Excel file fetched successfully")
    
    # Read Excel file
    df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")
    logger.debug("Excel file read into DataFrame")
    
    # Clean and prepare data
    df.columns = df.columns.str.strip()
    logger.debug(f"Columns found: {df.columns.tolist()}")
    
    # Check if required columns exist
    required_columns = ["Entidade (Nome)", "Data Venc.", "Dias", "Valor Pendente"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Colunas ausentes no arquivo Excel: {missing_columns}")
        st.stop()
    
    df["Entidade (Nome)"] = df["Entidade (Nome)"].astype(str).str.strip()
    df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
    df = df.dropna(subset=["Dias", "Data Venc."])
    df["Dias"] = df["Dias"].astype(int)
    df["Valor Pendente"] = pd.to_numeric(df["Valor Pendente"], errors="coerce")
    
    # Convert Data Venc. to datetime
    df["Data Venc."] = df["Data Venc."].apply(excel_to_datetime)
    if df["Data Venc."].isnull().any():
        st.warning("Algumas datas em 'Data Venc.' não puderam ser convertidas e foram ignoradas.")
        df = df.dropna(subset=["Data Venc."])
    
    st.success("Dados carregados com sucesso!")
    logger.debug("Data processing completed")

except requests.exceptions.RequestException as e:
    st.error(f"Erro ao carregar os dados: Falha na conexão com {url}. Detalhes: {e}")
    logger.error(f"Request error: {e}")
    st.stop()
except pd.errors.ParserError as e:
    st.error(f"Erro ao carregar os dados: Problema ao ler o arquivo Excel. Detalhes: {e}")
    logger.error(f"Parser error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Erro ao carregar os dados: Entidade. Detalhes: {e}")
    logger.error(f"General error: {e}")
    st.stop()

# Sidebar for filters
st.sidebar.header("🔎 Filtros")

# Entidade filter
entidades_unicas = sorted(df["Entidade (Nome)"].dropna().unique())
selected_entidades = st.sidebar.multiselect(
    "Selecione Entidades:", 
    entidades_unicas, 
    default=entidades_unicas[:5]  # Limit default to first 5 to avoid performance issues
)

# Data Venc. calendar mode (date range picker)
st.sidebar.header("📅 Filtro Data Venc.")
min_date = df["Data Venc."].min().date() if not df["Data Venc."].empty else datetime.today().date()
max_date = df["Data Venc."].max().date() if not df["Data Venc."].empty else datetime.today().date()
start_date, end_date = st.sidebar.date_input(
    "Selecione intervalo de Data Venc.:", 
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Dias range slider
st.sidebar.header("⏳ Filtro por Dias")
dias_min_default = int(df["Dias"].min()) if not df["Dias"].empty else 0
dias_max_default = int(df["Dias"].max()) if not df["Dias"].empty else 100
dias_min, dias_max = st.sidebar.slider(
    "Selecione o intervalo de Dias:",
    min_value=dias_min_default,
    max_value=dias_max_default,
    value=(dias_min_default, dias_max_default),
    step=1
)

# Filter the dataframe
df_filtrado = df[
    (df["Entidade (Nome)"].isin(selected_entidades)) &
    (df["Data Venc."].dt.date >= start_date) &
    (df["Data Venc."].dt.date <= end_date) &
    (df["Dias"] >= dias_min) &
    (df["Dias"] <= dias_max)
]

# Colorful highlighting based on Dias
def color_dias(val):
    try:
        if val > 30:
            color = 'red'
        elif val > 0:
            color = 'orange'
        else:
            color = 'green'
        return f'background-color: {color}; color: white;'
    except:
        return ''

# Display results
st.title("📊 Fornecedores Deb")
st.markdown(f"""
Exibindo resultados para:
- **Entidades:** {', '.join(selected_entidades) if selected_entidades else 'Nenhuma'}
- **Data Venc.:** {start_date} – {end_date}
- **Dias:** {dias_min} – {dias_max}
""")

# Styled dataframe
try:
    st.dataframe(
        df_filtrado.style
