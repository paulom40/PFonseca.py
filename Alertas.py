import streamlit as st
import pandas as pd
from io import BytesIO
import uuid

# 🚀 Page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# Custom CSS for colorful and stylish design
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        padding: 20px;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #ffffff 0%, #e6f3ff 100%);
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #ffffff;
        text-align: center;
        font-family: 'Poppins', sans-serif;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.3);
        font-size: 2.5em;
    }
    h2 {
        color: #2c3e50;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }
    h3 {
        color: #e91e63;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    .stDataFrame {
        border: 2px solid #ff8a65;
        border-radius: 12px;
        padding: 15px;
        background-color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff6b6b 0%, #ff8a65 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #e55d5d 0%, #e07b5a 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    .login-card {
        background: linear-gradient(145deg, #ffffff 0%, #f0f4f8 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        max-width: 450px;
        margin: 0 auto;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .login-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
    }
    .stTextInput input {
        border: 2px solid #ff8a65;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
        transition: all 0.3s ease;
        background-color: #f9f9f9;
    }
    .stTextInput input:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 8px rgba(255, 107, 107, 0.3);
        outline: none;
        background-color: #ffffff;
    }
    .login-title {
        color: #2c3e50;
        font-size: 28px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        margin-bottom: 30px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    .error-message {
        color: #d32f2f;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        margin-top: 10px;
    }
    .success-message {
        color: #2ecc71;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        margin-top: 10px;
    }
    .logo {
        display: block;
        margin: 0 auto 20px auto;
        border-radius: 10px;
        transition: transform 0.3s ease;
    }
    .logo:hover {
        transform: scale(1.1);
    }
    @media (max-width: 600px) {
        .login-card {
            padding: 20px;
            max-width: 90%;
        }
        .login-title {
            font-size: 24px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Hardcoded credentials (for demo purposes; use a secure database in production)
credentials = {
    "admin": "password123",
    "paulo": "teste",
    "user2": "dashboard456"
}

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login page
def login_page():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=150, caption="", use_container_width=False, output_format="PNG")
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

# Dashboard page
def dashboard_page():
    # URL to the Excel file
    url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"

    # Load the data
    try:
        df = pd.read_excel(url)
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

    # Ensure 'Dias' is numeric
    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')

    # Drop rows with NaN in 'Dias'
    df = df.dropna(subset=['Dias'])

    # Define the ranges and labels with colorful emojis
    ranges = [
        (-700, -40, "-700 to -40 dias 🟫"),
        (-40, -30, "30-40 dias 🟥"),
        (-30, -20, "20-30 dias 🟧"),
        (-20, -10, "10-20 dias 🟨"),
        (-10, 0, "0-10 dias 🟩"),
        (0, 10, "0-10 dias 🟦")
    ]

    # Sidebar for filters
    st.sidebar.markdown("### 🎨 Filters")
    st.sidebar.markdown("---")

    # Filter by Comercial
    unique_comercial = sorted(df['Comercial'].unique())
    selected_comercial = st.sidebar.multiselect("👨‍💼 Select Comercial", unique_comercial, default=unique_comercial)

    # Filter by Entidade
    unique_entidade = sorted(df['Entidade'].unique())
    selected_entidade = st.sidebar.multiselect("🏢 Select Entidade", unique_entidade, default=unique_entidade)

    # Filter by Ranges
    range_labels = [label for _, _, label in ranges]
    selected_ranges = st.sidebar.multiselect("📅 Select Ranges", range_labels, default=range_labels)

    # Filter the dataframe based on selections
    filtered_df = df[
        (df['Comercial'].isin(selected_comercial)) &
        (df['Entidade'].isin(selected_entidade))
    ]

    # Title with emoji
    st.markdown("<h1>📊 Alertas Vencimentos</h1>", unsafe_allow_html=True)

    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Summary data
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

    # Display summary table
    st.markdown("<h2>📋 Summary</h2>", unsafe_allow_html=True)
    if summary:
        summary_df = pd.DataFrame(summary)
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.markdown("⚠️ No data in selected ranges", unsafe_allow_html=True)

    # Display details for each range
    for low, high, label in ranges:
        if label in selected_ranges:
            st.markdown(f"<h3>{label}</h3>", unsafe_allow_html=True)
            range_filtered = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] < high)]
            if not range_filtered.empty:
                st.dataframe(range_filtered, use_container_width=True)
            else:
                st.markdown(f"⚠️ No alerts in this range", unsafe_allow_html=True)

    # Download filtered data as Excel
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
    else:
        st.markdown("⚠️ No data available to download", unsafe_allow_html=True)

    # Logout button
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #ffffff;'>Created with ❤️ using Streamlit</p>", unsafe_allow_html=True)

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()
