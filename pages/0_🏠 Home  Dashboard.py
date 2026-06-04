import streamlit as st

st.set_page_config(
    page_title="CentSaver -- Smart Expense Awareness System",
    page_icon="💰",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    text-align: center;
    padding: 4rem 1rem 3rem 1rem;
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f172a 100%);
    border-radius: 1.5rem;
    color: white;
    margin-bottom: 2rem;
}
.hero h1 {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #60a5fa, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    font-size: 1.2rem;
    color: #cbd5e1;
    max-width: 600px;
    margin: 0 auto 1.5rem auto;
}

.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.5rem;
}
.section-sub {
    color: #64748b;
    margin-bottom: 1.5rem;
}

.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 1rem;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.2s;
    height: 100%;
}
.card:hover {
    transform: translateY(-4px);
    border-color: #3b82f6;
    box-shadow: 0 10px 30px rgba(59,130,246,0.1);
}
.card h3 {
    margin: 0.5rem 0 0.3rem 0;
    font-size: 1.05rem;
    color: #0f172a;
}
.card p {
    margin: 0;
    font-size: 0.9rem;
    color: #64748b;
}

.quote {
    background: #f8fafc;
    border-left: 4px solid #3b82f6;
    padding: 1.5rem;
    border-radius: 0 1rem 1rem 0;
    font-style: italic;
    color: #334155;
    margin: 2rem 0;
}

.money-fact {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 1rem;
    padding: 1.5rem;
    text-align: center;
    margin: 1.5rem 0;
}
.money-fact h3 {
    margin: 0 0 0.5rem 0;
    color: #065f46;
}
.money-fact p {
    margin: 0;
    color: #374151;
}

.footer {
    text-align: center;
    padding: 2rem;
    color: #94a3b8;
    font-size: 0.85rem;
    border-top: 1px solid #f1f5f9;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">
    <h1>💰 CentSaver - Smart Expense Awareness System</h1>
    <p>Sadar. Catat. Hemat.<br>Mulai perjalanan keuangan sehatmu dari pengeluaran mikro yang sering luput dari pantauan.</p>
    <div style="margin-top: 1.5rem;">
        <a href="Tambah_Transaksi" target="_self">
            <button style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white; padding: 0.75rem 2rem; border-radius: 9999px; font-weight: 600; border: none; cursor: pointer; font-size: 1rem;">
                🚀 Mulai Catat Pengeluaran
            </button>
        </a>
    </div>
    <p style="font-size: 0.85rem; margin-top: 1rem; opacity: 0.6;">
        Dibuat dengan ❤️ oleh tim Capstone DBS Foundation Coding Camp 2026
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# AJAKAN
# ============================================================

st.markdown("""
<div class="quote">
    "Orang Indonesia cenderung <b>tidak menyadari</b> bahwa pengeluaran Rp 15.000–Rp 50.000 per hari untuk kopi, 
    snack, atau transportasi online bisa menumpuk jutaan rupiah per bulan. CentSaver hadir untuk membantumu 
    <b>melihat pola</b>, <b>memahami risiko</b>, dan <b>mengambil keputusan</b> yang lebih baik."
</div>
""", unsafe_allow_html=True)

# ============================================================
# FITUR
# ============================================================
st.markdown('<div class="section-title">🎯 Apa yang Bisa Kamu Lakukan?</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">CentSaver menggabungkan Data Science dan Deep Learning untuk keuangan pribadimu.</div>', unsafe_allow_html=True)

features = [
    ("➕", "Catat Transaksi", "Input pengeluaran harian dengan kategori otomatis. Gampang, cepat, no ribet."),
    ("📋", "Lihat Riwayat", "Seluruh transaksi tersimpan rapi. Filter per kategori, tanggal, atau nominal."),
    ("🚨", "Prediksi & Peringatan", "AI mendeteksi pola micro-spending dan memberi peringatan sebelum boncos."),
    ("📊", "Visualisasi Data", "Pahami kebiasaan belanjamu lewat grafik dan chart interaktif yang menarik."),
    ("🧪", " Implementasi A/B Testing", "Tim produk bisa melakukan A/B Testing untuk strategi penghematan berbasis data."),
    ("📰", "Literasi Keuangan", "Baca berita ekonomi, tips saham, dan edukasi finansial terkini di Indonesia."),
]

for i in range(0, len(features), 3):
    cols = st.columns(3)
    for col, (icon, title, desc) in zip(cols, features[i:i+3]):
        with col:
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ============================================================
# FAKTA MIKRO
# ============================================================
st.markdown('<div class="section-title">📉 Fakta: The Power of Micro-Spending</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("☕ Kopi/Minum", "Rp 25.000/hari", "Rp 750.000/bulan")
c2.metric("🍿 Snack/Jajanan", "Rp 20.000/hari", "Rp 600.000/bulan")
c3.metric("🚗 Transportasi", "Rp 30.000/hari", "Rp 900.000/bulan")

st.markdown("""
<div class="money-fact">
    <h3>💡 Bayangkan</h3>
    <p>Kalau bisa mengurangi <b>30%</b> dari pengeluaran mikro tersebut, kamu bisa menabung 
    <b>Rp 675.000/bulan</b> atau <b>Rp 8.1 juta/tahun!</b></p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================
# TENTANG
# ============================================================
st.markdown(
    '<div class="section-title">🎯 Fitur Utama</div>',
    unsafe_allow_html=True
)

st.markdown("""
- ➕ **Tambah Transaksi** — Mencatat pemasukan dan pengeluaran harian.
- 📋 **Riwayat Transaksi** — Menampilkan dan mengelola data historis transaksi.
- 🚨 **Prediksi & Peringatan AI** — Memprediksi tren pengeluaran dan memberikan peringatan dini.
- 📊 **Analisis Dataset** — Menyajikan visualisasi dan insight dari data transaksi.
- 🧪 **A/B Testing** — Membandingkan pola pengeluaran antar kategori.
- 📰 **Literasi Finansial** — Menyediakan edukasi dan informasi finansial.
""")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <b>CentSaver AI</b> — DBS Foundation Coding Camp 2026<br>
    "Mulai dari yang mikro, capai yang makro."
</div>
""", unsafe_allow_html=True)