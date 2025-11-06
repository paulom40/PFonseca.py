import streamlit as st
import pandas as pd
import json
from pathlib import Path

# 🔄 Carregamento dos dados
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)

    # Padroniza nomes
    df.columns = df.columns.str.strip().str.upper()
    renomear = {}
    for col in df.columns:
        if "CLIENTE" in col: renomear[col] = "Cliente"
        elif "QTD" in col: renomear[col] = "Qtd"
        elif "ARTIGO" in col: renomear[col] = "Artigo"
        elif "LÍQUIDO" in col: renomear[col] = "V_Liquido"
        elif "COMERCIAL" in col: renomear[col] = "Comercial"
        elif "CATEGORIA" in col: renomear[col] = "Categoria"
        elif "MÊS" in col or "MES" in col: renomear[col] = "Mes"
        elif "ANO" in col: renomear[col] = "Ano"
    df = df.rename(columns=renomear)
    return df

df = load_data()

# 📁 Caminho para presets
preset_path = Path("diagnosticos/presets_filtros.json")
preset_path.parent.mkdir(exist_ok=True)

# 📦 Funções de presets
def carregar_presets():
    if preset_path.exists():
        with open(preset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_preset(nome, filtros):
    presets = carregar_presets()
    presets[nome] = filtros
    with open(preset_path, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2)

# 🎛️ Filtros interativos
st.sidebar.header("🎛️ Filtros Dinâmicos")

def filtro_multiselect(label, coluna, valores=None):
    opcoes = sorted(df[coluna].dropna().unique())
    return st.sidebar.multiselect(label, opcoes, default=valores if valores else [])

# Carrega presets se selecionado
presets = carregar_presets()
preset_selecionado = st.sidebar.selectbox("📂 Carregar Preset", [""] + list(presets.keys()))
filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}

clientes = filtro_multiselect("Cliente", "Cliente", filtros.get("Cliente"))
artigos = filtro_multiselect("Artigo", "Artigo", filtros.get("Artigo"))
comerciais = filtro_multiselect("Comercial", "Comercial", filtros.get("Comercial"))
categorias = filtro_multiselect("Categoria", "Categoria", filtros.get("Categoria"))
meses = filtro_multiselect("Mês", "Mes", filtros.get("Mes"))
anos = filtro_multiselect("Ano", "Ano", filtros.get("Ano"))

# Aplica filtros
df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(clientes)]
if artigos: df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigos)]
if comerciais: df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais)]
if categorias: df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias)]
if meses: df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]

# 💾 Salvar novo preset
st.sidebar.markdown("💾 **Salvar Preset Atual**")
nome_preset = st.sidebar.text_input("Nome do preset")
if st.sidebar.button("Salvar preset") and nome_preset:
    filtros_atuais = {
        "Cliente": clientes,
        "Artigo": artigos,
        "Comercial": comerciais,
        "Categoria": categorias,
        "Mes": meses,
        "Ano": anos
    }
    salvar_preset(nome_preset, filtros_atuais)
    st.sidebar.success(f"Preset '{nome_preset}' salvo com sucesso!")

# 🧮 Diagnóstico lateral
st.sidebar.markdown("🧪 Diagnóstico de Filtros")
st.sidebar.write({
    "Clientes": clientes,
    "Artigos": artigos,
    "Comerciais": comerciais,
    "Categorias": categorias,
    "Meses": meses,
    "Anos": anos
})

# ✅ Validação
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()
else:
    st.success(f"✅ {len(df_filtrado)} registros encontrados após filtro.")
    st.dataframe(df_filtrado)
