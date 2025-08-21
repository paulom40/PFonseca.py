import streamlit as st
import pandas as pd

# Hardcoded login credentials (replace with your own or use environment variables)
USERNAME = "admin"
PASSWORD = "12345"

# Function to load data from URL
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
    try:
        df = pd.read_excel(url)
        # Ensure expected columns
        expected_columns = ['Cliente', 'Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf', 'Comercial', 'Mes', 'Ano']
        if not all(col in df.columns for col in expected_columns):
            st.error(f"Excel file must contain columns: {', '.join(expected_columns)}")
            return pd.DataFrame()
        # Convert numeric columns to percentages
        for col in ['Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf']:
            df[col] = df[col] * 100  # Convert decimal to percentage
        # Map months to numbers
        month_map = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
            'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }
        df['MonthNum'] = df['Mes'].map(month_map)
        df['Date'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['MonthNum'].astype(str) + '-01')
        return df
    except Exception as e:
        st.error(f"Error loading Excel file from URL: {e}")
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
    st.error("No data loaded. Please check the Excel file URL or try again later.")
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

# Format percentages for display
display_df = filtered_df.copy()
for col in ['Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf']:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")

# Main content
st.title("Dashboard de Vendas")

# Show filtered table
st.subheader("Dados Filtrados")
st.dataframe(display_df)

# Summary table for selected products
if not filtered_df.empty and selected_products:
    st.subheader("Resumo das Categorias Selecionadas")
    summary_data = filtered_df.groupby('Mes')[selected_products].sum().reset_index()
    # Format summary table percentages
    display_summary = summary_data.copy()
    for col in selected_products:
        display_summary[col] = display_summary[col].apply(lambda x: f"{x:.2f}%")
    st.dataframe(display_summary)
