import streamlit as st
import pandas as pd
import re

# Hardcoded login credentials (replace with your own or use st.secrets)
USERNAME = "admin"
PASSWORD = "12345"

# Function to parse the document string into DataFrame
def load_data():
    # Extract rows
    row_pattern = re.compile(r'row\d+: (.*)')
    rows = row_pattern.findall(st.secrets["document"])
    
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
