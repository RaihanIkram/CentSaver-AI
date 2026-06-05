import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Konfigurasi visualisasi
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11


def load_and_prepare_data(csv_path):
    """
    Load data dan filter transaksi mikro saja.
    """
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Asumsi: label = 1 artinya transaksi mikro
    micro_df = df[df['label'] == 1].copy()
    
    return df, micro_df


def get_top_categories(micro_df, n=5):
    """
    Ambil n kategori dengan jumlah transaksi terbanyak.
    """
    top = (micro_df.groupby('category')['amount']
           .agg(['count', 'sum', 'mean'])
           .sort_values('count', ascending=False)
           .head(n))
    return top


def run_ab_test(micro_df, group_a_name, group_b_name, alpha=0.05):
    """
    Jalankan A/B testing antara dua kategori.
    """
    # Ambil data per grup
    group_a = micro_df[micro_df['category'] == group_a_name]['amount'].dropna()
    group_b = micro_df[micro_df['category'] == group_b_name]['amount'].dropna()
    
    n_a = len(group_a)
    n_b = len(group_b)
    mean_a = group_a.mean()
    mean_b = group_b.mean()
    std_a = group_a.std()
    std_b = group_b.std()
    
    # Welch's t-test (varians tidak sama)
    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    
    # Mann-Whitney U (non-parametrik, alternatif kalau data tidak normal)
    u_stat, u_pvalue = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
    
    # Cohen's d (ukuran efek)
    pooled_var = ((n_a - 1) * group_a.var() + (n_b - 1) * group_b.var()) / (n_a + n_b - 2)
    pooled_std = np.sqrt(pooled_var)
    cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0
    
    # Tentukan ukuran efek
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        effect_size = "Besar"
    elif abs_d >= 0.5:
        effect_size = "Sedang"
    else:
        effect_size = "Kecil"
    
    # Hitung selisih persen
    diff_pct = ((mean_a - mean_b) / mean_b * 100) if mean_b != 0 else 0
    
    # Keputusan
    reject_h0 = p_value <= alpha
    
    return {
        'group_a': {'name': group_a_name, 'mean': mean_a, 'std': std_a, 'n': n_a},
        'group_b': {'name': group_b_name, 'mean': mean_b, 'std': std_b, 'n': n_b},
        't_stat': t_stat,
        'p_value': p_value,
        'u_stat': u_stat,
        'u_pvalue': u_pvalue,
        'cohens_d': cohens_d,
        'effect_size': effect_size,
        'diff_pct': diff_pct,
        'reject_h0': reject_h0,
        'alpha': alpha
    }


def create_visualizations(result, group_a_data, group_b_data):
    """
    Buat 3 panel visualisasi: boxplot, bar chart, ringkasan.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Panel 1: Boxplot
    data_for_box = pd.DataFrame({
        'Nominal': np.concatenate([group_a_data, group_b_data]),
        'Group': [result['group_a']['name']] * len(group_a_data) + 
                 [result['group_b']['name']] * len(group_b_data)
    })
    # Fix warning: pake hue dan legend=False
    sns.boxplot(data=data_for_box, x='Group', y='Nominal', 
                hue='Group', palette=['steelblue', 'coral'], 
                ax=axes[0], legend=False)
    axes[0].set_title('Perbandingan Distribusi')
    axes[0].set_ylabel('Nominal Transaksi (Rp)')
    
    # Panel 2: Bar chart rata-rata dengan 95% CI
    means = [result['group_a']['mean'], result['group_b']['mean']]
    stds = [result['group_a']['std'], result['group_b']['std']]
    ns = [result['group_a']['n'], result['group_b']['n']]
    cis = [1.96 * s / np.sqrt(n) for s, n in zip(stds, ns)]
    
    bars = axes[1].bar(
        [result['group_a']['name'], result['group_b']['name']], 
        means, yerr=cis, capsize=8,
        color=['steelblue', 'coral'], edgecolor='black', alpha=0.85
    )
    axes[1].set_title('Rata-rata +/- 95% CI')
    axes[1].set_ylabel('Rata-rata Nominal (Rp)')
    
    for bar, mean in zip(bars, means):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2, 
            bar.get_height() + max(cis) * 0.05,
            f'Rp {mean:,.0f}', ha='center', va='bottom', fontweight='bold'
        )
    
    # Panel 3: Ringkasan hasil uji
    axes[2].axis('off')
    
    keputusan = "TOLAK H0" if result['reject_h0'] else "GAGAL TOLAK H0"
    warna_box = 'lightgreen' if result['reject_h0'] else 'lightyellow'
    warna_border = 'green' if result['reject_h0'] else 'orange'
    
    result_text = (
        f"p-value (T-test): {result['p_value']:.4f}\n"
        f"p-value (Mann-Whitney): {result['u_pvalue']:.4f}\n"
        f"alpha: {result['alpha']}\n\n"
        f"{keputusan}\n\n"
        f"Cohen's d: {result['cohens_d']:.2f}\n"
        f"Ukuran efek: {result['effect_size']}"
    )
    
    axes[2].text(
        0.5, 0.5, result_text, transform=axes[2].transAxes, fontsize=13,
        verticalalignment='center', horizontalalignment='center',
        bbox=dict(
            boxstyle='round,pad=0.8', facecolor=warna_box, 
            edgecolor=warna_border, linewidth=2
        )
    )
    axes[2].set_title('Ringkasan Hasil Uji')
    
    plt.tight_layout()
    return fig


def create_summary_dataframe(result):
    """
    Buat tabel ringkasan untuk di-export ke CSV.
    """
    summary = pd.DataFrame({
        'Metrik': [
            'Rata-rata/Mean', 'Simpangan Baku/Std', 'Jumlah Sampel',
            'p-value (T-test)', 'p-value (Mann-Whitney)', 
            "Cohen's d", 'Ukuran Efek', 'Keputusan'
        ],
        f"Group A ({result['group_a']['name']})": [
            result['group_a']['mean'],
            result['group_a']['std'],
            result['group_a']['n'],
            result['p_value'],
            result['u_pvalue'],
            result['cohens_d'],
            result['effect_size'],
            'TOLAK H0' if result['reject_h0'] else 'GAGAL TOLAK H0'
        ],
        f"Group B ({result['group_b']['name']})": [
            result['group_b']['mean'],
            result['group_b']['std'],
            result['group_b']['n'],
            '-', '-', '-', '-', '-'
        ]
    })
    return summary


def get_interpretation(result):
    """
    Kasih interpretasi dan rekomendasi berdasarkan 4 skenario Dicoding.
    """
    p = result['p_value']
    d = abs(result['cohens_d'])
    alpha = result['alpha']
    
    if p <= alpha:
        if d >= 0.8:
            skenario = 1
            judul = "Skenario 1: Beda nyata & besar"
            penjelasan = "Perbedaan beneran ada DAN penting buat bisnis."
            saran = [
                "1. Terapkan strategi penghematan BERBEDA per kategori.",
                "2. Tetapkan batas pengeluaran (threshold) yang beda per kategori.",
                "3. Beri notifikasi 'Smart Alert' yang lebih sering buat kategori dengan rata-rata lebih tinggi."
            ]
        elif d >= 0.5:
            skenario = 2
            judul = "Skenario 2: Beda nyata & sedang"
            penjelasan = "Perbedaan ada dan cukup terasa, tapi tidak terlalu kuat."
            saran = [
                "1. Bisa bedakan strategi per kategori, tapi tetap fleksibel.",
                "2. Coba A/B testing lanjutan untuk test intervensi spesifik.",
                "3. Pantau metrik retention setelah strategi diterapkan."
            ]
        else:
            skenario = 3
            judul = "Skenario 3: Beda statistik tapi kecil"
            penjelasan = "Bedanya memang ada (bukan kebetulan), tapi dampaknya kecil."
            saran = [
                "1. Strategi penghematan bisa SAMA SAJA antar kategori.",
                "2. Fokus ke fitur lain yang lebih bermanfaat.",
                "3. Kalau ingin lebih yakin, tambah data atau perpanjang periode pengamatan."
            ]
    else:
        skenario = 4
        judul = "Skenario 4: Tidak ada beda"
        penjelasan = "Belum ada bukti kuat bahwa kedua kategori beda secara signifikan."
        saran = [
            "1. Pakai strategi penghematan yang SERAGAM.",
            "2. Tidak perlu bikin fitur khusus yang bedain perlakuan antar kategori.",
            "3. Kalau yakin ada beda, perluas durasi pengamatan atau ukuran sampel."
        ]
    
    return {
        'skenario': skenario,
        'judul': judul,
        'penjelasan': penjelasan,
        'saran': saran
    }