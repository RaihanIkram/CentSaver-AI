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
        padding: 1.2rem;
        border-left: 4px solid #7c3aed;
        margin-top: 0.8rem;
    }
    .insight-title {
        color: #a78bfa;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }
    .insight-body {
        color: #cbd5e1;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .bq-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .bq-question {
        color: #7dd3fc;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.6rem;
    }
    .bq-answer {
        color: #e2e8f0;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .rq-badge {
        display: inline-block;
        background-color: #7c3aed;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .section-divider {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #475569, transparent);
    }
    .kpi-highlight {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #334155;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }
    .flag-danger {
        color: #ef4444;
        font-weight: 600;
    }
    .flag-warning {
        color: #f59e0b;
        font-weight: 600;
    }
    .flag-safe {
        color: #10b981;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("📊 Visualisasi Dataset & Business Questions")
st.caption("Eksplorasi data transaksi dan jawaban atas pertanyaan bisnis berdasarkan analisis EDA.")

# ============================================================================
# MOCK DATA
# ============================================================================
df = pd.read_csv("data/centsaver_master_relabelling.csv")
df["date"] = pd.to_datetime(df["date"])
df["period_str"] = df["date"].dt.to_period("M").astype(str)
df["day_name"] = df["date"].dt.day_name()
df["day_type"] = df["day_name"].apply(lambda x: "Weekend" if x in ["Saturday","Sunday"] else "Weekday")
df["is_micro"] = df["label"] == 1

# --- MOCK DATA BERDASARKAN HASIL NOTEBOOK ---
np.random.seed(42)

# 1. Kategori TOP 5 + Lainnya (dari notebook Section 3)
# Top 5: Makanan & Minuman, Kebutuhan Dapur, Belanja & Lifestyle, Sewa & Cicilan, Tagihan Utilitas
# Sisanya digabung jadi "Lainnya"
top5_cats = pd.DataFrame({
    "category": [
        "Makanan & Minuman", "Kebutuhan Dapur", "Belanja & Lifestyle",
        "Sewa & Cicilan", "Tagihan Utilitas", "Lainnya"
    ],
    "total_amount": [
        1_169_127_987, 406_811_878, 384_771_273,
        299_748_200, 292_725_380, 1_827_068_282  # total sisanya
    ],
    "txn_count": [4374, 1948, 1049, 211, 891, 8480],
    "avg_amount": [267_290, 208_836, 366_798, 1_420_608, 328_536, 215_456]
})
top5_cats["percentage"] = (top5_cats["total_amount"] / top5_cats["total_amount"].sum() * 100).round(1)

# 2. Micro-spending ratio per kategori (dari Quest #1)
micro_ratio = pd.DataFrame({
    "category": [
        "Hobi & Olahraga", "Keluarga & Sosial", "Kesehatan", "Perjalanan",
        "Kebutuhan Rumah Tangga", "Sewa & Cicilan", "Lainnya",
        "Pendidikan", "Kopi & Minuman", "Belanja & Lifestyle"
    ],
    "avg_micro_pct": [42.59, 20.82, 17.20, 14.90, 14.09, 13.57, 12.55, 12.07, 11.84, 9.76],
    "flagged": [True, True, False, False, False, False, False, False, False, False]
})

# 3. Anomaly rate per kategori (dari Quest #3)
anomaly_data = pd.DataFrame({
    "category": [
        "Belanja & Lifestyle", "Hiburan & Gaya Hidup", "Kecantikan & Perawatan",
        "Transportasi", "Pendidikan", "Hobi & Olahraga",
        "Elektronik", "Keluarga & Sosial"
    ],
    "anomaly_rate": [0.0738, 0.0659, 0.0598, 0.0584, 0.0563, 0.0548, 0.0526, 0.0502],
    "max_growth": [13.25, 6.25, 75.44, 0.00, 0.00, 8.33, 5.26, 4.17]
})

# 4. Weekend impulse (dari Quest #3)
weekend_impulse = pd.DataFrame({
    "category": ["Transportasi", "Langganan Digital", "Kopi & Minuman", "Makanan & Minuman", 
                 "Hiburan & Gaya Hidup", "Belanja & Lifestyle", "Elektronik"],
    "weekend_boost": [0.63, 0.62, 0.43, 0.40, 0.35, 0.28, 0.15]
})

# 5. RFM Segment
rfm_data = pd.DataFrame({
    "segment": ["Occasional-Medium", "Rare-Low", "Regular-Low", "Frequent-Premium"],
    "micro_rate": [0.35, 0.33, 0.18, 0.04],
    "count": [320, 482, 280, 150],
    "risk_level": ["🔴 High", "🟡 Medium", "🟡 Medium", "🟢 Low"]
})

# 6. Model performance
model_metrics = pd.DataFrame({
    "metric": ["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"],
    "value": [0.9188, 0.62, 0.83, 0.71, 0.973],
    "target": [0.85, 0.60, 0.70, 0.65, 0.90],
    "status": ["✅ Pass", "✅ Pass", "✅ Pass", "✅ Pass", "✅ Pass"]
})

# ============================================================================
# TABS UTAMA
# ============================================================================
tab_viz, tab_bq = st.tabs(["📊 Visualisasi Dataset", "💡 Business Questions"])

# =============================================================================
# TAB 1: VISUALISASI DATASET (4 CHART)
# =============================================================================
with tab_viz:

    # --- KPI CARDS ---
    st.markdown("### 📈 Ringkasan Metrik")
    kpi_cols = st.columns(4)
    kpis = [
        ("💰 Total", "Rp 4.38 M", "10 tahun data"),
        ("📝 Transaksi", "16,953", "60.97% micro-spending"),
        ("⚠️ Leakage Bucket", "2 kategori", ">20% threshold"),
        ("🎯 Model Acc", "91.88%", "RF Anti-Leakage")
    ]
    for col, (icon, val, lbl) in zip(kpi_cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-highlight">
                <div style="font-size: 1.2rem;">{icon}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- ROW 1: 2 CHART ---
    left, right = st.columns(2)

    with left:
        st.subheader("🥧 Distribusi Kategori (Top 5 + Lainnya)")

        fig_pie = go.Figure(data=[go.Pie(
            labels=top5_cats["category"],
            values=top5_cats["total_amount"],
            hole=0.45,
            textinfo="label+percent",
            textposition="outside",
            pull=[0.05, 0, 0, 0, 0, 0],
            marker_colors=["#7c3aed", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#64748b"],
            textfont=dict(size=11, color="#f8fafc"),
            hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>"
        )])
        fig_pie.update_layout(
            showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"),
            height=360, uniformtext_minsize=10, uniformtext_mode="hide"
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">💡 Insight</div>
            <div class="insight-body">
                <b>Makanan & Minuman</b> mendominasi total amount (Rp 1.17M) dan jumlah transaksi (4,374). 
                Sisanya digabung dalam kategori <b>Lainnya</b> (Rp 1.83M) yang mencakup 8 kategori lainnya.
                <b>Sewa & Cicilan</b> memiliki rata-rata transaksi tertinggi (Rp 1.42M) namun frekuensi rendah — pola <i>bulk payment</i>.
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
        fig_micro.add_vline(x=20, line_dash="dash", line_color="#f59e0b", 
                           annotation_text="Threshold 20%", annotation_position="top")
        fig_micro.update_traces(
            textposition="outside", textfont=dict(size=10, color="#f8fafc"),
            hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>"
        )
        fig_micro.update_layout(
            xaxis_title="Rata-rata Micro-Spending (%)", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=10), height=360,
            showlegend=False, margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
            yaxis=dict(gridcolor="rgba(148,163,184,0.1)", categoryorder="total ascending")
        )
        st.plotly_chart(fig_micro, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">💡 Insight</div>
            <div class="insight-body">
                <span class="flag-danger">Hobi & Olahraga (42.59%)</span> dan 
                <span class="flag-danger">Keluarga & Sosial (20.82%)</span> melebihi threshold 20%.
                Rata-rata keseluruhan hanya 6.50% — <b>threshold global menipu</b>, pendekatan category-aware jauh lebih esensial.
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
            textposition="outside", textfont=dict(size=10, color="#f8fafc"),
            hovertemplate="<b>%{y}</b><br>%{x:.2%}<extra></extra>"
        )
        fig_anom.update_layout(
            xaxis_title="Anomaly Rate (Proporsi Bulan Anomali)", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=10), height=360,
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
                <b>Belanja & Lifestyle</b> paling volatile (7.37% anomaly rate, max growth 13.25x).
                Lonjakan sporadis di kategori ini adalah <b>primary trigger</b> untuk rekomendasi AI Chatbot.
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
            textposition="outside", textfont=dict(size=10, color="#f8fafc"),
            hovertemplate="<b>%{y}</b><br>+%{x:.0%}<extra></extra>"
        )
        fig_wknd.update_layout(
            xaxis_title="Selisih Risk Rate (Weekend - Weekday)", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=10), height=360,
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
                <b>Transportasi</b> dan <b>Langganan Digital</b> memiliki weekend boost tertinggi.
                Ini mengindikasikan <b>temporal vulnerability window</b> di akhir pekan yang harus ditangkap Chatbot.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- EDA EXPANDER ---
    with st.expander("🔬 Lihat Detail EDA (Statistik Deskriptif & Distribusi)", expanded=False):
        st.caption("Bagian teknis untuk validasi data. Tidak ditampilkan di dashboard utama.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background: #1e293b; padding: 1rem; border-radius: 8px;">
                <h4 style="color: #a78bfa; font-size: 0.9rem;">📊 Distribusi Label</h4>
                <table style="width:100%; color: #cbd5e1; font-size: 0.85rem;">
                    <tr><td>Normal (0)</td><td style="text-align:right"><b>87.83%</b> (14,892)</td></tr>
                    <tr><td>Micro-Spending (1)</td><td style="text-align:right"><b style="color:#ef4444">12.17%</b> (2,061)</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background: #1e293b; padding: 1rem; border-radius: 8px;">
                <h4 style="color: #a78bfa; font-size: 0.9rem;">📊 RFM Segment</h4>
                <table style="width:100%; color: #cbd5e1; font-size: 0.85rem;">
                    <tr><td>Occasional-Medium</td><td style="text-align:right"><span class="flag-danger">35% micro</span></td></tr>
                    <tr><td>Frequent-Premium</td><td style="text-align:right"><span class="flag-safe">4% micro</span></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        hist_vals = np.concatenate([
            np.random.exponential(35_000, 1200),
            np.random.exponential(250_000, 3000),
            np.random.exponential(1_500_000, 200)
        ])
        fig_hist = px.histogram(
            x=hist_vals, nbins=50, color_discrete_sequence=["#3b82f6"],
            labels={"x": "Nominal Transaksi (Rp)", "y": "Frekuensi"}
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc"), height=300,
            margin=dict(t=10, b=40, l=60, r=10),
            xaxis=dict(gridcolor="rgba(148,163,184,0.1)", tickformat="Rp ,.0f"),
            yaxis=dict(gridcolor="rgba(148,163,184,0.1)")
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    st.caption("📅 Dataset: centsaver_master_relabelling.csv | 16,953 baris | 2015-01-13 → 2025-12-30")

# =============================================================================
# TAB 2: BUSINESS QUESTIONS
# =============================================================================
with tab_bq:
    st.markdown("## 💡 Business Questions")
    st.caption("Tiga pertanyaan bisnis yang dijawab berdasarkan hasil analisis EDA dan modeling.")
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- RQ 1 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ1</span> 
        Seberapa besar dampak pengeluaran kecil yang tidak disadari terhadap total pengeluaran bulanan pengguna</div>
        <div class="bq-answer">
            <b>Jawaban:</b> Rata-rata micro-spending per bulan secara keseluruhan adalah <b>6.50%</b>, yang berada di bawah batas toleransi 20%. Namun, angka agregat ini sangat <b>menipu</b> karena menyembunyikan disparitas ekstrem antar kategori.<br><br>
            <table style="width:100%; color:#cbd5e1; font-size:0.88rem; margin: 0.8rem 0;">
                <tr style="border-bottom: 1px solid #475569;">
                    <td><b>Kategori</b></td><td style="text-align:right"><b>Micro-Spending %</b></td><td style="text-align:right"><b>Status</b></td>
                </tr>
                <tr><td>Hobi & Olahraga</td><td style="text-align:right" class="flag-danger">42.59%</td><td style="text-align:right" class="flag-danger">⚠️ FLAGGED</td></tr>
                <tr><td>Keluarga & Sosial</td><td style="text-align:right" class="flag-danger">20.82%</td><td style="text-align:right" class="flag-danger">⚠️ FLAGGED</td></tr>
                <tr><td>Kesehatan</td><td style="text-align:right">17.20%</td><td style="text-align:right" class="flag-safe">✅ Normal</td></tr>
                <tr><td>Perjalanan</td><td style="text-align:right">14.90%</td><td style="text-align:right" class="flag-safe">✅ Normal</td></tr>
                <tr><td>Belanja & Lifestyle</td><td style="text-align:right">9.76%</td><td style="text-align:right" class="flag-safe">✅ Normal</td></tr>
            </table>
            <b>Bukti Visual:</b> Chart <i>Micro-Spending Ratio per Kategori</i> (Tab Visualisasi) menunjukkan dua kategori yang melebihi threshold 20%.<br><br>
            <b>Implikasi Bisnis:</b> <b>Threshold global tidak efektif.</b> Pendekatan <i>category-aware baseline</i> (menggunakan Q25 dan median harian per kategori) jauh lebih esensial untuk mendeteksi akumulasi micro-spending yang sering "tertutup" oleh nominal besar di kategori lain. Sistem harus mengirim alert khusus untuk kategori flagged dengan format: <i>"Anda memiliki X transaksi kecil di [Kategori] minggu ini. Total akumulasi: Rp Y. Consider bundling your purchases."</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RQ 2 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ2</span> 
        Mampukah model AI sederhana secara otomatis dan akurat membedakan pengeluaran impulsif dengan transaksi kebutuhan pokok</div>
        <div class="bq-answer">
            <b>Jawaban:</b> <b>Ya, model memenuhi target.</b> Arsitektur Deep Learning (CentSaver) mencapai akurasi <b>88.5%</b> dengan status "Memenuhi Target ≥85%". Untuk memastikan validitas independen, tim Data Science juga membangun <b>baseline Random Forest dengan pendekatan anti-leakage</b> (tidak menggunakan fitur turunan dari definisi target seperti amount_ratio atau amount_zscore).<br><br>
            <table style="width:100%; color:#cbd5e1; font-size:0.88rem; margin: 0.8rem 0;">
                <tr style="border-bottom: 1px solid #475569;">
                    <td><b>Metrik</b></td><td style="text-align:right"><b>RF Baseline</b></td><td style="text-align:right"><b>Target</b></td><td style="text-align:right"><b>Status</b></td>
                </tr>
                <tr><td>Accuracy</td><td style="text-align:right" class="flag-safe"><b>91.88%</b></td><td style="text-align:right">≥ 85%</td><td style="text-align:right" class="flag-safe">✅ Pass</td></tr>
                <tr><td>Precision (Micro)</td><td style="text-align:right">62.00%</td><td style="text-align:right">—</td><td style="text-align:right" class="flag-warning">⚠️ Moderate</td></tr>
                <tr><td>Recall (Micro)</td><td style="text-align:right" class="flag-safe"><b>83.00%</b></td><td style="text-align:right">≥ 70%</td><td style="text-align:right" class="flag-safe">✅ Pass</td></tr>
                <tr><td>F1-Score</td><td style="text-align:right">71.00%</td><td style="text-align:right">—</td><td style="text-align:right" class="flag-safe">✅ Solid</td></tr>
                <tr><td>AUC-ROC</td><td style="text-align:right" class="flag-safe"><b>97.30%</b></td><td style="text-align:right">≥ 90%</td><td style="text-align:right" class="flag-safe">✅ Excellent</td></tr>
            </table>
            <b>Bukti Visual:</b> ROC Curve dengan AUC 0.973 (hampir sempurna) dan Confusion Matrix yang menunjukkan keseimbangan false positive/negative.<br><br>
            <b>Implikasi Bisnis:</b> Hasil baseline RF yang setara (91.88% vs 88.5% DL) membuktikan bahwa arah feature engineering tidak mengalami <i>overfit</i> pada signal artifisial. Fitur behavioral (nominal, waktu, kategori) sudah cukup kuat untuk prediksi yang valid secara eksternal. <b>Rekomendasi:</b> Deploy model ke FastAPI endpoint dengan threshold guard 85%–95% untuk keseimbangan precision-recall, dan retrain bulanan berbasis drift detection.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RQ 3 ---
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question"><span class="rq-badge">RQ3</span> 
        Fitur interaktif apa yang paling efektif dalam meningkatkan kesadaran pengelolaan keuangan pengguna</div>
        <div class="bq-answer">
            <b>Jawaban:</b> <b>Heatmap Month-over-Month (MoM) Growth</b> adalah visualisasi paling signifikan dengan korelasi <b>0.71</b> terhadap risk rate aktual. Heatmap ini bekerja secara spasial dengan menonjolkan sel-sel berwarna kontras (hotspot) yang merepresentasikan lonjakan di atas baseline historis per kategori.<br><br>
            <b>Hierarki Visualisasi Dashboard (berdasarkan trigger strength):</b><br>
            <table style="width:100%; color:#cbd5e1; font-size:0.88rem; margin: 0.8rem 0;">
                <tr style="border-bottom: 1px solid #475569;">
                    <td><b>Prioritas</b></td><td><b>Visualisasi</b></td><td><b>Trigger</b></td><td><b>Fungsi</b></td>
                </tr>
                <tr><td>🥇 HERO</td><td>Heatmap MoM Growth</td><td>"Lonjakan X% di [Kategori]"</td><td>Paling cepat memicu awareness</td></tr>
                <tr><td>🥈 SUPPORTING</td><td>Line Chart + Anomaly Marker</td><td>"Pola tidak normal"</td><td>Konteks historis & seasonality</td></tr>
                <tr><td>🥉 SECONDARY</td><td>Bar Chart Anomaly Rate</td><td>"Kategori ini volatile"</td><td>Perbandingan antar kategori</td></tr>
                <tr><td>4️⃣ CONTEXT</td><td>Weekend Impulse Boost</td><td>"Weekend boost terdeteksi"</td><td>Behavioral pattern</td></tr>
            </table>
            <b>Bukti Visual:</b> Chart <i>Anomaly Rate per Kategori</i> dan <i>Weekend Impulse Boost</i> (Tab Visualisasi).<br><br>
            <b>Implikasi Bisnis:</b> Heatmap MoM Growth harus ditempatkan di <b>hero section</b> dashboard. Aktifkan Chatbot suggestion otomatis saat MoM Growth &gt;20% dengan risk correlation ≥0.7. Tambahkan <i>weekend highlight zone</i> di Line Chart untuk memperjelas pola impulsivitas. Kategori <b>Belanja & Lifestyle</b> (7.37% anomaly rate) dan <b>Transportasi</b> (+63% weekend boost) adalah priority target untuk notifikasi real-time.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- KESIMPULAN & REKOMENDASI ---
    st.markdown("### 🎯 Kesimpulan & Rekomendasi Strategis")

    con1, con2 = st.columns(2)

    with con1:
        st.markdown("""
        <div style="background-color: #1e293b; padding: 1.2rem; border-radius: 12px; border-left: 4px solid #10b981;">
            <h4 style="color: #34d399; margin-bottom: 0.8rem; font-size: 1rem;">✅ Kesimpulan Utama</h4>
            <ul style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.7; padding-left: 1.2rem;">
                <li><b>RQ1:</b> Micro-spending ratio 6.50% overall, tapi <b>Hobi & Olahraga (42.59%)</b> dan <b>Keluarga & Sosial (20.82%)</b> adalah leakage bucket serius. Threshold global tidak efektif.</li>
                <li><b>RQ2:</b> Model DL 88.5% acc, RF baseline 91.88% — <b>memenuhi target ≥85%</b>. AUC 0.973 menunjukkan confidence ranking sangat kuat.</li>
                <li><b>RQ3:</b> <b>Heatmap MoM Growth</b> (korelasi 0.71) adalah visualisasi paling signifikan untuk memicu rekomendasi AI Chatbot.</li>
                <li><b>RFM:</b> Segmen <b>Occasional-Medium</b> adalah hidden risk (35% micro rate) — target utama edukasi finansial.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with con2:
        st.markdown("""
        <div style="background-color: #1e293b; padding: 1.2rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
            <h4 style="color: #fbbf24; margin-bottom: 0.8rem; font-size: 1rem;">💡 Rekomendasi Action</h4>
            <ul style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.7; padding-left: 1.2rem;">
                <li><b>Budget Cap Dinamis:</b> Per kategori (bukan global), fokus pada Hobi & Olahraga + Keluarga & Sosial.</li>
                <li><b>Micro-Spending Tracker:</b> Real-time accumulation tracker di dashboard dengan alert saat melebihi Q25 harian per kategori.</li>
                <li><b>Chatbot Trigger:</b> Aktifkan saat MoM Growth &gt;20% atau weekend boost terdeteksi.</li>
                <li><b>Gamification:</b> Program "Micro-Spending Challenge" untuk segmen Occasional-Medium.</li>
                <li><b>Retensi:</b> Loyalty reward untuk Frequent-Premium agar tidak churn.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.caption("📅 Dataset: centsaver_master_relabelling.csv | 16,953 baris | 2015-01-13 → 2025-12-30 | CentSaver © 2026")