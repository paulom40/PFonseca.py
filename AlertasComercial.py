import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import io
from io import BytesIO

# Page config
st.set_page_config(page_title="Due Invoices Summary", layout="wide")

# Title
st.title("Sum of Pending Values for Overdue Invoices")

# GitHub raw URL for the Excel file
github_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/V0808.xlsx"

# Load the Excel file from GitHub
@st.cache_data
def load_data():
    try:
        response = requests.get(github_url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")
        return df
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return None

df = load_data()

if df is not None:
    # Display raw data info
    st.subheader("Raw Data Preview")
    st.dataframe(df.head())
    
    # Convert relevant columns to numeric
    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df['Valor Pendente'] = pd.to_numeric(df['Valor Pendente'], errors='coerce')
    
    # Calculate days overdue: if Dias <=0, overdue by -Dias
    df['Days_Overdue'] = (-df['Dias']).clip(lower=0)  # Non-negative days overdue
    
    # Filter overdue invoices (Dias <= 0) and positive pending values
    overdue_df = df[(df['Dias'] <= 0) & (df['Valor Pendente'] > 0)].copy()
    
    summary = pd.DataFrame()
    total_overdue = 0
    
    if not overdue_df.empty:
        # Group by Entidade and Comercial, sum Valor Pendente, max Days_Overdue
        summary = overdue_df.groupby(['Entidade', 'Comercial']).agg({
            'Valor Pendente': 'sum',
            'Days_Overdue': 'max'
        }).reset_index()
        summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
        summary = summary.rename(columns={'Days_Overdue': 'Max Days Overdue'})
        
        # Display overall summary
        st.subheader("Overall Summary: Sum of Valor Pendente by Entidade and Comercial (Overdue)")
        st.dataframe(summary)
        
        # Total overdue amount
        total_overdue = summary['Valor Pendente'].sum()
        st.metric("Total Overdue Amount", f"€{total_overdue:,.2f}")
        
        # Resume Table: Filtered by Comercial
        st.subheader("Resume Table: Filtered by Comercial")
        comerciais = sorted(summary['Comercial'].unique())
        selected_comercial = st.selectbox("Select Comercial for Resume", ["All"] + list(comerciales))
        
        if selected_comercial == "All":
            filtered_summary = summary[['Comercial', 'Entidade', 'Valor Pendente', 'Max Days Overdue']]
            st.write("Showing all data")
        else:
            filtered_summary = summary[summary['Comercial'] == selected_comercial][['Comercial', 'Entidade', 'Valor Pendente', 'Max Days Overdue']]
            st.write(f"**Selected Comercial: {selected_comercial}**")
        
        st.dataframe(filtered_summary)
        
        # Sub total for selected
        sub_total = filtered_summary['Valor Pendente'].sum()
        st.metric("Sub Total", f"€{sub_total:,.2f}")
    else:
        st.warning("No overdue invoices found.")
    
    # Email section - always available
    st.subheader("Send Summary via Email (Per Commercial)")
    sender_email = st.text_input("Sender Email", value="your_email@example.com")
    sender_password = st.text_input("Sender Password", type="password")
    receiver_email = st.text_input("Receiver Email", value="recipient@example.com")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    
    if st.button("Send Emails Per Commercial"):
        try:
            if summary.empty:
                # Send a single email if no data
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = "Overdue Invoices Summary - No Overdue Invoices"
                
                body = """
Dear Recipient,

No overdue invoices found at this time.

Best regards,
Streamlit App
"""
                msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                text = msg.as_string()
                server.sendmail(sender_email, receiver_email, text)
                server.quit()
                
                st.success("Email sent: No overdue invoices.")
            else:
                # Group by Comercial
                commercial_groups = summary.groupby('Comercial')
                
                for comercial, group in commercial_groups:
                    sub_total = group['Valor Pendente'].sum()
                    
                    # Prepare email for this commercial
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['Subject'] = f"Overdue Invoices Summary for {comercial} - Total: €{sub_total:,.2f}"
                    
                    # Email body
                    body = f"""
Dear Recipient,

Please find the summary of overdue invoices for {comercial} below:

{group[['Entidade', 'Valor Pendente', 'Max Days Overdue']].to_string(index=False)}

Total for {comercial}: €{sub_total:,.2f}

Best regards,
Streamlit App
"""
                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Attach CSV for this commercial
                    csv_buffer = io.StringIO()
                    group.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    attachment = MIMEApplication(csv_buffer.getvalue(), _subtype="csv")
                    attachment.add_header('Content-Disposition', 'attachment', filename=f'overdue_summary_{comercial.replace(" ", "_")}.csv')
                    msg.attach(attachment)
                    
                    # Send email
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    text = msg.as_string()
                    server.sendmail(sender_email, receiver_email, text)
                    server.quit()
                
                st.success(f"Emails sent successfully for {len(commercial_groups)} commercials!")
                
        except Exception as e:
            st.error(f"Error sending emails: {str(e)}")
else:
    st.info("Unable to load the Excel file. Please check the GitHub link.")
