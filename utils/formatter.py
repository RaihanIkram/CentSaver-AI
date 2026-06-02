#utils/formatter.py
TYPE_MAP = {
"income": "Pemasukan",
"expense": "Pengeluaran"
}

STATUS_MAP = {
"HIGH": "Tinggi",
"WARNING": "Sedang",
"NORMAL": "Normal"
}

def rupiah(x):
    return f"Rp {x:,.0f}".replace(",", ".")
