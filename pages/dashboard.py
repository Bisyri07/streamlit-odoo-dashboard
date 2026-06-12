"""
Halaman: KPI ringkasan + distribusi status order + breakdown salesperson

"""

import os
import sys
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# Tambahkan root project ke path agar bisa import db.py

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_kpi_vs_period, get_status_order, get_revenue_per_salesperson


# ----------------------------- Konfigurasi Halaman -------------------------------

st.set_page_config(
    page_title="Dashboard Penjualan",
    page_icon="📊",
    layout="wide"
)


# --------------------------------- side bar --------------------------------------

with st.sidebar:
    st.title("Dashboard Penjualan")
    st.divider()


    st.markdown("Navigasi:")
    st.page_link("home.py", label="🏠 Home")
    st.page_link("pages/sales_trends.py", label="📈 Sales Trends")
    st.page_link("pages/top_products.py", label="🏆 Top Products")
    st.divider()


    st.subheader("🗓️ Filter Periode")

    # Preset Periode
    preset = st.selectbox(
        "Pilih Periode:", [
            "30 Hari Terakhir",
            "Bulan Ini",
            "Bulan Lalu",
            "3 Bulan Terakhir",
            "Tahun Ini",
            "Custom",
        ]
    )

    today = datetime.date.today()

    if preset == "30 Hari Terakhir":
        date_from = today - datetime.timedelta(days=30)
        date_to = today
    elif preset == "Bulan Ini":
        date_from = today.replace(day=1)
        date_to = today
    elif preset == "Bulan Lalu":
        first_this = today.replace(day=1)   # Hari pertama di bulan ini
        date_to = first_this - datetime.timedelta(days=1)   # Hari terakhir di bulan lalu
        date_from = date_to.replace(day=1)  # Hari pertama di bulan lalu
    elif preset == "3 Bulan Terakhir":
        date_from = today - datetime.timedelta(days=90)
        date_to = today
    elif preset == "Tahun Ini":
        date_from = today.replace(month=1, day=1)
        date_to = today
    else:
        date_from = st.date_input("Dari tanggal: ", today - datetime.timedelta(days=30))
        date_to = st.date_input("Sampai tanggal: ", today)

    st.caption(f"Periode: **{date_from}** s/d **{date_to}**")
    st.divider()

