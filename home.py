"""
Halaman utama Odoo Salaes Dashboard
"""

import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="Odoo Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# mendapatkan path logo secara relatif terhadap file ini
current_dir = Path(__file__).parent
logo_path = current_dir / "static" / "img" / "sales.png"


# -------------------- side bar global --------------------------------------
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo_path, width=130)

    st.title("Odoo sales Dashboard")

    st.divider()

    st.markdown("Navigasi:")

    st.page_link("home.py", label="🏠 Home")
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/sales_trends.py", label="📈 Sales Trends")
    st.page_link("pages/top_products.py", label="🏆 Top Products")



