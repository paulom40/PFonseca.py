import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import base64

st.set_page_config(layout="wide")
st.title("📊 Painel de Vencimentos")

# Carregar dados
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)
df.rename(columns=lambda x: x.strip(), inplace=True)

# Detectar colunas
venc_col = next((col for col in df.columns if 'venc' in col.lower()), None)
valor_pendente_col = next((col for col in df.columns if 'valor pendente' in col.lower()), None)
entidade_col = next((col for col in df.columns if 'entidade' in col.lower()), None)

if venc_col is None:
    st.error("❌ Coluna de vencimento não encontrada.")
    st.stop()
df[venc_col] = pd.to_datetime(df[venc_col], errors='coerce')

# Separadores
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Dashboard Semanal",
    "📆 Relatório Anual 2025",
    "🗓 Relatório Mensal 2025",
    "📈 Comparativo Mensal"
])

with tab1:
    st.sidebar.header("🔍 Filtro por Comercial")
    comerciais = df['Comercial'].dropna().unique() if 'Comercial' in df.columns else []
    comercial_selecionado = st.sidebar.selectbox("Selecione o comercial", ["Todos"] + list(comerciais))

    if comercial_selecionado != "Todos":
        df = df[df['Comercial'] == comercial_selecionado]

    if df.empty:
        st.warning(f"⚠️ Nenhum dado encontrado para o comercial '{comercial_selecionado}'.")
        st.stop()

    # Semana base = semana atual - 2
    hoje = datetime.today()
    semana_base = max(1, hoje.isocalendar().week - 2)
    ano_base = hoje.year
    data_base = datetime.strptime(f'{ano_base}-W{semana_base}-1', "%Y-W%W-%w").date()

    week1_start = data_base
    week1_end = week1_start + timedelta(days=6)
    week2_start = week1_end + timedelta(days=1)
    week2_end = week2_start + timedelta(days=6)
    week0_end = week1_start - timedelta(days=1)
    week0_start = week0_end - timedelta(days=6)

    df_week0 = df[(df[venc_col].dt.date >= week0_start) & (df[venc_col].dt.date <= week0_end)]
    df_week1 = df[(df[venc_col].dt.date >= week1_start) & (df[venc_col].dt.date <= week1_end)]
    df_week2 = df[(df[venc_col].dt.date >= week2_start) & (df[venc_col].dt.date <= week2_end)]

    def estilo_dias(val):
        if isinstance(val, int):
            if val < 0:
                return "color: red; font-weight: bold"
            elif val == 0:
                return "background-color: #fff3cd"
            else:
                return "background-color: #d4edda"
        return ""

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

    tabela_por_entidade(df_week0, "📋 Semana 0")
    tabela_por_entidade(df_week1, "📋 Semana 1")
    tabela_por_entidade(df_week2, "📋 Semana 2")

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

    resumo_por_semana(df_week0, "📊 Totais — Semana 0")
    resumo_por_semana(df_week1, "📊 Totais — Semana 1")
    resumo_por_semana(df_week2, "📊 Totais — Semana 2")

    st.subheader("📤 Exportar dados detalhados para Excel")

    def preparar_df_export(df_semana):
        df_temp = df_semana[[entidade_col, venc_col, valor_pendente_col, 'Comercial']].copy()
        df_temp["Dias"] = (df_temp[venc_col] - pd.Timestamp(datetime.today())).dt.days
        df_temp = df_temp.rename(columns={
            entidade_col: "Entidade",
            venc_col: "Data de Vencimento",
            valor_pendente_col: "Valor Pendente",
            "Comercial": "Comercial"
        })
        df_temp = df_temp[["Entidade", "Data de Vencimento", "Dias", "Valor Pendente", "Comercial"]]

        totais = df_temp.groupby("Entidade")["Valor Pendente"].sum().reset_index()
        totais["Data de Vencimento"] = ""
        totais["Dias"] = ""
        totais["Comercial"] = "—"
        totais = totais[["Entidade", "Data de Vencimento", "Dias", "Valor Pendente", "Comercial"]]
        totais["Entidade"] = totais["Entidade"] + " (Total)"

        return pd.concat([df_temp, totais], ignore_index=True)

    df_export0 = preparar_df_export(df_week0)
    df_export1 = preparar_df_export(df_week1)
    df_export2 = preparar_df_export(df_week2)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export0.to_excel(writer, sheet_name='Semana 0', index=False)
        df_export1.to_excel(writer, sheet_name='Semana 1', index=False)
        df_export2.to_excel(writer, sheet_name='Semana 2', index=False)
    output.seek(0)

    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Dashboard_Semanal.xlsx">📥 Baixar Excel</a>'
    st.markdown(href, unsafe_allow_html=True)

# Os separadores tab2, tab3 e tab4 continuam abaixo — posso enviar já formatados se quiseres.
