"""
A/B Testing Module for CentSaver AI
Compatible with Streamlit, Jupyter, and plain Python scripts.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path


def load_and_prepare_data(csv_path):
    """
    Load CSV and preprocess columns for A/B testing.
    Expected columns: date, amount, category, label
    """
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    # 'label' column: 1 = micro transaction, 0 = non-micro
    df['is_micro'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
    return df


def get_top_categories(micro_df, n=5):
    """
    Return top N categories by transaction count.
    """
    top = (
        micro_df.groupby('category')['amount']
        .agg(['count', 'sum', 'mean'])
        .sort_values('count', ascending=False)
        .head(n)
    )
    return top


def run_ab_test(micro_df, group_a_name, group_b_name, alpha=0.05):
    """
    Run independent t-test (Welch) and Mann-Whitney U on two category groups.
    Returns a dictionary with all metrics and test results.
    """
    group_a = micro_df[micro_df['category'] == group_a_name]['amount'].dropna()
    group_b = micro_df[micro_df['category'] == group_b_name]['amount'].dropna()

    if len(group_a) < 2 or len(group_b) < 2:
        raise ValueError("Each group must have at least 2 transactions.")

    # Descriptive stats
    stats_a = {
        'name': group_a_name,
        'n': len(group_a),
        'mean': float(group_a.mean()),
        'median': float(group_a.median()),
        'std': float(group_a.std()),
    }
    stats_b = {
        'name': group_b_name,
        'n': len(group_b),
        'mean': float(group_b.mean()),
        'median': float(group_b.median()),
        'std': float(group_b.std()),
    }

    # T-test (Welch, two-tailed)
    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)

    # Cohen's d (pooled std)
    pooled_std = np.sqrt(
        ((stats_a['n'] - 1) * group_a.var() + (stats_b['n'] - 1) * group_b.var()) 
        / (stats_a['n'] + stats_b['n'] - 2)
    )
    cohens_d = (stats_a['mean'] - stats_b['mean']) / pooled_std if pooled_std > 0 else 0.0

    # Mann-Whitney U (non-parametric)
    u_stat, u_pvalue = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')

    # Effect size interpretation
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        effect_size = "Besar"
    elif abs_d >= 0.5:
        effect_size = "Sedang"
    else:
        effect_size = "Kecil"

    return {
        'group_a': stats_a,
        'group_b': stats_b,
        't_stat': float(t_stat),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d),
        'effect_size': effect_size,
        'u_stat': float(u_stat),
        'u_pvalue': float(u_pvalue),
        'alpha': alpha,
        'reject_h0': bool(p_value <= alpha),
        'diff_pct': ((stats_a['mean'] - stats_b['mean']) / stats_b['mean'] * 100) if stats_b['mean'] != 0 else 0.0,
    }


def create_summary_dataframe(result):
    """
    Create a summary DataFrame from test result (good for CSV export).
    """
    rows = [
        ['Rata-rata/Mean', result['group_a']['mean'], result['group_b']['mean']],
        ['Nilai Tengah/Median', result['group_a']['median'], result['group_b']['median']],
        ['Simpangan Baku/Std', result['group_a']['std'], result['group_b']['std']],
        ['Jumlah Sampel', result['group_a']['n'], result['group_b']['n']],
        ['p-value (T-test)', result['p_value'], '-'],
        ['p-value (Mann-Whitney)', result['u_pvalue'], '-'],
        ["Cohen's d", result['cohens_d'], '-'],
        ['Keputusan', 'TOLAK H₀' if result['reject_h0'] else 'GAGAL TOLAK H₀', '-'],
    ]
    df = pd.DataFrame(rows, columns=['Metrik', f"Group A ({result['group_a']['name']})", f"Group B ({result['group_b']['name']})"])
    return df


def create_visualizations(result, group_a_series, group_b_series):
    """
    Create matplotlib Figure with 3 subplots.
    Returns the Figure object (do NOT call plt.show() here).
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # 1. Boxplot
    data_for_box = pd.DataFrame({
        'Nominal': pd.concat([group_a_series, group_b_series]),
        'Group': [result['group_a']['name']]*len(group_a_series) + [result['group_b']['name']]*len(group_b_series)
    })
    import seaborn as sns
    sns.boxplot(data=data_for_box, x='Group', y='Nominal', 
                palette=['steelblue', 'coral'], ax=axes[0])
    axes[0].set_title('Perbandingan Distribusi')
    axes[0].set_ylabel('Nominal Transaksi Mikro (Rp)')

    # 2. Bar chart with 95% CI
    means = [result['group_a']['mean'], result['group_b']['mean']]
    stds = [result['group_a']['std'], result['group_b']['std']]
    ns = [result['group_a']['n'], result['group_b']['n']]
    cis = [1.96 * s / np.sqrt(n) for s, n in zip(stds, ns)]

    bars = axes[1].bar(
        [result['group_a']['name'], result['group_b']['name']], 
        means, yerr=cis, capsize=8,
        color=['steelblue', 'coral'], edgecolor='black', alpha=0.85
    )
    axes[1].set_title('Rata-rata ± 95% CI')
    axes[1].set_ylabel('Rata-rata Nominal (Rp)')
    for bar, mean in zip(bars, means):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cis)*0.05,
                    f'Rp {mean:,.0f}', ha='center', va='bottom', fontweight='bold')

    # 3. Summary text panel
    axes[2].axis('off')
    result_text = (
        f"p-value: {result['p_value']:.4f}\n"
        f"α: {result['alpha']}\n\n"
        f"{'✅ TOLAK H₀' if result['reject_h0'] else '❌ GAGAL TOLAK H₀'}\n"
        f"Cohen's d: {result['cohens_d']:.2f}\n"
        f"(Ukuran efek: {result['effect_size']})"
    )
    axes[2].text(0.5, 0.5, result_text, transform=axes[2].transAxes,
                fontsize=14, verticalalignment='center', horizontalalignment='center',
                bbox=dict(boxstyle='round', 
                         facecolor='lightgreen' if result['reject_h0'] else 'lightyellow',
                         edgecolor='green' if result['reject_h0'] else 'orange', linewidth=2))
    axes[2].set_title('Ringkasan Hasil Uji')

    plt.tight_layout()
    return fig
