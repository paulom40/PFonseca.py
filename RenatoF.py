import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Vendas Dashboard", layout="wide", page_icon="📊")

# 📊 Title
st.title("📊 Alertas Vencimentos")



# 🚀 Page configuration
st.set_page_config(page_title="Vendas Dashboard", layout="wide", page_icon="📊")

# 📊 Title
st.title("📊 Alertas Vencimentos")

# 📥 Load data
url = "import streamlit as st
import pandas as pd
from io import BytesIO

# 🚀 Page configuration
st.set_page_config(page_title="Vendas Dashboard", layout="wide", page_icon="📊")

# 📊 Title
st.title("📊 Alertas Vencimentos")

# 📥 Load data
url = "url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/RFerreira.xlsx"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 Clean data
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# 📅 Define ranges
ranges = [
    (0, 15, "0 a 15 dias 🟦"),
    (16, 30, "16 a 30 dias 🟫"),
    (31, 60, "31 a 60 dias 🟧"),
    (61, 90, "61 a 90 dias 🟨"),
    (91, 365, "91 a 365 dias 🟥")
]

# 🎛️ Sidebar filters
st.sidebar.header("🎨 Filtros")
selected_comercial = st.sidebar.multiselect(
    "👨‍💼 Comercial",
    sorted(df['Comercial'].unique()),
    default=sorted(df['Comercial'].unique())
)
selected_entidade = st.sidebar.multiselect(
    "🏢 Entidade",
    sorted(df['Entidade'].unique()),
    default=sorted(df['Entidade'].unique())
)
selected_ranges = st.sidebar.multiselect(
    "📅 Intervalos de Dias",
    [r[2] for r in ranges],
    default=[r[2] for r in ranges]
)

# 🔍 Filter data
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 🔄 Refresh button
if st.button("🔄 Atualizar Dados"):
    st.rerun()

# 📋 Summary
st.subheader("📋 Resumo")
summary = []
for low, high, label in ranges:
    if label in selected_ranges:
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        summary.append({
            "Intervalo": label,
            "Quantidade": len(range_df),
            "Valor Pendente": range_df['Valor Pendente'].sum()
        })
if summary:
    st.dataframe(pd.DataFrame(summary), use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado nos intervalos selecionados")

# 📂 Detalhes por intervalo
for low, high, label in ranges:
    if label in selected_ranges:
        st.subheader(label)
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        if not range_df.empty:
            st.dataframe(range_df, use_container_width=True)
        else:
            st.info("⚠️ Nenhum alerta neste intervalo")

# 📥 Download Excel
if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=output.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ Nenhum dado disponível para download")

# ❤️ Footer
st.markdown("---")
st.markdown("<p style='text-align:center;'>Feito com ❤️ em Streamlit</p>", unsafe_allow_html=True)
"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 Clean data
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# 📅 Define ranges
ranges = [
    (0, 15, "0 a 15 dias 🟦"),
    (16, 30, "16 a 30 dias 🟫"),
    (31, 60, "31 a 60 dias 🟧"),
    (61, 90, "61 a 90 dias 🟨"),
    (91, 365, "91 a 365 dias 🟥")
]

# 🎛️ Sidebar filters
st.sidebar.header("🎨 Filtros")
selected_comercial = st.sidebar.multiselect(
    "👨‍💼 Comercial",
    sorted(df['Comercial'].unique()),
    default=sorted(df['Comercial'].unique())
)
selected_entidade = st.sidebar.multiselect(
    "🏢 Entidade",
    sorted(df['Entidade'].unique()),
    default=sorted(df['Entidade'].unique())
)
selected_ranges = st.sidebar.multiselect(
    "📅 Intervalos de Dias",
    [r[2] for r in ranges],
    default=[r[2] for r in ranges]
)

# 🔍 Filter data
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 🔄 Refresh button
if st.button("🔄 Atualizar Dados"):
    st.rerun()

# 📋 Summary
st.subheader("📋 Resumo")
summary = []
for low, high, label in ranges:
    if label in selected_ranges:
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        summary.append({
            "Intervalo": label,
            "Quantidade": len(range_df),
            "Valor Pendente": range_df['Valor Pendente'].sum()
        })
if summary:
    st.dataframe(pd.DataFrame(summary), use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado nos intervalos selecionados")

# 📂 Detalhes por intervalo
for low, high, label in ranges:
    if label in selected_ranges:
        st.subheader(label)
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        if not range_df.empty:
            st.dataframe(range_df, use_container_width=True)
        else:
            st.info("⚠️ Nenhum alerta neste intervalo")

# 📥 Download Excel
if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=output.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ Nenhum dado disponível para download")

# ❤️ Footer
st.markdown("---")
st.markdown("<p style='text-align:center;'>Feito com ❤️ em Streamlit</p>", unsafe_allow_html=True)
"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 Clean data
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# 📅 Define ranges
ranges = [
    (0, 15, "0 a 15 dias 🟦"),
    (16, 30, "16 a 30 dias 🟫"),
    (31, 60, "31 a 60 dias 🟧"),
    (61, 90, "61 a 90 dias 🟨"),
    (91, 365, "91 a 365 dias 🟥")
]

# 🎛️ Sidebar filters
st.sidebar.header("🎨 Filtros")
selected_comercial = st.sidebar.multiselect(
    "👨‍💼 Comercial",
    sorted(df['Comercial'].unique()),
    default=sorted(df['Comercial'].unique())
)
selected_entidade = st.sidebar.multiselect(
    "🏢 Entidade",
    sorted(df['Entidade'].unique()),
    default=sorted(df['Entidade'].unique())
)
selected_ranges = st.sidebar.multiselect(
    "📅 Intervalos de Dias",
    [r[2] for r in ranges],
    default=[r[2] for r in ranges]
)

# 🔍 Filter data
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 🔄 Refresh button
if st.button("🔄 Atualizar Dados"):
    st.rerun()

# 📋 Summary
st.subheader("📋 Resumo")
summary = []
for low, high, label in ranges:
    if label in selected_ranges:
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        summary.append({
            "Intervalo": label,
            "Quantidade": len(range_df),
            "Valor Pendente": range_df['Valor Pendente'].sum()
        })
if summary:
    st.dataframe(pd.DataFrame(summary), use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado nos intervalos selecionados")

# 📂 Detalhes por intervalo
for low, high, label in ranges:
    if label in selected_ranges:
        st.subheader(label)
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        if not range_df.empty:
            st.dataframe(range_df, use_container_width=True)
        else:
            st.info("⚠️ Nenhum alerta neste intervalo")

# 📥 Download Excel
if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=output.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ Nenhum dado disponível para download")

# ❤️ Footer
st.markdown("---")
st.markdown("<p style='text-align:center;'>Feito com ❤️ em Streamlit</p>", unsafe_allow_html=True)
