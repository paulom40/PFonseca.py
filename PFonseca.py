import pandas as pd
import requests
from io import BytesIO

# ✅ Correct raw file URL based on your GitHub username and repo name
url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Venc_040725.xlsx"
df = pd.read_excel(url, sheet_name="PFonseca2")

try:
    response = requests.get(url)
    response.raise_for_status()  # Throws HTTPError if download fails

    # 📖 Load specified sheet from Excel
    df = pd.read_excel(BytesIO(response.content), sheet_name="PFonseca2")
    print("Data loaded successfully!")
    print(df.head())  # View the first few rows
except requests.exceptions.HTTPError as e:
    print(f"HTTP error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")




print("Fetching from:", url)


print("Fetching from:", url)

# 📊 Load and Prepare Data
url = "https://raw.githubusercontent.com/<paulom40>/PFonseca.py/main/Venc_040725.xlsx"
df = pd.read_excel(url, sheet_name="PFonseca2")

df.columns = df.columns.str.strip()

# 🔄 Convert 'Dias' to clean numeric format
df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
df = df.dropna(subset=["Dias"])
df["Dias"] = df["Dias"].astype(int)

# 📅 Convert 'Data venc.' to datetime
df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce", dayfirst=True)


# 📋 Show raw DataFrame (optional)
if True:  # Set to False to hide
    st.subheader("Tabela Completa")
    st.dataframe(df)

# 🧭 Sidebar Filters
st.sidebar.header("Selecione o cliente")

Entidade = st.sidebar.selectbox(
    "Selecione o Cliente:",
    options=df["Entidade"].dropna().unique()
)

# 🔍 Filtra os dados pelo cliente selecionado
df_cliente = df[df["Entidade"] == Entidade]

# Sidebar: Selecione o Mês
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

mes_selecionado = st.sidebar.selectbox("Selecione o Mês:", meses)


# 🧾 Exibe em uma nova tabela abaixo
st.subheader("Dados do Cliente Selecionado")
st.dataframe(df_cliente)



st.write(f"Cliente selecionado: {Entidade}")

# Normaliza a coluna Mês
df["Mês"] = df["Mês"].astype(str).str.lower().str.strip()

# Normaliza o valor da sidebar também
mes_selecionado = mes_selecionado.lower().strip()

# Filtra e exibe
df_mes = df[df["Mês"] == mes_selecionado]
st.subheader(f"Resultados filtrados para o mês: {mes_selecionado.capitalize()}")
st.dataframe(df_mes)
