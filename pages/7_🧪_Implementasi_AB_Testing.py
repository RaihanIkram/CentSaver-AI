import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import streamlit as st
import pandas as pd
from pathlib import Path

# Import modul A/B testing dari root
# (karena Streamlit run dari root, import langsung jalan)
from ab_testing_module import (
    load_and_prepare_data,
    get_top_categories,
    run_ab_test,
    create_summary_dataframe,
    create_visualizations
)

st.set_page_config(page_title="Product Analytics", page_icon="🧪")

st.title("🧪 Implementasi A/B Testing")
st.caption("Halaman ini untuk tim internal: Data Scientist & Product Manager")
st.info("Menguji signifikansi statistik antar kategori transaksi mikro.")

# --- Upload atau load data ---
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    # Fallback: cari file di folder data/
    default_path = Path("data") / "centsaver_master_relabelling.csv"
    if default_path.exists():
        df = pd.read_csv(default_path)
        st.success(f"Menggunakan data lokal: `{default_path}`")
    else:
        st.warning("Upload file CSV atau letakkan dataset di folder `data/`.")
        st.stop()

# Preprocess
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['is_micro'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
micro_df = df[df['is_micro'] == 1].copy()

st.write(f"📁 Total: {len(df):,} transaksi | ☕ Mikro: {len(micro_df):,}")

# --- Pilih kategori ---
top_categories = get_top_categories(micro_df, n=5)
st.write("🔝 Top Kategori:")
st.dataframe(top_categories.style.format({"count": "{:,}", "sum": "Rp {:,.0f}", "mean": "Rp {:,.0f}"}))

cat_list = list(top_categories.index)
c1, c2 = st.columns(2)
with c1:
    group_a = st.selectbox("Group A (Kontrol)", cat_list, index=0)
with c2:
    group_b = st.selectbox("Group B (Perlakuan)", cat_list, index=1)

if group_a == group_b:
    st.error("Group A dan B tidak boleh sama!")
    st.stop()

alpha = st.slider("α (Signifikansi)", 0.01, 0.10, 0.05, 0.01)

if st.button("🚀 Jalankan A/B Testing", type="primary"):
    with st.spinner("Menghitung..."):
        result = run_ab_test(micro_df, group_a, group_b, alpha=alpha)

        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Rata-rata {group_a}", f"Rp {result['group_a']['mean']:,.0f}")
        m2.metric(f"Rata-rata {group_b}", f"Rp {result['group_b']['mean']:,.0f}")
        diff = result['diff_pct']
        m3.metric("Selisih", f"{diff:+.1f}%")

        st.divider()

        # Hasil uji
        c1, c2 = st.columns(2)
        with c1:
            st.write("**📊 T-Test (Welch)**")
            st.write(f"T-statistik: `{result['t_stat']:.4f}`")
            st.write(f"p-value: `{result['p_value']:.4f}`")
            st.write(f"Cohen's d: `{result['cohens_d']:.4f}` ({result['effect_size']})")
        with c2:
            st.write("**📋 Mann-Whitney U**")
            st.write(f"U-statistik: `{result['u_stat']:.0f}`")
            st.write(f"p-value: `{result['u_pvalue']:.4f}`")

        # Keputusan
        if result['reject_h0']:
            st.success(f"✅ **TOLAK H₀** — Terdapat perbedaan signifikan!")
        else:
            st.warning(f"❌ **GAGAL TOLAK H₀** — Belum cukup bukti perbedaan.")

        # Visualisasi
        st.divider()
        st.write("**📈 Visualisasi**")
        ga = micro_df[micro_df['category'] == group_a]['amount'].dropna()
        gb = micro_df[micro_df['category'] == group_b]['amount'].dropna()
        fig = create_visualizations(result, ga, gb)
        st.pyplot(fig)

        # Export
        st.divider()
        summary_df = create_summary_dataframe(result)
        st.dataframe(summary_df)
        csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download CSV", csv, "ab_testing_result.csv", "text/csv")