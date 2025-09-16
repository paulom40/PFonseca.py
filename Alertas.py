import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Vendas Dashboard", layout="wide", page_icon="📊")

# Session state for login and sidebar toggle
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_filters' not in st.session_state:
    st.session_state.show_filters = True

# Login credentials
credentials = {
    "admin": "password123",
    "paulo": "teste",
    "user2": "dashboard456"
}

# Login page
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

# Dashboard page
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

    # Ranges
    ranges = [
        (0, 15, "0 a 15 dias 🟦"),
        (16, 30, "16 a 30 dias 🟫"),
        (31, 60, "31 a 60 dias 🟧"),
        (61, 90, "61 a 90 dias 🟨"),
        (91, 365, "91 a 365 dias 🟥")
    ]

    # Toggle filter panel
    toggle_label = "🔽 Hide Filters" if st.session_state.show_filters else "🔼 Show Filters"
    if st.button(toggle_label):
        st.session_state.show_filters = not st.session_state.show_filters

    # Filters panel
    if st.session_state.show_filters:
        with st.container():
            st.subheader("🎨 Filters")
            selected_comercial = st.multiselect("👨‍💼 Comercial", sorted(df['Comercial'].unique()), default=sorted(df['Comercial'].unique()))
            selected_entidade = st.multiselect("🏢 Entidade", sorted(df['Entidade'].unique()), default=sorted(df['Entidade'].unique()))
            selected_ranges = st.multiselect("📅 Ranges", [r[2] for r in ranges], default=[r[2] for r in ranges])
    else:
        # Use default filters when hidden
        selected_comercial = sorted(df['Comercial'].unique())
        selected_entidade = sorted(df['Entidade'].unique())
        selected_ranges = [r[2] for r in ranges]

    # Filter data
    filtered_df = df[
        df['Comercial'].isin(selected_comercial) &
        df['Entidade'].isin(selected_entidade)
    ]

    # Summary
    st.subheader("📋 Summary")
    summary = []
    for low, high, label in ranges:
        if label in selected_ranges:
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            summary.append({
                "Range": label,
                "Count": len(range_df),
                "Total Pending": range_df['Valor Pendente'].sum()
            })
    if summary:
        st.dataframe(pd.DataFrame(summary))
    else:
        st.warning("⚠️ No data in selected ranges")

    # Details
    for low, high, label in ranges:
        if label in selected_ranges:
            st.subheader(label)
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            if not range_df.empty:
                st.dataframe(range_df)
            else:
                st.info("⚠️ No alerts in this range")

    # Logout
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# App logic
if st.session_state.logged_in:
    dashboard_page()
else:
    login_page()
