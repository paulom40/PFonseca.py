import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide", page_icon="📊")

# Custom CSS for colorful styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .sidebar .sidebar-content {
        background-color: #e6f3ff;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    h2 {
        color: #2980b9;
        font-family: 'Arial', sans-serif;
    }
    h3 {
        color: #e74c3c;
        font-family: 'Arial', sans-serif;
    }
    .stDataFrame {
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 10px;
    }
    .stTextInput input {
        border: 2px solid #3498db;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Hardcoded credentials (for demo purposes; use a secure database in production)
credentials = {
    "admin": "password123",
    "user1": "sales2025",
    "user2": "dashboard456"
}

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login page
def login_page():
    st.markdown("<h1>🔐 Login to Sales Dashboard</h1>", unsafe_allow_html=True)
    with st.form(key='login_form'):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button(label="Login 🚀")

        if submit_button:
            if username in credentials and credentials[username] == password:
                st.session_state.logged_in = True
                st.success("✅ Login successful! Welcome to the dashboard.")
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")

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
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Created with ❤️ using Streamlit</p>", unsafe_allow_html=True)

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()
