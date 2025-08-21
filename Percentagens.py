import streamlit as st
import pandas as pd
import re

# Hardcoded login credentials (replace with your own or use st.secrets)
USERNAME = "admin"
PASSWORD = "12345"

# Function to parse the document string into DataFrame
def parse_document_string(document):
    row_pattern = re.compile(r'row\d+: (.*)')
    rows = row_pattern.findall(document)
    
    data_list = []
    header = ['Cliente', 'Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf', 'Comercial', 'Mes', 'Ano']
    
    for row_str in rows[1:]:  # Skip header row1
        parts = row_str.split(',')
        client_parts = []
        for i, part in enumerate(parts):
            part = part.strip()
            try:
                float(part)
                num_start = i
                break
            except ValueError:
                client_parts.append(part)
        client = ','.join(client_parts).strip()
        remaining = parts[num_start:]
        if len(remaining) == 8:
            congelados, frescos, leitao, peixe, transf, comercial, mes, ano = remaining
            data_list.append({
                'Cliente': client,
                'Congelados': float(congelados),
                'Frescos': float(frescos),
                'Leitão': float(leitao),
                'Peixe': float(peixe),
                'Transf': float(transf),
                'Comercial': comercial.strip(),
                'Mes': mes.strip(),
                'Ano': int(ano.strip())
            })
    
    df = pd.DataFrame(data_list)
    
    # Map months to numbers
    month_map = {
        'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
        'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
    }
    df['MonthNum'] = df['Mes'].map(month_map)
    df['Date'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['MonthNum'].astype(str) + '-01')
    
    return df

# Function to load data (from secrets or uploaded file)
def load_data():
    try:
        # Try loading from st.secrets
        document = st.secrets["document"]
        return parse_document_string(document)
    except KeyError:
        # Fallback to file upload
        st.warning("No 'document' key found in st.secrets. Please upload the Excel file 'Perc2025_Com.xlsx'.")
        uploaded_file = st.file_uploader("Upload Perc2025_Com.xlsx", type=["xlsx"])
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                # Ensure expected columns
                expected_columns = ['Cliente', 'Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf', 'Comercial', 'Mes', 'Ano']
                if not all(col in df.columns for col in expected_columns):
                    st.error(f"Uploaded file must contain columns: {', '.join(expected_columns)}")
                    return pd.DataFrame()
                # Map months to numbers
                month_map = {
                    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
                    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
                }
                df['MonthNum'] = df['Mes'].map(month_map)
                df['Date'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['MonthNum'].astype(str) + '-01')
                return df
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

# Login system
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Incorrect username or password")

if not st.session_state.logged_in:
    st.stop()

# Load data
df = load_data()

if df.empty:
    st.error("No data loaded. Please configure st.secrets['document'] or upload the Excel file.")
    st.stop()

# Sidebars
with st.sidebar:
    st.header("Filtros")
    
    # Cliente multiselect
    clientes = sorted(df['Cliente'].unique())
    selected_clientes = st.multiselect("Cliente", clientes, default=[])
    
    # Comercial multiselect
    comerciais = sorted(df['Comercial'].unique())
    selected_comerciais = st.multiselect("Comercial", comerciais, default=[])
    
    # Product multiselect
    products = ['Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf']
    selected_products = st.multiselect("Categoria", products, default=products)
    
    # Timeline sidebar (months)
    months = sorted(df['Mes'].unique())
    selected_month = st.selectbox("Mes", ['Todos'] + months)
    
    # Buttons
    if st.button("Update Data"):
        df = load_data()
        st.success("Data updated!")
    
    if st.button("Clear Cache"):
        st.cache_clear()
        st.success("Cache cleared!")

# Filter data
filtered_df = df.copy()

if selected_clientes:
    filtered_df = filtered_df[filtered_df['Cliente'].isin(selected_clientes)]

if selected_comerciais:
    filtered_df = filtered_df[filtered_df['Comercial'].isin(selected_comerciais)]

if selected_month != 'Todos':
    filtered_df = filtered_df[filtered_df['Mes'] == selected_month]

# Main content
st.title("Dashboard de Vendas")

# Show filtered table
st.subheader("Dados Filtrados")
st.dataframe(filtered_df)

# Summary table for selected products
if not filtered_df.empty and selected_products:
    st.subheader("Resumo das Categorias Selecionadas")
    summary_data = filtered_df.groupby('Mes')[selected_products].sum().reset_index()
    st.dataframe(summary_data)
