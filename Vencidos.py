import pandas as pd
import requests
from io import BytesIO
import streamlit as st

st.set_page_config(layout="wide")

# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/VVencidos.xlsx"

try:
    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), sheet_name="VVencidos")
    df["Data Venc."] = pd.to_datetime(df["Data Venc."], origin='1899-12-30', unit='D', errors="coerce")

    st.success("📥 Dados carregados com sucesso!")

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

st.write("📅 Última atualização: 01/08/2025")

# -------------------------------
# 🧹 Clean and prepare data
# -------------------------------
df.columns = df.columns.str.strip()
df["Entidade"] = df["Entidade"].astype(str).str.strip()
df["Categoria"] = df["Categoria"].astype(str).str.strip()
df["Comercial"] = df["Comercial"].astype(str).str.strip()
df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
df = df.dropna(subset=["Dias"])
df["Dias"] = df["Dias"].astype(int)
df["Valor Pendente"] = pd.to_numeric(df["Valor Pendente"], errors="coerce")

# -------------------------------
# 🎛️ Sidebar: Hierarchical Filters
# -------------------------------
st.sidebar.header("🔎 Filtros")

# Step 1: Comercial
comercial_unicos = sorted(df["Comercial"].dropna().unique())
comercial_selecionado = st.sidebar.selectbox("Selecione o Comercial:", comercial_unicos)
df_comercial = df[df["Comercial"] == comercial_selecionado]

# Step 2: Categoria
categorias_unicas = sorted(df_comercial["Categoria"].dropna().unique())
selecionar_todas_categorias = st.sidebar.checkbox("Selecionar todas as Categorias", value=True)

if selecionar_todas_categorias:
    categorias_selecionadas = categorias_unicas
else:
    categorias_selecionadas = st.sidebar.multiselect("Selecione Categorias:", categorias_unicas)

df_categoria = df_comercial[df_comercial["Categoria"].isin(categorias_selecionadas)]

# Step 3: Entidade
entidades_unicas = sorted(df_categoria["Entidade"].dropna().unique())
select_all_entidades = st.sidebar.checkbox("Selecionar todas as Entidades", value=True)

if select_all_entidades:
    entidades_selecionadas = entidades_unicas
else:
    entidades_selecionadas = st.sidebar.multiselect("Selecione Entidades:", entidades_unicas)

df_entidade = df_categoria[df_categoria["Entidade"].isin(entidades_selecionadas)]

# Step 4: Dias slider
st.sidebar.markdown("### ⏳ Filtro por Dias até Vencimento")
dias_min_default = int(df_entidade["Dias"].min()) if not df_entidade.empty else 1
dias_max_default = int(df_entidade["Dias"].max()) if not df_entidade.empty else 360

dias_min, dias_max = st.sidebar.slider(
    "Selecione o intervalo de Dias:",
    min_value=1,
    max_value=360,
    value=(dias_min_default, dias_max_default),
    step=1
)

# Final filter
df_filtrado = df_entidade[
    (df_entidade["Dias"] >= dias_min) &
    (df_entidade["Dias"] <= dias_max)
]

# -------------------------------
# 📊 Display Results
# -------------------------------
st.title("📊 Vencimentos Comerciais")
st.markdown(f"""
Exibindo resultados para:
- **Comercial:** {comercial_selecionado}
- **Categorias:** {', '.join(categorias_selecionadas) if categorias_selecionadas else 'Nenhuma'}
- **Entidades:** {', '.join(entidades_selecionadas) if entidades_selecionadas else 'Nenhuma'}
- **Dias:** {dias_min}–{dias_max}
""")

st.dataframe(df_filtrado, use_container_width=True)

# -------------------------------
# 📈 Summary Metrics
# -------------------------------
total_registros = len(df_filtrado)
media_dias = df_filtrado["Dias"].mean() if total_registros > 0 else 0
valor_total = df_filtrado["Valor Pendente"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📌 Total de Registros", total_registros)
col2.metric("📆 Dias Médios", f"{media_dias:.1f}")
col3.metric("💰 Valor Pendente Total", f"€ {valor_total:,.2f}")

# -------------------------------
# 📤 Export to Excel with Summary
# -------------------------------
st.markdown("### 📤 Exportar para Excel")

def to_excel(df, resumo):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Vencimentos
        df.to_excel(writer, index=False, sheet_name='Vencimentos')

        # Sheet 2: Resumo
        resumo_df = pd.DataFrame(resumo.items(), columns=["Descrição", "Valor"])
        resumo_df.to_excel(writer, index=False, sheet_name='Resumo')

    output.seek(0)
    return output

resumo = {
    "Comercial": comercial_selecionado,
    "Categorias": ', '.join(categorias_selecionadas),
    "Entidades": ', '.join(entidades_selecionadas),
    "Dias": f"{dias_min}–{dias_max}",
    "Total de Registros": total_registros,
    "Dias Médios": f"{media_dias:.1f}",
    "Valor Pendente Total": f"€ {valor_total:,.2f}"
}

excel_data = to_excel(df_filtrado, resumo)

st.download_button(
    label="📥 Baixar Excel com Resumo",
    data=excel_data,
    file_name="vencimentos_comerciais.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
