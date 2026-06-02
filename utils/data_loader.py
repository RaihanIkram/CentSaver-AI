#utils/data_loader.py
from pathlib import Path
import pandas as pd

CSV_PATH = Path("data/transactions.csv")

def load_transactions():
    if not CSV_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(CSV_PATH)

    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            errors="coerce"
        )

    return df