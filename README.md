# 💰 CentSaver — Smart Expense Awareness System

**Capstone Project | DBS Foundation Coding Camp 2026**

---

## 🎯 Tentang Proyek

CentSaver adalah aplikasi dashboard berbasis **Streamlit** yang membantu pengguna mengontrol pengeluaran mikro (micro-spending) melalui:

- 📊 **Data Science**: EDA, visualisasi, A/B Testing, dan literasi keuangan
- 🧠 **AI Engineering**: Deep Learning dengan TensorFlow (custom components)

> Proyek ini merupakan bagian dari Projek Akhir (Capstone Project) dalam program Coding Camp powered by DBS Foundation.

---

## 🏛️ Arsitektur Dashboard

```
CentSaver-AI/
├── main.py                             ← Home Landing Page
├── Dashboard.py                        ← AI Dashboard (model inference)
├── ab_testing_module.py                ← Modul statistik A/B Testing
├── pages/
    ├── 0_🏠 Home Dashboard              ← Home Dashboard pengelanan project
│   ├── 1_➕_Tambah_Transaksi.py         ← Input transaksi harian
│   ├── 2_📋_Riwayat_Transaksi.py        ← Kelola riwayat pengeluaran
│   ├── 3_🔔_Prediksi_dan_Peringatan.py  ← AI Risk Detection & Alert
│   ├── 4_📊_Visualisasi_Dataset.py      ← EDA Interaktif
│   ├── 6_📰_Literasi_Keuangan.py        ← Berita ekonomi & edukasi finansial       
│   └── 7_🧪_Implementasi_AB_Testing     ← A/B Testing Console (internal)
├── utils/                               ← Helper functions
├── data/                                ← Dataset CSV
├── artifacts_centsaver/                 ← Model TensorFlow & scaler
├── Notebook-AI-DS/                      ← Notebook Dokumentasi
├── requirements.txt



```

---

## ✨ Fitur Utama

### 👤 User Dashboard (End-User)

| Fitur | Deskripsi |
|-------|-----------|
| ➕ Tambah Transaksi | Catat pengeluaran harian dengan kategori otomatis |
| 📋 Riwayat Transaksi | Filter, cari, dan kelola seluruh data historis |
| 🔔 Prediksi & Peringatan | Deep Learning mendeteksi risiko micro-spending |
| 📊 Visualisasi Dataset | EDA interaktif dengan grafik dan chart |
| 📰 Literasi Keuangan | Berita ekonomi, tips saham, edukasi finansial Indonesia |

### 🔬 Product Analytics Console (Internal Team)

| Fitur | Deskripsi |
|-------|-----------|
| 🧪 A/B Testing | Uji signifikansi statistik antar kategori (T-test Welch, Mann-Whitney U, Cohen's d) |
| 📈 Business Metrics | Perbandingan rata-rata, confidence interval, effect size |

### 🤖 AI Engineering

| Fitur | Deskripsi |
|-------|-----------|
| 🧠 Custom Layer | `SpendingAttentionBlock` |
| ⚖️ Custom Loss | `AdaptiveFocalLoss` |
| 📊 Custom Callback | TensorBoard tracking |
| 🚀 Model Inference | Real-time prediction via Streamlit |

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualisasi | Matplotlib, Seaborn, Plotly |
| Statistik | SciPy (T-test, Mann-Whitney U) |
| AI/ML | TensorFlow / Keras |
| Notebook | Jupyter / Google Colab |

---

## 🚀 Cara Menjalankan

### 1. Clone & Install
```bash
git clone https://github.com/RaihanIkram/CentSaver-AI
cd CentSaver-AI
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Jalankan Streamlit
```bash
streamlit run main.py
```

Akses di browser: `https://centsaver-cc26-pru458.streamlit.app/`

## 📰 Literasi Keuangan

Halaman edukasi yang menyajikan:
- Snapshot ekonomi Indonesia (literasi keuangan, IHSG, BI Rate, inflasi)
- Berita & insight terkini (saham, ekonomi, lifestyle)
- Tips keuangan praktis (50/30/20, dana darurat, reksa dana)
- Kamus istilah keuangan
- Referensi resmi dari OJK & Bank Indonesia

---

## 📁 Dataset

Dataset yang digunakan:
- `centsaver_master_relabelling.csv` — Data transaksi dengan label micro-spending
---

## 👥 Tim

**Capstone Team — DBS Foundation Coding Camp 2026**

- Data Science & AI Engineering Track

| Nama | Role | 
|------|------|
| [Raihan Ikram Maulana] | Data Science |
| [Amanda Ilma Zayta] | Data Science | 
| [Azka Ni'am] | AI Engineer | 
| [Fajar Ilhami Indo Syaputra] | AI Engineer | 
---

## 📚 Referensi

- Otoritas Jasa Keuangan & BPS. (2024). *National Survey On Financial Literacy And Inclusion 2024 Findings.* [OJK.go.id](https://ojk.go.id)
- Otoritas Jasa Keuangan & BPS. (2025). *Survei Nasional Literasi dan Inklusi Keuangan (SNLIK) 2025.* [OJK.go.id](https://ojk.go.id)
- Bank Indonesia. *Statistik Kebijakan Moneter.* [BI.go.id](https://bi.go.id)

---

## ⚠️ Catatan

- Modul **Product Analytics** (A/B Testing) ditujukan untuk tim internal (Data Scientist & Product Manager), bukan end-user.
- TensorFlow model memerlukan environment dengan library terinstall. Jika tidak tersedia, aplikasi akan berjalan dalam mode dummy dengan fallback prediction.

---