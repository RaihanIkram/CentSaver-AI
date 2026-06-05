import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats


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
tab_viz, tab_bq = st.tabs(["📊 Visualisasi Dataset", "💡 Pertanyaan Bisnis"])

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

def render_business_questions(df):
    # ============================================================
    # SAFETY PREP
    # ============================================================
    df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if "label" not in df.columns:
        st.error("Kolom 'label' tidak ditemukan di dataframe.")
        return

    df["label"] = df["label"].fillna(0).astype(int)

    if "amount_log" not in df.columns:
        df["amount_log"] = np.log1p(df["amount"])

    if "amount_winsorized" not in df.columns:
        q_low = df["amount"].quantile(0.005)
        q_high = df["amount"].quantile(0.995)
        df["amount_winsorized"] = df["amount"].clip(q_low, q_high)

    if "is_weekend" not in df.columns:
        df["is_weekend"] = (df["date"].dt.dayofweek >= 5).astype(int)

    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["date"].dt.dayofweek

    if "day_type" not in df.columns:
        df["day_type"] = np.where(df["is_weekend"] == 1, "Weekend", "Weekday")

    # Period bulanan untuk analisis sesuai notebook
    df["period_dt"] = df["date"].dt.to_period("M").dt.to_timestamp()

    # ============================================================
    # STYLE
    # ============================================================
    st.markdown("""
    <style>
    .bq-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(15,23,42,0.86));
        border: 1px solid rgba(148,163,184,0.25);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    .bq-question {
        font-size: 1.02rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .bq-answer {
        color: #cbd5e1;
        font-size: 0.93rem;
        line-height: 1.8;
    }
    .rq-badge {
        display: inline-block;
        padding: 0.18rem 0.55rem;
        border-radius: 999px;
        background: linear-gradient(90deg, #7c3aed, #a855f7);
        color: white;
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(148,163,184,0), rgba(148,163,184,0.35), rgba(148,163,184,0));
        margin: 18px 0 24px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # HEADER
    # ============================================================
    st.markdown("## 💡 Pertanyaan Bisnis")
    st.caption("Tiga pertanyaan utama dari analisis EDA.")
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ============================================================
    # RQ1 - MICRO-SPENDING RATIO
    # ============================================================
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

    THRESHOLD = 20

    monthly_micro = (
        df.groupby(["period_dt", "category"])
        .agg(
            total_monthly=("amount", "sum"),
            micro_monthly=("amount", lambda s: s[df.loc[s.index, "label"] == 1].sum()),
            txn_count=("amount", "size"),
            micro_count=("label", "sum"),
        )
        .reset_index()
        .sort_values(["period_dt", "category"])
    )

    monthly_micro["micro_pct"] = (monthly_micro["micro_monthly"] / monthly_micro["total_monthly"] * 100).fillna(0)
    monthly_micro["micro_pct"] = monthly_micro["micro_pct"].clip(0, 100)

    overall_monthly = (
        df.groupby("period_dt")
        .agg(
            total_monthly=("amount", "sum"),
            micro_monthly=("amount", lambda s: s[df.loc[s.index, "label"] == 1].sum()),
        )
        .reset_index()
        .sort_values("period_dt")
    )
    overall_monthly["micro_pct"] = (overall_monthly["micro_monthly"] / overall_monthly["total_monthly"] * 100).fillna(0)

    avg_micro_by_cat = (
        monthly_micro.groupby("category")
        .agg(
            avg_micro_pct=("micro_pct", "mean"),
            median_micro_pct=("micro_pct", "median"),
            max_micro_pct=("micro_pct", "max"),
            support=("micro_pct", "size"),
        )
        .sort_values("avg_micro_pct", ascending=False)
        .reset_index()
    )

    flagged_cats = avg_micro_by_cat.loc[avg_micro_by_cat["avg_micro_pct"] > THRESHOLD, "category"].tolist()

    c1, c2, c3 = st.columns(3)
    c1.metric("Rata-rata micro-spending bulanan", f"{overall_monthly['micro_pct'].mean():.2f}%")
    c2.metric("Kategori di atas threshold", f"{len(flagged_cats)}")
    c3.metric("Threshold analisis", f"{THRESHOLD}%")

    with st.expander("📊 Lihat Visualisasi RQ1", expanded=False):

        st.markdown("### 📊 Dampak Micro-Spending terhadap Pengeluaran Bulanan")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=overall_monthly["period_dt"],
            y=overall_monthly["micro_pct"],
            mode="lines+markers",
            name="Persentase Micro-Spending",
            line=dict(width=3),
            hovertemplate="%{x|%Y-%m}<br>Micro-spending: %{y:.2f}%<extra></extra>",
        ))
        fig1.add_hline(
            y=THRESHOLD,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Ambang {THRESHOLD}%",
            annotation_position="top left",
        )
        fig1.update_layout(
            title="A. Proporsi Micro-Spending terhadap Total Pengeluaran Bulanan",
            template="plotly_dark",
            height=420,
            hovermode="x unified",
            margin=dict(l=30, r=20, t=60, b=30),
        )
        fig1.update_xaxes(dtick="M12", tickformat="%Y", title="Tahun")
        fig1.update_yaxes(title="Persentase (%)")
        st.plotly_chart(fig1, use_container_width=True)

        top10 = avg_micro_by_cat.head(10).copy()
        top10["color"] = np.where(top10["category"].isin(flagged_cats), "crimson", "steelblue")

        fig2 = go.Figure(go.Bar(
            x=top10["avg_micro_pct"][::-1],
            y=top10["category"][::-1],
            orientation="h",
            marker_color=top10["color"][::-1],
            hovertemplate="%{y}<br>Rata-rata micro-spending: %{x:.2f}%<extra></extra>",
            name="Rata-rata micro-spending",
        ))
        fig2.add_vline(x=THRESHOLD, line_dash="dash", line_color="red")
        fig2.update_layout(
            title="B. Rata-rata Persentase Micro-Spending per Kategori",
            template="plotly_dark",
            height=420,
            margin=dict(l=30, r=20, t=60, b=30),
            showlegend=False,
        )
        fig2.update_xaxes(title="Persentase (%)")
        fig2.update_yaxes(title="")
        st.plotly_chart(fig2, use_container_width=True)

        top5_micro_cats = avg_micro_by_cat.head(5)["category"].tolist()
        stacked = (
            monthly_micro[monthly_micro["category"].isin(top5_micro_cats)]
            .groupby("period_dt")
            .agg(
                micro=("micro_monthly", "sum"),
                total=("total_monthly", "sum"),
            )
            .reset_index()
            .sort_values("period_dt")
        )
        stacked["non_micro"] = stacked["total"] - stacked["micro"]

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=stacked["period_dt"],
            y=stacked["micro"],
            mode="lines",
            name="Micro-spending",
            stackgroup="one",
            line=dict(width=0.8),
            hovertemplate="%{x|%Y-%m}<br>Micro: Rp %{y:,.0f}<extra></extra>",
        ))
        fig3.add_trace(go.Scatter(
            x=stacked["period_dt"],
            y=stacked["non_micro"],
            mode="lines",
            name="Non-Micro",
            stackgroup="one",
            line=dict(width=0.8),
            hovertemplate="%{x|%Y-%m}<br>Non-Micro: Rp %{y:,.0f}<extra></extra>",
        ))
        fig3.update_layout(
            title="C. Akumulasi Pengeluaran pada 5 Kategori Micro-Spending Teratas",
            template="plotly_dark",
            height=420,
            hovermode="x unified",
            margin=dict(l=30, r=20, t=60, b=30),
        )
        fig3.update_xaxes(dtick="M12", tickformat="%Y", title="Tahun")
        fig3.update_yaxes(title="Nominal (Rp)")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # ============================================================
    # RQ2 - KARAKTERISTIK MICRO-SPENDING VS NORMAL
    # ============================================================
    st.markdown("""
<div class="bq-card">
    <div class="bq-question">
        <span class="rq-badge">RQ2</span>
        Apa karakteristik yang membedakan transaksi micro-spending dengan transaksi normal?
    </div>
    <div class="bq-answer">
        Hasil analisis menunjukkan bahwa transaksi micro-spending memiliki nominal yang jauh lebih kecil
        dibandingkan transaksi normal. Selain itu, micro-spending lebih sering terjadi pada akhir pekan,
        dan beberapa kategori tertentu memiliki tingkat micro-spending yang lebih tinggi.
        <br><br>
        <b>Inti temuan:</b> perbedaan bukan hanya pada nominal, tetapi juga pada pola waktu dan kategori.
        <br>
        <b>Rekomendasi:</b> gunakan kombinasi nominal, waktu transaksi, dan frekuensi kategori sebagai indikator
        untuk deteksi dini micro-spending.
    </div>
</div>
""", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # PREPARASI DATA
    # ------------------------------------------------------------
    micro_df = df[df["label"] == 1].copy()
    normal_df = df[df["label"] == 0].copy()

# Kalau kolom pendukung belum ada, buat dulu
    if "amount_log" not in df.columns:
        df["amount_log"] = np.log1p(df["amount"])

    if "amount_winsorized" not in df.columns:
        q_low = df["amount"].quantile(0.005)
        q_high = df["amount"].quantile(0.995)
        df["amount_winsorized"] = df["amount"].clip(q_low, q_high)

    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["date"].dt.dayofweek

    if "is_weekend" not in df.columns:
        df["is_weekend"] = (df["date"].dt.dayofweek >= 5).astype(int)

    # ------------------------------------------------------------
    # BUKA / TUTUP VISUALISASI
    # ------------------------------------------------------------
    with st.expander("📊 Lihat Visualisasi RQ2", expanded=False):   
        
        # ------------------------------------------------------------
        # TABEL STATISTIK RINGKAS
        # ------------------------------------------------------------
        rq2_summary = pd.DataFrame({
        "Indikator": [
            "Rata-rata nominal",
            "Median nominal",
            "Simpangan baku",
            "Rata-rata log nominal",
            "Rata-rata hari transaksi",
            "Persentase transaksi akhir pekan"
        ],
        "Transaksi Normal": [
            normal_df["amount"].mean(),
            normal_df["amount"].median(),
            normal_df["amount"].std(),
            normal_df["amount_log"].mean(),
            normal_df["day_of_week"].mean(),
            normal_df["is_weekend"].mean() * 100
        ],
        "Micro-spending": [
            micro_df["amount"].mean(),
            micro_df["amount"].median(),
            micro_df["amount"].std(),
            micro_df["amount_log"].mean(),
            micro_df["day_of_week"].mean(),
            micro_df["is_weekend"].mean() * 100
        ]
    })

        st.markdown("### 📌 Ringkasan Statistik")
        st.dataframe(
        rq2_summary.style.format({
            "Transaksi Normal": "Rp {:,.0f}",
            "Micro-spending": "Rp {:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

        # ------------------------------------------------------------
        # UJI STATISTIK
        # ------------------------------------------------------------
        t_stat, p_val = stats.ttest_ind(
            micro_df["amount"],
            normal_df["amount"],
            equal_var=False,
            nan_policy="omit"
    )

        u_stat, u_pval = stats.mannwhitneyu(
        micro_df["amount"],
        normal_df["amount"],
        alternative="two-sided"
    )

        pooled_std = np.sqrt(
        ((len(micro_df) - 1) * micro_df["amount"].var() + (len(normal_df) - 1) * normal_df["amount"].var())
        / (len(micro_df) + len(normal_df) - 2)
    )

        cohens_d = (micro_df["amount"].mean() - normal_df["amount"].mean()) / pooled_std

        st.markdown("### 📊 Hasil Uji Statistik")
        m1, m2, m3 = st.columns(3)
        m1.metric(
        "p-value t-test",
        "< 0.0001" if p_val < 0.0001 else f"{p_val:.4f}"
    )
        m2.metric(
        "p-value Mann-Whitney",
        "< 0.0001" if u_pval < 0.0001 else f"{u_pval:.4f}"
        )
        m3.metric("Cohen's d", f"{cohens_d:.2f}")

        st.caption(
        "Nilai p yang sangat kecil menunjukkan perbedaan yang signifikan antara transaksi micro-spending dan normal."
    )

        # ------------------------------------------------------------
        # VISUALISASI 1 & 2
        # ------------------------------------------------------------
        st.markdown("### 📈 Visualisasi Perbedaan Nominal")

        col1, col2 = st.columns(2)

        with col1:
            fig5 = go.Figure()

            fig5.add_trace(go.Histogram(
            x=normal_df["amount"],
            nbinsx=50,
            name="Transaksi Normal",
            opacity=0.6,
            marker_color="steelblue",
            hovertemplate="Nominal: Rp %{x:,.0f}<extra>Transaksi Normal</extra>"
        ))

            fig5.add_trace(go.Histogram(
            x=micro_df["amount"],
            nbinsx=50,
            name="Micro-spending",
            opacity=0.6,
            marker_color="coral",
            hovertemplate="Nominal: Rp %{x:,.0f}<extra>Micro-spending</extra>"
        ))

            fig5.update_layout(
            barmode="overlay",
            title="Distribusi Nominal Transaksi",
            template="plotly_dark",
            height=420,
            margin=dict(l=20, r=20, t=60, b=20),
            legend_title_text=""
        )
            fig5.update_xaxes(title="Nominal Transaksi (Rp)")
            fig5.update_yaxes(title="Jumlah Transaksi")
            st.plotly_chart(fig5, use_container_width=True)

        with col2:
            fig6 = px.box(
            df,
            x="label",
            y="amount_winsorized",
            points="outliers",
            title="Perbandingan Nominal Transaksi",
            template="plotly_dark"
        )
            fig6.update_xaxes(
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["Transaksi Normal", "Micro-spending"],
            title="Jenis Transaksi"
        )
            fig6.update_yaxes(title="Nominal Winsorized (Rp)")
            fig6.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig6, use_container_width=True)

    # ------------------------------------------------------------
    # VISUALISASI 3 & 4
    # ------------------------------------------------------------
        st.markdown("### 🕒 Pola Waktu dan Kategori")

        col3, col4 = st.columns(2)

        with col3:
            weekend_comp = (
            df.groupby(["label", "is_weekend"])
            .size()
            .unstack(fill_value=0)
            .reindex(index=[0, 1], columns=[0, 1], fill_value=0)
        )

            weekend_comp_pct = weekend_comp.div(weekend_comp.sum(axis=1), axis=0) * 100
            weekend_plot_df = weekend_comp_pct.reset_index().melt(
            id_vars="label",
            var_name="Jenis Hari",
            value_name="Persentase"
        )

            weekend_plot_df["Jenis Transaksi"] = weekend_plot_df["label"].map({
            0: "Transaksi Normal",
            1: "Micro-spending"
        })
            weekend_plot_df["Jenis Hari"] = weekend_plot_df["Jenis Hari"].map({
            0: "Hari Kerja",
            1: "Akhir Pekan"
        })

            fig7 = px.bar(
            weekend_plot_df,
            x="Jenis Transaksi",
            y="Persentase",
            color="Jenis Hari",
            barmode="group",
            title="Perbandingan Transaksi Hari Kerja vs Akhir Pekan",
            template="plotly_dark",
            text_auto=".1f",
            color_discrete_map={
                "Hari Kerja": "steelblue",
                "Akhir Pekan": "coral"
            }
        )
            fig7.update_yaxes(title="Persentase (%)")
            fig7.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig7, use_container_width=True)

        with col4:
            cat_micro_rate = (
            df.groupby("category")["label"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

            fig8 = px.bar(
            cat_micro_rate.iloc[::-1],
            x="label",
            y="category",
            orientation="h",
            title="Tingkat Micro-spending per Kategori",
            template="plotly_dark",
            color="label",
            color_continuous_scale="Purples"
        )
            fig8.update_xaxes(title="Tingkat Micro-spending")
            fig8.update_yaxes(title="")
            fig8.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=60, b=20),
            coloraxis_showscale=False
        )
            st.plotly_chart(fig8, use_container_width=True)

    # ------------------------------------------------------------
    # KESIMPULAN RQ2
    # ------------------------------------------------------------
        st.markdown("""
    <div style="
        background-color: #1e293b;
        padding: 1rem 1.1rem;
        border-radius: 12px;
        border-left: 4px solid #38bdf8;
        margin-top: 0.8rem;
    ">
        <h4 style="color: #7dd3fc; margin-bottom: 0.6rem; font-size: 0.95rem;">🎯 Kesimpulan RQ2</h4>
        <ul style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.7; padding-left: 1.2rem;">
            <li>Nominal micro-spending jauh lebih kecil dibandingkan transaksi normal.</li>
            <li>Perbedaan ini signifikan secara statistik, bukan hanya kebetulan sampel.</li>
            <li>Micro-spending lebih sering muncul di akhir pekan.</li>
            <li>Kategori seperti Transportasi, Kopi & Minuman, dan Langganan Digital memiliki tingkat micro-spending lebih tinggi.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # ============================================================
    # RQ3 - VISUALISASI PALING EFEKTIF UNTUK MENUNJUKKAN LONJAKAN
    # ============================================================
    st.markdown("""
    <div class="bq-card">
        <div class="bq-question">
            <span class="rq-badge">RQ3</span>
            Visualisasi apa yang paling efektif untuk menyoroti lonjakan pengeluaran?
        </div>
        <div class="bq-answer">
            Hasil analisis menunjukkan bahwa <b>heatmap pertumbuhan bulanan (MoM)</b> adalah visualisasi yang paling efektif
            untuk mendeteksi lonjakan pengeluaran. Perubahan warna yang kontras membuat perubahan besar lebih cepat terlihat
            dibandingkan angka dalam tabel atau grafik biasa.<br><br>
            Kategori <b>Belanja & Lifestyle</b> tercatat paling volatil, sedangkan analisis akhir pekan menunjukkan bahwa
            <b>Transportasi</b> dan <b>Langganan Digital</b> memiliki lonjakan yang cukup signifikan pada hari libur.<br><br>
            <b>Kesimpulan utama:</b> heatmap menjadi visual utama, sedangkan grafik garis dengan penanda anomali dan
            analisis akhir pekan berfungsi sebagai pendukung untuk memberi konteks yang lebih lengkap.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # PERSIAPAN DATA
    # ------------------------------------------------------------
    monthly_cat = (
        df.groupby(["period_dt", "category"])
        .agg(total_amount=("amount", "sum"), txn_count=("amount", "size"))
        .reset_index()
        .sort_values(["category", "period_dt"])
    )

    monthly_cat["prev_amount"] = monthly_cat.groupby("category")["total_amount"].shift(1)
    monthly_cat["mom_growth"] = (
        (monthly_cat["total_amount"] - monthly_cat["prev_amount"]) /
        (monthly_cat["prev_amount"] + 1e-9)
    ).replace([np.inf, -np.inf], 0)
    monthly_cat["mom_growth_pct"] = monthly_cat["mom_growth"] * 100

    monthly_cat["amount_zscore"] = monthly_cat.groupby("category")["total_amount"].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-9)
    )
    monthly_cat["is_anomaly"] = (monthly_cat["amount_zscore"].abs() > 2).astype(int)

    anomaly_freq = (
        monthly_cat.groupby("category")
        .agg(
            anomaly_count=("is_anomaly", "sum"),
            total_months=("period_dt", "size"),
            avg_zscore=("amount_zscore", lambda x: x.abs().mean()),
            max_growth=("mom_growth_pct", "max"),
            avg_amount=("total_amount", "mean"),
        )
        .reset_index()
    )
    anomaly_freq["anomaly_rate"] = anomaly_freq["anomaly_count"] / anomaly_freq["total_months"]
    anomaly_freq = anomaly_freq.sort_values("anomaly_rate", ascending=False)

    weekend_impulse = (
        df.groupby(["category", "is_weekend"])
        .agg(micro_rate=("label", "mean"))
        .reset_index()
        .pivot(index="category", columns="is_weekend", values="micro_rate")
        .fillna(0)
    )
    weekend_impulse["weekend_boost"] = weekend_impulse[1] - weekend_impulse[0]
    weekend_impulse = weekend_impulse.sort_values("weekend_boost", ascending=False).head(8)

    # ------------------------------------------------------------
    # RINGKASAN CEPAT
    # ------------------------------------------------------------
    top_volatile_cat = anomaly_freq.iloc[0]["category"]
    top_volatile_rate = anomaly_freq.iloc[0]["anomaly_rate"] * 100

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Kategori paling volatil", top_volatile_cat)
    with col_b:
        st.metric("Tingkat anomali tertinggi", f"{top_volatile_rate:.2f}%")

    # ------------------------------------------------------------
    # BUKA / TUTUP VISUALISASI
    # ------------------------------------------------------------
    with st.expander("📊 Lihat Visualisasi RQ3", expanded=False):

        st.markdown("### 📊 Heatmap Pertumbuhan Bulanan")

        top10_cats = anomaly_freq.head(10)["category"].tolist()
        heatmap_data = monthly_cat[monthly_cat["category"].isin(top10_cats)].copy()
        heatmap_data["period_str"] = heatmap_data["period_dt"].dt.strftime("%Y-%m")

        recent_months = sorted(heatmap_data["period_str"].unique())[-24:]

        pivot_growth = heatmap_data.pivot_table(
            index="category",
            columns="period_str",
            values="mom_growth_pct",
            fill_value=0
        )

        pivot_growth = pivot_growth.reindex(columns=recent_months, fill_value=0)

        fig9 = go.Figure(data=go.Heatmap(
            z=pivot_growth.values,
            x=pivot_growth.columns.tolist(),
            y=pivot_growth.index.tolist(),
            colorscale="RdYlGn_r",
            zmid=0,
            colorbar=dict(title="MoM Growth (%)"),
            hovertemplate="Kategori: %{y}<br>Bulan: %{x}<br>Pertumbuhan: %{z:.2f}%<extra></extra>",
        ))

        fig9.update_layout(
            title="A. Heatmap Pertumbuhan Bulanan per Kategori",
            template="plotly_dark",
            height=520,
            margin=dict(l=30, r=20, t=60, b=30),
        )
        fig9.update_xaxes(title="Bulan")
        fig9.update_yaxes(title="")
        st.plotly_chart(fig9, use_container_width=True)

        st.markdown("### 🔥 Tingkat Anomali per Kategori")

        top8_anom = anomaly_freq.head(8).copy()
        top8_anom["warna"] = np.where(
            top8_anom["anomaly_rate"] > 0.15, "crimson",
            np.where(top8_anom["anomaly_rate"] > 0.08, "orange", "steelblue")
        )

        fig10 = go.Figure(go.Bar(
            x=top8_anom["anomaly_rate"][::-1],
            y=top8_anom["category"][::-1],
            orientation="h",
            marker_color=top8_anom["warna"][::-1],
            hovertemplate="%{y}<br>Tingkat anomali: %{x:.2%}<extra></extra>",
        ))

        fig10.update_layout(
            title="B. Tingkat Anomali per Kategori",
            template="plotly_dark",
            height=480,
            margin=dict(l=30, r=20, t=60, b=30),
            showlegend=False,
        )
        fig10.update_xaxes(title="Proporsi Bulan Anomali")
        fig10.update_yaxes(title="")
        st.plotly_chart(fig10, use_container_width=True)

        st.markdown("### 📈 Tren Pengeluaran dan Penanda Anomali")

        detail_cat = st.selectbox(
            "Pilih kategori untuk melihat detail tren",
            anomaly_freq["category"].tolist(),
            index=0,
            key="rq3_detail_category"
        )

        cat_ts = monthly_cat[monthly_cat["category"] == detail_cat].sort_values("period_dt")
        anomaly_pts = cat_ts[cat_ts["is_anomaly"] == 1]

        fig11 = go.Figure()

        fig11.add_trace(go.Scatter(
            x=cat_ts["period_dt"],
            y=cat_ts["total_amount"],
            mode="lines+markers",
            name="Total Pengeluaran",
            line=dict(width=3),
            hovertemplate="%{x|%Y-%m}<br>Total: Rp %{y:,.0f}<extra></extra>",
        ))

        fig11.add_trace(go.Scatter(
            x=anomaly_pts["period_dt"],
            y=anomaly_pts["total_amount"],
            mode="markers",
            name="Anomali",
            marker=dict(size=12, symbol="x", color="red"),
            hovertemplate="%{x|%Y-%m}<br>Anomali: Rp %{y:,.0f}<extra></extra>",
        ))

        fig11.update_layout(
            title=f"C. Tren Pengeluaran dan Anomali: {detail_cat}",
            template="plotly_dark",
            height=420,
            hovermode="x unified",
            margin=dict(l=30, r=20, t=60, b=30),
        )
        fig11.update_xaxes(dtick="M12", tickformat="%Y", title="Tahun")
        fig11.update_yaxes(title="Total Pengeluaran (Rp)")
        st.plotly_chart(fig11, use_container_width=True)

        st.markdown("### 📅 Peningkatan Micro-Spending Saat Akhir Pekan")

        fig13 = go.Figure(go.Bar(
            x=weekend_impulse["weekend_boost"][::-1],
            y=weekend_impulse.index[::-1],
            orientation="h",
            marker_color="teal",
            hovertemplate="%{y}<br>Selisih tingkat micro-spending: %{x:.4f}<extra></extra>",
        ))

        fig13.update_layout(
            title="D. Peningkatan Micro-Spending Saat Akhir Pekan",
            template="plotly_dark",
            height=380,
            margin=dict(l=30, r=20, t=60, b=30),
            showlegend=False,
        )
        fig13.update_xaxes(title="Selisih tingkat micro-spending (Weekend - Weekday)")
        fig13.update_yaxes(title="")
        st.plotly_chart(fig13, use_container_width=True)

    # ------------------------------------------------------------
    # KESIMPULAN RQ3
    # ------------------------------------------------------------
    st.markdown("""
    <div style="
        background-color:#1e293b;
        padding:1rem 1.1rem;
        border-radius:12px;
        border-left:4px solid #f59e0b;
        margin-top:0.8rem;">
        <h4 style="color:#fbbf24; margin-bottom:0.6rem; font-size:0.95rem;">🎯 Kesimpulan RQ3</h4>
        <ul style="color:#cbd5e1; font-size:0.85rem; line-height:1.7; padding-left:1.2rem;">
            <li>Heatmap pertumbuhan bulanan adalah visual paling efektif untuk menangkap lonjakan pengeluaran dengan cepat.</li>
            <li>Tingkat anomali membantu menunjukkan kategori yang paling tidak stabil dari waktu ke waktu.</li>
            <li>Grafik tren dengan penanda anomali memberi konteks historis yang lebih jelas.</li>
            <li>Analisis akhir pekan menunjukkan bahwa beberapa kategori lebih rentan mengalami peningkatan pengeluaran saat weekend.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.caption("📅 Dataset: centsaver_master_relabelling.csv | 16.953 baris | 2015–2025 | CentSaver")


# PAKAI INI DI DALAM TAB BQ
df = pd.read_csv("data/centsaver_master_relabelling.csv")
with tab_bq:
    render_business_questions(df)