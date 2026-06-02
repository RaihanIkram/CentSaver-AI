import pandas as pd

def generate_insight(df, forecast_df=None):
    """
    Generate insight sederhana dari data transaksi
    dan hasil forecasting.

    Parameters
    ----------
    df : pandas.DataFrame
        Data transaksi yang sudah difilter periode.

    forecast_df : pandas.DataFrame, optional
        Hasil forecast dari monthly_alert().

    Returns
    -------
    str
        Insight dalam bentuk teks yang bisa ditampilkan di UI.
    """

    insights = []

    if df is None or len(df) == 0:
        return "Belum terdapat data transaksi yang cukup untuk dianalisis."

    expense_df = df[df["type"] == "expense"].copy()

    if len(expense_df) == 0:
        return "Belum terdapat data pengeluaran yang cukup untuk dianalisis."

    # ==================================================
    # MICRO SPENDING
    # ==================================================

    micro_count = int(
        pd.to_numeric(
            expense_df["micro_label"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
        .sum()
    )

    micro_rate = (
        micro_count /
        len(expense_df)
    ) * 100

    insights.append(
        f"{micro_rate:.1f}% transaksi pengeluaran "
        f"terdeteksi sebagai micro spending."
    )

    # ==================================================
    # TOP CATEGORY
    # ==================================================

    try:
        top_category = (
            expense_df
            .groupby("category")["amount"]
            .sum()
            .idxmax()
        )

        insights.append(
            f"Kategori pengeluaran terbesar "
            f"adalah {top_category}."
        )
    except Exception:
        pass

    # ==================================================
    # TOTAL EXPENSE
    # ==================================================

    total_expense = (
        pd.to_numeric(
            expense_df["amount"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

    insights.append(
        f"Total pengeluaran pada periode ini "
        f"mencapai Rp {total_expense:,.0f}."
    )

    # ==================================================
    # RISK DETECTION
    # ==================================================

    risk_count = int(
        pd.to_numeric(
            expense_df["risk_label"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
        .sum()
    )

    insights.append(
        f"Terdapat {risk_count} transaksi "
        f"yang terindikasi berisiko."
    )

    # ==================================================
    # FORECAST INSIGHT
    # ==================================================

    if (
        forecast_df is not None
        and len(forecast_df) > 0
        and "growth_ratio" in forecast_df.columns
    ):
        try:
            top_alert = (
                forecast_df
                .sort_values(
                    "growth_ratio",
                    ascending=False
                )
                .iloc[0]
            )

            insights.append(
                f"{top_alert['category']} diprediksi "
                f"mengalami peningkatan pengeluaran "
                f"tertinggi pada periode berikutnya."
            )
        except Exception:
            pass

    # ==================================================
    # FINAL OUTPUT
    # ==================================================

    return "\n\n• " + "\n\n• ".join(insights)

