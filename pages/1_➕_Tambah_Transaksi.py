import uuid
import json
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

from main import TransactionRequest, predict_transaction  # tim AI

# =========================
# Category options (searchable dropdown)
# =========================
CATEGORY_MAP_PATH = Path("artifacts_centsaver/category_to_index.json")

# Kategori umum (nggak kebanyakan) – Indonesian UI
COMMON_CATEGORIES_ID = [
    "Makanan & Minuman",
    "Kopi & Minuman",
    "Transportasi",
    "Tagihan Utilitas",
    "Langganan Digital",
    "Kebutuhan Dapur",
    "Kebutuhan Rumah Tangga",
    "Kesehatan",
    "Pendidikan",
    "Sewa & Cicilan",
    "Hiburan & Gaya Hidup",
    "Belanja & Lifestyle",
    "Kecantikan & Perawatan",
    "Hobi & Olahraga",
    "Perjalanan",
    "Keluarga & Sosial",
    "Administrasi",
    "Elektronik",
    "Lainnya",
]

@st.cache_data
def load_model_categories() -> set:
    with open(CATEGORY_MAP_PATH, "r", encoding="utf-8") as f:
        cat2idx = json.load(f)
    return set(cat2idx.keys())

@st.cache_data
def build_common_category_options() -> list:
    model_cats = load_model_categories()

    # Ambil hanya kategori umum yang dikenal model
    opts = [c for c in COMMON_CATEGORIES_ID if c in model_cats]

    # Pastikan "Lainnya" tetap ada untuk UX, meski model tidak punya
    if "Lainnya" not in opts:
        opts.append("Lainnya")

    # Kalau ternyata banyak kategori di model gak masuk list umum (misal dataset beda),
    # fallback minimal: kalau opts kosong, pakai semua kategori model (biar tidak error)
    if len(opts) == 0:
        opts = sorted(list(model_cats))
        if "Lainnya" not in opts:
            opts.append("Lainnya")

    return opts

MODEL_CATS = load_model_categories()
COMMON_OPTIONS = build_common_category_options()

def default_expense_category() -> str:
    # Default yang enak: kalau ada "Makanan & Minuman" pakai itu, kalau nggak pakai item pertama
    return "Makanan & Minuman" if "Makanan & Minuman" in COMMON_OPTIONS else COMMON_OPTIONS[0]

# =========================
# CSV storage
# =========================
DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "transactions.csv"

COLUMNS = [
    "id","transaction_date","type","category","amount","note",
    "micro_label","micro_probability","risk_label","risk_probability",
    "amount_ratio_vs_category_avg","amount_zscore_vs_category",
    "created_at"
]

def ensure_csv():
    DATA_DIR.mkdir(exist_ok=True)
    if (not CSV_PATH.exists()) or (CSV_PATH.stat().st_size == 0):
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)

def load_df():
    ensure_csv()
    try:
        return pd.read_csv(CSV_PATH)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)
        return pd.read_csv(CSV_PATH)

def save_df(df: pd.DataFrame):
    df.to_csv(CSV_PATH, index=False)

# =========================
# UI
# =========================

st.set_page_config(
    page_title="CentSaver AI - Tambah Transaksi",
    page_icon="💸",
    layout="wide"
)

st.title("➕ Tambah Transaksi")

st.caption(
    "Catat pemasukan dan pengeluaran, lalu biarkan AI menganalisis transaksi secara otomatis."
)

ensure_csv()

tab_income, tab_expense = st.tabs(
    [
        "💰 Pemasukan",
        "💸 Pengeluaran (AI)"
    ]
)

# ==================================================
# TAB PEMASUKAN
# ==================================================

with tab_income:

    st.subheader("💰 Tambah Pemasukan")

    st.info(
        "Semua transaksi pemasukan akan otomatis disimpan sebagai kategori Pemasukan."
    )

    with st.form("income_form"):

        d = st.date_input(
            "Tanggal",
            value=date.today()
        )

        amt = st.number_input(
        "Nominal",
        min_value=0.0,
        step=1000.0
)
        if amt > 0:
            st.caption(
        f"💰 Rp {amt:,.0f}".replace(",", ".")
    )

        note = st.text_input(
            "Catatan (opsional)"
        )

        ok = st.form_submit_button(
            "Simpan Pemasukan"
        )

        cat = "Income"

    if ok:
        df = load_df()
        row = {
            "id": str(uuid.uuid4()),
            "transaction_date": str(d),
            "type": "income",
            "category": cat,
            "amount": float(amt),
            "note": note,
            "micro_label": "",
            "micro_probability": "",
            "risk_label": "",
            "risk_probability": "",
            "amount_ratio_vs_category_avg": "",
            "amount_zscore_vs_category": "",
            "created_at": datetime.utcnow().isoformat(),
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        save_df(df)
        st.success("Pemasukan berhasil disimpan.")

with tab_expense:

    st.subheader("💸 Tambah Pengeluaran")

    with st.form("expense_form"):

        d = st.date_input(
            "Tanggal",
            value=date.today(),
            key="exp_date"
        )

        default_cat = default_expense_category()

        cat_ui = st.selectbox(
            "Kategori Pengeluaran",
            options=COMMON_OPTIONS,
            index=COMMON_OPTIONS.index(default_cat)
            if default_cat in COMMON_OPTIONS
            else 0,
            key="exp_cat_select"
        )

        amt = st.number_input(
        "Nominal",
        min_value=0.0,
        step=1000.0
)
        if amt > 0:
            st.caption(
        f"💰 Rp {amt:,.0f}".replace(",", ".")
    )

        note = st.text_input(
            "Catatan (opsional)",
            key="exp_note"
        )

        ok = st.form_submit_button(
            "Analisis & Simpan"
        )

    if ok:

        category_for_model = cat_ui
        mapped_note = note

        if (
            cat_ui == "Lainnya"
            and "Lainnya" not in MODEL_CATS
        ):

            fallback_cat = (
                default_expense_category()
            )

            category_for_model = (
                fallback_cat
            )

            mapped_note = (
                mapped_note
                + f" | mapped_category={fallback_cat}"
            ).strip()

        req = TransactionRequest(
            amount=float(amt),
            category=category_for_model,
            transaction_date=d
        )

        out = predict_transaction(req)

        # =========================
        # HASIL AI
        # =========================

        st.divider()

        st.subheader(
            "🤖 Hasil Analisis AI"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Micro Spending",
            "Ya"
            if out["micro_label"] == 1
            else "Tidak"
        )

        c2.metric(
            "Kemungkinan Micro Spending",
            f'{out["micro_probability"] * 100:.1f}%'
        )

        c3.metric(
            "Transaksi Berisiko",
            "Ya"
            if out["risk_label"] == 1
            else "Tidak"
        )

        c4.metric(
            "Tingkat Risiko",
            f'{out["risk_probability"] * 100:.1f}%'
        )

        # =========================
        # INTERPRETASI AI
        # =========================

        st.subheader(
            "🧠 Interpretasi AI"
        )

        if out["risk_label"] == 1:

            st.error(
                """
Transaksi ini memiliki tingkat risiko yang relatif tinggi dibanding pola historis kategori yang sama.
                """
            )

        elif out["micro_label"] == 1:

            st.warning(
                """
AI mendeteksi transaksi ini berpotensi termasuk micro spending.

Pengeluaran kecil yang terjadi berulang kali dapat berdampak pada kondisi keuangan dalam jangka panjang.
                """
            )

        else:

            st.success(
                """
Transaksi terdeteksi sebagai pengeluaran yang masih berada dalam batas normal.
                """
            )

        # =========================
        # SIMPAN KE CSV
        # =========================

        df = load_df()

        row = {
            "id": str(uuid.uuid4()),
            "transaction_date": str(d),
            "type": "expense",
            "category": cat_ui,
            "amount": float(out["amount"]),
            "note": mapped_note,
            "micro_label": int(out["micro_label"]),
            "micro_probability": float(out["micro_probability"]),
            "risk_label": int(out["risk_label"]),
            "risk_probability": float(out["risk_probability"]),
            "amount_ratio_vs_category_avg": float(
                out["amount_ratio_vs_category_avg"]
            ),
            "amount_zscore_vs_category": float(
                out["amount_zscore_vs_category"]
            ),
            "created_at": datetime.utcnow().isoformat(),
        }

        df = pd.concat(
            [df, pd.DataFrame([row])],
            ignore_index=True
        )

        save_df(df)

        st.success(
            "✅ Transaksi berhasil disimpan."
        )

        # =========================
        # RIWAYAT TERAKHIR
        # =========================

        st.divider()

        st.subheader(
            "🕒 5 Transaksi Terakhir"
        )

        recent_df = (
            load_df()
            .sort_values(
                "created_at",
                ascending=False
            )
        )

        cols = [
            "transaction_date",
            "category",
            "amount"
        ]

        st.dataframe(
            recent_df[cols].head(5),
            use_container_width=True,
            hide_index=True
        )