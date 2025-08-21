import streamlit as st
import pandas as pd

# --- Simple login system ---
users = {
    "paulojt": "yourpassword",
    "guest": "guest123"
}

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.sidebar.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --- Load Excel from GitHub ---
url = "https://github.com/paulom40/PFonseca.py/raw/main/Perc2025_Com.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(url)
    return df

df = load_data()

# --- Format and Display ---
st.title("📊 2025 Percentage Dashboard")
st.write(f"Welcome, **{st.session_state['username']}**!")

# Format numeric columns as percentages
for col in df.select_dtypes(include='number').columns:
    df[col] = df[col].apply(lambda x: f"{x:.2%}")

st.dataframe(df, use_container_width=True)
