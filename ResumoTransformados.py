# Adicione no início do arquivo, após os imports
import base64

def add_custom_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
    }
    
    /* Customização dos tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Chame a função no main()
def main():
    add_custom_css()
    # ... resto do código
