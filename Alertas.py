import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# URL to the Excel file
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"

# Load the data
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# Ensure 'Dias' is numeric
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')

# Drop rows with NaN in 'Dias'
df = df.dropna(subset=['Dias'])

# Define the ranges and labels
ranges = [
    (-40, -30, "30-40 dias"),
    (-30, -20, "20-30 dias"),
    (-20, -10, "10-20 dias"),
    (-10, 0, "0-10 dias"),
    (0, 10, "0-10 dias")
]

# Sidebar for filters
st.sidebar.title("Filters")

# Filter by Comercial
unique_comercial = sorted(df['Comercial'].unique())
selected_comercial = st.sidebar.multiselect("Select Comercial", unique_comercial, default=unique_comercial)

# Filter by Entidade
unique_entidade = sorted(df['Entidade'].unique())
selected_entidade = st.sidebar.multiselect("Select Entidade", unique_entidade, default=unique_entidade)

# Filter by Ranges
range_labels = [label for _, _, label in ranges]
selected_ranges = st.sidebar.multiselect("Select Ranges", range_labels, default=range_labels)

# Filter the dataframe based on selections
filtered_df = df[
    (df['Comercial'].isin(selected_comercial)) &
    (df['Entidade'].isin(selected_entidade))
]

st.title("Alertas Vencimentos")

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
st.subheader("Summary")
if summary:
    summary_df = pd.DataFrame(summary)
    st.dataframe(summary_df)
else:
    st.write("No data in selected ranges")

# Display details for each range
for low, high, label in ranges:
    if label in selected_ranges:
        st.subheader(label)
        range_filtered = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] < high)]
        if not range_filtered.empty:
            st.dataframe(range_filtered)
        else:
            st.write("No alerts in this range")

# Download filtered data as Excel
if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtered_Data')
    excel_data = output.getvalue()
    st.download_button(
        label="Download Filtered Data as Excel",
        data=excel_data,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.write("No data available to download")
