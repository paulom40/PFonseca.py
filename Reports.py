import streamlit as st
import pandas as pd
import requests
import io
from io import BytesIO
import uuid
import altair as alt
from datetime import datetime

# ------------------ 🔐 LOGIN SYSTEM ------------------
USER_CREDENTIALS = {
    "admin": "1234",
    "paulo": "teste"
}

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["authenticated"] = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ------------------ 📊 MAIN APP ------------------
st.set_page_config(page_title="Bracar Reports", layout="wide")

@st.cache_data
def load_data(_cache_buster):
    url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name='Sheet1')
        df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce').fillna(0)
        df['Overdue Category'] = pd.cut(
            df['Dias'],
            bins=[-float('inf'), 10, 30, 60, 90, float('inf')],
            labels=['<=10 days', '11-30 days', '31-60 days', '61-90 days', '90+ days'],
            include_lowest=True
        )
        for col in ['Data Venc.', 'Data Doc.', 'Data Receb.']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    except requests.RequestException as e:
        st.error(f"❌ Failed to load V0808.xlsx from GitHub: {str(e)}")
        return pd.DataFrame()

st.markdown("<h1 style='color:#4B8BBE;'>📊 Relatório Recebimentos </h1>", unsafe_allow_html=True)
st.markdown(f"**Atualizado em {datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🔄 Update Data"):
    st.cache_data.clear()
    st.session_state["cache_buster"] = str(uuid.uuid4())

if "cache_buster" not in st.session_state:
    st.session_state["cache_buster"] = str(uuid.uuid4())

df = load_data(st.session_state["cache_buster"])

if df.empty:
    st.warning("⚠️ No data available. Please check the data source or try updating the data.")
    st.stop()

# Sidebar Filters
st.sidebar.markdown("### 🎛️ Filters")
st.sidebar.markdown("---")

selected_comercial = st.sidebar.multiselect(
    '🧑‍💼 Select Comercial',
    options=sorted(df['Comercial'].dropna().unique()),
    default=sorted(df['Comercial'].dropna().unique())
)

selected_entidade = st.sidebar.multiselect(
    '🏢 Select Entidade',
    options=sorted(df['Entidade'].dropna().unique()),
    default=[]
)

max_dias = int(df['Dias'].max()) if not df['Dias'].isna().all() else 0
dias_range = st.sidebar.slider(
    '📅 Select Off Days Range',
    min_value=0,
    max_value=max_dias,
    value=(0, max_dias),
    step=1
)
min_dias, max_dias = dias_range

available_date_columns = [col for col in ['Data Venc.', 'Data Doc.', 'Data Receb.'] if col in df.columns]
if not available_date_columns:
    st.error("❌ No valid date columns found in the data.")
    st.stop()

date_column = st.sidebar.selectbox(
    "🗂️ Choose date column to filter",
    options=available_date_columns
)

min_date = df[date_column].min()
max_date = df[date_column].max()

if pd.isna(min_date) or pd.isna(max_date):
    st.error(f"❌ Invalid dates in {date_column}. Please check the data.")
    st.stop()

selected_date_range = st.sidebar.date_input(
    f"📆 Select {date_column} range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle single date or tuple from date_input
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
else:
    start_date = end_date = selected_date_range if isinstance(selected_date_range, datetime) else min_date

# Filter Data
filtered_df = df[
    (df['Dias'].notna()) &
    (df['Dias'] >= min_dias) & (df['Dias'] <= max_dias) &
    (df[date_column].notna()) &
    (df[date_column] >= pd.to_datetime(start_date)) & 
    (df[date_column] <= pd.to_datetime(end_date))
]

if selected_comercial:
    filtered_df = filtered_df[filtered_df['Comercial'].isin(selected_comercial)]

if selected_entidade:
    filtered_df = filtered_df[filtered_df['Entidade'].isin(selected_entidade)]

if filtered_df.empty:
    st.warning("⚠️ No data matches the selected filters.")
else:
    filtered_df_display = filtered_df.copy()
    filtered_df_display['Dias'] = filtered_df_display['Dias'].round(0).astype(int)
    filtered_df_display['Valor Pendente'] = filtered_df_display['Valor Pendente'].apply(lambda x: f"€{x:,.2f}")

    st.markdown(f"<h4 style='color:#4B8BBE;'>📅 Análise desde os dias <b>{min_dias}</b> a <b>{max_dias}</b></h4>", unsafe_allow_html=True)
    st.markdown(
        f"<h5 style='color:#4B8BBE;'>📆 Registos com <b>{date_column}</b> entre <b>{start_date.strftime('%d-%m-%Y')}</b> e <b>{end_date.strftime('%d-%m-%Y')}</b></h5>",
        unsafe_allow_html=True
    )

    st.markdown("### 📋 Tabela de dados:")
    st.dataframe(
        filtered_df_display[['Comercial', 'Entidade', 'Data Venc.', 'Dias', 'Valor Pendente', 'Documento', 'N.º Doc.', 'Overdue Category']],
        use_container_width=True
    )

    st.markdown("### 🧮 Relatório por Comercial")
    summary_comercial = filtered_df.groupby('Comercial').agg(
        Total_Pending=('Valor Pendente', 'sum'),
        Avg_Dias=('Dias', 'mean'),
        Count=('Dias', 'count')
    ).reset_index()
    summary_comercial['Total_Pending'] = summary_comercial['Total_Pending'].round(2)
    summary_comercial['Avg_Dias'] = summary_comercial['Avg_Dias'].round(0).astype(int)
    summary_comercial_display = summary_comercial.copy()
    summary_comercial_display['Total_Pending'] = summary_comercial_display['Total_Pending'].apply(lambda x: f"€{x:,.2f}")
    st.table(summary_comercial_display)

    st.markdown("### 🧾 Relatório por Entidade")
    summary_entidade = filtered_df.groupby('Entidade').agg(
        Total_Pending=('Valor Pendente', 'sum'),
        Max_Dias=('Dias', 'max'),
        Count=('Dias', 'count')
    ).reset_index()
    summary_entidade['Total_Pending'] = summary_entidade['Total_Pending'].round(2)
    summary_entidade['Max_Dias'] = summary_entidade['Max_Dias'].round(0).astype(int)
    summary_entidade_display = summary_entidade.copy()
    summary_entidade_display['Total_Pending'] = summary_entidade_display['Total_Pending'].apply(lambda x: f"€{x:,.2f}")
    st.table(summary_entidade_display)

    # 🕒 Entidades with last Data Doc > 30 and > 90 days
    today = pd.Timestamp.today()
    entidade_last_doc = (
        df.groupby('Entidade')['Data Doc.']
        .max()
        .reset_index()
        .rename(columns={'Data Doc.': 'Last Data Doc'})
    )
    entidade_last_doc['Days Since Last Doc'] = (today - entidade_last_doc['Last Data Doc']).dt.days

    entidade_doc_30 = entidade_last_doc[entidade_last_doc['Days Since Last Doc'] > 30].copy()
    entidade_doc_30.sort_values(by='Days Since Last Doc', ascending=False, inplace=True)

    entidade_doc_90 = entidade_last_doc[entidade_last_doc['Days Since Last Doc'] > 90].copy()
    entidade_doc_90.sort_values(by='Days Since Last Doc', ascending=False, inplace=True)

    st.markdown("### ⏳ Entidades com último documento há mais de 30 dias")
    if not entidade_doc_30.empty:
        st.dataframe(entidade_doc_30, use_container_width=True)
        st.markdown("### 📊 Dias desde último documento por Entidade (>30 dias)")
        chart_30 = alt.Chart(entidade_doc_30).mark_bar().encode(
            x=alt.X('Entidade', sort='-y'),
            y='Days Since Last Doc',
            tooltip=['Entidade', 'Days Since Last Doc']
        ).properties(width=800, height=400)
        st.altair_chart(chart_30, use_container_width=True)
    else:
        st.info("ℹ️ No entities with last document older than 30 days.")

    st.markdown("### 🔴 Entidades com último documento há mais de 90 dias")
    if not entidade_doc_90.empty:
        st.dataframe(entidade_doc_90, use_container_width=True)
        st.markdown("### 📊 Dias desde último documento por Entidade (>90 dias)")
        chart_90 = alt.Chart(entidade_doc_90).mark_bar().encode(
            x=alt.X('Entidade', sort='-y'),
            y='Days Since Last Doc',
            tooltip=['Entidade', 'Days Since Last Doc']
        ).properties(width=800, height=400)
        st.altair_chart(chart_90, use_container_width=True)
    else:
        st.info("ℹ️ No entities with last document older than 90 days.")

    # ------------------ 📥 EXPORT TO EXCEL ------------------
    st.markdown("### 📤 Exportar dados filtrados para Excel")

    def to_excel_bytes(df1, df2, df3):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df1.to_excel(writer, sheet_name='Dados Filtrados', index=False)
            df2.to_excel(writer, sheet_name='Resumo Comercial', index=False)
            df3.to_excel(writer, sheet_name='Resumo Entidade', index=False)

            if 'Dias' in df1.columns:
                workbook = writer.book
                format_red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                worksheet = writer.sheets['Dados Filtrados']
                col_idx = df1.columns.get_loc('Dias') + 1  # +1 for Excel column indexing
                worksheet.conditional_format(f'{chr(65 + col_idx)}2:{chr(65 + col_idx)}1000', {
                    'type': 'cell',
                    'criteria': '>',
                    'value': 90,
                    'format': format_red
                })

        output.seek(0)
        return output

    excel_data = to_excel_bytes(filtered_df, summary_comercial, summary_entidade)
    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="Relatorio_Recebimentos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
