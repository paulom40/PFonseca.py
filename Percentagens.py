import streamlit as st
import pandas as pd
import plotly.express as px
import io

# -------------------------------
# 🔐 Simple Login System
# -------------------------------
users = {
    "paulojt": "1234",
    "admin": "adminpass"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# -------------------------------
# 📊 Main App
# -------------------------------
st.title("📊 Análise de Vendas por Categoria")

# Upload Excel file
uploaded_file = st.file_uploader("📂 Carregue o ficheiro Excel", type=["xlsx"])

if uploaded_file:
    # Load and clean data
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Show available columns
    st.sidebar.subheader("📋 Colunas disponíveis")
    st.sidebar.write(df.columns.tolist())

    # Check for required columns
    if "Mes" in df.columns and "Ano" in df.columns:
        # Sidebar filters
        selected_mes = st.sidebar.multiselect("📅 Selecione o Mês", options=df["Mes"].dropna().unique())
        selected_ano = st.sidebar.multiselect("📆 Selecione o Ano", options=df["Ano"].dropna().unique())

        # Filter data
        filtered_df = df.copy()
        if selected_mes:
            filtered_df = filtered_df[filtered_df["Mes"].isin(selected_mes)]
        if selected_ano:
            filtered_df = filtered_df[filtered_df["Ano"].isin(selected_ano)]

        # Define categorias
        categorias = ["Congelados", "Frescos", "Leitão", "Peixe", "Transf"]
        available_categorias = [cat for cat in categorias if cat in filtered_df.columns]

        if available_categorias:
            # Melt data for visualization
            melted_df = filtered_df.melt(
                id_vars=["Mes", "Ano"],
                value_vars=available_categorias,
                var_name="Categoria",
                value_name="Valor"
            )

            # Plot chart
            fig = px.bar(
                melted_df,
                x="Mes",
                y="Valor",
                color="Categoria",
                barmode="group",
                facet_col="Ano",
                title="📈 Vendas por Categoria"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Export filtered data to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')
                writer.save()
                processed_data = output.getvalue()

            st.download_button(
                label="📥 Download dos dados filtrados em Excel",
                data=processed_data,
                file_name="dados_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ Nenhuma das categorias esperadas foi encontrada no ficheiro.")
    else:
        st.error("❌ As colunas 'Mes' e 'Ano' são obrigatórias no ficheiro.")
else:
    st.info("👆 Por favor, carregue um ficheiro Excel para começar.")
