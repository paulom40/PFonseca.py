import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# Layout básico
st.set_page_config(layout="centered")
st.markdown("<style>div.block-container{padding-top:1rem;padding-bottom:1rem}</style>", unsafe_allow_html=True)
st.title("📱 Dashboard de Vencimentos")

# Carregar dados
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)

# Detectar coluna de vencimento
venc_col = next((col for col in df.columns if 'venc' in col.lower()), None)
if venc_col is None:
    st.error("❌ Nenhuma coluna de vencimento encontrada.")
    st.stop()

df[venc_col] = pd.to_datetime(df[venc_col], errors='coerce')

# Sidebar: filtro por comercial
with st.sidebar:
    st.header("🔍 Filtro por Comercial")
    comerciais = df['Comercial'].dropna().unique() if 'Comercial' in df.columns else []
    comercial_selecionado = st.selectbox("Selecione o comercial", comerciais)

# Filtrar dados
df = df[df['Comercial'] == comercial_selecionado]

# Intervalos de datas
today = datetime.today().date()
week1_start, week1_end = today, today + timedelta(days=6)
week2_start, week2_end = week1_end + timedelta(days=1), week1_end + timedelta(days=7)

df_week1 = df[(df[venc_col].dt.date >= week1_start) & (df[venc_col].dt.date <= week1_end)]
df_week2 = df[(df[venc_col].dt.date >= week2_start) & (df[venc_col].dt.date <= week2_end)]

# Funções auxiliares
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vencimentos')
    return output.getvalue()

def highlight_rows(row):
    overdue = row[venc_col].date() < today
    high_value = row['Valor'] > 10000 if 'Valor' in row else False
    if overdue:
        return ['background-color: #ffcccc'] * len(row)
    elif high_value:
        return ['background-color: #ccffcc'] * len(row)
    else:
        return [''] * len(row)

# Abas
tab1, tab2, tab3, tab4 = st.tabs(["📋 Resumo", "📊 Gráficos", "📅 Vencimentos", "📈 Histórico"])

# 📋 RESUMO
with tab1:
    st.subheader("Totais por Cliente")
    if 'Cliente' in df.columns and 'Valor' in df.columns:
        resumo_week1 = df_week1.groupby('Cliente')['Valor'].sum().rename('Semana 1')
        resumo_week2 = df_week2.groupby('Cliente')['Valor'].sum().rename('Semana 2')
        resumo_total = pd.concat([resumo_week1, resumo_week2], axis=1).fillna(0)
        resumo_total['Total'] = resumo_total['Semana 1'] + resumo_total['Semana 2']
        resumo_total = resumo_total.sort_values(by='Total', ascending=False)
        st.dataframe(resumo_total.style.format({'Semana 1': '€ {:,.2f}', 'Semana 2': '€ {:,.2f}', 'Total': '€ {:,.2f}'}),
                     use_container_width=True)
    else:
        st.info("ℹ️ Dados insuficientes para gerar a tabela resumo.")

# 📊 GRÁFICOS
with tab2:
    st.subheader("Visualização por Cliente")
    chart_type = st.radio("Tipo de gráfico:", ["Barra comparativa", "Pizza total"], horizontal=True)
    df_combined = pd.concat([df_week1, df_week2])
    if 'Cliente' in df_combined.columns and 'Valor' in df_combined.columns:
        if chart_type == "Barra comparativa":
            df_week1_chart = df_week1.groupby('Cliente')['Valor'].sum().rename('Semana 1')
            df_week2_chart = df_week2.groupby('Cliente')['Valor'].sum().rename('Semana 2')
            chart_df = pd.concat([df_week1_chart, df_week2_chart], axis=1).fillna(0)
            chart_df['Total'] = chart_df['Semana 1'] + chart_df['Semana 2']
            chart_df = chart_df.sort_values(by='Total', ascending=False).drop(columns='Total')
            st.bar_chart(chart_df)
        else:
            pie_data = df_combined.groupby('Cliente')['Valor'].sum()
            st.pyplot(pie_data.plot.pie(autopct='%1.1f%%', figsize=(5, 5), ylabel='').figure)
    else:
        st.info("ℹ️ Dados insuficientes para gerar o gráfico.")

# 📅 VENCIMENTOS
with tab3:
    st.subheader(f"🗓 Semana 1: {week1_start.strftime('%d/%m')} → {week1_end.strftime('%d/%m')}")
    if 'Valor' in df.columns and not df_week1.empty:
        st.metric("Total Semana 1", f"€ {df_week1['Valor'].sum():,.2f}")
    st.dataframe(df_week1.style.apply(highlight_rows, axis=1), use_container_width=True)
    st.download_button("📥 Baixar Semana 1", data=to_excel_bytes(df_week1),
                       file_name="vencimentos_semana1.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader(f"🗓 Semana 2: {week2_start.strftime('%d/%m')} → {week2_end.strftime('%d/%m')}")
    if 'Valor' in df.columns and not df_week2.empty:
        st.metric("Total Semana 2", f"€ {df_week2['Valor'].sum():,.2f}")
    st.dataframe(df_week2.style.apply(highlight_rows, axis=1), use_container_width=True)
    st.download_button("📥 Baixar Semana 2", data=to_excel_bytes(df_week2),
                       file_name="vencimentos_semana2.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 📈 HISTÓRICO
with tab4:
    st.subheader("📈 Histórico por Cliente")
    if 'Cliente' in df.columns and venc_col:
        historico = df.groupby(['Cliente', venc_col])['Valor'].sum().reset_index()
        historico = historico.sort_values(by=venc_col)
        st.line_chart(historico.pivot(index=venc_col, columns='Cliente', values='Valor'))
    else:
        st.info("ℹ️ Dados insuficientes para gerar histórico.")
