with tab1:
    st.sidebar.header("🔍 Filtro por Comercial")
    comerciais = df['Comercial'].dropna().unique() if 'Comercial' in df.columns else []
    comercial_selecionado = st.sidebar.selectbox("Selecione o comercial", ["Todos"] + list(comerciais))

    if comercial_selecionado != "Todos":
        df = df[df['Comercial'] == comercial_selecionado]

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

    def resumo_por_semana(df_semana, titulo):
        st.subheader(titulo)
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

    tabela_por_entidade(df_week0, "📋 Semana 0")
    tabela_por_entidade(df_week1, "📋 Semana 1")
    tabela_por_entidade(df_week2, "📋 Semana 2")

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
with tab2:
    st.header("📆 Relatório Anual 2025 — Evolução Semanal por Entidade e Comercial")

    df_2025 = df[df[venc_col].dt.year == 2025].copy()
    df_2025["Semana"] = df_2025[venc_col].dt.isocalendar().week
    semana_limite = max(1, datetime.today().isocalendar().week - 2)

    df_detalhado = (
        df_2025[df_2025["Semana"] <= semana_limite]
        .groupby(["Semana", entidade_col, "Comercial"])[valor_pendente_col]
        .sum()
        .reset_index()
        .sort_values(by=["Semana", valor_pendente_col], ascending=[True, False])
    )

    media = df_detalhado[valor_pendente_col].mean()
    def destaque_maior(val):
        if isinstance(val, (int, float)) and val > media:
            return "background-color: #f8d7da; font-weight: bold"
        return ""

    st.dataframe(
        df_detalhado.style
        .format({valor_pendente_col: "€ {:,.2f}"})
        .applymap(destaque_maior, subset=[valor_pendente_col]),
        use_container_width=True
    )

    st.subheader("📊 Evolução Semanal do Valor Pendente (Total)")
    df_total_semana = df_detalhado.groupby("Semana")[valor_pendente_col].sum().reset_index()
    st.bar_chart(df_total_semana.set_index("Semana"))

    output_detalhado = io.BytesIO()
    with pd.ExcelWriter(output_detalhado, engine='xlsxwriter') as writer:
        df_detalhado.to_excel(writer, sheet_name='Evolução Semanal Detalhada', index=False)
        df_total_semana.to_excel(writer, sheet_name='Resumo Semanal Total', index=False)
    output_detalhado.seek(0)

    b64_detalhado = base64.b64encode(output_detalhado.read()).decode()
    href_detalhado = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_detalhado}" download="Relatorio_Anual_2025.xlsx">📥 Baixar Excel</a>'
    st.markdown(href_detalhado, unsafe_allow_html=True)
