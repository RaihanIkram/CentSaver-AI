import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from pathlib import Path

# Import modul A/B testing
from ab_testing_module import (
    load_and_prepare_data,
    get_top_categories,
    run_ab_test,
    create_summary_dataframe,
    create_visualizations,
    get_interpretation
)

st.set_page_config(page_title="A/B Testing - CentSaver", page_icon="📊")

st.title("Implementasi A/B Testing")
st.caption("Halaman ini untuk tim internal: Data Scientist & Product Manager")
st.info("Menguji signifikansi statistik antar kategori transaksi mikro.")

#Upload atau load data
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    micro_df = df[df['label'] == 1].copy()
    micro_df['date'] = pd.to_datetime(micro_df['date'], errors='coerce')
    micro_df['amount'] = pd.to_numeric(micro_df['amount'], errors='coerce')
    st.success("Data berhasil di-upload!")
else:
    default_path = Path("data") / "centsaver_master_relabelling.csv"
    if default_path.exists():
        df = pd.read_csv(default_path)
        micro_df = df[df['label'] == 1].copy()
        micro_df['date'] = pd.to_datetime(micro_df['date'], errors='coerce')
        micro_df['amount'] = pd.to_numeric(micro_df['amount'], errors='coerce')
        st.success(f"Menggunakan data lokal: `{default_path}`")
    else:
        st.warning("Upload file CSV atau letakkan dataset di folder `data/`.")
        st.stop()

st.write(f"Total: {len(df):,} transaksi | Mikro: {len(micro_df):,}")

#Pilih kategori
top_categories = get_top_categories(micro_df, n=5)
st.write("Top Kategori:")
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

alpha = st.slider("alpha (Signifikansi)", 0.01, 0.10, 0.05, 0.01)

#Penjelasan singkat
with st.expander("Lihat penjelasan metode"):
    st.write("""
    **Kenapa pakai Mann-Whitney U?**
    
    Dari histogram data transaksi, kita lihat distribusinya miring ke kanan (right-skewed) 
    dan ada banyak outlier. Data keuangan biasanya seperti itu.
    
    Karena datanya tidak normal, kita pakai **Mann-Whitney U** sebagai alternatif dari t-test. 
    
    Kita tampilkan **Welch's t-test** untuk perbandingan.
    """)

# Jalankan uji
if st.button("Jalankan A/B Testing", type="primary"):
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
            st.write("**T-Test (Welch)**")
            st.write(f"T-statistik: `{result['t_stat']:.4f}`")
            st.write(f"p-value: `{result['p_value']:.4f}`")
            st.write(f"Cohen's d: `{result['cohens_d']:.4f}` ({result['effect_size']})")
        with c2:
            st.write("**Mann-Whitney U**")
            st.write(f"U-statistik: `{result['u_stat']:.0f}`")
            st.write(f"p-value: `{result['u_pvalue']:.4f}`")
        
        # Keputusan
        if result['reject_h0']:
            st.success(f"**TOLAK H0** — Terdapat perbedaan signifikan!")
        else:
            st.warning(f"**GAGAL TOLAK H0** — Belum cukup bukti perbedaan.")
        
        # Interpretasi & Rekomendasi (4 Skenario Dicoding)
        st.divider()
        interp = get_interpretation(result)
        
        st.subheader("Interpretasi & Rekomendasi")
        st.write(f"**{interp['judul']}**")
        st.write(interp['penjelasan'])
        
        st.write("**Saran:**")
        for s in interp['saran']:
            st.write(s)
        
        # Visualisasi
        st.divider()
        st.write("**Visualisasi**")
        ga = micro_df[micro_df['category'] == group_a]['amount'].dropna()
        gb = micro_df[micro_df['category'] == group_b]['amount'].dropna()
        fig = create_visualizations(result, ga, gb)
        st.pyplot(fig)
        
        # Export hasil
        st.divider()
        st.write("**Tabel Ringkasan**")
        summary_df = create_summary_dataframe(result)
        st.dataframe(summary_df)
        
        # Download CSV
        csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV", 
            csv, 
            "ab_testing_result.csv", 
            "text/csv",
            help="Download hasil uji ke file CSV untuk dokumentasi atau laporan."
        )
        
        st.caption("Catatan: Signifikan secara statistik tidak selalu berarti signifikan secara bisnis. Selalu cek p-value + Cohen's d sebelum ambil keputusan produk.")