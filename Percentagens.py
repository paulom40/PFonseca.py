import streamlit as st
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# --- Login System ---
users = {
    "paulojt": "yourpassword",
    "guest": "guest123",
    "paulo": "teste"
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

# --- Refresh Button ---
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()

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

# --- Comercial Filter ---
if "Comercial" in df.columns:
    comercial_options = df["Comercial"].dropna().unique().tolist()
    selected_comercial = st.sidebar.multiselect("🏷️ Comercial", comercial_options, default=comercial_options)
else:
    selected_comercial = []

if selected_mes and mes_column:
    filtered_df = filtered_df[filtered_df[mes_column].astype(str).isin(selected_mes)]


# --- Apply Filters ---
filtered_df = df.copy()

for col, (min_val, max_val) in filters.items():
    filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]

if selected_comercial:
    filtered_df = filtered_df[filtered_df["Comercial"].isin(selected_comercial)]

if selected_mes:
    filtered_df = filtered_df[filtered_df["Mes"].isin(selected_mes)]

# --- Create Numeric Copy for Charting ---
numeric_df = filtered_df.copy()
for col in filter_columns:
    if col in numeric_df.columns:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')

# --- Format Percentages for Display ---
for col in filtered_df.select_dtypes(include='number').columns:
    if col != "Ano":
        filtered_df[col] = filtered_df[col].apply(lambda x: f"{x:.2%}")

# --- Display Data ---
st.title("📈 2025 Percentage Dashboard")
st.write(f"Bem vindo, **{st.session_state['username']}**!")
st.dataframe(filtered_df, use_container_width=True)

# --- Heatmap Chart: Sorted from High to Low (Top to Bottom) ---
st.subheader("🔥 Heatmap de Percentagens por Comercial (Top → Bottom)")

if "Comercial" in numeric_df.columns:
    comercial_avg = numeric_df.groupby("Comercial")[filter_columns].mean()

    # Sort Comerciais by total average percentage descending
    comercial_avg["Total"] = comercial_avg.sum(axis=1)
    comercial_avg = comercial_avg.sort_values("Total", ascending=False).drop(columns="Total")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        comercial_avg,
        annot=True,
        fmt=".2%",
        cmap="Reds",
        linewidths=0.5,
        linecolor='white',
        ax=ax
    )

    ax.set_title("Comparação de Categorias por Comercial (Ordenado de Cima para Baixo)", fontsize=14)
    st.pyplot(fig)



# --- Download Button ---
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    return output.getvalue()

excel_data = to_excel(filtered_df)

st.download_button(
    label="📥 Download filtered data as Excel",
    data=excel_data,
    file_name="filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
