import streamlit as st
import pandas as pd
import io

# -------------------------------
# 🔐 Login na Sidebar
# -------------------------------
users = {
    "paulojt": "1234",
    "admin": "adminpass"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.sidebar.success("✅ Login bem-sucedido!")
        else:
            st.sidebar.error("❌ Credenciais inválidas")
    st.stop()

# -------------------------------
# 📊 Aplicação Principal
# -------------------------------
st.title("📂 Filtro por Mês e Ano + Totais Médios")

# 📥 Carregar ficheiro Excel do GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"
try:
    df = pd.read_excel(url, engine='openpyxl')  # Explicitly use openpyxl engine

    # 🔧 Limpar nomes de colunas
    df.columns = [col.strip() for col in df.columns]
    df.columns = [col.replace('\n', '').replace('\r', '').replace('\t', '') for col in df.columns]

    # 🧪 Diagnóstico: mostrar colunas reais
    st.sidebar.subheader("📋 Colunas encontradas")
    st.sidebar.write(df.columns.tolist())

    # 🛠️ Renomear colunas semelhantes a 'Mes' e 'Ano'
    original_columns = df.columns.tolist()
    mes_col = next((col for col in original_columns if "mes" in col.lower()), None)
    ano_col = next((col for col in original_columns if "ano" in col.lower()), None)

    if mes_col:
        df.rename(columns={mes_col: "Mes"}, inplace=True)
        st.sidebar.write(f"Renomeado '{mes_col}' para 'Mes'")
    if ano_col:
        df.rename(columns={ano_col: "Ano"}, inplace=True)
        st.sidebar.write(f"Renomeado '{ano_col}' para 'Ano'")

    # Debugging: Show renamed columns
    st.sidebar.subheader("📋 Colunas após renomeação")
    st.sidebar.write(df.columns.tolist())

    # ✅ Verificar colunas obrigatórias
    required_cols = {"Mes", "Ano"}
    actual_cols = set(df.columns)
    missing = required_cols - actual_cols

    if missing:
        st.error(f"❌ O ficheiro precisa conter as colunas: {missing}")
        st.write("Dados das primeiras linhas para diagnóstico:")
        st.write(df.head())  # Show first few rows to debug
        st.stop()

    # Definir colunas de categorias (percentagens numéricas)
    categoria_cols = ['Congelados', 'Frescos', 'Leitão', 'Peixe', 'Transf', 'Comercial']

    # Verificar se as colunas de categorias existem
    missing_cats = set(categoria_cols) - actual_cols
    if missing_cats:
        st.error(f"❌ Colunas de categorias ausentes: {missing_cats}")
        st.stop()

    # 📅 Filtros
    available_meses = sorted(df["Mes"].dropna().unique())
    available_anos = sorted(df["Ano"].dropna().unique())

    selected_mes = st.sidebar.multiselect("📅 Selecione o(s) Mês(es)", available_meses)
    selected_ano = st.sidebar.multiselect("📆 Selecione o(s) Ano(s)", available_anos)

    # 🔍 Aplicar filtros
    filtered_df = df.copy()
    if selected_mes:
        filtered_df = filtered_df[filtered_df["Mes"].isin(selected_mes)]
    if selected_ano:
        filtered_df = filtered_df[filtered_df["Ano"].isin(selected_ano)]

    # Verificar se há dados após o filtro
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    else:
        # 📄 Mostrar dados filtrados
        st.subheader("📄 Dados Filtrados")
        st.dataframe(filtered_df, use_container_width=True)

        # 📊 Calcular médias por Mês (apenas colunas numéricas de categorias)
        media_por_mes = (
            filtered_df.groupby("Mes")[categoria_cols]
            .mean()
            .round(2)
            .sort_index()
        )

        st.subheader("📊 Médias por Mês (%)")
        st.dataframe(media_por_mes)

        # 📈 Gráfico de barras
        st.bar_chart(media_por_mes)

        # 📤 Exportar dados filtrados e médias
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='DadosFiltrados')
            media_por_mes.to_excel(writer, sheet_name='MediasPorMes')
        processed_data = output.getvalue()

        st.download_button(
            label="📥 Download (.xlsx) dos dados e médias",
            data=processed_data,
            file_name="dados_e_medias.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"❌ Erro ao processar o ficheiro: {e}")
    st.stop()
