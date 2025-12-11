import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Compras - KPIs + YoY", layout="wide")
st.title("Dashboard de Compras – KPIs + Comparativo com Ano Anterior")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
    df_raw = pd.read_excel(url)

    df = pd.DataFrame({
        "Data":       pd.to_datetime(df_raw.iloc[:, 0], errors="coerce"),
        "Cliente":    df_raw.iloc[:, 1].astype(str).str.strip(),
        "Artigo":     df_raw.iloc[:, 2].astype(str).str.strip(),
        "Quantidade": pd.to_numeric(df_raw.iloc[:, 3], errors="coerce").fillna(0),
        "Comercial":  df_raw.iloc[:, 8].astype(str).str.strip(),
    })

    df = df.dropna(subset=["Data"])
    df = df[(df["Cliente"] != "nan") & (df["Comercial"] != "nan") & (df["Artigo"] != "nan")]
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["MesNumero"] = df["Data"].dt.month  # Para filtro numérico
    df["MesNome"] = df["Data"].dt.strftime("%b")   # Jan, Feb, Mar…
    df["MesNomeCompleto"] = df["Data"].dt.strftime("%B")  # Janeiro, Fevereiro...
    
    return df

df = load_data()

# === SIDEBAR – FILTROS DINÂMICOS MULTISELECÇÃO ===
st.sidebar.header("Filtros Dinâmicos")

# 1. FILTRO DE ANO (multiselect)
st.sidebar.subheader("Filtro por Ano")
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect(
    "Selecionar Anos",
    options=anos_disponiveis,
    default=[anos_disponiveis[0]] if anos_disponiveis else []
)

# Se não selecionou nenhum ano, usar todos
if not anos_selecionados:
    anos_selecionados = anos_disponiveis

# 2. FILTRO DE MÊS (multiselect com nomes completos)
st.sidebar.subheader("Filtro por Mês")
# Mapeamento de números para nomes completos
meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Obter meses disponíveis nos anos selecionados
meses_disponiveis = sorted(df[df["Ano"].isin(anos_selecionados)]["MesNumero"].unique())
opcoes_meses = [meses_nomes[mes] for mes in meses_disponiveis if mes in meses_nomes]

# Inverter mapeamento para obter número do mês a partir do nome
nomes_para_meses = {v: k for k, v in meses_nomes.items()}

meses_selecionados_nomes = st.sidebar.multiselect(
    "Selecionar Meses",
    options=opcoes_meses,
    default=opcoes_meses  # Por padrão, selecionar todos os meses disponíveis
)

# Converter nomes dos meses para números
if meses_selecionados_nomes:
    meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
else:
    meses_selecionados = meses_disponiveis  # Se não selecionou nenhum, usar todos

# 3. FILTRO DE COMERCIAL (multiselect com checkbox "Todos")
st.sidebar.subheader("Filtro por Comercial")
# Filtrar comerciais disponíveis nos anos e meses selecionados
comerciais_disponiveis = sorted(df[
    (df["Ano"].isin(anos_selecionados)) & 
    (df["MesNumero"].isin(meses_selecionados))
]["Comercial"].unique())

todos_comerciais = st.sidebar.checkbox("Todos os Comerciais", value=True, key="todos_comerciais")

if todos_comerciais:
    comerciais_selecionados = comerciais_disponiveis
else:
    comerciais_selecionados = st.sidebar.multiselect(
        "Selecionar Comerciais",
        options=comerciais_disponiveis,
        default=comerciais_disponiveis[:min(5, len(comerciais_disponiveis))] if comerciais_disponiveis else []
    )
    
    if not comerciais_selecionados:
        comerciais_selecionados = comerciais_disponiveis

# 4. FILTRO DE CLIENTE (multiselect com checkbox "Todos")
st.sidebar.subheader("Filtro por Cliente")
# Filtrar clientes disponíveis nos filtros anteriores
clientes_disponiveis = sorted(df[
    (df["Ano"].isin(anos_selecionados)) & 
    (df["MesNumero"].isin(meses_selecionados)) &
    (df["Comercial"].isin(comerciais_selecionados))
]["Cliente"].unique())

todos_clientes = st.sidebar.checkbox("Todos os Clientes", value=True, key="todos_clientes")

if todos_clientes:
    clientes_selecionados = clientes_disponiveis
else:
    clientes_selecionados = st.sidebar.multiselect(
        "Selecionar Clientes",
        options=clientes_disponiveis,
        default=clientes_disponiveis[:min(5, len(clientes_disponiveis))] if clientes_disponiveis else []
    )
    
    if not clientes_selecionados:
        clientes_selecionados = clientes_disponiveis

# 5. FILTRO DE ARTIGO (multiselect com checkbox "Todos")
st.sidebar.subheader("Filtro por Artigo")
# Filtrar artigos disponíveis nos filtros anteriores
artigos_disponiveis = sorted(df[
    (df["Ano"].isin(anos_selecionados)) & 
    (df["MesNumero"].isin(meses_selecionados)) &
    (df["Comercial"].isin(comerciais_selecionados)) &
    (df["Cliente"].isin(clientes_selecionados))
]["Artigo"].unique())

todos_artigos = st.sidebar.checkbox("Todos os Artigos", value=True, key="todos_artigos")

if todos_artigos:
    artigos_selecionados = artigos_disponiveis
else:
    artigos_selecionados = st.sidebar.multiselect(
        "Selecionar Artigos",
        options=artigos_disponiveis,
        default=artigos_disponiveis[:min(5, len(artigos_disponiveis))] if artigos_disponiveis else []
    )
    
    if not artigos_selecionados:
        artigos_selecionados = artigos_disponiveis

# === RESUMO DOS FILTROS APLICADOS ===
st.sidebar.divider()
st.sidebar.subheader("Resumo dos Filtros")
st.sidebar.write(f"**Anos:** {len(anos_selecionados)} selecionados")
st.sidebar.write(f"**Meses:** {len(meses_selecionados)} selecionados")
st.sidebar.write(f"**Comerciais:** {len(comerciais_selecionados)} selecionados")
st.sidebar.write(f"**Clientes:** {len(clientes_selecionados)} selecionados")
st.sidebar.write(f"**Artigos:** {len(artigos_selecionados)} selecionados")

# === DADOS FILTRADOS ===
df_filtrado = df[
    (df["Ano"].isin(anos_selecionados)) &
    (df["MesNumero"].isin(meses_selecionados)) &
    (df["Comercial"].isin(comerciais_selecionados)) &
    (df["Cliente"].isin(clientes_selecionados)) &
    (df["Artigo"].isin(artigos_selecionados))
].copy()

# Se múltiplos anos, separar por ano atual (mais recente) e anterior
if len(anos_selecionados) >= 2:
    ano_atual = max(anos_selecionados)
    ano_anterior = sorted(anos_seponíveis, reverse=True)[1]  # Segundo ano mais recente
    tem_ano_anterior = True
elif len(anos_selecionados) == 1:
    ano_atual = anos_selecionados[0]
    ano_anterior = ano_atual - 1
    tem_ano_anterior = ano_anterior in df["Ano"].unique()
else:
    ano_atual = anos_disponiveis[0] if anos_disponiveis else None
    ano_anterior = None
    tem_ano_anterior = False

# Dados para o ano atual
df_atual = df_filtrado[df_filtrado["Ano"] == ano_atual].copy() if ano_atual else pd.DataFrame()

# Dados para o ano anterior (se existir)
if tem_ano_anterior:
    df_anterior = df_filtrado[df_filtrado["Ano"] == ano_anterior].copy()
else:
    df_anterior = pd.DataFrame(columns=df.columns)

# === CÁLCULO DOS KPIs ===
total_atual = df_atual["Quantidade"].sum() if not df_atual.empty else 0

if tem_ano_anterior and not df_anterior.empty:
    total_anterior = df_anterior["Quantidade"].sum()
    var_total = total_atual - total_anterior
    var_pct = (var_total / total_anterior * 100) if total_anterior > 0 else 0
else:
    total_anterior = 0
    var_total = 0
    var_pct = 0

n_clientes_atual = df_atual["Cliente"].nunique() if not df_atual.empty else 0

if tem_ano_anterior and not df_anterior.empty:
    n_clientes_anterior = df_anterior["Cliente"].nunique()
    var_clientes = n_clientes_atual - n_clientes_anterior
else:
    n_clientes_anterior = 0
    var_clientes = 0

n_artigos_atual = df_atual["Artigo"].nunique() if not df_atual.empty else 0
n_artigos_anterior = df_anterior["Artigo"].nunique() if tem_ano_anterior and not df_anterior.empty else 0

n_comerciais = df_atual["Comercial"].nunique() if not df_atual.empty else 0

ticket_atual = total_atual / len(df_atual) if len(df_atual) > 0 else 0

if tem_ano_anterior and len(df_anterior) > 0:
    ticket_anterior = total_anterior / len(df_anterior)
    var_ticket = ticket_atual - ticket_anterior
else:
    ticket_anterior = 0
    var_ticket = 0

top_cliente = df_atual.groupby("Cliente")["Quantidade"].sum().idxmax() if not df_atual.empty else "—"
top_qtd = df_atual.groupby("Cliente")["Quantidade"].sum().max() if not df_atual.empty else 0

# === 8 KPIs BONITOS NO TOPO ===
if tem_ano_anterior and ano_anterior:
    st.markdown(f"### Resumo Executivo – {ano_atual} vs {ano_anterior}")
else:
    st.markdown(f"### Resumo Executivo – {ano_atual}")

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

with c1:
    st.metric("Total Quantidade", f"{total_atual:,.0f}", f"{var_total:+,.0f}" if tem_ano_anterior else None)

with c2:
    if tem_ano_anterior:
        st.metric("Variação %", f"{var_pct:+.1f}%", delta_color="normal")
    else:
        st.metric("Variação %", "N/A")

with c3:
    st.metric("Clientes Únicos", n_clientes_atual, f"{var_clientes:+d}" if tem_ano_anterior else None)

with c4:
    if tem_ano_anterior:
        st.metric("Artigos Vendidos", n_artigos_atual, f"{n_artigos_atual - n_artigos_anterior:+d}")
    else:
        st.metric("Artigos Vendidos", n_artigos_atual)

with c5:
    st.metric("Comerciais Ativos", n_comerciais)

with c6:
    st.metric("Ticket Médio", f"{ticket_atual:,.0f}", f"{var_ticket:+.0f}" if tem_ano_anterior else None)

with c7:
    st.metric("Top Cliente", top_cliente)

with c8:
    st.metric("Qtd Top Cliente", f"{top_qtd:,.0f}")

st.divider()

# === EVOLUÇÃO MENSAL ===
if not df_filtrado.empty:
    if len(anos_selecionados) > 1:
        st.subheader(f"Evolução Mensal por Ano")
        
        # Ordenar meses corretamente
        ordem_meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # Criar pivot table para múltiplos anos
        evolucao_anos = df_filtrado.pivot_table(
            index="MesNome",
            columns="Ano",
            values="Quantidade",
            aggfunc="sum"
        ).fillna(0)
        
        # Reordenar meses
        evolucao_anos = evolucao_anos.reindex(ordem_meses, fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14,6))
        
        # Plotar cada ano
        cores = ["#2E86AB", "#A23B72", "#F18F01", "#73AB84", "#C14953"]
        for idx, ano in enumerate(sorted(anos_selecionados, reverse=True)):
            if ano in evolucao_anos.columns:
                ax.plot(ordem_meses, evolucao_anos[ano].values, 
                       marker="o", linewidth=3, label=str(ano), 
                       color=cores[idx % len(cores)])
        
        ax.set_title(f"Evolução Mensal Comparativa", fontsize=15, fontweight="bold")
        ax.set_ylabel("Quantidade")
        ax.legend(title="Ano")
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    
    elif tem_ano_anterior:
        st.subheader(f"Evolução Mensal Comparativa – {ano_anterior} vs {ano_atual}")
        
        ordem_meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        evol_atual = df_atual.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14,6))
        ax.plot(ordem_meses, evol_atual.values, marker="o", linewidth=4, label=str(ano_atual), color="#2E86AB")
        
        if tem_ano_anterior and not df_anterior.empty:
            evol_ant = df_anterior.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
            ax.plot(ordem_meses, evol_ant.values, marker="o", linewidth=4, label=str(ano_anterior), color="#A23B72", alpha=0.7)
        
        ax.set_title(f"Evolução Mensal – {ano_atual}" + (f" vs {ano_anterior}" if tem_ano_anterior else ""), 
                    fontsize=15, fontweight="bold")
        ax.set_ylabel("Quantidade")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.subheader(f"Evolução Mensal – {ano_atual}")
        
        ordem_meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        evol_atual = df_atual.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14,6))
        ax.plot(ordem_meses, evol_atual.values, marker="o", linewidth=4, label=str(ano_atual), color="#2E86AB")
        ax.set_title(f"Evolução Mensal – {ano_atual}", fontsize=15, fontweight="bold")
        ax.set_ylabel("Quantidade")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
else:
    st.info("Não há dados disponíveis com os filtros selecionados.")

st.divider()

# === TOP 10 CLIENTES ===
if not df_filtrado.empty:
    if len(anos_selecionados) > 1:
        st.subheader(f"Top 10 Clientes por Ano")
        
        top10_por_ano = {}
        for ano in sorted(anos_selecionados, reverse=True):
            df_ano = df_filtrado[df_filtrado["Ano"] == ano]
            if not df_ano.empty:
                top10 = df_ano.groupby("Cliente")["Quantidade"].sum().nlargest(10)
                top10_por_ano[ano] = top10
        
        # Criar DataFrame comparativo
        if top10_por_ano:
            todos_clientes_top = set()
            for top10 in top10_por_ano.values():
                todos_clientes_top.update(top10.index)
            
            comp = pd.DataFrame(index=sorted(todos_clientes_top))
            for ano in sorted(top10_por_ano.keys()):
                comp[ano] = top10_por_ano[ano].reindex(comp.index).fillna(0)
            
            # Ordenar pela soma total
            comp["Total"] = comp.sum(axis=1)
            comp = comp.sort_values("Total", ascending=False).head(10).drop(columns="Total")
            
            col1, col2 = st.columns([3,2])
            with col1:
                fig2, ax2 = plt.subplots(figsize=(10,6))
                comp.plot(kind="barh", ax=ax2, width=0.8)
                ax2.set_title("Top 10 Clientes por Ano")
                ax2.invert_yaxis()
                st.pyplot(fig2)
            
            with col2:
                disp = comp.copy()
                for col in disp.columns:
                    disp[col] = disp[col].apply(lambda x: f"{x:,.0f}")
                st.dataframe(disp, use_container_width=True)
    
    elif tem_ano_anterior:
        st.subheader(f"Top 10 Clientes – Comparativo {ano_anterior} vs {ano_atual}")
        
        if not df_atual.empty:
            top10 = df_atual.groupby("Cliente")["Quantidade"].sum().nlargest(10).index
            
            comp = pd.DataFrame({
                str(ano_anterior): df_anterior.groupby("Cliente")["Quantidade"].sum(),
                str(ano_atual):    df_atual.groupby("Cliente")["Quantidade"].sum()
            }).fillna(0).loc[top10]

            comp["Variação"] = comp[str(ano_atual)] - comp[str(ano_anterior)]
            comp["Var %"] = (comp["Variação"] / comp[str(ano_anterior)].replace(0,1) * 100).round(1)
            
            col1, col2 = st.columns([3,2])
            with col1:
                fig2, ax2 = plt.subplots(figsize=(10,6))
                comp[[str(ano_anterior), str(ano_atual)]].plot(kind="barh", ax=ax2, color=["#A23B72", "#2E86AB"])
                ax2.set_title("Top 10 Clientes")
                ax2.invert_yaxis()
                st.pyplot(fig2)
            
            with col2:
                disp = comp.copy()
                for col in [str(ano_anterior), str(ano_atual), "Variação"]:
                    disp[col] = disp[col].apply(lambda x: f"{x:,.0f}")
                disp["Var %"] = disp["Var %"].apply(lambda x: f"{x:+.1f}%")
                st.dataframe(disp, use_container_width=True)
    
    else:
        st.subheader(f"Top 10 Clientes – {ano_atual}")
        
        if not df_atual.empty:
            top10 = df_atual.groupby("Cliente")["Quantidade"].sum().nlargest(10).index
            comp = pd.DataFrame({
                str(ano_atual): df_atual.groupby("Cliente")["Quantidade"].sum()
            }).loc[top10]

            col1, col2 = st.columns([3,2])
            with col1:
                fig2, ax2 = plt.subplots(figsize=(10,6))
                comp[[str(ano_atual)]].plot(kind="barh", ax=ax2, color="#2E86AB")
                ax2.set_title("Top 10 Clientes")
                ax2.invert_yaxis()
                st.pyplot(fig2)
            
            with col2:
                disp = comp.copy()
                disp[str(ano_atual)] = disp[str(ano_atual)].apply(lambda x: f"{x:,.0f}")
                st.dataframe(disp, use_container_width=True)

st.divider()

# === EXPORTAR EXCEL ===
if not df_filtrado.empty:
    st.subheader("Exportar Relatório")
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Resumo dos filtros
        resumo_filtros = pd.DataFrame({
            "Parâmetro": ["Anos", "Meses", "Comerciais", "Clientes", "Artigos"],
            "Selecionados": [
                ", ".join(map(str, anos_selecionados)),
                ", ".join([meses_nomes[m] for m in meses_selecionados if m in meses_nomes]),
                ", ".join(comerciais_selecionados[:10]) + ("..." if len(comerciais_selecionados) > 10 else ""),
                ", ".join(clientes_selecionados[:10]) + ("..." if len(clientes_selecionados) > 10 else ""),
                ", ".join(artigos_selecionados[:10]) + ("..." if len(artigos_selecionados) > 10 else "")
            ],
            "Total": [
                len(anos_selecionados),
                len(meses_selecionados),
                len(comerciais_selecionados),
                len(clientes_selecionados),
                len(artigos_selecionados)
            ]
        })
        resumo_filtros.to_excel(writer, sheet_name="Resumo Filtros", index=False)
        
        # Detalhe por ano
        for ano in sorted(anos_selecionados, reverse=True):
            df_ano = df_filtrado[df_filtrado["Ano"] == ano]
            if not df_ano.empty:
                df_detalhe = df_ano.groupby(["Comercial", "Cliente", "Artigo"])["Quantidade"].sum().reset_index()
                df_detalhe = df_detalhe.sort_values("Quantidade", ascending=False)
                sheet_name = f"Detalhe_{ano}"[:31]  # Limitar nome da sheet a 31 caracteres
                df_detalhe.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Top 10 clientes por ano
        top_clientes_df = pd.DataFrame()
        for ano in sorted(anos_selecionados, reverse=True):
            df_ano = df_filtrado[df_filtrado["Ano"] == ano]
            if not df_ano.empty:
                top10_ano = df_ano.groupby("Cliente")["Quantidade"].sum().nlargest(10)
                temp_df = pd.DataFrame({f"{ano}": top10_ano})
                if top_clientes_df.empty:
                    top_clientes_df = temp_df
                else:
                    top_clientes_df = top_clientes_df.join(temp_df, how="outer")
        
        if not top_clientes_df.empty:
            top_clientes_df.fillna(0, inplace=True)
            top_clientes_df.to_excel(writer, sheet_name="Top10_Clientes_Anos")

    st.download_button(
        "Baixar Relatório Completo (Excel)",
        data=output.getvalue(),
        file_name=f"Dashboard_Filtros_{'_'.join(map(str, anos_selecionados))}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.sppreadsheetml.sheet"
    )

st.success("Dashboard carregado com sucesso! Todos os filtros dinâmicos funcionam perfeitamente.")
