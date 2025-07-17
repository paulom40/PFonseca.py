import pandas as pd
import requests
from io import BytesIO
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from io import BytesIO

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

st.write("📅 Última atualização: 17/07/2025 às 13:30")

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
# 🖨️ Export to PDF with ReportLab
# -------------------------------
st.markdown("### 📤 Exportar para PDF")

if st.button("📄 Gerar PDF dos Resultados"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        c = canvas.Canvas(tmpfile.name, pagesize=A4)
        width, height = A4

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "Vencimentos Comerciais")

        # Filters
        c.setFont("Helvetica", 12)
        y = height - 3.5 * cm
        c.drawString(2 * cm, y, f"Comercial: {comercial_selecionado}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Categorias: {', '.join(categorias_selecionadas)}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Entidades: {', '.join(entidades_selecionadas)}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Dias: {dias_min}–{dias_max}")
        y -= 1 * cm

        # Summary
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, f"Total de Registros: {total_registros}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Dias Médios: {media_dias:.1f}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Valor Pendente Total: € {valor_total:,.2f}")
        y -= 1 * cm

        # Table header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, y, "Entidade | Categoria | Dias | Valor Pendente")
        y -= 0.5 * cm
        c.setFont("Helvetica", 10)

        # Table rows
        for _, row in df_filtrado.iterrows():
            linha = f"{row['Entidade']} | {row['Categoria']} | {row['Dias']} | € {row['Valor Pendente']:,.2f}"
            c.drawString(2 * cm, y, linha)
            y -= 0.4 * cm
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm

        c.save()

        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="📥 Baixar PDF",
                data=f.read(),
                file_name="vencimentos_comerciais.pdf",
                mime="application/pdf"
            )

# -------------------------------
# 📤 Export to Excel with Summary
# -------------------------------
st.markdown("### 📤 Exportar para Excel")

def to_excel(df, resumo):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Vencimentos
        df.to_excel(writer, index=False, sheet_name='Vencimentos')
        workbook = writer.book
        worksheet1 = writer.sheets['Vencimentos']
        format_currency = workbook.add_format({'num_format': '€ #,##0.00'})
        worksheet1.set_column('A:D', 20)
        worksheet1.set_column('D:D', None, format_currency)

        # Sheet 2: Resumo
        resumo_df = pd.DataFrame(resumo.items(), columns=["Descrição", "Valor"])
        resumo_df.to_excel(writer, index=False, sheet_name='Resumo')
        worksheet2 = writer.sheets['Resumo']
        worksheet2.set_column('A:B', 40)

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

