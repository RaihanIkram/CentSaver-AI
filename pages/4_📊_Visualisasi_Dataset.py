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
    .flag-danger { color: #ef4444; font-weight: 600; }
    .flag-warning { color: #f59e0b; font-weight: 600; }
    .flag-safe { color: #10b981; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("📊 Visualisasi Dataset & Business Questions")
st.caption("Hasil analisis data transaksi 10 tahun (2015-2025).")

# ============================================================================
# MOCK DATA 
# ============================================================================
df = pd.read_csv("data/centsaver_master_relabelling.csv")
df["date"] = pd.to_datetime(df["date"])
df["period_str"] = df["date"].dt.to_period("M").astype(str)
df["day_name"] = df["date"].dt.day_name()
df["day_type"] = df["day_name"].apply(lambda x: "Weekend" if x in ["Saturday","Sunday"] else "Weekday")
df["is_micro"] = df["label"] == 1

# --- MOCK DATA DARI NOTEBOOK EDA ---
np.random.seed(42)

# 1. Kategori TOP 5 + Lainnya
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

# 2. Micro-spending ratio
micro_ratio = pd.DataFrame({
    "category": [
        "Hobi & Olahraga", "Keluarga & Sosial", "Kesehatan", "Perjalanan",
        "Kebutuhan Rumah Tangga", "Sewa & Cicilan", "Lainnya",
        "Pendidikan", "Kopi & Minuman", "Belanja & Lifestyle"
    ],
    "avg_micro_pct": [42.59, 20.82, 17.20, 14.90, 14.09, 13.57, 12.55, 12.07, 11.84, 9.76],
    "flagged": [True, True, False, False, False, False, False, False, False, False]
})

# 3. Anomaly rate (dari Quest #3 notebook, hal 31-34)
anomaly_data = pd.DataFrame({
    "category": [
        "Belanja & Lifestyle", "Hiburan & Gaya Hidup", "Kecantikan & Perawatan",
        "Transportasi", "Pendidikan", "Hobi & Olahraga",
        "Elektronik", "Keluarga & Sosial"
    ],
    "anomaly_rate": [0.0738, 0.0659, 0.0598, 0.0584, 0.0563, 0.0548, 0.0526, 0.0502],
    "max_growth": [13.25, 6.25, 75.44, 0.00, 0.00, 8.33, 5.26, 4.17]
})

# 4. Weekend impulse (dari Quest #3 notebook, hal 31-34)
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
    st.markdown("### 📈 Ringkasan")
    kpi_cols = st.columns(4)
    kpis = [
        ("💰 Total", "Rp 4.38 M", "10 tahun"),
        ("📝 Transaksi", "16,953", "87.8% normal"),
        ("⚠️ Leakage", "2 kategori", ">20% micro"),
        ("🎯 Akurasi", "91.88%", "model RF")
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
            <div class="insight-title">💡 Temuan</div>
            <div class="insight-body">
                Makanan & Minuman paling besar (26.7%). Sisanya digabung jadi "Lainnya" biar tidak terlalu ramai. Sewa & Cicilan nominalnya gede tapi jarang — biasanya bayar tahunan.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.subheader("📊 Micro-Spending Ratio")

        colors = ["#ef4444" if f else "#3b82f6" for f in micro_ratio["flagged"]]
        fig_micro = px.bar(
            micro_ratio, y="category", x="avg_micro_pct",
            orientation="h", color="flagged",
            color_discrete_map={True: "#ef4444", False: "#3b82f6"},
            text=micro_ratio["avg_micro_pct"].apply(lambda x: f"{x:.1f}%")
        )
        fig_micro.add_vline(x=20, line_dash="dash", line_color="#f59e0b", 
                           annotation_text="Batas 20%", annotation_position="top")
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
            <div class="insight-title">💡 Temuan</div>
            <div class="insight-body">
                Hobi & Olahraga 42.6% — hampir separuh! Keluarga & Sosial juga kena 20.8%. Rata-rata keseluruhan cuma 6.5%, jadi kalau pakai batas yang sama buat semua kategori, banyak yang lolos.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- ROW 2: 2 CHART ---
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("🔥 Anomaly Rate")

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
            <div class="insight-title">💡 Temuan</div>
            <div class="insight-body">
                Belanja & Lifestyle paling tidak stabil — 7.4% bulannya anomali. Lonjakannya bisa 13x dari bulan sebelumnya. Ini yang paling susah diprediksi.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right2:
        st.subheader("⚡ Weekend Impulse")

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
            <div class="insight-title">💡 Temuan</div>
            <div class="insight-body">
                Transportasi naik 63% di akhir pekan. Langganan Digital juga naik 62%. Orang lebih sering beli pulsa/streaming pas Sabtu-Minggu.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- EDA EXPANDER ---
    with st.expander("🔬 Detail EDA (untuk reviewer)", expanded=False):
        st.caption("Data lengkap ada di notebook. Ini ringkasannya.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background: #1e293b; padding: 0.8rem; border-radius: 8px; font-size: 0.8rem; color: #cbd5e1;">
                <b>Distribusi Label</b><br>
                Normal: 87.83% (14,892)<br>
                Micro: 12.17% (2,061)
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background: #1e293b; padding: 0.8rem; border-radius: 8px; font-size: 0.8rem; color: #cbd5e1;">
                <b>RFM Segment</b><br>
                Occasional-Medium: 35% micro<br>
                Frequent-Premium: 4% micro
            </div>
            """, unsafe_allow_html=True)

        st.caption("📅 Dataset: centsaver_master_relabelling.csv | 16,953 baris | 2015-2025")

# =============================================================================
# TAB 2: BUSINESS QUESTIONS 
# =============================================================================
with tab_bq:
    st.markdown("## 💡 Business Questions")
    st.caption("Tiga pertanyaan utama dari analisis data.")
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- RQ 1 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ1</span> 
        Seberapa besar dampak pengeluaran kecil yang tidak disadari terhadap total pengeluaran bulanan pengguna</div>
        <div class="bq-answer">
            <b>Kalau dirata-rata, cuma 6.5%.</b> Tapi jangan percaya rata-rata.<br><br>
            Di kategori Hobi & Olahraga, pengeluaran kecilnya 42.6% — hampir separuh! Keluarga & Sosial juga 20.8%. Jadi kalau pakai batas 20% untuk semua kategori, Hobi bakal lolos terus.<br><br>
            <b>Solusi:</b> Batasnya harus beda tiap kategori. Kalau Hobi sudah lebih dari 30% micro-spending, kasih peringatan.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RQ 2 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ2</span> 
        Mampukah model AI sederhana secara otomatis dan akurat membedakan pengeluaran impulsif dengan transaksi kebutuhan pokok</div>
        <div class="bq-answer">
            <b>Bisa, 91.88% akurat.</b> Targetnya cuma 85%, jadi ini lebih dari cukup.<br><br>
            Model belajar dari 3 pola: nominal transaksi, waktu (weekday/weekend), dan kategori. Dari 100 transaksi impulsif, model bisa nangkep 83. Sisanya 17 mungkin lolos — tapi sudah jauh lebih baik daripada tidak ada deteksi sama sekali.<br><br>
            <b>Solusi:</b> Tiap kali user input transaksi baru, model cek dalam 0.5 detik. Kalau terdeteksi impulsif, muncul pop-up: "Yakin lanjut? Ini terdeteksi sebagai pengeluaran impulsif."
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RQ 3 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ3</span> 
        Fitur interaktif apa yang paling efektif dalam meningkatkan kesadaran pengelolaan keuangan pengguna</div>
        <div class="bq-answer">
            <b>Heatmap pertumbuhan bulanan (MoM Growth).</b> Kenapa? Karena manusia lebih cepat tangkap warna daripada angka.<br><br>
            Bayangin buka dashboard, terus lihat ada kotak merah di kategori Belanja. Langsung ngeh — "Wah, belanjaku naik nih!" Kalau cuma tabel angka, banyak yang tidak sadar.<br><br>
            <b>Urutan efektivitas:</b><br>
            1. Heatmap MoM Growth — sadar dalam 1 detik<br>
            2. Grafik garis + titik anomali — tahu kapan mulai "salah"<br>
            3. Batang anomaly rate — bandingkan antar kategori<br>
            4. Weekend boost — sadar pola mingguan<br><br>
            <b>Solusi:</b> Heatmap ditaruh paling atas dashboard. Kalau ada kotak merah, langsung kirim notifikasi: "Pengeluaran [Kategori] naik 25% bulan ini. Cek detailnya."
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
                <li>Pengeluaran kecil itu berbahaya. Rata-rata 6.5%, tapi Hobi bisa 42.6%.</li>
                <li>Model AI akurat 91.88%. Siap dipakai di aplikasi nyata.</li>
                <li>Warna lebih powerful daripada angka. Heatmap paling efektif.</li>
                <li>Tiap kategori beda. Batas harus disesuaikan, bukan satu aturan.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with con2:
        st.markdown("""
        <div style="background-color: #1e293b; padding: 1rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
            <h4 style="color: #fbbf24; margin-bottom: 0.6rem; font-size: 0.95rem;">💡 Rekomendasi</h4>
            <ul style="color: #cbd5e1; font-size: 0.82rem; line-height: 1.6; padding-left: 1.2rem;">
                <li>Batas pengeluaran dinamis per kategori. Hobi & Keluarga paling ketat.</li>
                <li>Tracker real-time: total micro-spending hari ini di dashboard.</li>
                <li>Notifikasi pintar: kalau ada lonjakan >20% dari bulan lalu.</li>
                <li>Tantangan hemat: "7 hari tanpa micro-spending" untuk user sering kena peringatan.</li>
                <li>Reward loyal: user yang konsisten hemat dikasih reward.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.caption("📅 Dataset: centsaver_master_relabelling.csv | 16,953 baris | 2015-2025 | CentSaver")