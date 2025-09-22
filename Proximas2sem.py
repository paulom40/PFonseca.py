import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
import base64

# Layout mobile
st.set_page_config(layout="centered")
st.markdown("<style>div.block-container{padding-top:1rem;padding-bottom:1rem}</style>", unsafe_allow_html=True)
st.title("📱 Dashboard de Vencimentos")

# Carregar dados
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)
df.rename(columns=lambda x: x.strip(), inplace=True)

# Detectar colunas principais
venc_col = next((col for col in df.columns if 'venc' in col.lower()), None)
valor_pendente_col = next((col for col in df.columns if 'valor pendente' in col.lower()), None)
entidade_col = next((col for col in df.columns if 'entidade' in col.lower()), None)

# Validar coluna de vencimento
if venc_col is None:
    st.error("❌ Nenhuma coluna de vencimento encontrada.")
    st.stop()
df[venc_col] = pd.to_datetime(df[venc_col], errors='coerce')

# Filtro por comercial
with st.sidebar:
    st.header("🔍 Filtro por Comercial")
    comerciais = df['Comercial'].dropna().unique() if 'Comercial' in df.columns else []
    comercial_selecionado = st.selectbox("Selecione o comercial", ["Todos"] + list(comerciais))

if comercial_selecionado != "Todos":
    df = df[df['Comercial'] == comercial_selecionado]

if df.empty:
    st.warning(f"⚠️ Nenhum dado encontrado para o comercial '{comercial_selecionado}'.")
    st.stop()

# Intervalos dinâmicos
datas_validas = df[venc_col].dropna().dt.date
datas_futuras = datas_validas[datas_validas >= datetime.today().date()]
base_date = datas_futuras.min() if not datas_futuras.empty else datas_validas.min()

week1_start = base_date
week1_end = week1_start + timedelta(days=6)
week2_start = week1_end + timedelta(days=1)
week2_end = week2_start + timedelta(days=6)
week0_end = week1_start - timedelta(days=1)
week0_start = week0_end - timedelta(days=6)

df_week0 = df[(df[venc_col].dt.date >= week0_start) & (df[venc_col].dt.date <= week0_end)]
df_week1 = df[(df[venc_col].dt.date >= week1_start) & (df[venc_col].dt.date <= week1_end)]
df_week2 = df[(df[venc_col].dt.date >= week2_start) & (df[venc_col].dt.date <= week2_end)]

# Cartão fixo com intervalos
st.markdown(f"""
<style>
.fixed-card {{
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: #f0f8ff;
    padding: 1rem;
    border-radius: 8px;
    border-left: 5px solid #4682B4;
    margin-bottom: 1rem;
}}
</style>
<div class="fixed-card">
    <h4 style="margin-top:0">📅 Intervalos com base nos dados disponíveis</h4>
    <ul style="padding-left:1rem">
        <li><strong>🗓 Semana 0:</strong> {week0_start.strftime('%d/%m/%Y')} → {week0_end.strftime('%d/%m/%Y')}</li>
        <li><strong>🗓 Semana 1:</strong> {week1_start.strftime('%d/%m/%Y')} → {week1_end.strftime('%d/%m/%Y')}</li>
        <li><strong>🗓 Semana 2:</strong> {week2_start.strftime('%d/%m/%Y')} → {week2_end.strftime('%d/%m/%Y')}</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Função para exportar gráfico
def export_figure(fig, filename):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 Baixar gráfico como imagem</a>'
    st.markdown(href, unsafe_allow_html=True)

# 📋 Resumo por Entidade
st.subheader("📋 Valor Pendente por Entidade — Semana 0")
if entidade_col and valor_pendente_col and not df_week0.empty:
    resumo_entidade_sem0 = df_week0.groupby(entidade_col)[valor_pendente_col].sum().sort_values(ascending=False)
    st.dataframe(resumo_entidade_sem0.reset_index().style.format({valor_pendente_col: '€ {:,.2f}'}), use_container_width=True)
else:
    st.info("ℹ️ Nenhum dado disponível para Semana 0.")

st.subheader("📋 Valor Pendente por Entidade — Semana 1")
if entidade_col and valor_pendente_col and not df_week1.empty:
    resumo_entidade_sem1 = df_week1.groupby(entidade_col)[valor_pendente_col].sum().sort_values(ascending=False)
    st.dataframe(resumo_entidade_sem1.reset_index().style.format({valor_pendente_col: '€ {:,.2f}'}), use_container_width=True)
else:
    st.info("ℹ️ Nenhum dado disponível para Semana 1.")

st.subheader("📋 Valor Pendente por Entidade — Semana 2")
if entidade_col and valor_pendente_col and not df_week2.empty:
    resumo_entidade_sem2 = df_week2.groupby(entidade_col)[valor_pendente_col].sum().sort_values(ascending=False)
    st.dataframe(resumo_entidade_sem2.reset_index().style.format({valor_pendente_col: '€ {:,.2f}'}), use_container_width=True)
else:
    st.info("ℹ️ Nenhum dado disponível para Semana 2.")

# 📊 Gráfico comparativo por entidade
st.subheader("📊 Comparativo por Entidade — Semana 0, 1 e 2")
if entidade_col and valor_pendente_col:
    sem0 = df_week0.groupby(entidade_col)[valor_pendente_col].sum().rename("Semana 0")
    sem1 = df_week1.groupby(entidade_col)[valor_pendente_col].sum().rename("Semana 1")
    sem2 = df_week2.groupby(entidade_col)[valor_pendente_col].sum().rename("Semana 2")

    comparativo = pd.concat([sem0, sem1, sem2], axis=1).fillna(0)
    comparativo["Total"] = comparativo.sum(axis=1)
    comparativo = comparativo.sort_values(by="Total", ascending=False).drop(columns="Total")

    top_n = 8
    top_entidades = comparativo.head(top_n)
    outros = comparativo.iloc[top_n:].sum()
    if outros.sum() > 0:
        outros_df = pd.DataFrame({
            "Semana 0": [outros["Semana 0"]],
            "Semana 1": [outros["Semana 1"]],
            "Semana 2": [outros["Semana 2"]],
        }, index=["Outros"])
        comparativo = pd.concat([top_entidades, outros_df])

    fig, ax = plt.subplots(figsize=(10, 6))
    comparativo.plot(kind="bar", ax=ax)
    ax.set_ylabel("Valor Pendente (€)")
    ax.set_title("Comparativo por Entidade")
    ax.legend(title="Semana")
    for container in ax.containers:
        ax.bar_label(container, fmt="€ %.0f")

    st.pyplot(fig)
    export_figure(fig, "comparativo_entidades.png")
else:
    st.info("ℹ️ Dados insuficientes para gerar o gráfico comparativo por entidade.")
