import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Vendas Dashboard", layout="wide", page_icon="📊")

# 🔒 Demo credentials
credentials = {
    "admin": "password123",
    "paulo": "teste",
    "user2": "dashboard456"
}

# 🧠 Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 🔐 Login page
def login_page():
    st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=150)
    st.title("🔐 Login to Sales Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login 🚀"):
        if credentials.get(username) == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

# 📊 Dashboard page
def dashboard_page():
    st.title("📊 Alertas Vencimentos")

    # Load data
    url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/V0808.xlsx"
    try:
        df = pd.read_excel(url)
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return

    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df.dropna(subset=['Dias'], inplace=True)

    # Define ranges
    ranges = [
        (0, 15, "0 a 15 dias 🟦"),
        (16, 30, "16 a 30 dias 🟫"),
        (31, 60, "31 a 60 dias 🟧"),
        (61, 90, "61 a 90 dias 🟨"),
        (91, 365, "91 a 365 dias 🟥")
    ]

    # 🎛️ Sidebar filters
    st.sidebar.header("🎨 Filtros")
    selected_comercial = st.sidebar.multiselect(
        "👨‍💼 Comercial",
        sorted(df['Comercial'].unique()),
        default=sorted(df['Comercial'].unique())
    )
    selected_entidade = st.sidebar.multiselect(
        "🏢 Entidade",
        sorted(df['Entidade'].unique()),
        default=sorted(df['Entidade'].unique())
    )
    selected_ranges = st.sidebar.multiselect(
        "📅 Intervalos de Dias",
        [r[2] for r in ranges],
        default=[r[2] for r in ranges]
    )

    # Filter data
    filtered_df = df[
        df['Comercial'].isin(selected_comercial) &
        df['Entidade'].isin(selected_entidade)
    ]

    # 🔄 Refresh
    if st.button("🔄 Atualizar Dados"):
        st.rerun()

    # 📋 Summary
    st.subheader("📋 Resumo")
    summary = []
    for low, high, label in ranges:
        if label in selected_ranges:
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            summary.append({
                "Intervalo": label,
                "Quantidade": len(range_df),
                "Valor Pendente": range_df['Valor Pendente'].sum()
            })
    if summary:
        st.dataframe(pd.DataFrame(summary))
    else:
        st.warning("⚠️ Nenhum dado nos intervalos selecionados")

    # 📂 Detalhes
    for low, high, label in ranges:
        if label in selected_ranges:
            st.subheader(label)
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            if not range_df.empty:
                st.dataframe(range_df)
            else:
                st.info("⚠️ Nenhum alerta neste intervalo")

    # 📥 Download
    if not filtered_df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
        st.download_button(
            label="📥 Baixar dados filtrados em Excel",
            data=output.getvalue(),
            file_name="dados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ Nenhum dado disponível para download")

    # 🔓 Logout
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ❤️ Footer
    st.markdown("---")
    st.markdown("<p style='text-align:center;'>Feito com ❤️ em Streamlit</p>", unsafe_allow_html=True)

# 🧠 App logic
if st.session_state.logged_in:
    dashboard_page()
else:
    login_page()
