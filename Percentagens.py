import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

# Hardcoded login credentials (replace with your own or use st.secrets)
USERNAME = "user"
PASSWORD = "pass"

# Function to parse the document string into DataFrame
@st.cache_data
def load_data():
    # The full document string should be pasted here. Since it's truncated in the prompt, placeholders are used.
    # In practice, copy the entire <DOCUMENT> content here.
    document = """## Paste the full document string here from the user message ##
<DOCUMENT filename="Perc2025_Com.xlsx">
<SHEET id="0" name="Sheet1">row1: Cliente,Congelados,Frescos,Leitão,Peixe,Transf,Comercial,Mês,Ano
# ... all rows ...
</SHEET></DOCUMENT>"""
    
    # Extract rows
    row_pattern = re.compile(r'row\d+: (.*)')
    rows = row_pattern.findall(document)
    
    data_list = []
    header = ['Cliente', 'Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf', 'Comercial', 'Mês', 'Ano']
    
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
                'Mês': mes.strip(),
                'Ano': int(ano.strip())
            })
    
    df = pd.DataFrame(data_list)
    
    # Map months to numbers
    month_map = {
        'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
        'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
    }
    df['MonthNum'] = df['Mês'].map(month_map)
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
    
    # Cliente sidebar
    clientes = sorted(df['Cliente'].unique())
    selected_cliente = st.selectbox("Cliente", ['Todos'] + clientes)
    
    # Comercial sidebar
    comerciais = sorted(df['Comercial'].unique())
    selected_comercial = st.selectbox("Comercial", ['Todos'] + comerciais)
    
    # Product choices
    products = ['Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf']
    selected_product = st.selectbox("Categoria", products)
    
    # Timeline sidebar (months)
    months = sorted(df['Mês'].unique())
    selected_month = st.selectbox("Mês", ['Todos'] + months)
    
    # Buttons
    if st.button("Update Data"):
        st.cache_data.clear()
        df = load_data()
        st.success("Data updated!")
    
    if st.button("Clear Cache"):
        st.cache_clear()
        st.success("Cache cleared!")

# Filter data
filtered_df = df.copy()

if selected_cliente != 'Todos':
    filtered_df = filtered_df[filtered_df['Cliente'] == selected_cliente]

if selected_comercial != 'Todos':
    filtered_df = filtered_df[filtered_df['Comercial'] == selected_comercial]

if selected_month != 'Todos':
    filtered_df = filtered_df[filtered_df['Mês'] == selected_month]

# Main content
st.title("Dashboard de Vendas")

# Show filtered table
st.dataframe(filtered_df)

# Chart example: bar chart for selected product
if not filtered_df.empty:
    st.subheader(f"Gráfico de {selected_product}")
    chart_data = filtered_df.groupby('Mês')[selected_product].sum().reset_index()
    st.bar_chart(chart_data.set_index('Mês'))

# Alert for clients not buying >30 days
current_date = datetime(2025, 8, 21)  # As per the prompt

def check_no_buy(client):
    client_df = df[df['Cliente'] == client]
    if client_df.empty:
        return False
    # Assume purchase if sum of products > 0
    client_df = client_df[(client_df['Congelados'] + client_df['Frescos'] + client_df['Leitão'] + client_df['Peixe'] + client_df['Transf']) > 0]
    if client_df.empty:
        return True
    last_purchase = client_df['Date'].max()
    days_since = (current_date - last_purchase).days
    return days_since > 30

if selected_cliente != 'Todos':
    if check_no_buy(selected_cliente):
        st.warning(f"Alerta: O cliente {selected_cliente} não comprou há mais de 30 dias!")
else:
    inactive_clients = [c for c in clientes if check_no_buy(c)]
    if inactive_clients:
        st.warning(f"Clientes inativos (>30 dias): {', '.join(inactive_clients)}")
