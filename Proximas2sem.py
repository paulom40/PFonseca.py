import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# Load Excel from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)

# Ensure date column is datetime
df['Vencimento'] = pd.to_datetime(df['Vencimento'], errors='coerce')

# Define today's date
today = datetime.today().date()

# Define week ranges
week1_start = today
week1_end = today + timedelta(days=6)

week2_start = week1_end + timedelta(days=1)
week2_end = week2_start + timedelta(days=6)

# Filter data
df_week1 = df[(df['Vencimento'].dt.date >= week1_start) & (df['Vencimento'].dt.date <= week1_end)]
df_week2 = df[(df['Vencimento'].dt.date >= week2_start) & (df['Vencimento'].dt.date <= week2_end)]

# Helper to convert DataFrame to XLSX
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vencimentos')
    return output.getvalue()

# Layout
st.set_page_config(layout="centered")
st.title("📅 Vencimentos nas Próximas Duas Semanas")

# Week 1
st.subheader(f"🗓 Semana 1: {week1_start.strftime('%d/%m/%Y')} até {week1_end.strftime('%d/%m/%Y')}")
st.metric("Total Semana 1", f"€ {df_week1['Valor'].sum():,.2f}")
st.dataframe(df_week1, use_container_width=True)
st.download_button("📥 Baixar Semana 1 (.xlsx)", data=to_excel_bytes(df_week1),
                   file_name="vencimentos_semana1.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Week 2
st.subheader(f"🗓 Semana 2: {week2_start.strftime('%d/%m/%Y')} até {week2_end.strftime('%d/%m/%Y')}")
st.metric("Total Semana 2", f"€ {df_week2['Valor'].sum():,.2f}")
st.dataframe(df_week2, use_container_width=True)
st.download_button("📥 Baixar Semana 2 (.xlsx)", data=to_excel_bytes(df_week2),
                   file_name="vencimentos_semana2.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
