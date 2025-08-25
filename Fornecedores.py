import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime
import numpy as np

# Set page configuration for a wide layout and custom title
st.set_page_config(page_title="Fornecedores Debt Viewer", layout="wide", page_icon="📊")

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
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame th {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
        padding: 10px;
    }
    .stDataFrame td {
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    .stDataFrame tr:nth-child(even) {
        background-color: #f9fafb;
    }
    .stDataFrame tr:hover {
        background-color: #e6f0fa;
    }
    .summary-box {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .summary-box p {
        margin: 5px 0;
        font-size: 16px;
        color: #1e3a8a;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def download_excel_file(url):
    """Download and read an Excel file from a URL."""
    try:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status
        # Read the Excel file
        df = pd.read_excel(io.BytesIO(response.content))
        
        # Log column names for debugging
        st.write("Columns in Excel file:", df.columns.tolist())
        
        # Check if 'Data Venc' exists
        if 'Data Venc' not in df.columns:
            st.error("Column 'Data Venc' not found in the Excel file. Available columns: " + ", ".join(df.columns))
            return None
        
        # Process 'Data Venc' column
        if not pd.api.types.is_datetime64_any_dtype(df['Data Venc']):
            if df['Data Venc'].dtype in [np.float64, np.int64]:
                # Convert Excel serial dates
                df['Data Venc'] = pd.to_datetime(df['Data Venc'].apply(lambda x: pd.Timestamp('1899-12-30') + pd.Timedelta(days=x) if pd.notnull(x) else x))
            else:
                # Convert string dates
                df['Data Venc'] = pd.to_datetime(df['Data Venc'], errors='coerce')
        
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to download Excel file from URL: {e}")
        return None
    except pd.errors.ParserError as e:
        st.error(f"Failed to parse Excel file: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error while processing Excel file: {e}")
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
            if username == "paulo" and password == "teste":
                st.session_state["logged_in"] = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")

        # Filters (visible only after login)
        if st.session_state.get("logged_in", False):
            st.header("Filters")
            # Load Excel data from Dropbox for filter options
            url = "https://www.dropbox.com/scl/fi/378p5bzv5oejc9e2omvp5/Fornecedores_Deb.xlsx?rlkey=e27iy6mdtadqlxnrr2fn220r1&st=y76pe09o&dl=1"
            df = download_excel_file(url)
            if df is not None:
                # Entidade filter
                if "Entidade " in df.columns:
                    entidades = ["All"] + sorted(df["Entidade "].dropna().unique().tolist())
                    selected_entidade = st.selectbox("Select Entidade", entidades, index=0)
                else:
                    st.warning("Column 'Entidade ' not found in Excel file.")
                    selected_entidade = "All"

                # Date range filter for Data Venc
                st.subheader("Select Date Range")
                min_date = df["Data Venc"].min().date() if df is not None and not df["Data Venc"].empty else datetime(2023, 1, 1)
                max_date = df["Data Venc"].max().date() if df is not None and not df["Data Venc"].empty else datetime.today()
                start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
                end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
            else:
                selected_entidade, start_date, end_date = "All", None, None

    # Main content
    st.title("Fornecedores Bracar")
    
    if st.session_state.get("logged_in", False):
        # Load Excel data from Dropbox
        url = "https://www.dropbox.com/scl/fi/378p5bzv5oejc9e2omvp5/Fornecedores_Deb.xlsx?rlkey=e27iy6mdtadqlxnrr2fn220r1&st=y76pe09o&dl=1"
        df = download_excel_file(url)
        if df is not None:
            # Apply filters
            filtered_df = df[["Entidade ", "Data Venc", "Dias", "Valor Pendente"]].copy()
            if selected_entidade != "All" and "Entidade " in df.columns:
                filtered_df = filtered_df[filtered_df["Entidade "] == selected_entidade]
            if start_date and end_date:
                try:
                    filtered_df = filtered_df[
                        (filtered_df["Data Venc"] >= pd.to_datetime(start_date)) &
                        (filtered_df["Data Venc"] <= pd.to_datetime(end_date))
                    ]
                except Exception as e:
                    st.error(f"Error filtering by date: {e}")

            st.subheader("Dados Filtrados")
            # Format Data Venc for display
            filtered_df["Data Venc"] = filtered_df["Data Venc"].dt.strftime("%Y-%m-%d")
            # Format Valor Pendente as currency
            filtered_df["Valor Pendente"] = filtered_df["Valor Pendente"].apply(lambda x: f"€{x:,.2f}")
            # Display DataFrame with custom styling
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={
                    "Entidade ": st.column_config.TextColumn("Entidade", width="large"),
                    "Data Venc": st.column_config.TextColumn("Due Date", width="medium"),
                    "Dias": st.column_config.NumberColumn("Days", width="small", format="%d"),
                    "Valor Pendente": st.column_config.TextColumn("Pending Value", width="medium")
                }
            )

            # Summary section
            if not filtered_df.empty:
                total_valor_pendente = filtered_df["Valor Pendente"].str.replace("€", "").str.replace(",", "").astype(float).sum()
                num_records = len(filtered_df)
                st.markdown("### Sumario")
                st.markdown(
                    f"""
                    <div class="summary-box">
                        <p><strong>Total Valor Pendente:</strong> €{total_valor_pendente:,.2f}</p>
                        <p><strong>Number of Records:</strong> {num_records}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("No data available for the selected filters.")
    else:
        st.info("Please log in to view the supplier debt data.")

if __name__ == "__main__":
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    main()
