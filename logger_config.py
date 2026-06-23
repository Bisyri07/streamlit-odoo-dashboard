"""
logger_config.py
─────────────────
Konfigurasi logging TERPUSAT untuk seluruh aplikasi.
 
CARA PAKAI di file lain (db.py, Home.py, pages/*.py):
 
    from logger_config import get_logger
    logger = get_logger(__name__)
 
    logger.info("Pesan info")
    logger.warning("Pesan warning")
    logger.error("Pesan error", exc_info=True)   # exc_info=True wajib di dalam except
 
Kenapa dipusatkan di sini?
- Supaya SEMUA file (db.py, Home.py, pages/*.py) menulis ke FILE LOG YANG SAMA
  (app.log) dengan FORMAT YANG SAMA (waktu, level, nama file, nomor baris).
- Kalau konfigurasi diulang-ulang di setiap file, handler bisa terdaftar
  dobel dan log akan tertulis berkali-kali untuk 1 event yang sama.
"""


import os
import logging


# bikin file di path yg sama dengan file ini
LOG_FILE = os.path.join(os.path.dirname(__file__), "app.log")


# Ubah ke "false" saat deploy ke production.
# Cara set: DEBUG_MODE=false streamlit run 🏠_Home.py
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"



def _setup_root_logger():
    """
    Dipanggil HANYA SEKALI.
    Mendaftarkan 2 handler ke root logger:
      1. FileHandler  → tulis semua log ke app.log
      2. StreamHandler → tulis semua log ke console/terminal
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


# ── Guard: pastikan setup hanya dijalankan sekali ──────
# Streamlit suka re-run script, jadi tanpa guard ini, handler bisa
# terdaftar berkali-kali → 1 log akan tercetak 2x, 3x, dst.
if not logging.getLogger().handlers:
    _setup_root_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Ambil logger dengan nama modul pemanggil.
    Selalu panggil dengan __name__ supaya log menunjukkan
    file mana yang menulis log tersebut.
 
        `logger = get_logger(__name__)`
    """
    return logging.getLogger(name)


def get_recent_logs(n_lines: int=50) -> str:
    """Ambil N baris terakhir dari file log — dipakai oleh Log Viewer di sidebar."""
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return "".join(lines[-n_lines:])


def clear_logs():
    """Kosongkan file log — dipakai oleh tombol 'Bersihkan Log' di sidebar."""
    open(LOG_FILE, "W").close()


def log_and_show_error(logger: logging.Logger, e: Exception, context: str, user_msg: str = None):
    """
    Helper terpusat untuk dipakai di setiap blok `except` pada halaman Streamlit.
 
    Yang dilakukan:
      1. Selalu mencatat error LENGKAP (termasuk file & nomor baris asli)
         ke app.log dan console lewat exc_info=True.
      2. Selalu menampilkan pesan ramah ke user di UI (st.error).
      3. HANYA jika DEBUG_MODE aktif, tampilkan juga traceback teknis
         lengkap di expander -- supaya production tidak membocorkan
         detail kode/database ke end-user.
 
    Cara pakai di halaman:
        from logger_config import get_logger, log_and_show_error
        logger = get_logger(__name__)
        ...
        try:
            df = get_kpi_vs_period(...)
        except Exception as e:
            log_and_show_error(logger, e, context="Memuat KPI")
    """

    import streamlit as st
    import traceback


    logger.error(f"[{context}] {e}", exc_info=True)

    st.error(f"❌ {user_msg or f'Gagal: {context}'}")

    if DEBUG_MODE:
        with st.expander(f"🔍 Detail teknis — {context} (DEBUG_MODE)"):
            st.code(traceback.format_exc(), language="python")












