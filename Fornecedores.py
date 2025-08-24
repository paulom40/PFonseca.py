import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# Set page configuration for a wide layout and custom title
st.set_page_config(page_title="Excel Data Viewer", layout="wide", page_icon="📊")

# Custom CSS for a vibrant, beautiful UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #e6f0fa 0%, #f6f8fc 100%);
        padding: 20px;
        border-radius: 10px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 20px;
        color: white;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #059669;
    }
    .stTextInput>div>input, .stSelectbox>div>select, .stDateInput>div>input {
        border-radius: 8px;
        padding: 10px;
        background-color: #ffffff;
        border: 1px solid #3b82f6;
    }
    .dataframe {
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        color: #1e3a8a;
        font-family: 'Segoe UI', sans-serif;
    }
    .stAlert {
        border-radius: 8px;
        background-color: #fef3c7;
        color: #92400e;
    }
    .css-1d391kg {  /* Streamlit sidebar title */
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

def download_excel_file(url):
    """Download and read an Excel file from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_excel(io.BytesIO(response.content))
    except Exception as e:
        st.error(f"Failed to download or read Excel file: {e}")
        return None

def main():
    # Sidebar for login and filters
    with st.sidebar:
        st.header("Login")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        login_button = st.button("Login")

        # Simple login logic (replace with real authentication in production)
        if login_button:
            if username == "admin" and password == "password":
                st.session_state["logged_in"] = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")

        # Filters (visible only after login)
        if st.session_state.get("logged_in", False):
            st.header("Filters")
            # Load Excel data for filter options
            url = "https://github.com/paulom40/PFonseca.py/raw/main/Fornecedores_Deb.xlsx"
            df = download_excel_file(url)
            if df is not None:
                # Entidade filter (assuming 'Entidade' column exists)
                if "Entidade" in df.columns:
                    entidades = ["All"] + sorted(df["Entidade"].unique().tolist())
                    selected_entidade = st.selectbox("Select Entidade", entidades, index=0)
                else:
                    st.warning("Column 'Entidade' not found in Excel file.")
                    selected_entidade = "All"

                # Date range filter (assuming a date column, e.g., 'Data')
                date_columns = df.select_dtypes(include=['datetime64', 'object']).columns
                date_column = next((col for col in date_columns if "data" in col.lower()), None)
                if date_column:
                    st.subheader("Select Date Range")
                    start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
                    end_date = st.date_input("End Date", value=datetime.today())
                else:
                    st.warning("No date column found in Excel file.")
                    start_date, end_date = None, None
            else:
                selected_entidade, start_date, end_date = "All", None, None

    # Main content
    st.title("Excel Data Viewer")
    
    if st.session_state.get("logged_in", False):
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Fornecedores_Deb.xlsx"
        df = download_excel_file(url)
        if df is not None:
            # Apply filters
            filtered_df = df.copy()
            if selected_entidade != "All" and "Entidade" in df.columns:
                filtered_df = filtered_df[filtered_df["Entidade"] == selected_entidade]
            if date_column and start_date and end_date:
                try:
                    filtered_df[date_column] = pd.to_datetime(filtered_df[date_column])
                    filtered_df = filtered_df[
                        (filtered_df[date_column] >= pd.to_datetime(start_date)) &
                        (filtered_df[date_column] <= pd.to_datetime(end_date))
                    ]
                except Exception as e:
                    st.error(f"Error filtering by date: {e}")

            st.subheader("Filtered Data from Fornecedores_Deb.xlsx")
            # Display DataFrame with custom styling
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={col: st.column_config.Column(width="medium") for col in filtered_df.columns}
            )
    else:
        st.info("Please log in to view the Excel data.")

if __name__ == "__main__":
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    main()
