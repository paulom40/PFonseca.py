import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide", page_icon="📊")

# 🌌 Custom CSS for animated background and stylish login
st.markdown("""
    <style>
    body {
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    .main {
        background: linear-gradient(-45deg, #1f1c2c, #928dab, #2c3e50, #34495e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        padding: 20px;
        min-height: 100vh;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .sidebar .sidebar-content {
        background-color: #e6f3ff;
    }
    h1 {
        color: #ffffff;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    h2 {
        color: #2980b9;
        font-family: 'Segoe UI', sans-serif;
    }
    h3 {
        color: #e74c3c;
        font-family: 'Segoe UI', sans-serif;
    }
    .stDataFrame {
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .login-card {
        background: rgba(0, 0, 0, 0.7);
        padding: 40px;
        border-radius: 30px;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        max-width: 400px;
        margin: 60px auto;
        text-align: center;
        color: #ecf0f1;
        font-family: 'Segoe UI', sans-serif;
        animation: fadeIn 2s ease;
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    .login-title {
        color: #ffffff;
        font-size: 28px;
        margin-bottom: 25px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
    }
    .stTextInput input {
        background-color: #2c3e50;
        color: #ecf0f1;
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
        transition: border-color 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #2980b9;
        outline: none;
    }
    .error-message {
        color: #e74c3c;
        font-weight: bold;
        margin-top: 10px;
    }
    .success-message {
        color: #2ecc71;
        font-weight: bold;
        margin-top: 10px;
    }
    .logo {
        display: block;
        margin: 0 auto 20px auto;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# 🔐 Hardcoded credentials (demo only)
credentials = {
    "admin": "password123",
    "paulo": "teste",
    "user2": "dashboard456"
}

# 🔄 Session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 🔐 Login page
def login_page():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=150, caption="", use_container_width=False)
    st.markdown("<h2 class='login-title'>🔐 Login to Sales Dashboard</h2>", unsafe_allow_html=True)
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login 🚀"):
        if username in credentials and credentials[username] == password:
            st.session_state.logged_in = True
            st.markdown("<p class='success-message'>✅ Login successful! Redirecting...</p>", unsafe_allow_html=True)
            st.rerun()
        else:
            st.markdown("<p class='error-message'>❌ Invalid username or password. Please try again.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 📊 Dashboard page
def dashboard_page():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
    try:
        df = pd.read_excel(url)
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df = df.dropna(subset=['Dias'])

    ranges = [
        (-700, -40, "-700 to -40 dias 🟫"),
        (-40, -30, "30-40 dias 🟥"),
        (-30, -20, "20-30 dias 🟧"),
        (-20, -10, "10-20 dias 🟨"),
        (-10, 0, "0-10 dias 🟩"),
        (0, 10, "0-10 dias 🟦")
    ]

    st.sidebar.markdown("### 🎨 Filters")
    st.sidebar.markdown("---")
    unique_comercial = sorted(df['Comercial'].unique())
    selected_comercial = st.sidebar.multiselect("👨‍💼 Select Comercial", unique_comercial, default=unique_comercial)
    unique_entidade = sorted(df['Entidade'].unique())
    selected_entidade = st.sidebar.multiselect("🏢 Select Entidade", unique_entidade, default=unique_entidade)
    range_labels = [label for _, _, label in ranges]
    selected_ranges = st.sidebar.multiselect("📅 Select Ranges", range_labels, default=range_labels)

    filtered_df = df[
        (df['Comercial'].isin(selected_comercial)) &
        (df['Entidade'].isin(selected_entidade))
    ]

    st.markdown("<h1>📊 Alertas Vencimentos</h1>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Data"):
        st.rerun()

    summary = []
    for low, high, label in ranges:
        if label in selected_ranges:
            range_filtered = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] < high)]
            count = len(range_filtered)
            total_pending = range_filtered['Valor Pendente'].sum() if 'Valor Pendente' in df.columns else 0
            summary.append({
                "Range": label,
                "Count": count,
                "Total Pending": total_pending
            })

    st.markdown("<h2>📋 Summary</h2>", unsafe_allow_html=True)
    if summary:
        summary_df = pd.DataFrame(summary)
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.markdown("⚠️ No data in selected ranges", unsafe_allow_html=True)

    for low, high, label in ranges:
        if label in selected_ranges:
            st.markdown(f"<h3>{label}</h3>", unsafe_allow_html=True)
            range_filtered = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] < high)]
            if not range_filtered.empty:
                st.dataframe(range_filtered, use_container_width=True)
            else:
                st.markdown(f"⚠️ No alerts in this range", unsafe_allow_html=True)

    if not filtered_df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Filtered_Data')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 Download Filtered Data as Excel",
            data=excel_data,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button"
        )
