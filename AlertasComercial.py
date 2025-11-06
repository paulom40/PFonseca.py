import streamlit as st
import glob
import pandas as pd
from pathlib import Path

st.subheader("📚 Histórico de Diagnósticos Exportados")

# Lista arquivos na pasta
arquivos = sorted(glob.glob("diagnosticos/diagnostico_vendas_*.xlsx"), reverse=True)
datas_disponiveis = [Path(a).stem.split("_")[-2:] for a in arquivos]
datas_formatadas = [f"{d[0]} {d[1].replace('-',':')}" for d in datas_disponiveis]

# Filtros
data_selecionada = st.selectbox("📅 Selecionar data", datas_formatadas if datas_formatadas else ["Nenhuma"])
cliente_filtro = st.text_input("🔍 Filtrar por cliente (opcional)")

# Log de execução
logs = Path("diagnosticos/log_execucao.txt")
if logs.exists():
    with open(logs, "r", encoding="utf-8") as f:
        st.text_area("📜 Log de Execução", f.read(), height=200)
# Exibe arquivo correspondente
if arquivos and data_selecionada != "Nenhuma":
    idx = datas_formatadas.index(data_selecionada)
    arquivo = arquivos[idx]
    nome = Path(arquivo).name

    # Se filtro de cliente estiver ativo, tenta abrir e filtrar
    if cliente_filtro:
        try:
            df_check = pd.read_excel(arquivo, sheet_name="Ticket Médio Cliente")
            df_filtrado = df_check[df_check["Cliente"].str.contains(cliente_filtro, case=False, na=False)]
            st.write(f"🔎 Registros encontrados para '{cliente_filtro}':", len(df_filtrado))
            st.dataframe(df_filtrado)
        except Exception as e:
            st.warning(f"⚠️ Não foi possível aplicar filtro: {e}")

    with open(arquivo, "rb") as f:
        st.download_button(
            label=f"📥 Baixar {nome}",
            data=f.read(),
            file_name=nome,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Nenhum diagnóstico exportado ainda.")
