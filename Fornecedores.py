import streamlit as st
import pandas as pd
import requests
import io

# Set page configuration for a wide layout and custom title
st.set_page_config(page_title="Excel Data Viewer", layout="wide", page_icon="📊")

# Custom CSS for a modern, beautiful UI
st.markdown("""
    <style>
    .main { background-color: #f0f2f5; padding: 20px; }
    .sidebar .sidebar-content { background-color: #2c3e50; padding: 20px; color: white; }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .stTextInput>div>input {
        border-radius: 5px;
        padding: 8px;
    }
    .dataframe { border: none; border-radius: 5px; }
    h1, h2, h3 { color: #2c3e50; }
    .stAlert { border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

def download_excel_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_excel(io.BytesIO(response.content))
    except Exception as e:
        st.error(f"Failed to download or read Excel file: {e}")
        return None

def main():
    # Sidebar for login
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

    # Main content
    st.title("Excel Data Viewer")
    
    if st.session_state.get("logged_in", False):
        # Load and display Excel data
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Fornecedores_Deb.xlsx"
        df = download_excel_file(url)
        if df is not None:
            st.subheader("Data from Fornecedores_Deb.xlsx")
            # Display DataFrame with custom styling
            st.dataframe(
                df,
                use_container_width=True,
                column_config={col: st.column_config.Column(width="medium") for col in df.columns}
            )
    else:
        st.info("Please log in to view the Excel data.")

if __name__ == "__main__":
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    main()
```
