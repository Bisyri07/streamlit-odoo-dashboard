"""
Halaman: KPI ringkasan + distribusi status order + breakdown salesperson

"""

import os
import sys
import locale
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


# ------------------------- menggunakan bulan Indonesia ----------------------------
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')


# --------------------------------- side bar ---------------------------------------

with st.sidebar:
    st.title("Dashboard Penjualan")
    st.divider()


    st.markdown("Navigasi:")
    st.page_link("home.py", label="🏠 Home")
    st.page_link("pages/sales_trends.py", label="📈 Sales Trends")
    st.page_link("pages/top_products.py", label="🏆 Top Products")
    st.divider()


    # Preset Periode
    preset = st.selectbox(
        "🗓️ Filter Periode:", [
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

    st.divider()

    # Hitung periode pembanding (sama panjangnya, sebelum periode ini)
    delta_days = (date_to - date_from).days
    prev_to = date_from - datetime.timedelta(days=1)
    prev_from = prev_to - datetime.timedelta(days=delta_days)
    st.caption(f"dibandingkan: **{prev_from}** s/d **{prev_to}**")

    # st.markdown(f"delta_days: {delta_days}")
    # st.markdown(f"prev_to: {prev_to}")
    # st.markdown(f"prev_from: {prev_from}")

    st.divider()


# ════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════

st.title("Sales Dashboard 📊", text_alignment="center")
st.caption(f"Period: **{date_from.strftime('%d %B %Y')}** to **{date_to.strftime('%d %B %Y')}**", text_alignment="center")
st.divider()


# ════════════════════════════════════════════════════════
# KPI CARDS
# ════════════════════════════════════════════════════════

st.subheader("📌 Ringkasan KPI")

with st.spinner("Memuat data KPI..."):
    try:
        kpi = get_kpi_vs_period(
            str(date_from), str(date_to),
            str(prev_from), str(prev_to),
        )
 
        def fmt_indo_number(val, decimal_places=0):
            if val is None:
                return "0"
            # Format dengan standar python (koma untuk ribuan, titik untuk desimal)
            formatted = f"{val:,.{decimal_places}f}"
            # Tukar koma menjadi titik, dan desimal titik menjadi koma (format Indonesia)
            temp = "___TEMP___"
            formatted = formatted.replace(",", temp).replace(".", ",").replace(temp, ".")
            return formatted

        def fmt_rupiah(val):
            if val is None:
                val = 0
            if val >= 1_000_000_000:
                return f"Rp {val/1_000_000_000:.2f} M"
            elif val >= 1_000_000:
                return f"Rp {val/1_000_000:.1f} Jt"
            else:
                return f"Rp {val:,.0f}"
 
        def fmt_delta(val):
            if val is None:
                return None
            return f"{val:+.1f}%"
 
        col1, col2, col3, col4 = st.columns(4)
 
        col1.metric(
            "💰 Total Revenue",
            fmt_rupiah(kpi.get("total_revenue", 0)),
            delta=fmt_delta(kpi.get("revenue_delta")),
        )
        col2.metric(
            "🧾 Jumlah Order",
            fmt_indo_number(kpi.get('jumlah_order', 0), 0),
            delta=fmt_delta(kpi.get("order_delta")),
        )
        col3.metric(
            "👥 Pelanggan Aktif",
            fmt_indo_number(kpi.get('jumlah_pelanggan', 0), 0),
            delta=fmt_delta(kpi.get("pelanggan_delta")),
        )
        col4.metric(
            "📦 Total Qty Terjual",
            fmt_indo_number(kpi.get('total_qty', 0), 0),
            delta=fmt_delta(kpi.get("qty_delta")),
        )
 
        # KPI tambahan: rata-rata nilai order
        col5, col6, col7, col8 = st.columns(4)
        rata = kpi.get("rata_nilai_order", 0)
        col5.metric("🧮 Rata-rata Nilai Order", fmt_rupiah(rata))
 
        total_rev = kpi.get("total_revenue", 0)
        n_order   = kpi.get("jumlah_order", 1) or 1
        n_pelanggan = kpi.get("jumlah_pelanggan", 1) or 1
 
        col6.metric("💵 Revenue per Pelanggan", fmt_rupiah(total_rev / n_pelanggan))
        col7.metric("📋 Order per Pelanggan",   fmt_rupiah(n_order / n_pelanggan))
        col8.metric("📅 Hari dalam Periode",    f"{delta_days + 1} hari")
 
        st.caption("⬆️⬇️ Delta dibandingkan periode sebelumnya dengan panjang yang sama.")
 
    except Exception as e:
        st.error(f"Gagal memuat KPI: {e}")


