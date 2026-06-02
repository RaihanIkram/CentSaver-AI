from pathlib import Path
import pandas as pd
import streamlit as st

CSV_PATH = Path("data/transactions.csv")

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="CentSaver AI - Riwayat Transaksi",
    page_icon="💸",
    layout="wide"
)


st.title("📜 Riwayat Transaksi")

st.caption(
    "Lihat dan telusuri seluruh transaksi yang telah tercatat."
)

# ==================================================
# LOAD DATA
# ==================================================

if not CSV_PATH.exists():
    st.warning("Data transaksi belum tersedia.")
    st.stop()

df = pd.read_csv(CSV_PATH)

if df.empty:
    st.info("Belum ada transaksi yang tersimpan.")
    st.stop()

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)

# ==================================================
# FILTER
# ==================================================

with st.expander(
    "🔎 Filter Transaksi",
    expanded=True
):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        t = st.selectbox(
            "Jenis Transaksi",
            [
                "Semua",
                "Pemasukan",
                "Pengeluaran"
            ]
        )

    with c2:
        cats = ["Semua"] + sorted(
            [
                c
                for c in df["category"]
                .dropna()
                .unique()
                .tolist()
                if str(c).strip() != ""
            ]
        )

        cat = st.selectbox(
            "Kategori",
            cats
        )

    with c3:
        micro = st.selectbox(
            "Micro Spending",
            [
                "Semua",
                "Ya",
                "Tidak"
            ]
        )

    with c4:
        risk = st.selectbox(
            "Risiko",
            [
                "Semua",
                "Ya",
                "Tidak"
            ]
        )

    dmin = df["transaction_date"].min()
    dmax = df["transaction_date"].max()

    dr = st.date_input(
        "Rentang Tanggal",
        value=(
            dmin.date(),
            dmax.date()
        )
    )

# ==================================================
# APPLY FILTER
# ==================================================

f = df.copy()

if t == "Pemasukan":
    f = f[f["type"] == "income"]

elif t == "Pengeluaran":
    f = f[f["type"] == "expense"]

if cat != "Semua":
    f = f[f["category"] == cat]

if micro != "Semua":

    f["micro_label"] = pd.to_numeric(
        f["micro_label"],
        errors="coerce"
    )

    f = f[
        f["micro_label"]
        .fillna(-1)
        .astype(int)
        ==
        (
            1
            if micro == "Ya"
            else 0
        )
    ]

if risk != "Semua":

    f["risk_label"] = pd.to_numeric(
        f["risk_label"],
        errors="coerce"
    )

    f = f[
        f["risk_label"]
        .fillna(-1)
        .astype(int)
        ==
        (
            1
            if risk == "Ya"
            else 0
        )
    ]

if (
    isinstance(dr, tuple)
    and len(dr) == 2
):
    start = pd.to_datetime(dr[0])
    end = pd.to_datetime(dr[1])

    f = f[
        (f["transaction_date"] >= start)
        &
        (f["transaction_date"] <= end)
    ]

# ==================================================
# KPI
# ==================================================

income_sum = (
    f.loc[
        f["type"] == "income",
        "amount"
    ]
    .sum()
)

expense_sum = (
    f.loc[
        f["type"] == "expense",
        "amount"
    ]
    .sum()
)

balance = income_sum - expense_sum

f["micro_label_num"] = (
    pd.to_numeric(
        f.get("micro_label", 0),
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Total Pemasukan",
    f"Rp {income_sum:,.0f}".replace(",", ".")
)

c2.metric(
    "💸 Total Pengeluaran",
    f"Rp {expense_sum:,.0f}".replace(",", ".")
)

c3.metric(
    "🏦 Saldo",
    f"Rp {balance:,.0f}".replace(",", ".")
)

c4.metric(
    "🔎 Micro Spending",
    int(f["micro_label_num"].sum())
)

# ==================================================
# SORTING
# ==================================================

st.subheader(
    "📋 Daftar Transaksi"
)

sort_by = st.selectbox(
    "Urutkan Berdasarkan",
    [
        "Tanggal Terbaru",
        "Nominal Terbesar",
        "Nominal Terkecil"
    ]
)

if sort_by == "Tanggal Terbaru":

    f = f.sort_values(
        "transaction_date",
        ascending=False
    )

elif sort_by == "Nominal Terbesar":

    f = f.sort_values(
        "amount",
        ascending=False
    )

else:

    f = f.sort_values(
        "amount",
        ascending=True
    )

# ==================================================
# FORMAT TABLE
# ==================================================

display_df = f.copy()

display_df["transaction_date"] = (
    pd.to_datetime(
        display_df["transaction_date"]
    )
    .dt.strftime("%d-%m-%Y")
)

display_df["type"] = (
    display_df["type"]
    .replace(
        {
            "income": "Pemasukan",
            "expense": "Pengeluaran"
        }
    )
)

display_df["micro_label"] = (
    pd.to_numeric(
        display_df["micro_label"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
    .replace(
        {
            1: "Ya",
            0: "Tidak"
        }
    )
)

display_df["risk_label"] = (
    pd.to_numeric(
        display_df["risk_label"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
    .replace(
        {
            1: "Ya",
            0: "Tidak"
        }
    )
)

display_df["amount"] = (
    display_df["amount"]
    .apply(
        lambda x:
        f"Rp {x:,.0f}".replace(",", ".")
    )
)

display_df = display_df.rename(
    columns={
        "transaction_date": "Tanggal",
        "type": "Jenis",
        "category": "Kategori",
        "amount": "Nominal",
        "note": "Catatan",
        "micro_label": "Micro Spending",
        "risk_label": "Risiko"
    }
)

st.dataframe(
    display_df[
        [
            "Tanggal",
            "Jenis",
            "Kategori",
            "Nominal",
            "Catatan",
            "Micro Spending",
            "Risiko"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# DOWNLOAD CSV
# ==================================================

st.download_button(
    "⬇️ Unduh Data CSV",
    data=f.to_csv(index=False).encode("utf-8"),
    file_name="riwayat_transaksi.csv",
    mime="text/csv"
)