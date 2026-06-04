#forecast_alerts.py
import pandas as pd
import streamlit as st
import plotly.express as px

from main import MonthlyAlertRequest, monthly_alert

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="CentSaver - Prediksi & Peringatan",
    page_icon="💸",
    layout="wide"
)

st.title("🚨 Prediksi & Peringatan AI")

st.caption(
    "Analisis prediksi pengeluaran berdasarkan pola historis transaksi dan model AI."
)

# ==================================================
# INPUT PERIODE
# ==================================================

col1, col2 = st.columns(2)

with col1:

    month = st.selectbox(
        "📅 Bulan Prediksi",
        list(range(1, 13)),
        index=6
    )

with col2:

    year = st.selectbox(
        "📆 Tahun Prediksi",
        list(range(2024, 2036)),
        index=2
    )

generate = st.button(
    "🔍 Lihat Prediksi AI",
    use_container_width=True
)

if generate:

    req = MonthlyAlertRequest(
        month=int(month),
        year=int(year)
    )

    result = monthly_alert(req)

    df = pd.DataFrame(
        result["items"]
    )

    if len(df) == 0:
        st.warning(
            "Belum tersedia data prediksi."
        )
        st.stop()

    status_map = {
        "HIGH": "Tinggi",
        "WARNING": "Waspada",
        "NORMAL": "Normal"
    }

    df["status_id"] = (
        df["status"]
        .map(status_map)
    )

    # ==================
    # KPI
    # ==================

    high_count = len(df[df["status"] == "HIGH"])
    warning_count = len(df[df["status"] == "WARNING"])
    normal_count = len(df[df["status"] == "NORMAL"])

    total_forecast = (
    df["forecast_total"]
    .sum()
)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🔴 Perlu Perhatian",
        high_count
    )

    c2.metric(
       "🟡 Waspada",
        warning_count
    )

    c3.metric(
        "🟢 Stabil",
        normal_count
    )

    c4.metric(
    "💰 Prediksi Total Pengeluaran",
    f"Rp {total_forecast:,.0f}"
)

    

    # ==================
    # Tabel Prediksi
    # ==================

    st.divider()

    st.subheader("📊 Ringkasan Prediksi per Kategori")

    alert_df = (
    df.sort_values(
        "growth_ratio",
        ascending=False
    )
)



    table_df = pd.DataFrame()

    table_df["Kategori"] = (
        alert_df["category"]
)

    table_df["Prediksi Pengeluaran"] = (
        alert_df["forecast_total"]
    .round(0)
)

    table_df["Rata-rata Sebelumnya"] = (
     alert_df["historical_reference"]
    .round(0)
)

    table_df["Perubahan"] = (
    (
        (alert_df["growth_ratio"] - 1)
        * 100
    )
    .round(1)
    .astype(str)
    + "%"
)

    table_df["Tingkat Perhatian"] = (
        alert_df["status_id"]
)

    st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)

    # ==================================================
    # CHART KENAIKAN
    # ==================================================

    growth_chart = (
    alert_df[
        ["category", "growth_ratio"]
    ]
    .sort_values(
        "growth_ratio",
        ascending=False
    )
)

    fig = px.bar(
    growth_chart,
    x="category",
    y="growth_ratio"
)

    fig.update_layout(
    xaxis_title="Kategori",
    yaxis_title="Tingkat Kenaikan"
)

    st.plotly_chart(
    fig,
    use_container_width=True
)

    # ==================================================
    # CHART PREDIKSI NOMINAL
    # ==================================================

    amount_chart = (
    alert_df[
        ["category", "forecast_total"]
    ]
    .sort_values(
        "forecast_total",
        ascending=False
    )
)

    fig = px.bar(
    amount_chart,
    x="category",
    y="forecast_total"
)

    fig.update_layout(
    xaxis_title="Kategori",
    yaxis_title="Prediksi Pengeluaran"
)

    st.plotly_chart(
    fig,
    use_container_width=True
)
    

    # ==================================================
    # RINGKASAN AI
    # ==================================================

    top_alert = alert_df.iloc[0]

    st.divider()

    st.subheader(
    "🤖 Ringkasan AI"
)

    growth_percent = (
    (top_alert["growth_ratio"] - 1)
    * 100
)
    highest_spending = (
    alert_df
    .sort_values(
        "forecast_total",
        ascending=False
    )
    .iloc[0]
)

    st.info(
    f"""
📈 **Kategori dengan kenaikan tertinggi**

**{top_alert['category']}**
diprediksi mengalami peningkatan pengeluaran tertinggi dibanding pola sebelumnya.

Perkiraan pengeluaran:
Rp {top_alert['forecast_total']:,.0f}

Potensi kenaikan:
{growth_percent:.1f}% atau sekitar
**{top_alert['growth_ratio']:.2f} kali**
lebih tinggi dibanding rata-rata historis.

Tingkat perhatian:
**{top_alert['status_id']}**

--------------------------------------------

💰 **Kategori dengan prediksi pengeluaran terbesar**

**{highest_spending['category']}**

Diperkirakan menghabiskan dana sebesar:

Rp {highest_spending['forecast_total']:,.0f}

Kategori ini merupakan penyumbang pengeluaran terbesar pada periode prediksi.

--------------------------------------------

💡 **Rekomendasi AI**

Fokuskan pemantauan pada kategori
**{top_alert['category']}**
karena mengalami kenaikan paling signifikan, serta kategori
**{highest_spending['category']}**
karena memiliki nominal pengeluaran terbesar.
"""
)