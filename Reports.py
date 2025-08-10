import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# Load the Excel data from GitHub
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_excel(io.BytesIO(response.content), sheet_name='Sheet1')
        # Convert Dias to numeric
        df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
        # Filter for overdue (Dias > 10)
        overdue = df[df['Dias'] > 10].copy()
        # Add overdue category
        overdue['Overdue Category'] = pd.cut(overdue['Dias'], bins=[10, 30, 60, 90, float('inf')],
                                           labels=['11-30 days', '31-60 days', '61-90 days', '90+ days'])
        return overdue
    else:
        st.error("Failed to load V0808.xlsx from GitHub. Check the URL or repository access.")
        return pd.DataFrame()

st.title('Overdue Payment Reports')
st.markdown('Interactive reports from V0808.xlsx, filtered for Dias > 10. Grouped by Comercial, Entidade, and Dias.')

df = load_data()

if not df.empty:
    # Sidebar filters
    st.sidebar.header('Filters')
    selected_comercial = st.sidebar.multiselect('Select Comercial', options=sorted(df['Comercial'].unique()),
                                               default=sorted(df['Comercial'].unique()))
    selected_entidade = st.sidebar.multiselect('Select Entidade', options=sorted(df['Entidade'].unique()), default=[])
    min_dias = st.sidebar.slider('Minimum Dias Overdue', min_value=11, max_value=int(df['Dias'].max()), value=11)

    # Apply filters
    filtered_df = df[(df['Dias'] >= min_dias)]
    if selected_comercial:
        filtered_df = filtered_df[filtered_df['Comercial'].isin(selected_comercial)]
    if selected_entidade:
        filtered_df = filtered_df[filtered_df['Entidade'].isin(selected_entidade)]

    # Report Sections
    st.header('Overdue Records Table')
    st.dataframe(filtered_df[['Comercial', 'Entidade', 'Dias', 'Valor Pendente', 'Documento', 'Série', 'N.º Doc.', 'Categoria']],
                 use_container_width=True)

    st.header('Summary by Comercial')
    summary_comercial = filtered_df.groupby('Comercial').agg(
        Total_Pending=('Valor Pendente', 'sum'),
        Avg_Dias=('Dias', 'mean'),
        Count=('Dias', 'count')
    ).reset_index()
    summary_comercial['Total_Pending'] = summary_comercial['Total_Pending'].round(2)
    summary_comercial['Avg_Dias'] = summary_comercial['Avg_Dias'].round(1)
    st.table(summary_comercial)

    st.header('Summary by Entidade')
    summary_entidade = filtered_df.groupby('Entidade').agg(
        Total_Pending=('Valor Pendente', 'sum'),
        Avg_Dias=('Dias', 'mean'),
        Count=('Dias', 'count')
    ).reset_index()
    summary_entidade['Total_Pending'] = summary_entidade['Total_Pending'].round(2)
    summary_entidade['Avg_Dias'] = summary_entidade['Avg_Dias'].round(1)
    st.table(summary_entidade)

    st.header('Overdue Distribution by Dias Category')
    fig, ax = plt.subplots()
    filtered_df['Overdue Category'].value_counts().plot(kind='bar', ax=ax, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    ax.set_xlabel('Overdue Category')
    ax.set_ylabel('Count')
    st.pyplot(fig)

    # Download option
    st.header('Download Filtered Data')
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button('Download CSV', csv, 'overdue_report.csv', 'text/csv')
