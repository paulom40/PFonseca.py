import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

st.set_page_config(page_title="Alertas de Compras", page_icon="Alert", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .main-header {font-size:2.5rem; color:#1f77b4; text-align:center; margin:2rem 0; font-weight:700;}
    .section-header {font-size:1.6rem; color:#2c3e50; margin:2rem 0 1rem; padding-bottom:0.5rem; border-bottom:3px solid #3498db; font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Alertas de Compras</h1>", unsafe_allow_html=True)

# Botão Voltar
if st.button("Voltar ao Dashboard Principal"):
    st.switch_page("Dashboard_Principal.py")

# --- Verificar dados ---
if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte ao Dashboard Principal para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# --- Padronizar Mês/Ano ---
meses = {'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12,
         '1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'11':11,'12':12}

def padronizar(s, tipo='mes'):
    s = str(s).lower().strip()
    s = re.sub(r'[^a-z0-9]', '', s)
    if tipo == 'mes':
        return f"{meses.get(s, 0):02d}" if meses.get(s) else None
    else:  # ano
        nums = re.sub(r'\D', '', s)
        if len(nums) == 4: return nums
        if len(nums) == 2: return f"20{nums}" if int(nums) < 50 else f"19{nums}"
        return None

df['Mes'] = df['Mes'].apply(padronizar)
df['Ano'] = df['Ano'].apply(lambda x: padronizar(x, 'ano'))
df = df.dropna(subset=['Mes', 'Ano'])
df['Periodo'] = df['Ano'] + '-' + df['Mes']
df['Mes_Nome'] = df['Mes'].map({f"{i:02d}": m for i, m in enumerate(
    "Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez".split(), 1)})

# --- Análise de Alertas ---
if len(df['Periodo'].unique()) < 2:
    st.warning("São necessários pelo menos 2 períodos para análise.")
    st.stop()

agg = df.groupby(['Cliente', 'Periodo'])['Qtd'].sum().reset_index()
periodos = sorted(agg['Periodo'].unique())
atual, anterior = periodos[-1], periodos[-2]

qtd = agg.pivot(index='Cliente', columns='Periodo', values='Qtd').fillna(0)
qtd['Atual'] = qtd[atual]
qtd['Anterior'] = qtd[anterior]
qtd['Var_%'] = ((qtd['Atual'] - qtd['Anterior']) / qtd['Anterior'].replace(0, 1)) * 100

subidas = qtd[qtd['Var_%'] > 20].copy()
descidas = qtd[qtd['Var_%'] < -20].copy()
inativos = qtd[(qtd['Anterior'] > 0) & (qtd['Atual'] == 0)].copy()

subidas = subidas.sort_values('Var_%', ascending=False)[['Anterior', 'Atual', 'Var_%']]
descidas = descidas.sort_values('Var_%')[['Anterior', 'Atual', 'Var_%']]
inativos = inativos.sort_values('Anterior', ascending=False)[['Anterior', 'Atual']]

subidas.index.name = descidas.index.name = inativos.index.name = 'Cliente'
subidas = subidas.reset_index()
descidas = descidas.reset_index()
inativos = inativos.reset_index().assign(Var_%=-100)

# --- Interface ---
st.markdown("<div class='section-header'>Análise de Tendências</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Subidas", len(subidas))
col2.metric("Descidas", len(descidas))
col3.metric("Inativos", len(inativos))

tab1, tab2, tab3 = st.tabs([f"Subidas ({len(subidas)})", f"Descidas ({len(descidas)})", f"Inativos ({len(inativos)})"])

with tab1:
    if not subidas.empty:
        st.dataframe(subidas, use_container_width=True)
        fig = px.bar(subidas.head(10), x='Var_%', y='Cliente', orientation='h', title="Top 10 Subidas", color='Var_%')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Nenhum cliente com subida >20%")

with tab2:
    if not descidas.empty:
        st.dataframe(descidas, use_container_width=True)
        fig = px.bar(descidas.head(10), x='Var_%', y='Cliente', orientation='h', title="Top 10 Descidas", color='Var_%')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Nenhum cliente com descida >20%")

with tab3:
    if not inativos.empty:
        st.dataframe(inativos, use_container_width=True)
        fig = px.bar(inativos.head(10), x='Anterior', y='Cliente', orientation='h', title="Top 10 Volumes Perdidos", color='Anterior')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Nenhum cliente parou de comprar")

# --- Footer ---
st.markdown("---")
st.caption(f"Atualizado em: {datetime.now():%d/%m/%Y %H:%M}")
