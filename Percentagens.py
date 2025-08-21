import streamlit as st
import pandas as pd

# --- Login System ---
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

# --- Format "Ano" as integer ---
if "Ano" in df.columns:
    df["Ano"] = df["Ano"].astype(int)

# --- Sidebar Filters ---
st.sidebar.title("📊 Filter Percentages")

filter_columns = ["Congelados", "Frescos", "Leitão", "Peixe", "Transf"]
filters = {}

for col in filter_columns:
    if col in df.columns:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        filters[col] = st.sidebar.slider(
            f"{col} (%)", min_value=0.0, max_value=1.0,
            value=(min_val, max_val), step=0.01
        )

# --- Apply Filters ---
filtered_df = df.copy()
for col, (min_val, max_val) in filters.items():
    filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]

# --- Format Percentages ---
for col in filtered_df.select_dtypes(include='number').columns:
    if col != "Ano":
        filtered_df[col] = filtered_df[col].apply(lambda x: f"{x:.2%}")

# --- Display ---
st.title("📈 2025 Percentage Dashboard")
st.write(f"Welcome, **{st.session_state['username']}**!")
st.dataframe(filtered_df, use_container_width=True)
