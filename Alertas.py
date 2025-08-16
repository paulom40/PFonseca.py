import streamlit as st
import pandas as pd

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
    (-40, -30, "Overdue 30-40 days"),
    (-30, -20, "Overdue 20-30 days"),
    (-20, -10, "Overdue 10-20 days"),
    (-10, 0, "Overdue 0-10 days"),
    (0, 10, "Due in 0-10 days")
]

st.title("Invoice Aging Alerts")

# Summary data
summary = []

for low, high, label in ranges:
    filtered = df[(df['Dias'] >= low) & (df['Dias'] < high)]
    count = len(filtered)
    total_pending = filtered['Valor Pendente'].sum() if 'Valor Pendente' in df.columns else 0
    summary.append({
        "Range": label,
        "Count": count,
        "Total Pending": total_pending
    })

# Display summary table
st.subheader("Summary")
summary_df = pd.DataFrame(summary)
st.dataframe(summary_df)

# Display details for each range
for low, high, label in ranges:
    st.subheader(label)
    filtered = df[(df['Dias'] >= low) & (df['Dias'] < high)]
    if not filtered.empty:
        st.dataframe(filtered)
    else:
        st.write("No alerts in this range")
