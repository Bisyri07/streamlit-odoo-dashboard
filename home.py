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


# ----------------------------- side bar global -------------------------------
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo_path, width=130)

    # st.title("Odoo sales Dashboard")

    st.divider()

    st.markdown("Navigasi:")

    st.page_link("home.py", label="🏠 Home")
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/sales_trends.py", label="📈 Sales Trends")
    st.page_link("pages/top_products.py", label="🏆 Top Products")
    st.divider()
    st.caption("Sumber: PostgreSQL odoo 14")


# ----------------------------- Konten Home -------------------------------

st.title("Sales Dashboard Homepage", text_alignment="center")
st.markdown("Selamat datang! Aplikasi ini menampilkan data penjualan langsung dari database PostgreSQL Odoo.", text_alignment="center")
st.divider()

col1, col2, col3 = st.columns(3)


with col1:
    with st.container(border=True):
        st.markdown("### Dashboard Penjualan 📊")
        st.markdown(
            "Ringkasan KPI utama: total revenue, jumlah order, "
            "pelanggan aktif, dan distribusi status order."
        )
        st.page_link("pages/dashboard.py", label="Buka Dashboard →")

with col2:
    with st.container(border=True):
        st.markdown("### Tren Penjualan 📈")
        st.markdown(
            "Grafik tren revenue dan jumlah order dari waktu ke waktu, "
            "bisa dilihat per hari maupun per bulan."
        )
        st.page_link("pages/sales_trends.py", label="Buka Tren →")

with col3:
    with st.container(border=True):
        st.markdown("### Top Produk & Pelanggan 🏆")
        st.markdown(
            "Produk terlaris dan pelanggan dengan revenue tertinggi "
            "dalam periode yang dipilih."
        )
        st.page_link("pages/top_products.py", label="Buka Top Produk →")

st.divider()


# ----------------------------- Konten Home -------------------------------

st.subheader("Status Koneksi Database 🔌")

if st.button("Test Koneksi ke PostgreSQL 🔄"):
    try:
        from db import run_query
        df = run_query("SELECT version()")
        st.success(f"Koneksi berhasil! PostgreSQL version ✅: `{df.iloc[0,0]}`")
    except Exception as e:
        st.error(f"❌ Koneksi gagal: {e}")
        st.info(
            "Pastikan file `.env` sudah diisi sesuai server PostgreSQL kamu:\n"
            "```\nDB_HOST=localhost\nDB_PORT=5434\n"
            "DB_NAME=nama_db_odoo\nDB_USER=odoo\nDB_PASSWORD=password\n```\n"
            "Kalau PostgreSQL kamu memang berjalan di port lain, ganti `DB_PORT` sesuai port itu."
        )
