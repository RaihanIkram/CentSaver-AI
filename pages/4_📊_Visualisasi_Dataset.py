import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ============================================================================
# KONFIGURASI PAGE
# ============================================================================
st.set_page_config(
    page_title="Visualisasi & Business Questions | CentSaver",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS CUSTOM
# ============================================================================
st.markdown("""
<style>
    .insight-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #7c3aed;
        margin-top: 0.6rem;
    }
    .insight-title {
        color: #a78bfa;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }
    .insight-body {
        color: #cbd5e1;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .bq-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .bq-question {
        color: #7dd3fc;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .bq-answer {
        color: #e2e8f0;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .rq-badge {
        display: inline-block;
        background-color: #7c3aed;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .section-divider {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #475569, transparent);
    }
    .kpi-highlight {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 0.8rem;
        text-align: center;
        border: 1px solid #334155;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .kpi-label {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("📊 Visualisasi Dataset & Business Questions")
st.caption("Hasil analisis EDA CentSaver — 16.953 transaksi, 2015–2025.")

# ============================================================================
# MOCK DATA — SESUAI NOTEBOOK DS2
# ============================================================================
np.random.seed(42)

# 1. Distribusi Kategori
top5_cats = pd.DataFrame({
    "category": [
        "Makanan & Minuman", "Kebutuhan Dapur", "Belanja & Lifestyle",
        "Sewa & Cicilan", "Tagihan Utilitas", "Lainnya"
    ],
    "total_amount": [
        1_169_127_987, 406_811_878, 384_771_273,
        299_748_200, 292_725_380, 1_827_068_282
    ],
    "txn_count": [4374, 1948, 1049, 211, 891, 8480],
    "avg_amount": [267_290, 208_836, 366_798, 1_420_608, 328_536, 215_456]
})
top5_cats["percentage"] = (top5_cats["total_amount"] / top5_cats["total_amount"].sum() * 100).round(1)

# 2. Micro-Spending Ratio 
micro_ratio = pd.DataFrame({
    "category": [
        "Transportasi", "Kopi & Minuman", "Langganan Digital", "Makanan & Minuman",
        "Hiburan & Gaya Hidup", "Belanja & Lifestyle", "Elektronik",
        "Kebutuhan Rumah Tangga", "Kebutuhan Dapur", "Hobi & Olahraga"
    ],
    "avg_micro_pct": [15.86, 13.53, 12.45, 10.90, 5.23, 0.00, 0.00, 0.00, 0.00, 0.00]
})
micro_ratio["flagged"] = micro_ratio["avg_micro_pct"] > 10

# 3. Anomaly Rate
anomaly_data = pd.DataFrame({
    "category": [
        "Belanja & Lifestyle", "Hiburan & Gaya Hidup", "Kecantikan & Perawatan",
        "Transportasi", "Pendidikan", "Hobi & Olahraga",
        "Elektronik", "Keluarga & Sosial"
    ],
    "anomaly_rate": [0.0738, 0.0659, 0.0598, 0.0584, 0.0563, 0.0548, 0.0526, 0.0502]
})

# 4. Weekend Impulse
weekend_impulse = pd.DataFrame({
    "category": ["Transportasi", "Langganan Digital", "Kopi & Minuman", "Makanan & Minuman",
                 "Hiburan & Gaya Hidup", "Belanja & Lifestyle", "Elektronik"],
    "weekend_boost": [0.63, 0.62, 0.43, 0.40, 0.35, 0.28, 0.15]
})

# ============================================================================
# TABS UTAMA
# ============================================================================
tab_viz, tab_bq = st.tabs(["📊 Visualisasi Dataset", "💡 Business Questions"])

# =============================================================================
# TAB 1: VISUALISASI DATASET
# =============================================================================
with tab_viz:

    # --- KPI CARDS ---
    st.markdown("### 📈 Ringkasan Dataset")
    kpi_cols = st.columns(4)
    kpis = [
        ("💰 Total Transaksi", "Rp 4.38 M", "10 tahun (2015–2025)"),
        ("📝 Jumlah Data", "16,953", "18 kategori"),
        ("📊 Label", "87.8% Normal", "12.2% Micro-spending"),
        ("⚠️ Outlier", "12.2%", "> Rp 590.950")
    ]
    for col, (icon, val, lbl) in zip(kpi_cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-highlight">
                <div style="font-size: 1.1rem;">{icon}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- ROW 1: 2 CHART ---
    left, right = st.columns(2)

    with left:
        st.subheader("🥧 Distribusi Kategori")

        fig_pie = go.Figure(data=[go.Pie(
            labels=top5_cats["category"],
            values=top5_cats["total_amount"],
            hole=0.45,
            textinfo="label+percent",
            textposition="outside",
            pull=[0.05, 0, 0, 0, 0, 0],
            marker_colors=["#7c3aed", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#64748b"],
            textfont=dict(size=10, color="#f8fafc"),
            hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>"
        )])
        fig_pie.update_layout(
            showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"),
            height=340, uniformtext_minsize=9, uniformtext_mode="hide"
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">💡 Insight</div>
            <div class="insight-body">
                Mayoritas pengeluaran terkonsentrasi pada Makanan & Minuman (26.7%) yang mencerminkan 
                kebutuhan harian dengan frekuensi tinggi. Sewa & Cicilan meskipun nominalnya besar, 
                sifatnya sporadis — biasanya pembayaran tahunan yang bisa diprediksi.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.subheader("📊 Micro-Spending Ratio per Kategori")

        colors = ["#ef4444" if f else "#3b82f6" for f in micro_ratio["flagged"]]
        fig_micro = px.bar(
            micro_ratio, y="category", x="avg_micro_pct",
            orientation="h", color="flagged",
            color_discrete_map={True: "#ef4444", False: "#3b82f6"},
            text=micro_ratio["avg_micro_pct"].apply(lambda x: f"{x:.1f}%")
        )
        fig_micro.add_vline(x=10, line_dash="dash", line_color="#f59e0b", 
                           annotation_text="Batas 10%", annotation_position="top")
        fig_micro.update_traces(
            textposition="outside", textfont=dict(size=9, color="#f8fafc"),
            hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>"
        )
        fig_micro.update_layout(
            xaxis_title="Micro-Spending (%)", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=9), height=340,
            showlegend=False, margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
            yaxis=dict(gridcolor="rgba(148,163,184,0.1)", categoryorder="total ascending")
        )
        st.plotly_chart(fig_micro, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">💡 Insight</div>
            <div class="insight-body">
                Tiga kategori kebutuhan harian mendominasi micro-spending: Transportasi (15.9%), 
                Kopi & Minuman (13.5%), dan Langganan Digital (12.5%). Berbeda dengan asumsi umum, 
                pengeluaran kecil justru lebih banyak terjadi pada aktivitas rutin dibandingkan hobi.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- ROW 2: 2 CHART ---
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("🔥 Anomaly Rate per Kategori")

        fig_anom = px.bar(
            anomaly_data, y="category", x="anomaly_rate",
            orientation="h", color="anomaly_rate",
            color_continuous_scale="YlOrRd",
            text=anomaly_data["anomaly_rate"].apply(lambda x: f"{x*100:.1f}%")
        )
        fig_anom.update_traces(
            textposition="outside", textfont=dict(size=9, color="#f8fafc"),
            hovertemplate="<b>%{y}</b><br>%{x:.2%}<extra></extra>"
        )
        fig_anom.update_layout(
            xaxis_title="Anomaly Rate", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=9), height=340,
            showlegend=False, coloraxis_showscale=False,
            margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
            yaxis=dict(gridcolor="rgba(148,163,184,0.1)", categoryorder="total ascending")
        )
        st.plotly_chart(fig_anom, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">💡 Insight</div>
            <div class="insight-body">
                Belanja & Lifestyle menunjukkan ketidakstabilan tertinggi dengan 7.4% periode mengalami 
                anomali. Lonjakannya tidak mengikuti pola musiman, sehingga sulit dideteksi dengan 
                peramalan konvensional dan memerlukan pendekatan berbasis perilaku.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right2:
        st.subheader("⚡ Weekend Impulse Boost")

        fig_wknd = px.bar(
            weekend_impulse, y="category", x="weekend_boost",
            orientation="h", color="weekend_boost",
            color_continuous_scale="Teal",
            text=weekend_impulse["weekend_boost"].apply(lambda x: f"+{x*100:.0f}%")
        )
        fig_wknd.update_traces(
            textposition="outside", textfont=dict(size=9, color="#f8fafc"),
            hovertemplate="<b>%{y}</b><br>+%{x:.0%}<extra></extra>"
        )
        fig_wknd.update_layout(
            xaxis_title="Weekend Boost", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=9), height=340,
            showlegend=False, coloraxis_showscale=False,
            margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
            yaxis=dict(gridcolor="rgba(148,163,184,0.1)", categoryorder="total ascending")
        )
        st.plotly_chart(fig_wknd, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">💡 Insight</div>
            <div class="insight-body">
                Akhir pekan menjadi waktu rawan bagi beberapa kategori. Transportasi melonjak 63% 
                dan Langganan Digital 62% — kemungkinan besar karena aktivitas rekreasi dan 
                hiburan digital yang meningkat saat waktu luang.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# =============================================================================
# TAB 2: BUSINESS QUESTIONS
# =============================================================================
with tab_bq:
    st.markdown("## 💡 Business Questions")
    st.caption("Tiga pertanyaan utama dari analisis EDA.")
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- RQ 1 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ1</span> 
        Seberapa besar dampak pengeluaran kecil terhadap total pengeluaran bulanan?</div>
        <div class="bq-answer">
            Secara agregat, micro-spending menyumbang <b>3,11%</b> dari total pengeluaran per bulan. 
            Angka ini berada di bawah ambang batas 20%, namun tidak bisa digeneralisasi.<br><br>
            Kategori dengan proporsi tertinggi adalah <b>Transportasi (15,86%)</b>, 
            <b>Kopi & Minuman (13,53%)</b>, dan <b>Langganan Digital (12,45%)</b>. 
            Temuan ini menunjukkan pengeluaran kecil lebih banyak terjadi pada kebutuhan harian berulang 
            dibandingkan pengeluaran hobi atau sosial.<br><br>
            <b>Rekomendasi:</b> Tetapkan ambang batas per kategori berdasarkan median historis. 
            Untuk kategori frekuensi tinggi seperti Transportasi dan Kopi & Minuman, 
            aktifkan peringatan saat akumulasi mingguan melebihi kuartil bawah.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RQ 2 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ2</span> 
        Apa karakteristik yang membedakan transaksi micro-spending dengan normal?</div>
        <div class="bq-answer">
            Terdapat perbedaan signifikan antara kedua kelas. Nominal micro-spending jauh lebih rendah 
            (rata-rata <b>Rp38.799</b> vs <b>Rp288.800</b>, median <b>Rp28.100</b> vs <b>Rp128.100</b>). 
            Perbedaan ini signifikan secara statistik dengan effect size besar.<br><br>
            Selain nominal, pola waktu juga berbeda: micro-spending lebih sering terjadi di <b>akhir pekan</b>. 
            Kategori <b>Transportasi</b>, <b>Kopi & Minuman</b>, dan <b>Langganan Digital</b> 
            memiliki micro-spending rate tertinggi.<br><br>
            <b>Rekomendasi:</b> Gunakan tiga indikator utama untuk deteksi dini: 
            nominal di bawah median kategori, transaksi di akhir pekan, dan frekuensi berulang di merchant sama.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RQ 3 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ3</span> 
        Visualisasi apa yang paling efektif untuk menyoroti lonjakan pengeluaran?</div>
        <div class="bq-answer">
            <b>Heatmap Month-over-Month (MoM) Growth</b> adalah visualisasi paling efektif. 
            Perubahan warna kontras lebih cepat menarik perhatian dibandingkan angka dalam tabel.<br><br>
            <b>Belanja & Lifestyle</b> tercatat paling volatile dengan anomaly rate <b>7,37%</b>. 
            Analisis weekend juga menunjukkan <b>Transportasi</b> dan <b>Langganan Digital</b> 
            memiliki lonjakan signifikan di akhir pekan.<br><br>
            <b>Urutan efektivitas visualisasi:</b><br>
            1. Heatmap MoM Growth — deteksi spike dalam 1 detik<br>
            2. Grafik garis + penanda anomali — konteks historis dan musiman<br>
            3. Batang perbandingan antarkategori — melihat kategori paling tidak stabil<br>
            4. Weekend impulse boost — identifikasi pola akhir pekan<br><br>
            <b>Rekomendasi:</b> Tempatkan heatmap di posisi utama dashboard. 
            Jika terdeteksi kotak merah (lonjakan >20%), sistem otomatis mengirim notifikasi: 
            <i>"Pengeluaran [Kategori] naik signifikan dari bulan lalu."</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- KESIMPULAN & REKOMENDASI ---
    st.markdown("### 🎯 Kesimpulan & Rekomendasi")

    con1, con2 = st.columns(2)

    with con1:
        st.markdown("""
        <div style="background-color: #1e293b; padding: 1rem; border-radius: 12px; border-left: 4px solid #10b981;">
            <h4 style="color: #34d399; margin-bottom: 0.6rem; font-size: 0.95rem;">✅ Kesimpulan</h4>
            <ul style="color: #cbd5e1; font-size: 0.82rem; line-height: 1.6; padding-left: 1.2rem;">
                <li>Micro-spending rata-rata 3,11% per bulan, namun terkonsentrasi di kategori kebutuhan harian: Transportasi, Kopi & Minuman, dan Langganan Digital.</li>
                <li>Transaksi micro-spending memiliki nominal jauh lebih kecil dan cenderung terjadi di akhir pekan. Perbedaan ini signifikan secara statistik.</li>
                <li>Heatmap MoM Growth paling efektif memicu kesadaran. Belanja & Lifestyle adalah kategori paling volatile dengan anomaly rate 7,37%.</li>
                <li>Karakteristik kategori dan waktu menjadi fondasi yang kuat untuk deteksi otomatis.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with con2:
        st.markdown("""
        <div style="background-color: #1e293b; padding: 1rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
            <h4 style="color: #fbbf24; margin-bottom: 0.6rem; font-size: 0.95rem;">💡 Rekomendasi</h4>
            <ul style="color: #cbd5e1; font-size: 0.82rem; line-height: 1.6; padding-left: 1.2rem;">
                <li><b>Batas Per Kategori:</b> Sesuaikan ambang pengeluaran berdasarkan median historis masing-masing kategori, bukan satu angka untuk semua.</li>
                <li><b>Tracker Real-Time:</b> Tampilkan akumulasi micro-spending mingguan di dashboard untuk kategori Transportasi dan Kopi & Minuman.</li>
                <li><b>Notifikasi Pintar:</b> Trigger otomatis saat pertumbuhan bulanan >20% atau terdeteksi anomali dari pola historis.</li>
                <li><b>Weekend Guard:</b> Peringatan khusus untuk kategori dengan lonjakan akhir pekan tinggi (Transportasi, Langganan Digital).</li>
                <li><b>Segmentasi Pengguna:</b> Fokus edukasi finansial pada segmen dengan frekuensi rendah dan nominal menengah, karena mereka memiliki micro-spending rate tertinggi.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.caption("📅 Dataset: centsaver_master_relabelling.csv | 16.953 baris | 2015–2025 | CentSaver")