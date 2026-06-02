import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from scipy import stats

st.set_page_config(page_title="CentSaver AI - Visualisasi Dataset", page_icon="📊", layout="wide")
st.title("📊 Visualisasi Dataset")
st.caption("Eksplorasi data transaksi untuk memahami pola pemasukan, pengeluaran, dan perilaku keuangan.")

CSV_PATH = Path("data/centsaver_master_relabelling.csv")
if not CSV_PATH.exists():
    st.warning("❌ File `data/centsaver_master_relabelling.csv` tidak ditemukan.")
    st.stop()

df = pd.read_csv(CSV_PATH)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["is_micro"] = pd.to_numeric(df["label"], errors="coerce").fillna(0).astype(int)
df["type"] = "expense"
df["category"] = df["category"].astype(str)
df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year
df["day_of_week"] = df["date"].dt.dayofweek
df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
df["day_type"] = np.where(df["is_weekend"] == 1, "weekend", "weekday")
df["period"] = df["date"].dt.to_period("M")

expense_df = df.copy()

st.info(f"📁 Dataset: **centsaver_master_relabelling.csv** | **{len(df):,}** baris | {df['date'].min().date()} → {df['date'].max().date()}")

tab_viz, tab_bq = st.tabs(["📈 Visualisasi Dataset", "🎯 Business Questions"])

# ==================================================
# TAB 1: VISUALISASI
# ==================================================
with tab_viz:
    with st.sidebar:
        st.markdown("### 🎛️ Filter")
        min_d, max_d = df["date"].min().date(), df["date"].max().date()
        dr = st.date_input("📅 Rentang", [min_d, max_d], min_value=min_d, max_value=max_d)
        df_v = df[(df["date"].dt.date >= dr[0]) & (df["date"].dt.date <= dr[1])].copy() if len(dr) == 2 else df.copy()
        cats = sorted(df_v["category"].unique())
        sel = st.multiselect("📦 Kategori", cats, default=cats)
        df_v = df_v[df_v["category"].isin(sel)]

    total_expense = df_v["amount"].sum()
    n_trans = len(df_v)
    n_micro = int(df_v["is_micro"].sum())
    avg_amount = df_v["amount"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💸 Total", f"Rp {total_expense:,.0f}")
    c2.metric("📝 Transaksi", f"{n_trans}")
    c3.metric("☕ Pengeluaran Mikro/Micro", f"{n_micro}")
    c4.metric("📊 Rata-rata", f"Rp {avg_amount:,.0f}")
    st.divider()

    # --- Row 1: Pie & Bar ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🥧 Distribusi Kategori")
        cs = df_v.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=False)
        fig = px.pie(cs, values="amount", names="category", hole=0.4, template="plotly_white")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

        # INSIGHT PIE - KOMPREHENSIF
        top_cat = cs.iloc[0]['category'] if len(cs) > 0 else "-"
        top_pct = (cs.iloc[0]['amount'] / total_expense * 100) if len(cs) > 0 and total_expense > 0 else 0
        insight_pie = f"""
        💡 **Insight Distribusi Kategori**

        **Temuan:** Kategori **{top_cat}** mendominasi pengeluaran dengan **{top_pct:.1f}%** dari total.

        **Mengapa:** Ini menunjukkan bahwa prioritas pengeluaran terkonsentrasi pada kategori tersebut.

        **Risiko/Akibat:** {'⚠️ **Risiko tinggi** — jika satu kategori >30%, alokasi keuangan kurang terdiversifikasi. Disarankan untuk meninjau ulang anggaran atau mendiversifikasi pengeluaran.' if top_pct > 30 else '✅ **Sehat** — proporsi masih dalam batas wajar dan tidak terlalu terkonsentrasi pada satu kategori.'}
        """
        st.info(insight_pie)

    with c2:
        st.subheader("📊 Trend Bulanan")
        m = df_v.groupby("period")["amount"].sum().reset_index()
        m["period_str"] = m["period"].astype(str)
        fig = px.bar(m, x="period_str", y="amount", template="plotly_white", color="amount", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

        # INSIGHT TREND - KOMPREHENSIF
        if len(m) > 1:
            max_month = m.loc[m['amount'].idxmax(), 'period_str']
            min_month = m.loc[m['amount'].idxmin(), 'period_str']
            max_amt = m['amount'].max()
            min_amt = m['amount'].min()
            mom_change = ((m['amount'].iloc[-1] - m['amount'].iloc[-2]) / m['amount'].iloc[-2] * 100) if len(m) >= 2 and m['amount'].iloc[-2] > 0 else 0
            insight_trend = f"""
            💡 **Insight Trend Bulanan**

            **Temuan:** Pengeluaran tertinggi di **{max_month}** (Rp {max_amt:,.0f}), terendah di **{min_month}** (Rp {min_amt:,.0f}). Perubahan bulan terakhir: **{mom_change:+.1f}%**.

            **Mengapa:** Fluktuasi ini dapat disebabkan oleh momen tertentu (liburan, periode gajian) atau perubahan kebutuhan bulanan.

            **Risiko/Akibat:** {'⚠️ **Waspada** — lonjakan >30% dari bulan sebelumnya dapat menjadi indikasi overspending. Sebaiknya dievaluasi apakah pengeluaran tersebut sudah direncanakan atau bersifat impulsif.' if abs(mom_change) > 30 else '✅ **Stabil** — perubahan bulanan masih dalam batas wajar (<30%).'}
            """
            st.info(insight_trend)
        else:
            st.info("💡 **Insight:** Data bulanan terbatas untuk analisis tren komprehensif.")

    # --- Row 2: Line & Histogram ---
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("📈 Trend per Kategori (Top 5)")
        top5 = cs.head(5)["category"].tolist()
        mcat = df_v[df_v["category"].isin(top5)].groupby(["period", "category"])["amount"].sum().reset_index()
        mcat["period_str"] = mcat["period"].astype(str)
        fig = px.line(mcat, x="period_str", y="amount", color="category", markers=True, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # INSIGHT LINE - KOMPREHENSIF
        if not mcat.empty:
            latest = mcat.sort_values(['category', 'period']).groupby('category').tail(1)
            latest_top = latest.sort_values('amount', ascending=False).iloc[0] if len(latest) > 0 else None
            if latest_top is not None:
                insight_line = f"""
                💡 **Insight Trend Kategori**

                **Temuan:** Pada bulan terakhir, **{latest_top['category']}** mencatatkan pengeluaran tertinggi (Rp {latest_top['amount']:,.0f}).

                **Mengapa:** Kategori ini secara konsisten menjadi pengeluaran terbesar, yang mengindikasikan kebutuhan primer atau kebiasaan yang cenderung sulit dihindari.

                **Risiko/Akibat:** {'⚠️ **Perlu strategi** — kategori dominan yang terus meningkat berpotensi mengurangi tabungan. Disarankan untuk menetapkan batas anggaran mingguan pada kategori ini.' if latest_top['amount'] > total_expense * 0.25 else '✅ **Terjaga** — meski tertinggi, proporsinya masih terkontrol dengan baik.'}
                """
                st.info(insight_line)

    with c4:
        st.subheader("📏 Distribusi Nominal")
        fig = px.histogram(df_v, x="amount", nbins=30, template="plotly_white", color="is_micro",
                          color_discrete_map={0: "#3498DB", 1: "#E74C3C"}, barmode="overlay")
        st.plotly_chart(fig, use_container_width=True)

        # INSIGHT HISTOGRAM - KOMPREHENSIF
        micro_pct = (df_v['is_micro'].sum() / len(df_v) * 100) if len(df_v) > 0 else 0
        avg_micro_amt = df_v[df_v['is_micro'] == 1]['amount'].mean() if len(df_v[df_v['is_micro'] == 1]) > 0 else 0
        insight_hist = f"""
        💡 **Insight Distribusi Nominal**

        **Temuan:** **{micro_pct:.1f}%** transaksi adalah pengeluaran mikro/micro-spending (rata-rata Rp {avg_micro_amt:,.0f}).

        **Mengapa:** Transaksi kecil sering dianggap tidak berdampak, namun frekuensi yang tinggi dapat mengakibatkan akumulasi signifikan.

        **Risiko/Akibat:** {'⚠️ **Bahaya tersembunyi** — pengeluaran mikro/pengeluaran mikro >15% mengindikasikan akumulasi tanpa disadari. Contoh: Rp 20.000/hari setara Rp 600.000/bulan. Disarankan untuk menggunakan pelacak pengeluaran real-time.' if micro_pct > 15 else '✅ **Aman** — proporsi micro-spending masih terkontrol (<15%).'}
        """
        st.info(insight_hist)

    # --- Row 3: Hari & Weekend ---
    st.subheader("🔥 Pola Transaksi per Hari")
    df_v["day_name"] = df_v["date"].dt.day_name()
    hd = df_v.groupby("day_name")["amount"].sum().reset_index()
    hd["day_name"] = pd.Categorical(hd["day_name"], categories=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], ordered=True)
    hd = hd.sort_values("day_name")
    fig = px.bar(hd, x="day_name", y="amount", template="plotly_white", color="amount", color_continuous_scale="YlOrRd")
    st.plotly_chart(fig, use_container_width=True)

    # INSIGHT HARI - KOMPREHENSIF
    top_day = hd.loc[hd['amount'].idxmax(), 'day_name'] if not hd.empty else "-"
    top_day_amt = hd['amount'].max() if not hd.empty else 0
    is_weekend_top = top_day in ['Saturday', 'Sunday']
    insight_day = f"""
    💡 **Insight Pola Harian**

    **Temuan:** Hari **{top_day}** mencatatkan pengeluaran terbesar (Rp {top_day_amt:,.0f}).

    **Mengapa:** {'Weekend biasanya diisi aktivitas santai, belanja, atau hiburan — yang cenderung bersifat impulsif.' if is_weekend_top else 'Hari kerja dengan pengeluaran tinggi umumnya disebabkan oleh kebutuhan operasional (transportasi, makan siang).'}

    **Risiko/Akibat:** {'⚠️ **Weekend trap** — pengeluaran tinggi di akhir pekan merupakan pola impulsif yang umum. Rekomendasi: tetapkan batas anggaran akhir pekan sebelum hari Sabtu.' if is_weekend_top else '✅ **Weekday pattern** — pengeluaran di hari kerja umumnya sudah direncanakan. Pastikan tidak ada penghargaan diri (treat yourself) yang berlebihan di tengah minggu.'}
    """
    st.info(insight_day)

    st.subheader("🌴 Weekend vs Weekday")
    wk = df_v.groupby("day_type")["amount"].sum().reset_index()
    fig = px.bar(wk, x="day_type", y="amount", template="plotly_white", color="day_type", color_discrete_map={"weekday": "#3498DB", "weekend": "#E74C3C"})
    st.plotly_chart(fig, use_container_width=True)

    # INSIGHT WEEKEND - KOMPREHENSIF
    if not wk.empty:
        wk_dict = dict(zip(wk['day_type'], wk['amount']))
        weekday_amt = wk_dict.get('weekday', 0)
        weekend_amt = wk_dict.get('weekend', 0)
        total_wk = weekday_amt + weekend_amt
        if total_wk > 0:
            weekend_pct = weekend_amt / total_wk * 100
            insight_wk = f"""
            💡 **Insight Weekend vs Weekday**

            **Temuan:** **{weekend_pct:.1f}%** pengeluaran terjadi pada akhir pekan (Sabtu–Minggu).

            **Mengapa:** Akhir pekan adalah waktu luang, acara sosial, dan penghargaan diri — yang semuanya dapat memicu impulsivitas.

            **Risiko/Akibat:** {'⚠️ **Red flag** — pengeluaran akhir pekan >35% mengindikasikan pola yang cenderung hedonistik. Risiko: anggaran mingguan dapat habis di hari pertama. Solusi: alokasikan 70% anggaran untuk kebutuhan hari kerja.' if weekend_pct > 35 else '✅ **Seimbang** — proporsi akhir pekan dan hari kerja masih dalam batas wajar. Pertahankan pola ini.'}
            """
            st.info(insight_wk)

# ==================================================
# TAB 2: BUSINESS QUESTIONS
# ==================================================
with tab_bq:
    st.header("🎯 Business Questions & Strategic Insights")
    st.divider()
    q1, q2, q3 = st.tabs(["❓ Q1: Pengeluaran Mikro/Micro-Spending Ratio", "📈 Q2: Pengeluaran Mikro/Micro vs Normal", "🎯 Q3: Anomaly & Visual"])

    # ==================== Q1 ====================
    with q1:
        st.subheader("Q1: Berapa persentase pengeluaran mikro/micro-spending vs total per kategori?")

        monthly_micro = expense_df.groupby(['period', 'category']).agg(
            total_monthly=('amount', 'sum'),
            micro_monthly=('amount', lambda x: x[expense_df.loc[x.index, 'is_micro'] == 1].sum())
        ).reset_index()
        monthly_micro['micro_pct'] = (monthly_micro['micro_monthly'] / monthly_micro['total_monthly'] * 100).fillna(0).clip(0, 100)

        avg_micro = monthly_micro.groupby('category').agg(
            avg=('micro_pct', 'mean'), med=('micro_pct', 'median'), mx=('micro_pct', 'max'), n=('micro_pct', 'size')
        ).sort_values('avg', ascending=False).reset_index()

        THRESHOLD = 20
        flagged = avg_micro[avg_micro['avg'] > THRESHOLD]['category'].tolist()

        overall = expense_df.groupby('period').agg(
            total=('amount', 'sum'),
            micro=('amount', lambda x: x[expense_df.loc[x.index, 'is_micro'] == 1].sum())
        ).reset_index()
        overall['micro_pct'] = (overall['micro'] / overall['total'] * 100).fillna(0)
        overall_avg = overall['micro_pct'].mean()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💸 Total", f"Rp {expense_df['amount'].sum():,.0f}")
        m2.metric("🔥 Top Pengeluaran Mikro/Micro", avg_micro.iloc[0]['category'] if len(avg_micro) > 0 else "-", f"{avg_micro.iloc[0]['avg']:.1f}%" if len(avg_micro) > 0 else "")
        m3.metric("📊 Secara Keseluruhan/Overall", f"{overall_avg:.2f}%", f"< {THRESHOLD}%")
        m4.metric("⚠️ Kategori Waspada/Flagged", f"{len(flagged)}", f">{THRESHOLD}%")
        st.divider()

        cf, cc = st.columns([1, 3])
        with cf:
            st.markdown("### 🎛️ Filter")
            show_micro = st.toggle("☕ Pengeluaran Mikro/Micro-Spending Only", False)
            max_amt = int(expense_df['amount'].max())
            threshold = st.slider("💰 ambang batas/Threshold (Rp)", 0, max_amt, int(max_amt * 0.2), 10000)
            all_cats = sorted(expense_df['category'].unique())
            selected = st.multiselect("📦 Kategori", all_cats, default=all_cats)

            dq = expense_df.copy()
            if show_micro:
                dq = dq[dq['is_micro'] == 1]
            dq = dq[dq['amount'] >= threshold]
            dq = dq[dq['category'].isin(selected)]
            st.info(f"**{len(dq)}** transaksi")

        with cc:
            if not dq.empty:
                cs = dq.groupby('category')['amount'].sum().reset_index().sort_values('amount', ascending=True)
                fig = px.bar(cs, x='amount', y='category', orientation='h', color='amount', color_continuous_scale='Reds', template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                # INSIGHT BAR CHART Q1 (DINAMIS + KOMPREHENSIF)
                top_dq = cs.iloc[-1]['category'] if len(cs) > 0 else "-"
                top_dq_amt = cs.iloc[-1]['amount'] if len(cs) > 0 else 0
                dq_total = dq['amount'].sum()
                top_dq_pct = (top_dq_amt / dq_total * 100) if dq_total > 0 else 0
                insight_q1_bar = f"""
                💡 **Insight Filter Aktif**

                **Temuan:** Dari **{len(dq)}** transaksi hasil filter, **{top_dq}** mendominasi (**{top_dq_pct:.1f}%**).

                **Mengapa:** Filter ini menunjukkan kategori mana yang paling esensial dalam kondisi tertentu.

                **Risiko/Akibat:** {'⚠️ **Perlu pemotongan budget!** Satu kategori >40% dari data hasil filter berarti pengeluaran kurang terdiversifikasi. Disarankan untuk mencari alternatif lebih hemat atau mengurangi frekuensi.' if top_dq_pct > 40 else '✅ **Distribusi masih wajar** — tidak ada kategori yang mendominasi secara berlebihan.'}
                """
                st.info(insight_q1_bar)

            if len(avg_micro) > 0:
                fig = px.bar(avg_micro.head(10), x='avg', y='category', orientation='h', color='avg', color_continuous_scale='RdYlGn_r', template="plotly_white")
                fig.add_vline(x=THRESHOLD, line_dash="dash", line_color="red", annotation_text=f"ambang batas/Threshold {THRESHOLD}%")
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("💡 Insight Q1 Komprehensif", expanded=True):
            fs = ", ".join(flagged) if flagged else "Tidak ada"
            insight_q1 = f"""
            **Jawaban Q1:** Rata-rata pengeluaran mikro/micro-spending per bulan adalah **{overall_avg:.2f}%**, di bawah ambang batas/threshold **{THRESHOLD}%**.

            **Temuan:** Kategori dengan pengeluaran mikro/micro-spending tinggi: **{fs}**.

            **Mengapa:** pengeluaran mikro/micro-spending sering "tidak terasa" karena nominal kecil, tapi akumulasi bulanan bisa beda nyata/signifikan.

            **Risiko/Akibat:** {'⚠️ **Kategori flagged melebihi threshold!** Jika micro-spending >20%, artinya 1/5 pengeluaran kategori itu adalah transaksi kecil yang mungkin tidak perlu. Rekomendasi: aktifkan smart alert saat micro-spending melebihi 30% budget mingguan.' if flagged else '✅ **Aman** — tidak ada kategori yang melebihi threshold 20%. Semua kategori masih dalam batas wajar.'}
            """
            st.success(insight_q1)

    # ==================== Q2 ====================
    with q2:
        st.subheader("Q2: Apa karakteristik yang membedakan pengeluaran mikro/micro-spending dengan normal?")

        micro = expense_df[expense_df['is_micro'] == 1]
        normal = expense_df[expense_df['is_micro'] == 0]

        compare = pd.DataFrame({
            'Normal': [normal['amount'].mean(), normal['amount'].median(), normal['amount'].std()],
            'Micro': [micro['amount'].mean(), micro['amount'].median(), micro['amount'].std()]
        }, index=['Mean', 'Median', 'Std'])

        if len(micro) > 1 and len(normal) > 1:
            t_stat, p_val = stats.ttest_ind(micro['amount'], normal['amount'])
            u_stat, u_pval = stats.mannwhitneyu(micro['amount'], normal['amount'], alternative='two-sided')
            ps = np.sqrt(((len(micro)-1)*micro['amount'].var() + (len(normal)-1)*normal['amount'].var()) / (len(micro)+len(normal)-2))
            cohens_d = (micro['amount'].mean() - normal['amount'].mean()) / ps if ps > 0 else 0
        else:
            t_stat = p_val = u_stat = u_pval = cohens_d = 0

        es = "Besar" if abs(cohens_d) >= 0.8 else "Sedang" if abs(cohens_d) >= 0.5 else "Kecil"

        m1, m2, m3 = st.columns(3)
        m1.metric("📊 Rata-rata/Mean Normal", f"Rp {compare.loc['Mean', 'Normal']:,.0f}")
        m2.metric("☕ Rata-rata/Mean Pengeluaran Mikro/Micro", f"Rp {compare.loc['Mean', 'Micro']:,.0f}")
        m3.metric("📉 ukuran efek/Cohen's d", f"{cohens_d:.2f}", es)
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Distribusi Amount")
            if len(micro) > 0 and len(normal) > 0:
                hist = pd.concat([
                    pd.DataFrame({'amount': normal['amount'], 'tipe': 'Normal'}),
                    pd.DataFrame({'amount': micro['amount'], 'tipe': 'Pengeluaran Mikro/Micro'})
                ])
                fig = px.histogram(hist, x='amount', color='tipe', nbins=30, template="plotly_white", color_discrete_map={'Normal': '#3498DB', 'Pengeluaran Mikro/Micro': '#E74C3C'})
                st.plotly_chart(fig, use_container_width=True)

                # INSIGHT HISTOGRAM Q2 - KOMPREHENSIF
                micro_mean = compare.loc['Mean', 'Micro']
                normal_mean = compare.loc['Mean', 'Normal']
                diff_pct = ((normal_mean - micro_mean) / normal_mean * 100) if normal_mean > 0 else 0
                insight_q2_hist = f"""
                💡 **Insight Distribusi**

                **Temuan:** pengeluaran mikro/micro-spending **{diff_pct:.0f}%** lebih kecil dibandingkan normal (Rp {micro_mean:,.0f} vs Rp {normal_mean:,.0f}).

                **Mengapa:** pengeluaran mikro/micro-spending adalah transaksi bernominal kecil yang sering dianggap tidak penting — seperti kopi, camilan, atau parkir.

                **Risiko/Akibat:** {'⚠️ **Perlu diwaspadai!** Meski nominalnya kecil, Rp 25.000/hari selama 30 hari setara Rp 750.000/bulan. Solusi: tetapkan batas pengeluaran harian Rp 50.000.' if diff_pct > 70 else '✅ **Perbedaan moderat** — micro-spending masih terkontrol.'}
                """
                st.info(insight_q2_hist)
        with c2:
            st.markdown("#### Boxplot Comparison")
            if len(micro) > 0 and len(normal) > 0:
                box = pd.concat([
                    pd.DataFrame({'amount': normal['amount'], 'label': 'Normal'}),
                    pd.DataFrame({'amount': micro['amount'], 'label': 'Pengeluaran Mikro/Micro'})
                ])
                fig = px.box(box, x='label', y='amount', color='label', template="plotly_white", color_discrete_map={'Normal': '#3498DB', 'Pengeluaran Mikro/Micro': '#E74C3C'})
                st.plotly_chart(fig, use_container_width=True)

                # INSIGHT BOXPLOT Q2 - KOMPREHENSIF
                insight_q2_box = f"""
                💡 **Insight Variabilitas**

                **Temuan:** Variabilitas Normal (std: Rp {compare.loc['Std', 'Normal']:,.0f}) vs Pengeluaran Mikro/Micro (std: Rp {compare.loc['Std', 'Micro']:,.0f}).

                **Mengapa:** {'Pengeluaran Mikro/Pengeluaran mikro lebih konsisten (simpangan baku lebih kecil) karena nominalnya selalu kecil dan lebih mudah diprediksi.' if compare.loc['Std', 'Micro'] < compare.loc['Std', 'Normal'] else 'Pengeluaran normal lebih bervariasi karena nominalnya bisa sangat kecil maupun sangat besar.'}

                **Risiko/Akibat:** {'⚠️ **Pengeluaran Mikro/Micro lebih berbahaya!** Karena konsisten dan kecil, user tidak sadar sedang "dibakar perlahan". Rekomendasi: weekly audit transaksi <Rp 50.000.' if compare.loc['Std', 'Micro'] < compare.loc['Std', 'Normal'] else '✅ **Pengeluaran normal lebih transparan** — pengguna cenderung sadar karena nominalnya besar dan frekuensinya jarang.'}
                """
                st.info(insight_q2_box)

        s1, s2, s3 = st.columns(3)
        s1.metric("uji beda rata-rata/T-test p", f"{p_val:.4f}", "Beda nyata/Signifikan" if p_val < 0.05 else "Tidak")
        s2.metric("uji beda kelompok/Mann-Whitney p", f"{u_pval:.4f}", "Beda nyata/Signifikan" if u_pval < 0.05 else "Tidak")
        s3.metric("Besaran Pengaruh/Effect Size", es)

        with st.expander("💡 Insight Q2 Komprehensif", expanded=True):
            insight_q2 = f"""
            **Jawaban Q2:** pengeluaran mikro/micro-spending beda nyata/signifikan lebih kecil (p={p_val:.4f}, ukuran efek/Cohen's d={cohens_d:.2f}).

            **Temuan:** Rata-rata/Mean Normal Rp {compare.loc['Mean', 'Normal']:,.0f} vs Pengeluaran Mikro/Micro Rp {compare.loc['Mean', 'Micro']:,.0f}. Nilai Tengah/Median Normal Rp {compare.loc['Median', 'Normal']:,.0f} vs Pengeluaran Mikro/Micro Rp {compare.loc['Median', 'Micro']:,.0f}.

            **Mengapa:** Perbedaan statistik yang beda nyata/signifikan memvalidasi bahwa label memiliki karakteristik yang dapat dipisahkan — ini dasar untuk model AI deteksi pengeluaran mikro/micro-spending.

            **Risiko/Akibat:** {'⚠️ **Effect size besar!** Perbedaan ini sangat beda nyata/signifikan secara praktis. Model AI bisa dengan confidence tinggi membedakan micro vs normal. Tapi hati-hati: jangan terlalu agresif flagging, bisa jadi kesalahan deteksi/false positive untuk transaksi kecil yang sebenarnya penting (obat, transport).' if abs(cohens_d) >= 0.8 else '⚠️ **Effect size sedang** — model perlu tuning threshold untuk balance ketepatan & kelengkapan/precision-recall.' if abs(cohens_d) >= 0.5 else '⚠️ **Effect size kecil** — perlu rekayasa fitur/feature engineering tambahan untuk memperkuat pemisahan.'}
            """
            st.info(insight_q2)

    # ==================== Q3 ====================
    with q3:
        st.subheader("Q3: Visualisasi mana yang paling menonjolkan lonjakan pengeluaran impulsif?")

        mc = expense_df.groupby(['period', 'category']).agg(
            total=('amount', 'sum'), txn=('amount', 'size')
        ).reset_index().sort_values(['category', 'period'])

        mc['prev'] = mc.groupby('category')['total'].shift(1)
        mc['mom'] = ((mc['total'] - mc['prev']) / (mc['prev'] + 1e-9)).replace([np.inf, -np.inf], 0) * 100
        mc['z'] = mc.groupby('category')['total'].transform(lambda x: (x - x.mean()) / (x.std() + 1e-9))
        mc['anom'] = (mc['z'].abs() > 2).astype(int)

        af = mc.groupby('category').agg(
            anom=('anom', 'sum'), months=('period', 'size'), z=('z', lambda x: x.abs().mean()), mg=('mom', 'max')
        ).reset_index()
        af['rate'] = af['anom'] / af['months']
        af = af.sort_values('rate', ascending=False)

        wi = expense_df.groupby(['category', 'is_weekend']).agg(mr=('is_micro', 'mean')).reset_index().pivot(index='category', columns='is_weekend', values='mr').fillna(0)
        if 1 in wi.columns and 0 in wi.columns:
            wi['boost'] = wi[1] - wi[0]
        else:
            wi['boost'] = 0
        wi = wi.sort_values('boost', ascending=False)

        m1, m2, m3 = st.columns(3)
        m1.metric("🔥 fluktuatif/Volatile", af.iloc[0]['category'] if len(af) > 0 else "-", f"Rate: {af.iloc[0]['rate']:.1%}" if len(af) > 0 else "")
        m2.metric("📈 Max MoM", f"{af['mg'].max():.1f}%" if len(af) > 0 else "")
        m3.metric("🌴 Weekend", wi.index[0] if len(wi) > 0 else "-", f"Boost: {wi.iloc[0]['boost']:.1%}" if len(wi) > 0 else "")
        st.divider()

        st.markdown("#### 📊 Perubahan Pengeluaran dari Bulan Sebelumnya (pertumbuhan bulanan/MoM Growth %)")
        if len(mc) > 0:
            rm = sorted(mc['period'].unique())[-6:]
            hd = mc[mc['period'].isin(rm)].copy()
            hd['ms'] = hd['period'].astype(str)
            pv = hd.pivot_table(index='category', columns='ms', values='mom', fill_value=0)
            if not pv.empty:
                pv_reset = pv.reset_index().melt(id_vars='category', var_name='bulan', value_name='mom_growth')
                fig = px.bar(pv_reset, x='bulan', y='mom_growth', color='category', 
                             title="Perubahan Pengeluaran dari Bulan Sebelumnya (pertumbuhan bulanan/MoM Growth %)", 
                             template="plotly_white", barmode='group')
                st.plotly_chart(fig, use_container_width=True)

                # INSIGHT MoM - KOMPREHENSIF + PENJELASAN
                max_growth = pv_reset['mom_growth'].max()
                max_grow_cat = pv_reset.loc[pv_reset['mom_growth'].idxmax(), 'category'] if max_growth > 0 else "-"
                insight_mom = f"""
                💡 **Insight Perubahan Bulanan (MoM)**

                **Temuan:** Lonjakan tertinggi **{max_growth:.1f}%** di kategori **{max_grow_cat}**.

                **Mengapa:** Rumus: **((Bulan Ini - Bulan Lalu) / Bulan Lalu) × 100%**. Angka positif menunjukkan kenaikan, negatif menunjukkan penurunan, dan >50% merupakan lonjakan besar.

                **Risiko/Akibat:** {'⚠️ **PERINGATAN!** Lonjakan >50% merupakan indikasi kuat overspending atau pembelian impulsif. Penyebabnya dapat berupa promo menyesatkan, FOMO, atau penghargaan diri yang berlebihan. Rekomendasi: tunda pengeluaran untuk kategori ini selama 2 minggu.' if max_growth > 50 else '⚠️ **Perhatian** — lonjakan 30-50% masih perlu dipantau. Cek apakah ada event khusus (liburan, lebaran) yang menyebabkan kenaikan.' if max_growth > 30 else '✅ **Stabil** — perubahan bulanan masih dalam batas wajar (<30%).'}
                """
                st.info(insight_mom)
            else:
                st.info("Data tidak mencukupi untuk visualisasi MoM.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ⚠️ Anomaly Rate")
            if len(af) > 0:
                fig = px.bar(af.head(8), x='category', y='rate', template="plotly_white", color='rate', color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)

                # INSIGHT ANOMALY - KOMPREHENSIF
                top_anom = af.iloc[0]['category'] if len(af) > 0 else "-"
                top_rate = af.iloc[0]['rate'] if len(af) > 0 else 0
                insight_anom = f"""
                💡 **Insight Anomaly Rate**

                **Temuan:** **{top_anom}** paling fluktuatif/volatile (tingkat ketidaknormalan/anomaly rate {top_rate:.1%}).

                **Mengapa:** tingkat ketidaknormalan/Anomaly rate = proporsi bulan di mana pengeluaran kategori melebihi/melewati batas normal (skor penyimpangan/Z-score > 2). Semakin tinggi = semakin tidak prediktabil.

                **Risiko/Akibat:** {'⚠️ **Kategori ini sulit diprediksi!** Pengeluarannya naik turun drastis setiap bulan. Risiko: perencanaan anggaran dapat gagal. Solusi: gunakan "rata-rata berjalan/rolling average 3 bulan" sebagai patokan, bukan hanya bulan lalu.' if top_rate > 0.15 else '✅ **Kategori stabil** — pengeluarannya relatif konsisten, sehingga memudahkan perencanaan anggaran.'}
                """
                st.info(insight_anom)
        with c2:
            st.markdown("#### 🌴 Weekend Impulse Boost")
            if len(wi) > 0:
                fig = px.bar(wi.head(8).reset_index(), x='category', y='boost', template="plotly_white", color='boost', color_continuous_scale='Teal')
                st.plotly_chart(fig, use_container_width=True)

                # INSIGHT WEEKEND - KOMPREHENSIF
                top_wk = wi.index[0] if len(wi) > 0 else "-"
                top_boost = wi.iloc[0]['boost'] if len(wi) > 0 else 0
                insight_wk = f"""
                💡 **Insight Weekend Impulse**

                **Temuan:** **{top_wk}** naik **{top_boost:.1%}** di weekend (Sabtu-Minggu).

                **Mengapa:** Weekend boost = (Pengeluaran Mikro/Micro-rate Weekend - Pengeluaran Mikro/Micro-rate Weekday). Positif = lebih banyak pengeluaran mikro/micro-spending di weekend. Negatif = lebih banyak di weekday.

                **Risiko/Akibat:** {'⚠️ **Jebakan akhir pekan terkonfirmasi!** Kategori ini memicu pembelian impulsif di akhir pekan. Strategi: "Sabtu Tanpa Pengeluaran" — tetapkan 1 hari akhir pekan tanpa pengeluaran non-esensial.' if top_boost > 0.1 else '✅ **Pola normal** — tidak ada perbedaan beda nyata/signifikan antara weekday dan weekend.'}
                """
                st.info(insight_wk)

        with st.expander("💡 Insight Q3 Komprehensif", expanded=True):
            tv = af.iloc[0]['category'] if len(af) > 0 else "-"
            tr = af.iloc[0]['rate'] if len(af) > 0 else 0
            insight_q3 = f"""
            **Jawaban Q3:** Visualisasi **Perubahan Pengeluaran Bulanan (pertumbuhan bulanan/MoM Growth)** paling beda nyata/signifikan untuk memicu awareness.

            **Temuan:** Kategori **{tv}** menunjukkan pola fluktuatif/volatile (tingkat ketidaknormalan/anomaly rate {tr:.1%}).

            **Mengapa:** Heatmap/bar pertumbuhan bulanan/MoM Growth langsung menunjukkan "berapa persen naik/turun dari bulan lalu" — bahasa yang paling mudah dipahami user.

            **Risiko/Akibat:** {'⚠️ **Dashboard Priority: HERO visual!** pertumbuhan bulanan/MoM Growth harus jadi chart pertama yang dilihat user. Trigger: "Lonjakan X% di [Kategori]" → langsung muncul rekomendasi action. Jika tidak ditangkap, user bisa kehabisan budget di minggu pertama!' if tr > 0.15 else '✅ **Secondary priority** — kategori ini stabil, fokus pada kategori lain yang lebih fluktuatif/volatile.'}
            """
            st.warning(insight_q3)

st.divider()
st.caption("🚀 CentSaver | DBS Foundation Capstone Project 2026")