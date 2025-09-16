import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Vendas Dashboard", layout="wide", page_icon="📊")

# 🔒 Hardcoded credentials (demo only)
credentials = {
    "admin": "password123",
    "paulo": "teste",
    "user2": "dashboard456"
}

# 🧠 Session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 🎨 Custom CSS
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .main {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        padding: 20px;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
        border-radius: 10px;
        padding: 20px;
    }
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
    }
    h1 {
        color: #ffffff;
        text-align: center;
        font-size: 2.5em;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff6b6b, #ff8a65);
        color: white;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    .login-card {
        background: #f0f4f8;
        padding: 40px;
        border-radius: 20px;
        max-width: 450px;
        margin: auto;
        text-align: center;
    }
    .login-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 30px;
    }
    .error-message {
        color: #d32f2f;
        font-weight: 600;
    }
    .success-message {
        color: #2ecc71;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 🔐 Login page
def login_page():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=150)
    st.markdown("<h2 class='login-title'>🔐 Login to Sales Dashboard</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login 🚀"):
        if credentials.get(username) == password:
            st.session_state.logged_in = True
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True)

# 📊 Dashboard page
def dashboard_page():
    st.markdown("<h1>📊 Alertas Vencimentos</h1>", unsafe_allow_html=True)

    # Load Excel data
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
    st.sidebar.header("🎨 Filters")
    selected_comercial = st.sidebar.multiselect("👨‍💼 Comercial", sorted(df['Comercial'].unique()), default=sorted(df['Comercial'].unique()))
    selected_entidade = st.sidebar.multiselect("🏢 Entidade", sorted(df['Entidade'].unique()), default=sorted(df['Entidade'].unique()))
    selected_ranges = st.sidebar.multiselect("📅 Ranges", [r[2] for r in ranges], default=[r[2] for r in ranges])

    # Filter data
    filtered_df = df[
        df['Comercial'].isin(selected_comercial) &
        df['Entidade'].isin(selected_entidade)
    ]

    # 🔄 Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # 📋 Summary
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

    # 📂 Detailed tables
    for low, high, label in ranges:
        if label in selected_ranges:
            st.subheader(label)
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            if not range_df.empty:
                st.dataframe(range_df)
            else:
                st.info("⚠️ No alerts in this range")

    # 📥 Download filtered data
    if not filtered_df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Filtered_Data')
        st.download_button(
            label="📥 Download Filtered Data as Excel",
            data=output.getvalue(),
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No data available to download")

    # 🔓 Logout
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ❤️ Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #ffffff;'>Created with ❤️ using Streamlit</p>", unsafe_allow_html=True)

# 🧠 App logic
if st.session_state.logged_in:
    dashboard_page()
else:
    login_page()
