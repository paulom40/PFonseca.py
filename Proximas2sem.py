import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
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

# Estilo condicional por vencimento
def estilo_dias(val):
    if isinstance(val, int):
        if val < 0:
            return "color: red; font-weight: bold"
        elif val == 0:
            return "background-color: #fff3cd"
        else:
            return "background-color: #d4edda"
    return ""

# Tabela por entidade com destaque visual
def tabela_por_entidade(df_semana, titulo):
    st.subheader(titulo)
    if entidade_col and valor_pendente_col and venc_col and 'Comercial' in df.columns:
        df_temp = df_semana[[entidade_col, venc_col, valor_pendente_col, 'Comercial']].copy()
        df_temp["Dias"] = (df_temp[venc_col] - pd.Timestamp(datetime.today())).dt.days
        df_temp = df_temp.rename(columns={
            entidade_col: "Entidade",
            venc_col: "Data de Vencimento",
            valor_pendente_col: "Valor Pendente",
            "Comercial": "Comercial"
        })
        df_temp = df_temp[["Entidade", "Data de Vencimento", "Dias", "Valor Pendente", "Comercial"]]
        st.dataframe(
            df_temp.style
            .format({"Valor Pendente": "€ {:,.2f}", "Dias": "{:+d}"})
            .applymap(estilo_dias, subset=["Dias"]),
            use_container_width=True
        )
    else:
        st.info("ℹ️ Dados insuficientes para gerar a tabela.")

# Mostrar tabelas por semana
tabela_por_entidade(df_week0, "📋 Valor Pendente por Entidade — Semana 0")
tabela_por_entidade(df_week1, "📋 Valor Pendente por Entidade — Semana 1")
tabela_por_entidade(df_week2, "📋 Valor Pendente por Entidade — Semana 2")

# Resumos por entidade e comercial
def resumo_por_semana(df_semana, titulo):
    st.subheader(titulo)
    if entidade_col and valor_pendente_col and 'Comercial' in df.columns and not df_semana.empty:
        resumo = (
            df_semana.groupby([entidade_col, 'Comercial'])[valor_pendente_col]
            .sum()
            .reset_index()
            .sort_values(by=valor_pendente_col, ascending=False)
        )
        st.dataframe(
            resumo.style.format({valor_pendente_col: "€ {:,.2f}"}),
            use_container_width=True
        )
    else:
        st.info(f"ℹ️ Nenhum dado disponível para {titulo}.")

resumo_por_semana(df_week0, "📊 Soma por Entidade e Comercial — Semana 0")
resumo_por_semana(df_week1, "📊 Soma por Entidade e Comercial — Semana 1")
resumo_por_semana(df_week2, "📊 Soma por Entidade e Comercial — Semana 2")

# Exportação dos resumos para Excel
st.subheader("📤 Exportar totais por Entidade e Comercial para Excel")

def resumo_excel(df_semana):
    return (
        df_semana.groupby([entidade_col, 'Comercial'])[valor_pendente_col]
        .sum()
        .reset_index()
        .sort_values(by=valor_pendente_col, ascending=False)
    )

resumo0 = resumo_excel(df_week0)
resumo1 = resumo_excel(df_week1)
resumo2 = resumo_excel(df_week2)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    resumo0.to_excel(writer, sheet_name='Semana 0', index=False)
    resumo1.to_excel(writer, sheet_name='Semana 1', index=False)
    resumo2.to_excel(writer, sheet_name='Semana 2', index=False)
output.seek(0)

b64 = base64.b64encode(output.read()).decode()
href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Totais_Entidade_Comercial.xlsx">📥 Baixar Excel com totais por entidade e comercial</a>'
st.markdown(href, unsafe_allow_html=True)
