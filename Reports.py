import streamlit as st
import pandas as pd
import requests
import io
from io import BytesIO

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
        else:
            st.error("❌ Invalid username or password")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ------------------ 📊 MAIN APP ------------------
st.set_page_config(page_title="Overdue Payment Reports", layout="wide")

@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_excel(io.BytesIO(response.content), sheet_name='Sheet1')
        df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
        df['Overdue Category'] = pd.cut(
            df['Dias'],
            bins=[10, 30, 60, 90, float('inf')],
            labels=['11-30 days', '31-60 days', '61-90 days', '90+ days']
        )
        for col in ['Data Venc.', 'Data Doc.', 'Data Receb.']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    else:
        st.error("❌ Failed to load V0808.xlsx from GitHub. Check the URL or repository access.")
        return pd.DataFrame()

st.markdown("<h1 style='color:#4B8BBE;'>📊 Relatório Recebimentos </h1>", unsafe_allow_html=True)
st.markdown('**Atualizado em 10/08/2025**')

df = load_data()

if not df.empty:
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

    dias_range = st.sidebar.slider(
        '📅 Select Off Days Range',
        min_value=0,
        max_value=int(df['Dias'].max()),
        value=(0, int(df['Dias'].max())),
        step=1
    )
    min_dias, max_dias = dias_range

    available_date_columns = [col for col in ['Data Venc.', 'Data Doc.', 'Data Receb.'] if col in df.columns]
    date_column = st.sidebar.selectbox(
        "🗂️ Choose date column to filter",
        options=available_date_columns
    )

    min_date = df[date_column].min()
    max_date = df[date_column].max()

    selected_date_range = st.sidebar.date_input(
        f"📆 Select {date_column} range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    start_date, end_date = selected_date_range

    filtered_df = df[
        (df['Dias'] >= min_dias) & (df['Dias'] <= max_dias) &
        (df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))
    ]

    if selected_comercial:
        filtered_df = filtered_df[filtered_df['Comercial'].isin(selected_comercial)]

    if selected_entidade:
        filtered_df = filtered_df[filtered_df['Entidade'].isin(selected_entidade)]

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
        filtered_df_display[['Comercial', 'Entidade', 'Data Venc.', 'Dias', 'Valor Pendente', 'Documento', 'N.º Doc.', 'Categoria']],
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

    st.markdown("### 📥 Download Filtered Data")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtered Records')
        summary_comercial.to_excel(writer, index=False, sheet_name='Summary by Comercial')
        summary_entidade.to_excel(writer, index=False, sheet_name='Summary by Entidade')

        workbook = writer.book
        currency_format = workbook.add_format({'num_format': '€#,##0.00'})
        integer_format = workbook.add_format({'num_format': '0'})

        worksheet1 = writer.sheets['Filtered Records']
        dias_index1 = filtered_df.columns.get_loc('Dias')
        valor_index1 = filtered_df.columns.get_loc('Valor Pendente')
        worksheet1.set_column(dias_index1, dias_index1, 10, integer_format)
        worksheet1.set_column(valor_index1, valor_index1, 15, currency_format)

        worksheet2 = writer.sheets['Summary by Comercial']
        valor_index2 = summary_comercial.columns.get_loc('Total_Pending')
        avg_dias_index2 = summary_comercial.columns.get_loc('Avg_Dias')
        worksheet2.set_column(valor_index2, valor_index2, 15, currency_format)
        worksheet2.set_column(avg_dias_index2, avg_dias_index2, 10, integer_format)

        worksheet3 = writer.sheets['Summary by Entidade']
        valor_index3 = summary_entidade.columns.get_loc('Total_Pending')
        Max_dias_index3 = summary_entidade.columns.get_loc('Max_Dias')
        worksheet3.set_column(valor_index3, valor_index3, 15, currency_format)
        worksheet3.set_column(Max_dias_index3, Max_dias_index3, 10, integer_format)

    output.seek(0)
    st.download_button(
        label='📤 Download Excel',
        data=output,
        file_name='overdue_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
