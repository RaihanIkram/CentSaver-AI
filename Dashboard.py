import pandas as pd
import streamlit as st
import plotly.express as px

from utils.data_loader import load_transactions
from utils.formatter import (
    rupiah,
    TYPE_MAP,
    STATUS_MAP
)
from utils.ai_insight import generate_insight

from main import (
    MonthlyAlertRequest,
    monthly_alert
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="CentSaver AI - Dashboard",
    page_icon="💸",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================

df = load_transactions()

st.title("💰 CentSaver AI")
st.caption(
    "Monitoring Keuangan Personal Berbasis AI"
)

if df.empty:
    st.warning(
        "Belum terdapat data transaksi."
    )
    st.stop()

# ==================================================
# FILTER PERIODE
# ==================================================

st.subheader("📅 Filter Periode")

periode = st.selectbox(
    "Pilih Periode",
    [
        "Semua Data",
        "7 Hari Terakhir",
        "30 Hari Terakhir",
        "Bulan Ini",
        "Tahun Ini"
    ]
)

today = pd.Timestamp.today()

df_filtered = df.copy()

if periode == "7 Hari Terakhir":

    df_filtered = df[
        df["transaction_date"]
        >= (
            today
            - pd.Timedelta(days=7)
        )
    ]

elif periode == "30 Hari Terakhir":

    df_filtered = df[
        df["transaction_date"]
        >= (
            today
            - pd.Timedelta(days=30)
        )
    ]

elif periode == "Bulan Ini":

    df_filtered = df[
        (
            df["transaction_date"].dt.month
            == today.month
        )
        &
        (
            df["transaction_date"].dt.year
            == today.year
        )
    ]

elif periode == "Tahun Ini":

    df_filtered = df[
        df["transaction_date"].dt.year
        == today.year
    ]

# ==================================================
# KPI KEUANGAN
# ==================================================

income_total = (
    df_filtered[
        df_filtered["type"] == "income"
    ]["amount"]
    .sum()
)

expense_total = (
    df_filtered[
        df_filtered["type"] == "expense"
    ]["amount"]
    .sum()
)

balance = (
    income_total
    - expense_total
)

micro_count = int(
    pd.to_numeric(
        df_filtered["micro_label"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)

risk_count = int(
    pd.to_numeric(
        df_filtered["risk_label"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)

st.subheader(
    "💰 Ringkasan Keuangan"
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Pemasukan",
    rupiah(income_total)
)

c2.metric(
    "Total Pengeluaran",
    rupiah(expense_total)
)

c3.metric(
    "Saldo",
    rupiah(balance)
)

c4.metric(
    "Micro Spending",
    micro_count
)

c5.metric(
    "Transaksi Berisiko",
    risk_count
)

# ==================================================
# RINGKASAN AI
# ==================================================

expense_df = df_filtered[
    df_filtered["type"] == "expense"
].copy()

if len(expense_df) > 0:

    micro_rate = (
        pd.to_numeric(
            expense_df["micro_label"],
            errors="coerce"
        )
        .fillna(0)
        .mean()
        * 100
    )

    risk_rate = (
        pd.to_numeric(
            expense_df["risk_label"],
            errors="coerce"
        )
        .fillna(0)
        .mean()
        * 100
    )

    st.divider()

    st.subheader(
        "🤖 Ringkasan AI"
    )

    a1, a2, a3, a4 = st.columns(4)

    a1.metric(
        "Persentase Micro Spending",
        f"{micro_rate:.1f}%"
    )

    a2.metric(
        "Persentase Risiko",
        f"{risk_rate:.1f}%"
    )

    a3.metric(
        "Jumlah Pengeluaran",
        len(expense_df)
    )

    a4.metric(
        "Jumlah Micro Spending",
        int(
            pd.to_numeric(
                expense_df["micro_label"],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )
    )

# ==================================================
# ANALISIS DATA
# ==================================================
st.divider()

st.subheader("📊 Analisis Data")

mode = st.radio(
    "Tampilkan Analisis",
    [
        "Pengeluaran",
        "Pemasukan"
    ],
    horizontal=True
)

if mode == "Pengeluaran":
    analysis_df = df_filtered[
        df_filtered["type"] == "expense"
    ].copy()
else:
    analysis_df = df_filtered[
        df_filtered["type"] == "income"
    ].copy()

def to_monthly_frame(frame: pd.DataFrame, value_col: str = "amount", agg: str = "sum") -> pd.DataFrame:
    temp = frame.copy()
    temp["transaction_date"] = pd.to_datetime(
        temp["transaction_date"],
        errors="coerce"
    )
    temp = temp.dropna(subset=["transaction_date"])

    temp["periode_sort"] = (
        temp["transaction_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    temp["periode_label"] = temp["periode_sort"].dt.strftime("%b %Y")

    if agg == "sum":
        out = (
            temp.groupby(
                ["periode_sort", "periode_label"],
                as_index=False
            )[value_col]
            .sum()
            .sort_values("periode_sort")
        )
    else:
        out = (
            temp.groupby(
                ["periode_sort", "periode_label"],
                as_index=False
            )
            .size()
            .rename(columns={"size": value_col})
            .sort_values("periode_sort")
        )

    return out


if len(analysis_df) > 0:

    left_col, right_col = st.columns(2)

    # ==================================================
    # PENGELUARAN
    # ==================================================

    if mode == "Pengeluaran":

        with left_col:
            st.markdown("#### 🥧 Distribusi Kategori")

            category_sum = (
                analysis_df
                .groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            if len(category_sum) > 5:
                top5 = category_sum.head(5).copy()
                others = category_sum.iloc[5:]["amount"].sum()

                if others > 0:
                    others_df = pd.DataFrame({
                        "category": ["Lainnya"],
                        "amount": [others]
                    })
                    pie_df = pd.concat([top5, others_df], ignore_index=True)
                else:
                    pie_df = top5
            else:
                pie_df = category_sum

            fig_pie = px.pie(
                pie_df,
                names="category",
                values="amount",
                hole=0.35
            )

            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=10, b=10)
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )


# ==================================================
# TOTAL MICRO SPENDING PER BULAN
# ==================================================

        with right_col:

            st.markdown("#### 📊 Total Micro Spending per Bulan")

            micro_df = analysis_df[
                pd.to_numeric(
                    analysis_df["micro_label"],
                    errors="coerce"
                )
                .fillna(0)
                .astype(int) == 1
            ].copy()

            if len(micro_df) > 0:
                trend_df = to_monthly_frame(
                    micro_df,
                    value_col="total_micro",
                    agg="count"
                )

                fig_bar = px.bar(
                    trend_df,
                    x="periode_label",
                    y="total_micro",
                    text="total_micro"
                )

                fig_bar.update_xaxes(
                    type="category",
                    categoryorder="array",
                    categoryarray=trend_df["periode_label"].tolist()
                )

                fig_bar.update_layout(
                    xaxis_title="Periode",
                    yaxis_title="Jumlah Micro Spending",
                    margin=dict(l=10, r=10, t=10, b=10)
                )

                st.plotly_chart(
                    fig_bar,
                    use_container_width=True
                )

            else:
                st.info("Belum ada transaksi micro spending pada periode ini.")
    # ==================================================
    # PEMASUKAN
    # ==================================================
    else:

        with left_col:

            st.markdown("#### 💰 Total Pemasukan per Bulan")

            income_monthly = to_monthly_frame(
                analysis_df,
                value_col="amount",
                agg="sum"
            )

            if len(income_monthly) > 0:
                fig_income = px.bar(
                    income_monthly,
                    x="periode_label",
                    y="amount",
                    text="amount"
                )

                fig_income.update_xaxes(
                    type="category",
                    categoryorder="array",
                    categoryarray=income_monthly["periode_label"].tolist()
                )

                fig_income.update_layout(
                    xaxis_title="Periode",
                    yaxis_title="Total Pemasukan",
                    margin=dict(l=10, r=10, t=10, b=10)
                )

                st.plotly_chart(
                    fig_income,
                    use_container_width=True
                )

            else:
                st.info("Belum ada data pemasukan pada periode ini.")

        with right_col:

            st.markdown("#### 📈 Jumlah Transaksi Pemasukan per Bulan")

            income_count = to_monthly_frame(
                analysis_df,
                value_col="jumlah_transaksi",
                agg="count"
            )

            if len(income_count) > 0:
                fig_count = px.bar(
                    income_count,
                    x="periode_label",
                    y="jumlah_transaksi",
                    text="jumlah_transaksi"
                )

                fig_count.update_xaxes(
                    type="category",
                    categoryorder="array",
                    categoryarray=income_count["periode_label"].tolist()
                )

                fig_count.update_layout(
                    xaxis_title="Periode",
                    yaxis_title="Jumlah Transaksi",
                    margin=dict(l=10, r=10, t=10, b=10)
                )

                st.plotly_chart(
                    fig_count,
                    use_container_width=True
                )

            else:
                st.info("Belum ada data pemasukan pada periode ini.")

else:
    st.info("Belum terdapat data yang cukup untuk ditampilkan.")

# ==================================================
#INSIGHT AI
# ==================================================

st.divider()

st.subheader("🤖 Insight AI")

forecast_df = None

try:

    current_month = pd.Timestamp.today().month
    current_year = pd.Timestamp.today().year

    forecast_result = monthly_alert(
        MonthlyAlertRequest(
            month=current_month,
            year=current_year
        )
    )

    forecast_df = pd.DataFrame(
        forecast_result["items"]
    )

except Exception:
    forecast_df = None

with st.container(
    border=True
):
    st.markdown(
        generate_insight(
            df_filtered,
            forecast_df
        )
    )
# ==================================================
# PUSAT PERINGATAN AI
# ==================================================

st.divider()

st.subheader("🚨 Pusat Peringatan AI")

try:

    current_month = pd.Timestamp.today().month
    current_year = pd.Timestamp.today().year

    forecast_result = monthly_alert(
        MonthlyAlertRequest(
            month=current_month,
            year=current_year
        )
    )

    alert_df = pd.DataFrame(
        forecast_result["items"]
    )

    if len(alert_df) > 0:

        display_alerts = (
            alert_df
            .sort_values(
                "forecast_total",
                ascending=False
            )
            .head(3)
        )

        cols = st.columns(
            len(display_alerts)
        )

        for i, (_, row) in enumerate(
            display_alerts.iterrows()
        ):

            status = STATUS_MAP.get(
                row["status"],
                row["status"]
            )

            with cols[i]:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {row['category']}"
                    )

                    st.metric(
                        "Prediksi Pengeluaran",
                        rupiah(
                            row[
                                "forecast_total"
                            ]
                        )
                    )

                    st.write(
                        f"**Tingkat Perhatian:** {status}"
                    )

                    if row["status"] == "HIGH":

                        st.error(
                            "Perlu perhatian segera."
                        )

                    elif row["status"] == "WARNING":

                        st.warning(
                            "Perlu dipantau."
                        )

                    else:

                        st.success(
                            "Masih dalam batas normal."
                        )

except Exception as e:

    st.info(
        "Data prediksi belum tersedia."
    )

# ==================================================
# TRANSAKSI TERBARU
# ==================================================

st.divider()

st.subheader("🕒 Transaksi Terbaru")

recent_df = (
    df_filtered
    .copy()
)

recent_df = recent_df.sort_values(
    "transaction_date",
    ascending=False
)

recent_df["transaction_date"] = (
    pd.to_datetime(
        recent_df["transaction_date"]
    )
    .dt.strftime("%Y-%m-%d")
)

recent_df["Jenis"] = (
    recent_df["type"]
    .map(TYPE_MAP)
)

recent_df["Micro Spending"] = (
    pd.to_numeric(
        recent_df["micro_label"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
    .map(
        {
            1: "Ya",
            0: "Tidak"
        }
    )
)

recent_df["Risiko"] = (
    pd.to_numeric(
        recent_df["risk_label"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
    .map(
        {
            1: "Ya",
            0: "Tidak"
        }
    )
)

recent_df["Nominal"] = (
    recent_df["amount"]
    .apply(rupiah)
)

show_cols = [
    "transaction_date",
    "Jenis",
    "category",
    "Nominal",
    "Micro Spending",
    "Risiko"
]

rename_map = {
    "transaction_date": "Tanggal",
    "category": "Kategori"
}

recent_df = (
    recent_df[
        show_cols
    ]
    .rename(
        columns=rename_map
    )
)

st.dataframe(
    recent_df.head(10),
    use_container_width=True,
    hide_index=True
)

