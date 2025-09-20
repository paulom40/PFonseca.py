import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# Load Excel from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)

# Detect vencimento column
venc_col = next((col for col in df.columns if 'venc' in col.lower()), None)
if venc_col is None:
    st.error("❌ Nenhuma coluna de vencimento encontrada.")
    st.stop()

df[venc_col] = pd.to_datetime(df[venc_col], errors='coerce')

# Sidebar filters
st.sidebar.header("🔍 Filtros")
unique_empresas = df['Empresa'].dropna().unique() if 'Empresa' in df.columns else []
selected_empresas = st.sidebar.multiselect("Empresa", unique_empresas, default=unique_empresas)

# Apply filters
if 'Empresa' in df.columns:
    df = df[df['Empresa'].isin(selected_empresas)]

# Date ranges
today = datetime.today().date()
week1_start, week1_end = today, today + timedelta(days=6)
week2_start, week2_end = week1_end + timedelta(days=1), week1_end + timedelta(days=7)

df_week1 = df[(df[venc_col].dt.date >= week1_start) & (df[venc_col].dt.date <= week1_end)]
df_week2 = df[(df[venc_col].dt.date >= week2_start) & (df[venc_col].dt.date <= week2_end)]

# Excel export
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vencimentos')
    return output.getvalue()

# Conditional formatting helper
def highlight_rows(row):
    overdue = row[venc_col].date() < today
    high_value = row['Valor'] > 10000 if 'Valor' in row else False
    if overdue:
        return ['background-color: #ffcccc'] * len(row)
    elif high_value:
        return ['background-color: #ccffcc'] * len(row)
    else:
        return [''] * len(row)

# Layout
st.set_page_config(layout="centered")
st.title("📅 Vencimentos nas Próximas Duas Semanas")

# Semana 1
st.subheader(f"🗓 Semana 1: {week1_start.strftime('%d/%m/%Y')} até {week1_end.strftime('%d/%m/%Y')}")
if 'Valor' in df.columns:
    st.metric("Total Semana 1", f"€ {df_week1['Valor'].sum():,.2f}")
st.dataframe(df_week1.style.apply(highlight_rows, axis=1), use_container_width=True)
st.download_button("📥 Baixar Semana 1 (.xlsx)", data=to_excel_bytes(df_week1),
                   file_name="vencimentos_semana1.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Semana 2
st.subheader(f"🗓 Semana 2: {week2_start.strftime('%d/%m/%Y')} até {week2_end.strftime('%d/%m/%Y')}")
if 'Valor' in df.columns:
    st.metric("Total Semana 2", f"€ {df_week2['Valor'].sum():,.2f}")
st.dataframe(df_week2.style.apply(highlight_rows, axis=1), use_container_width=True)
st.download_button("📥 Baixar Semana 2 (.xlsx)", data=to_excel_bytes(df_week2),
                   file_name="vencimentos_semana2.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
