"""
db.py — Modul koneksi dan query ke PostgreSQL Odoo
Dipakai bersama oleh semua halaman Streamlit.
"""

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ── Logging ─────────────────────────────────────────────
# __name__ di sini akan bernilai "db" -> log akan tampil sebagai
from logger_config import get_logger
logger = get_logger(__name__)


# Muat variabel dari file .env
load_dotenv()


# ── Buat koneksi engine (di-cache agar tidak buat ulang) ──
@st.cache_resource
def get_engine():
    """
    Buat SQLAlchemy engine sekali dan di-cache.
    Konfigurasi diambil dari .env atau st.secrets (jika deploy di Streamlit Cloud).
    """
    try:
        # Coba dari st.secrets dulu (untuk Streamlit Cloud)
        host     = st.secrets["DB_HOST"]
        port     = st.secrets["DB_PORT"]
        dbname   = st.secrets["DB_NAME"]
        user     = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
        logger.info("fetch DB configuration")
    except Exception:
        # Fallback ke .env (untuk lokal)
        host     = os.getenv("DB_HOST", "localhost")
        port     = os.getenv("DB_PORT", "5432")
        dbname   = os.getenv("DB_NAME", "odoo")
        user     = os.getenv("DB_USER", "odoo")
        password = os.getenv("DB_PASSWORD", "odoo")
        logger.info("DB configuration is taken from .env (st.secrets unavailable)")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

    try:
        engine = create_engine(url, pool_pre_ping=True)
        logger.info(f"Database engine created for host={host} db={dbname}")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}", exc_info=True)
        raise


def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """Jalankan query SQL dan kembalikan hasilnya sebagai DataFrame."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Query successful, {len(df)} rows returned | params={params}")
            return df
        
    except Exception as e:
        logger.error(f"Query failed | params={params} | error: {e}", exc_info=True)
        raise RuntimeError("Failed to execute database query: {e}") from e


# ════════════════════════════════════════════════════════
# QUERY — KPI
# ════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_kpi_summary(date_from: str, date_to: str) -> dict:
    """
    Ringkasan KPI penjualan:
    - Total revenue (amount_total)
    - Jumlah order
    - Jumlah pelanggan unik
    - Rata-rata nilai order
    - Total qty terjual
    """
    sql = """
        SELECT
            COUNT(DISTINCT so.id)                          AS jumlah_order,
            COUNT(DISTINCT so.partner_id)                  AS jumlah_pelanggan,
            COALESCE(SUM(so.amount_total), 0)              AS total_revenue,
            COALESCE(AVG(so.amount_total), 0)              AS rata_nilai_order,
            COALESCE(SUM(sol.product_uom_qty), 0)          AS total_qty
        FROM sale_order so
        LEFT JOIN sale_order_line sol ON sol.order_id = so.id
        WHERE so.state IN ('sale', 'done')
          AND so.date_order::date BETWEEN :date_from AND :date_to
    """
    df = run_query(sql, {"date_from": date_from, "date_to": date_to})

    if df.empty:
        return {}
    
    row = df.iloc[0]

    return {
        "jumlah_order"    : int(row["jumlah_order"]),
        "jumlah_pelanggan": int(row["jumlah_pelanggan"]),
        "total_revenue"   : float(row["total_revenue"]),
        "rata_nilai_order": float(row["rata_nilai_order"]),
        "total_qty"       : float(row["total_qty"]),
    }


@st.cache_data(ttl=300)
def get_kpi_vs_period(date_from: str, date_to: str,
                       prev_from: str, prev_to: str) -> dict:
    """
    Bandingkan KPI periode sekarang vs periode sebelumnya
    untuk menghitung delta (naik/turun).
    """
    try:
        now  = get_kpi_summary(date_from, date_to)
        prev = get_kpi_summary(prev_from, prev_to)

        def delta_pct(curr, past):
            if past == 0:
                return None
            return round((curr - past) / past * 100, 1)

        result = {
            "revenue_delta"   : delta_pct(now.get("total_revenue",    0), prev.get("total_revenue",    0)),
            "order_delta"     : delta_pct(now.get("jumlah_order",     0), prev.get("jumlah_order",     0)),
            "pelanggan_delta" : delta_pct(now.get("jumlah_pelanggan", 0), prev.get("jumlah_pelanggan", 0)),
            "qty_delta"       : delta_pct(now.get("total_qty",        0), prev.get("total_qty",        0)),
            **now,
        }
        logger.info(f"KPI is calculated as success for the period {date_from} to {date_to}")
        return result
    
    except Exception as e:
        logger.error(f"Gagal hitung KPI vs period | periode={date_from}~{date_to} | error: {e}", exc_info=True)
        raise


# ════════════════════════════════════════════════════════
# QUERY — TREN WAKTU
# ════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_tren_harian(date_from: str, date_to: str) -> pd.DataFrame:
    """Tren revenue dan jumlah order per hari."""
    sql = """
        SELECT
            so.date_order::date                   AS tanggal,
            COUNT(so.id)                           AS jumlah_order,
            COALESCE(SUM(so.amount_total), 0)      AS revenue
        FROM sale_order so
        WHERE so.state IN ('sale', 'done')
          AND so.date_order::date BETWEEN :date_from AND :date_to
        GROUP BY so.date_order::date
        ORDER BY tanggal
    """
    return run_query(sql, {"date_from": date_from, "date_to": date_to})


@st.cache_data(ttl=300)
def get_tren_bulanan(date_from: str, date_to: str) -> pd.DataFrame:
    """Tren revenue dan jumlah order per bulan."""
    sql = """
        SELECT
            TO_CHAR(so.date_order, 'YYYY-MM')      AS bulan,
            COUNT(so.id)                            AS jumlah_order,
            COALESCE(SUM(so.amount_total), 0)       AS revenue
        FROM sale_order so
        WHERE so.state IN ('sale', 'done')
          AND so.date_order::date BETWEEN :date_from AND :date_to
        GROUP BY TO_CHAR(so.date_order, 'YYYY-MM')
        ORDER BY bulan
    """
    return run_query(sql, {"date_from": date_from, "date_to": date_to})


# ════════════════════════════════════════════════════════
# QUERY — BREAKDOWN
# ════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_top_produk(date_from: str, date_to: str, limit: int = 10) -> pd.DataFrame:
    """Top produk berdasarkan revenue."""
    sql = """
        SELECT
            pp.id                                          AS product_id,
            COALESCE(pt.name->>'en_US', pt.name::text)     AS nama_produk,
            SUM(sol.product_uom_qty)                       AS total_qty,
            SUM(sol.price_subtotal)                        AS total_revenue
        FROM sale_order_line sol
        JOIN sale_order so      ON so.id  = sol.order_id
        JOIN product_product pp ON pp.id  = sol.product_id
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE so.state IN ('sale', 'done')
          AND so.date_order::date BETWEEN :date_from AND :date_to
        GROUP BY pp.id, pt.name
        ORDER BY total_revenue DESC
        LIMIT :limit
    """
    return run_query(sql, {"date_from": date_from, "date_to": date_to, "limit": limit})


@st.cache_data(ttl=300)
def get_top_pelanggan(date_from: str, date_to: str, limit: int = 10) -> pd.DataFrame:
    """Top pelanggan berdasarkan revenue."""
    sql = """
        SELECT
            rp.name                                AS nama_pelanggan,
            COUNT(so.id)                           AS jumlah_order,
            COALESCE(SUM(so.amount_total), 0)      AS total_revenue
        FROM sale_order so
        JOIN res_partner rp ON rp.id = so.partner_id
        WHERE so.state IN ('sale', 'done')
          AND so.date_order::date BETWEEN :date_from AND :date_to
        GROUP BY rp.name
        ORDER BY total_revenue DESC
        LIMIT :limit
    """
    return run_query(sql, {"date_from": date_from, "date_to": date_to, "limit": limit})


@st.cache_data(ttl=300)
def get_revenue_per_salesperson(date_from: str, date_to: str) -> pd.DataFrame:
    """Revenue per salesperson."""
    sql = """
        SELECT
            ru.name                                AS salesperson,
            COUNT(so.id)                           AS jumlah_order,
            COALESCE(SUM(so.amount_total), 0)      AS total_revenue
        FROM sale_order so
        JOIN res_users ru ON ru.id = so.user_id
        WHERE so.state IN ('sale', 'done')
          AND so.date_order::date BETWEEN :date_from AND :date_to
        GROUP BY ru.name
        ORDER BY total_revenue DESC
    """
    return run_query(sql, {"date_from": date_from, "date_to": date_to})


# ════════════════════════════════════════════════════════
# QUERY — STATUS ORDER
# ════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_status_order(date_from: str, date_to: str) -> pd.DataFrame:
    """Distribusi order berdasarkan status."""
    sql = """
        SELECT
            state,
            COUNT(*) AS jumlah
        FROM sale_order
        WHERE date_order::date BETWEEN :date_from AND :date_to
        GROUP BY state
        ORDER BY jumlah DESC
    """
    df = run_query(sql, {"date_from": date_from, "date_to": date_to})
    label_map = {
        "draft"  : "Quotation",
        "sent"   : "Quotation Sent",
        "sale"   : "Sales Order",
        "done"   : "Locked",
        "cancel" : "Cancelled",
    }
    if not df.empty:
        df["state"] = df["state"].map(label_map).fillna(df["state"])
    return df