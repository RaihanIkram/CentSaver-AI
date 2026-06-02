import streamlit as st

st.set_page_config(page_title="Literasi Keuangan | CentSaver", page_icon="📰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero-lit {
    background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);
    padding: 2.5rem 2rem;
    border-radius: 1.5rem;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-lit h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; }
.hero-lit p { font-size: 1.1rem; opacity: 0.95; max-width: 700px; margin: 0 auto; }

.news-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: all 0.2s;
}
.news-card:hover {
    border-color: #10b981;
    box-shadow: 0 8px 24px rgba(16,185,129,0.08);
    transform: translateY(-2px);
}
.news-card h4 { margin: 0 0 0.4rem 0; color: #064e3b; font-size: 1.05rem; }
.news-card p { margin: 0; color: #4b5563; font-size: 0.9rem; line-height: 1.5; }
.news-card .tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    margin-top: 0.5rem;
    margin-right: 0.3rem;
}
.tag-saham { background: #dbeafe; color: #1e40af; }
.tag-ekonomi { background: #fef3c7; color: #92400e; }
.tag-lifestyle { background: #d1fae5; color: #065f46; }
.tag-edukasi { background: #ede9fe; color: #5b21b6; }

.tip-box {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 1rem;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.tip-box h4 { margin: 0 0 0.4rem 0; color: #065f46; }
.tip-box p { margin: 0; color: #374151; font-size: 0.9rem; }

.stat-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
    padding: 1rem;
    text-align: center;
}
.stat-card h2 { margin: 0; font-size: 1.8rem; color: #059669; }
.stat-card p { margin: 0.2rem 0 0 0; font-size: 0.85rem; color: #6b7280; }

.ref-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 1rem;
    padding: 1.25rem;
    margin-top: 1.5rem;
}
.ref-box h4 { margin: 0 0 0.75rem 0; color: #0f172a; }
.ref-box a { color: #2563eb; text-decoration: none; }
.ref-box a:hover { text-decoration: underline; }
.ref-item {
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
    font-size: 0.9rem;
    color: #334155;
}
.ref-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero-lit">
    <h1>📰 Literasi Keuangan & Ekonomi</h1>
    <p>Perkembangan ekonomi Indonesia, edukasi finansial, dan insight pasar untuk membantumu 
    membuat keputusan keuangan yang lebih cerdas setiap hari.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SNAPSHOT
# ============================================================
st.markdown("### 📊 Snapshot Ekonomi Indonesia")
cols = st.columns(4)
stats = [
    ("🇮🇩", "38.3%", "Indeks Literasi Keuangan 2024 (OJK)"),
    ("📈", "7,300", "IHSG (perkiraan 2026)"),
    ("🏦", "5.75%", "BI Rate (perkiraan)"),
    ("💸", "2.8%", "Target Inflasi 2026"),
]
for col, (icon, val, label) in zip(cols, stats):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{icon} {val}</h2>
            <p>{label}</p>
        </div>
        """, unsafe_allow_html=True)

st.caption("Sumber: [OJK](https://www.ojk.go.id) & [BPS](https://www.bps.go.id). Data ilustratif untuk edukasi.")
st.divider()

# ============================================================
# BERITA
# ============================================================
st.markdown("### 🗞️ Insight & Berita Terkini")

news = [
    {
        "title": "Literasi Keuangan Indonesia Masih di Bawah 40%, Apa yang Bisa Dilakukan?",
        "desc": "Survei Nasional Literasi dan Inklusi Keuangan (SNLIK) 2024 oleh OJK dan BPS menunjukkan hanya 38.3% masyarakat Indonesia memiliki literasi keuangan yang memadai. Generasi muda (Gen Z dan Millennials) justru menunjukkan peningkatan minat investasi, namun masih banyak yang terjebak dalam micro-spending tanpa sadar.",
        "tags": ["edukasi", "lifestyle"]
    },
    {
        "title": "The Latte Factor: Mengapa Pengeluaran Mikro Bisa Merusak Keuangan Jangka Panjang",
        "desc": "Konsep 'Latte Factor' menunjukkan bahwa pengeluaran kecil Rp 25.000–Rp 50.000 per hari untuk kopi, snack, atau transportasi online bisa menumpuk hingga jutaan rupiah per bulan. Solusinya bukan berhenti total, tapi sadar dan terencana.",
        "tags": ["lifestyle", "edukasi"]
    },
    {
        "title": "IHSG Diproyeksikan Stabil di Kisaran 7,000–7,500 Tahun 2026",
        "desc": "Analis memperkirakan Indeks Harga Saham Gabungan (IHSG) akan didukung oleh sektor konsumer dan teknologi. Bagi investor pemula, reksadana indeks masih menjadi pintu masuk yang paling aman untuk berpartisipasi di pasar saham.",
        "tags": ["saham", "ekonomi"]
    },
    {
        "title": "Bank Indonesia Pertahankan Suku Bunga Acuan untuk Stabilitas Rupiah",
        "desc": "Kebijakan moneter ketat dipertahankan untuk mengendalikan inflasi dan menjaga stabilitas nilai tukar. Bagi masyarakat, ini berarti suku bunga deposito dan tabungan tetap menarik sebagai instrumen safe haven.",
        "tags": ["ekonomi", "edukasi"]
    },
    {
        "title": "Gen Z Dominasi Pasar Reksa Dana: 60% Investor Baru Berusia di Bawah 30 Tahun",
        "desc": "Tren investasi reksadana semakin digandrungi generasi muda. Platform digital memudahkan akses dengan modal mulai dari Rp 10.000. Namun, penting untuk memahami profil risiko sebelum memilih produk.",
        "tags": ["saham", "lifestyle"]
    },
    {
        "title": "Efek Domino Micro-Spending: Dari Rp 20.000/hari ke Rp 7.3 Juta/tahun",
        "desc": "Sebuah studi perilaku menunjukkan bahwa pengeluaran 'kecil' yang tidak tercatat bisa mencapai 15–20% dari total pendapatan bulanan. Tools seperti CentSaver AI dirancang untuk membantu generasi digital menyadari pola ini.",
        "tags": ["lifestyle", "edukasi"]
    },
]

for item in news:
    tags_html = ""
    for tag in item["tags"]:
        tags_html += f'<span class="tag tag-{tag}">{tag.upper()}</span>'
    st.markdown(f"""
    <div class="news-card">
        <h4>{item['title']}</h4>
        <p>{item['desc']}</p>
        {tags_html}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# TIPS
# ============================================================
st.markdown("### 💡 Tips Keuangan Praktis")
tips = [
    ("🎯 Rule 50/30/20", "Alokasikan 50% untuk kebutuhan, 30% untuk keinginan, dan 20% untuk tabungan/investasi. Modifikasi sesuai kondisimu."),
    ("📱 Catat Semua Pengeluaran", "Gunakan aplikasi seperti CentSaver untuk mencatat pengeluaran mikro. Awareness adalah langkah pertama menuju kontrol."),
    ("🛡️ Dana Darurat dulu, Investasi kemudian", "Pastikan punya dana darurat 3–6x pengeluaran bulanan sebelum mulai investasi berisiko."),
    ("📈 Mulai dari Reksa Dana Pasar Uang", "Untuk pemula, RDPU menawarkan likuiditas tinggi dan risiko rendah. Cocok untuk belajar sebelum masuk saham."),
    ("☕ Tantangan 'No-Spend Weekend'", "Coba 1 akhir pekan tanpa pengeluaran non-esensial. Hasilnya bisa mengejutkan dan membentuk kebiasaan baru."),
]
for title, desc in tips:
    st.markdown(f"""
    <div class="tip-box">
        <h4>{title}</h4>
        <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# GLOSSARY
# ============================================================
with st.expander("📚 Kamus Istilah Keuangan"):
    st.markdown("""
    | Istilah | Penjelasan |
    |---------|------------|
    | **Literasi Keuangan** | Kemampuan memahami, menganalisis, dan mengelola informasi keuangan untuk pengambilan keputusan yang tepat. |
    | **Micro-Spending** | Pengeluaran kecil dan sering yang sering luput dari perhatian (kopi, snack, parkir, dll.). |
    | **IHSG** | Indeks Harga Saham Gabungan — indikator performa pasar saham Indonesia. |
    | **BI Rate** | Suku bunga acuan Bank Indonesia yang memengaruhi suku bunga perbankan. |
    | **Reksa Dana** | Wadah berinvestasi secara kolektif dengan mengelola dana investor oleh Manajer Investasi. |
    | **Dana Darurat** | Tabungan yang disiapkan untuk kebutuhan tak terduga (sakit, PHK, perbaikan rumah). Idealnya 3–6x pengeluaran bulanan. |
    | **Inflasi** | Kenaikan harga barang dan jasa secara umum dalam periode tertentu yang mengurangi daya beli. |
    """)

# ============================================================
# REFERENSI
# ============================================================
st.divider()
st.markdown("### 📑 Referensi")

st.info("""
📎 **Sumber Data & Bacaan Lanjutan**
""")

st.markdown("""
**Otoritas Jasa Keuangan & Badan Pusat Statistik (2024)**  
*OJK and Statistics Indonesia Present National Survey On Financial Literacy And Inclusion 2024 Findings*  
🔗 https://www.ojk.go.id/en/berita-dan-kegiatan/siaran-pers/Pages/OJK-And-Statistics-Indonesia-Present-National-Survey-On-Financial-Literacy-And-Inclusion-2024-Findings.aspx

---

**Otoritas Jasa Keuangan & Badan Pusat Statistik (2025)**  
*Siaran Pers Bersama: Indeks Literasi dan Inklusi Keuangan Masyarakat Meningkat, OJK dan BPS Umumkan Hasil Survei Nasional Literasi dan Inklusi Keuangan (SNLIK) Tahun 2025*  
🔗 https://www.ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/OJK-dan-BPS-Umumkan-Hasil-Survei-Nasional-Literasi-Dan-Inklusi-Keuangan-SNLIK-Tahun-2025.aspx

---

**Bank Indonesia**  
*Statistik Kebijakan Moneter & Perbankan*  
🔗 https://www.bi.go.id/id/statistik/default.aspx
""")
# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style="text-align:center; padding:2rem; color:#9ca3af; font-size:0.85rem; border-top:1px solid #f3f4f6; margin-top:2rem;">
    <b>CentSaver AI</b> — Capstone Project DBS Foundation Coding Camp 2026<br>
    "Edukasi adalah investasi terbaik yang tidak bisa diinflasi."
</div>
""", unsafe_allow_html=True)