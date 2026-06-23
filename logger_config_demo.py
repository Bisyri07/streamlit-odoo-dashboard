"""
============================================================
  DEMO: Logging & Error Handling di Streamlit
  Topik: logging module, traceback, st.exception,
         try-except per section, decorator logging,
         log ke file, log ke UI (expander/sidebar)
============================================================
 
Cara menjalankan:
  pip install streamlit pandas
  streamlit run streamlit_logging_demo.py
"""

import os
import sys
import logging
import datetime
import functools
import traceback
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Logging streamlit", page_icon="🐍", layout="centered")


# ════════════════════════════════════════════════════════
# SETUP LOGGING (letakkan di bagian paling atas file)
# ════════════════════════════════════════════════════════
# Konfigurasi ini idealnya dilakukan SEKALI saja, jadi taruh

LOG_FILE = "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="UTF-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


st.title("🐍 Logging & Error Handling")
st.markdown(
    "Pelajari cara mencatat error **dengan nomor baris**, menampilkannya "
    "di **console** (terminal tempat `streamlit run` dijalankan) maupun di **UI**."
)

st.divider()


# ════════════════════════════════════════════════════════
# 1. LOGGING DASAR — modul `logging` Python
# ════════════════════════════════════════════════════════

st.header("1. 📝 Logging Dasar dengan modul `logging`")
st.markdown(
    "Gunakan modul **`logging`** bawaan Python (bukan `print()`), karena otomatis "
    "menyertakan **waktu, level, nama file, dan nomor baris**."
)
 
st.code('''\
import logging
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),   # simpan ke file
        logging.StreamHandler(),          # tampilkan di console
    ],
)
logger = logging.getLogger(__name__)
 
logger.debug("Detail untuk debugging")
logger.info("Informasi umum, misal: 'User membuka halaman X'")
logger.warning("Peringatan, misal: 'Data kosong, pakai default'")
logger.error("Error, misal: 'Gagal konek ke database'")
logger.critical("Error fatal yang menghentikan aplikasi")
''', language="python")


st.markdown("**Coba langsung — klik tombol untuk menulis log, lalu cek terminal:**")

col1, col2, col3, col4 = st.columns(4)

if col1.button("ℹ️ Log Info"):
    logger.info("User mengklik tombol 'Log Info' di baris ini")
    st.success("✅ Log INFO ditulis — cek terminal kamu!")
if col2.button("⚠️ Log Warning"):
    logger.warning("Contoh warning: stok produk hampir habis")
    st.warning("⚠️ Log WARNING ditulis — cek terminal kamu!")
if col3.button("❌ Log Error"):
    logger.error("Contoh error: gagal memproses data pelanggan")
    st.error("❌ Log ERROR ditulis — cek terminal kamu!")
if col4.button("🔥 Log Critical"):
    logger.critical("Contoh critical: koneksi database terputus total")
    st.error("🔥 Log CRITICAL ditulis — cek terminal kamu!")


st.info(
    "💡 Karena format log menyertakan `%(lineno)d`, setiap baris log otomatis "
    "menunjukkan **nomor baris kode** tempat `logger.xxx()` dipanggil."
)

st.divider()

# ════════════════════════════════════════════════════════
# 2. MENANGKAP ERROR DENGAN NOMOR BARIS — traceback
# ════════════════════════════════════════════════════════
st.header("2. 📍 Menangkap Error dengan Nomor Baris Pasti")
st.markdown(
    "Saat terjadi **exception** (bukan log manual), gunakan modul **`traceback`** "
    "untuk mendapatkan file, baris, dan stack trace lengkap di mana error terjadi."
)
 
st.code('''\
import traceback
 
def proses_data(df):
    hasil = df["kolom_yang_tidak_ada"]   # <- baris ini akan error
    return hasil
 
try:
    proses_data(df)
except Exception as e:
    # exc_info=True menyertakan traceback lengkap ke log
    logger.error(f"Gagal proses data: {e}", exc_info=True)
 
    # Tampilkan detail teknis (untuk developer) di UI
    with st.expander("🔍 Detail error (klik untuk lihat)"):
        st.code(traceback.format_exc(), language="python")
 
    # Tampilkan pesan ramah (untuk end-user) di UI
    st.error("Terjadi kesalahan saat memproses data. Tim teknis sudah diberi tahu.")
''', language="python")
 
st.markdown("**Coba langsung — tombol ini sengaja memicu error:**")
 
if st.button("💥 Picu Error: Akses Kolom yang Tidak Ada"):
    try:
        df_demo = pd.DataFrame({"nama": ["A", "B"], "harga": [100, 200]})
        hasil = df_demo["kolom_yang_tidak_ada"]   # baris ini sengaja error
    except Exception as e:
        logger.error(f"Gagal proses data: {e}", exc_info=True)
 
        with st.expander("🔍 Detail error teknis (untuk developer)", expanded=True):
            st.code(traceback.format_exc(), language="python")
 
        st.error("⚠️ Terjadi kesalahan saat memproses data. Tim teknis sudah diberi tahu.")
 
st.caption(
    "Perhatikan: traceback di atas menunjukkan **nama file dan nomor baris pasti** "
    "tempat error terjadi (`hasil = df_demo[...]`)."
)
 
st.divider()


# ════════════════════════════════════════════════════════
# 3. st.exception() — cara native Streamlit
# ════════════════════════════════════════════════════════
st.header("3. 🎯 st.exception() — Cara Native Streamlit")
st.markdown(
    "Streamlit punya fungsi bawaan **`st.exception()`** yang otomatis menampilkan "
    "traceback lengkap dengan format rapi langsung di UI — tanpa perlu `traceback.format_exc()` manual."
)
 
st.code('''\
try:
    hasil = 10 / 0   # akan memicu ZeroDivisionError
except Exception as e:
    logger.error(f"Error pembagian: {e}", exc_info=True)
    st.exception(e)   # tampilkan traceback rapi di UI
''', language="python")
 
if st.button("💥 Picu Error: Pembagian dengan Nol"):
    try:
        angka = 10
        pembagi = 0
        hasil = angka / pembagi   # baris ini akan error
    except Exception as e:
        logger.error(f"Error pembagian: {e}", exc_info=True)
        st.exception(e)
 
st.warning(
    "⚠️ **Penting:** `st.exception()` menampilkan detail teknis lengkap (termasuk "
    "nama variabel & struktur kode). **Jangan tampilkan ini ke end-user di aplikasi "
    "production** — gunakan hanya saat development, atau bungkus dengan kondisi "
    "`if DEBUG_MODE:` (lihat bagian 6)."
)
 
st.divider()
 
 
# ════════════════════════════════════════════════════════
# 4. DECORATOR — otomatis log setiap fungsi
# ════════════════════════════════════════════════════════
st.header("4. 🎁 Decorator — Logging Otomatis per Fungsi")
st.markdown(
    "Daripada menulis `try-except` di setiap fungsi, buat **decorator** yang "
    "otomatis menangkap dan mencatat error — lebih rapi dan konsisten."
)
 
st.code('''\
import functools
 
def log_errors(func):
    """Decorator: otomatis log error tanpa menghentikan aplikasi."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error di fungsi '{func.__name__}': {e}",
                exc_info=True
            )
            st.error(f"❌ Gagal menjalankan '{func.__name__}'. Lihat log untuk detail.")
            return None
    return wrapper
 
 
@log_errors
def hitung_rata_rata(data: list):
    return sum(data) / len(data)   # error jika data kosong (ZeroDivisionError)
 
hitung_rata_rata([])   # otomatis ter-log, aplikasi tidak crash
''', language="python")
 
def log_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error di fungsi '{func.__name__}': {e}", exc_info=True)
            st.error(f"❌ Gagal menjalankan '{func.__name__}'. Lihat log untuk detail.")
            with st.expander("🔍 Detail teknis"):
                st.code(traceback.format_exc(), language="python")
            return None
    return wrapper
 
@log_errors
def hitung_rata_rata(data):
    return sum(data) / len(data)
 
if st.button("💥 Picu Error via Decorator (list kosong)"):
    hasil = hitung_rata_rata([])
    if hasil is not None:
        st.success(f"Rata-rata: {hasil}")
 
st.divider()
 
 
# ════════════════════════════════════════════════════════
# 5. LOG VIEWER DI SIDEBAR / EXPANDER — untuk developer
# ════════════════════════════════════════════════════════
st.header("5. 👀 Menampilkan Isi Log File Langsung di UI")
st.markdown(
    "Berguna saat develop atau deploy di server tanpa akses terminal — "
    "developer bisa lihat log langsung dari browser."
)
 
st.code('''\
with st.sidebar:
    with st.expander("🐛 Log Viewer (Developer)", expanded=False):
        if os.path.exists("app.log"):
            with open("app.log", "r", encoding="utf-8") as f:
                log_lines = f.readlines()[-50:]   # 50 baris terakhir
            st.code("".join(log_lines), language="log")
 
            if st.button("🗑️ Bersihkan Log"):
                open("app.log", "w").close()
                st.rerun()
        else:
            st.caption("Belum ada file log.")
''', language="python")
 
with st.sidebar:
    st.divider()
    with st.expander("🐛 Log Viewer (Developer)", expanded=False):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log_lines = f.readlines()[-30:]
            if log_lines:
                st.code("".join(log_lines), language="log")
            else:
                st.caption("Log masih kosong.")
            if st.button("🗑️ Bersihkan Log", key="clear_log_btn"):
                open(LOG_FILE, "w").close()
                st.rerun()
        else:
            st.caption("File log belum dibuat. Klik tombol log di atas dulu.")
 
st.info("👈 Lihat **sidebar kiri**, buka expander 'Log Viewer' untuk melihat isi `app.log` langsung dari UI.")
 
st.divider()
 
 
# ════════════════════════════════════════════════════════
# 6. MODE DEBUG — tampilkan detail hanya saat development
# ════════════════════════════════════════════════════════
st.header("6. 🔧 Mode Debug — Detail Error Hanya untuk Developer")
st.markdown(
    "Di production, **jangan** tampilkan traceback teknis ke end-user (bisa membocorkan "
    "struktur kode/database). Gunakan flag `DEBUG_MODE` untuk kontrol."
)
 
st.code('''\
import os
 
# Set lewat environment variable: DEBUG_MODE=true streamlit run app.py
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
 
def handle_error(e: Exception, context: str = ""):
    """Tangani error secara konsisten di seluruh aplikasi."""
    logger.error(f"[{context}] {e}", exc_info=True)   # selalu log lengkap
 
    if DEBUG_MODE:
        # Developer/staging: tampilkan semua detail
        st.error(f"❌ Error di '{context}'")
        with st.expander("🔍 Traceback lengkap", expanded=True):
            st.code(traceback.format_exc(), language="python")
    else:
        # Production: pesan ramah saja untuk end-user
        st.error("⚠️ Terjadi kesalahan. Tim kami sudah diberi tahu otomatis.")
 
# Pemakaian:
try:
    hasil = 1 / 0
except Exception as e:
    handle_error(e, context="Kalkulasi Rata-rata")
''', language="python")
 
DEBUG_MODE = st.toggle("🔧 Simulasikan DEBUG_MODE = True", value=True)
 
def handle_error(e: Exception, context: str = ""):
    logger.error(f"[{context}] {e}", exc_info=True)
    if DEBUG_MODE:
        st.error(f"❌ Error di '{context}'")
        with st.expander("🔍 Traceback lengkap (hanya tampil saat DEBUG_MODE)", expanded=True):
            st.code(traceback.format_exc(), language="python")
    else:
        st.error("⚠️ Terjadi kesalahan. Tim kami sudah diberi tahu otomatis.")
 
if st.button("💥 Picu Error dengan Mode Debug"):
    try:
        hasil = 1 / 0
    except Exception as e:
        handle_error(e, context="Kalkulasi Rata-rata")
 
st.divider()
 
 
# ════════════════════════════════════════════════════════
# 7. GLOBAL ERROR HANDLER — bungkus seluruh halaman
# ════════════════════════════════════════════════════════
st.header("7. 🛡️ Membungkus Seluruh Halaman dengan Error Handler")
st.markdown(
    "Agar error di **bagian manapun** halaman tidak membuat seluruh app crash putih "
    "(blank page), bungkus logika utama halaman dalam satu `try-except` besar."
)
 
st.code('''\
def render_halaman():
    st.title("Dashboard Penjualan")
 
    # ... semua logika halaman: query DB, hitung KPI, render chart ...
    df = ambil_data_dari_db()
    tampilkan_kpi(df)
    tampilkan_chart(df)
 
 
if __name__ == "__main__":
    try:
        render_halaman()
    except Exception as e:
        logger.critical(f"Halaman gagal total: {e}", exc_info=True)
        st.error(
            "😞 Halaman gagal dimuat. Silakan refresh, atau hubungi tim IT "
            "jika masalah berlanjut."
        )
        if DEBUG_MODE:
            st.exception(e)
''', language="python")
 
st.success(
    "✅ Pola ini **sangat direkomendasikan** untuk setiap halaman dashboard — "
    "satu bagian KPI yang gagal tidak akan menjatuhkan seluruh halaman."
)
 
st.divider()
 
 
# ════════════════════════════════════════════════════════
# RINGKASAN
# ════════════════════════════════════════════════════════
st.header("📖 Ringkasan — Kapan Pakai Apa?")
 
ringkasan = pd.DataFrame({
    "Teknik": [
        "logging.info/warning/error()",
        "traceback.format_exc()",
        "st.exception(e)",
        "Decorator @log_errors",
        "Log viewer di sidebar",
        "DEBUG_MODE flag",
        "Try-except per halaman",
    ],
    "Kapan Dipakai": [
        "Catat kejadian penting (siapa akses apa, kapan) — selalu aktif",
        "Saat butuh detail lokasi error (file & nomor baris) di log/file",
        "Cara cepat tampilkan traceback rapi di UI saat development",
        "Banyak fungsi butuh error handling yang sama → hindari duplikasi kode",
        "Deploy di server tanpa akses terminal, developer cek log via browser",
        "Beda tampilan error untuk developer (detail) vs end-user (ramah)",
        "Mencegah 1 bagian error membuat seluruh halaman blank/crash",
    ],
})
st.table(ringkasan)
 
st.markdown("---")
st.subheader("💡 Best Practice Ringkas")
st.markdown("""
1. **Selalu** gunakan modul `logging`, jangan `print()` — otomatis ada waktu & nomor baris.
2. **Selalu** panggil `exc_info=True` saat log error di dalam blok `except` agar traceback lengkap tersimpan.
3. **Pisahkan** pesan untuk developer (detail teknis di log/expander) dan untuk end-user (pesan ramah).
4. **Bungkus** query database / API eksternal dengan try-except spesifik, jangan satu try-except raksasa untuk semua hal.
5. **Gunakan flag `DEBUG_MODE`** dari environment variable agar production tidak membocorkan detail teknis.
""")



