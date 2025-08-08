import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import requests
from io import BytesIO

# Setting page configuration to wide mode
st.set_page_config(layout="wide")

# Title of the application
st.title("Sales Data Analysis Dashboard")

# Reading the Excel data from URL
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/1semestrePM.xlsx"
    response = requests.get(url)
    if response.status_code == 200:
        # Load Excel file from the response content
        data = pd.read_excel(BytesIO(response.content))
        
        # Rename 'Data' column to 'Date' if it exists
        if "Data" in data.columns:
            data = data.rename(columns={"Data": "Date"})
        
        # Cleaning and processing data
        data["Quantidade"] = pd.to_numeric(data["Quantidade"], errors="coerce")
        data["PM"] = pd.to_numeric(data["PM"], errors="coerce")
        data["V Líquido"] = pd.to_numeric(data["V Líquido"], errors="coerce")
        
        # Clean and convert "Date" column to numeric, handling invalid entries
        data["Date"] = pd.to_numeric(data["Date"], errors="coerce")
        
        # Convert valid Excel serial dates to datetime, filtering out-of-bounds values
        def convert_serial_date(x):
            if pd.notnull(x):
                # Limit to reasonable date range (e.g., 1900 to 2100)
                # Excel serial date 1 = 1900-01-01, 73048 ≈ 2100-01-01
                if 1 <= x <= 73048:
                    try:
                        return pd.to_datetime("1899-12-30") + pd.Timedelta(days=x)
                    except (ValueError, OverflowError):
                        return pd.NaT
                else:
                    return pd.NaT
            return pd.NaT
        
        data["Date"] = data["Date"].apply(convert_serial_date)
        
        # Extract week number for valid dates
        data["Week"] = data["Date"].dt.isocalendar().week.where(data["Date"].notnull(), np.nan)
        
        # Handling missing values in critical columns
        data = data.dropna(subset=["Quantidade", "PM", "Mês", "Ano", "Artigo"])
        
        return data
    else:
        st.error("Failed to load data from URL")
        return pd.DataFrame()

# Loading data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Ano filter
anos = sorted(df["Ano"].unique()) if not df.empty else []
selected_ano = st.sidebar.selectbox("Select Ano", ["All"] + list(anos), index=0)

# Mês filter
meses = sorted(df["Mês"].unique()) if not df.empty else []
selected_mes = st.sidebar.selectbox("Select Mês", ["All"] + list(meses), index=0)

# Artigo filter
artigos = sorted(df["Artigo"].unique()) if not df.empty else []
selected_artigo = st.sidebar.selectbox("Select Artigo", ["All"] + list(artigos), index=0)

# Filtering data
filtered_df = df.copy()
if selected_ano != "All":
    filtered_df = filtered_df[filtered_df["Ano"] == selected_ano]
if selected_mes != "All":
    filtered_df = filtered_df[filtered_df["Mês"] == selected_mes]
if selected_artigo != "All":
    filtered_df = filtered_df[filtered_df["Artigo"] == selected_artigo]

# KPIs
st.header("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

# Average PM
avg_pm = filtered_df["PM"].mean() if not filtered_df.empty else 0
col1.metric("Average PM", f"{avg_pm:.2f}")

# Average Quantidade by Month
avg_qty_month = filtered_df.groupby("Mês")["Quantidade"].mean().mean() if not filtered_df.empty else 0
col2.metric("Average Quantidade by Month", f"{avg_qty_month:.2f}")

# Average Quantidade by Week
avg_qty_week = filtered_df.groupby("Week")["Quantidade"].mean().mean() if not filtered_df.empty else 0
col3.metric("Average Quantidade by Week", f"{avg_qty_week:.2f}")

# Displaying the filtered data table
st.header("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)
