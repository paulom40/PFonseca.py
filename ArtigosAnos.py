import streamlit as st
import pandas as pd
import io
import altair as alt
import pages.tendencias_mensais as tm

st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Carregar e limpar os dados
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')
df.columns = df.columns.str.strip().str.upper()
df['ANO'] = pd.to_numeric(df['ANO'].astype(str).str.strip(), errors='coerce').astype('Int64')
df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')

# 🔎 Identificar coluna de quantidade
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR', 'KGS']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

st.sidebar.title("📍 Navegação")
page = st.sidebar.selectbox("Ir para página", ["Página Inicial", "Tendências Mensais"])

if page == "Página Inicial":
    st.title("Bem-vindo à página inicial!")

elif page == "Tendências Mensais" and quantity_col:
    # 🎛️ Filtros
    st.sidebar.header("🔎 Filtros")
    selected_produto = st.sidebar.multiselect("Produto", options=df['PRODUTO'].dropna().unique(),
                                              default=df['PRODUTO'].dropna().unique())
    selected_mes = st.sidebar.multiselect("Mês", options=df['MÊS'].dropna().unique(),
                                          default=df['MÊS'].dropna().unique())
    anos_disponiveis = sorted(df['ANO'].dropna().unique().tolist())
    selected_ano = st.sidebar.multiselect("Ano (Comparar)", options=anos_disponiveis,
                                          default=anos_disponiveis)

    # 🔍 Aplicar filtros
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MÊS'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ]

    # ➕ Adicionar anos ausentes
    for ano in selected_ano:
        if ano not in filtered_df['ANO'].dropna().unique():
            placeholder = {
                'ANO': ano,
                'PRODUTO': selected_produto[0] if selected_produto else None,
                'MÊS': selected_mes[0] if selected_mes else None,
                quantity_col: 0,
                'PM': 0 if 'PM' in df.columns else None
            }
            filtered_df = pd.concat([filtered_df, pd.DataFrame([placeholder])], ignore_index=True)

    # 🔎 Chamar visualização modular
    tm.render(df, filtered_df, quantity_col, selected_ano)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada no arquivo.")
