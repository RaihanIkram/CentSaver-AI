# 💰 CentSaver AI — Project 2 (Full Version)

**Capstone Project | DBS Foundation Coding Camp 2026**

Versi lengkap dengan semua **main quest** dan **side quest** Data Science & AI Engineering.

---

## 🎯 Tentang Proyek

CentSaver AI adalah aplikasi dashboard berbasis **Streamlit** yang membantu pengguna mengontrol **pengeluaran mikro (micro-spending)** melalui:
- 📊 **Data Science:** EDA, visualisasi, A/B Testing, dan literasi keuangan
- 🧠 **AI Engineering:** Deep Learning dengan TensorFlow (custom components)

> "Sadar. Catat. Hemat."

---

## 🏗️ Arsitektur Dashboard

```
📦 project2/
├── main.py                          ← Home Landing Page
├── Dashboard.py                     ← AI Dashboard (model inference)
├── ab_testing_module.py             ← Modul statistik A/B Testing
├── core_backend.py                  ← Backend AI (TensorFlow model loader)
├── pages/
│   ├── 1_➕_Tambah_Transaksi.py     ← Input transaksi harian
│   ├── 2_📋_Riwayat_Transaksi.py    ← Kelola riwayat pengeluaran
│   ├── 3_🔔_Prediksi_dan_Peringatan.py  ← AI Risk Detection & Alert
│   ├── 4_📊_Visualisasi_Dataset.py  ← EDA Interaktif
│   ├── 5_🧪_Product_Analytics.py   ← A/B Testing Console (internal)
│   └── 6_📰_Literasi_Keuangan.py   ← Berita ekonomi & edukasi finansial
├── utils/                           ← Helper functions
├── data/                            ← Dataset CSV
├── artifacts_centsaver/             ← Model TensorFlow & scaler
├── ab_testing_analysis.ipynb        ← Notebook dokumentasi A/B Testing
└── requirements.txt
```

---

## ✨ Fitur Utama

### 👤 User Dashboard (End-User)
| Fitur | Deskripsi |
|-------|-----------|
| ➕ **Tambah Transaksi** | Catat pengeluaran harian dengan kategori otomatis |
| 📋 **Riwayat Transaksi** | Filter, cari, dan kelola seluruh data historis |
| 🔔 **Prediksi & Peringatan** | Deep Learning mendeteksi risiko micro-spending |
| 📊 **Visualisasi Dataset** | EDA interaktif dengan grafik dan chart |
| 📰 **Literasi Keuangan** | Berita ekonomi, tips saham, edukasi finansial Indonesia |

### 🔬 Product Analytics Console (Internal Team)
| Fitur | Deskripsi |
|-------|-----------|
| 🧪 **A/B Testing** | Uji signifikansi statistik antar kategori (T-test Welch, Mann-Whitney U, Cohen's d) |
| 📈 **Business Metrics** | Perbandingan rata-rata, confidence interval, effect size |

### 🤖 AI Engineering
| Fitur | Deskripsi |
|-------|-----------|
| 🧠 **Custom Layer** | `SpendingAttentionBlock` |
| 📉 **Custom Loss** | `AdaptiveFocalLoss` |
| 📊 **Custom Callback** | TensorBoard tracking |
| 🚀 **Model Inference** | Real-time prediction via Streamlit |
| 🔌 **FastAPI** | REST API endpoint untuk model serving |

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualisasi | Matplotlib, Seaborn, Plotly |
| Statistik | SciPy (T-test, Mann-Whitney U) |
| AI/ML | TensorFlow / Keras |
| API | FastAPI |
| Notebook | Jupyter / Google Colab |

---

## 🚀 Cara Menjalankan

### 1. Clone & Install
```bash
git clone <repo-url>
cd project2
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Jalankan Streamlit
```bash
streamlit run main.py
```

Akses di browser: `http://localhost:8501`

### 3. Jalankan FastAPI (Opsional)
```bash
uvicorn core_backend:app --reload
```

---

## 📋 Checklist Capstone

### Main Quest — Data Science
- [x] Collect & analyze problems, determine final solution
- [x] Define measurable business questions
- [x] End-to-end Data Wrangling (Gather, Assess, Clean)
- [x] Exploratory Data Analysis (EDA)
- [x] Data Visualizations & Explanatory Analysis
- [x] Interactive Streamlit Dashboard
- [x] Interactive model inference interface

### Main Quest — AI Engineering
- [x] Build Deep Learning model with TensorFlow Functional API / Model Subclassing
- [x] Custom Layer, Custom Loss Function, Custom Callback
- [x] Save & export model (`.keras` / SavedModel)
- [x] Simple inference code

### Side Quest — Data Science
- [x] **A/B Testing using Python** (Welch's T-test, Mann-Whitney U, Cohen's d)
- [x] Feature Engineering
- [ ] Deploy dashboard to Streamlit Cloud *(opsional)*
- [ ] Comprehensive technical report in PDF *(opsional)*

### Side Quest — AI Engineering
- [x] Standalone REST API using FastAPI
- [x] Fully custom training & evaluation loop with `tf.GradientTape`
- [x] Generative AI API for secondary features
- [x] TensorBoard integration
- [x] Model performance: Accuracy ≥ 85%, MAE ≤ 0.02

---

## 📊 A/B Testing Module

Modul statistik untuk membandingkan pola pengeluaran mikro antar kategori.

### Metode
- **Welch's T-test** (two-tailed, unequal variance)
- **Mann-Whitney U** (non-parametric alternative)
- **Cohen's d** (effect size)

### Cara Pakai
1. Buka tab **🧪 Product Analytics** di sidebar
2. Upload dataset CSV atau gunakan data lokal
3. Pilih 2 kategori untuk dibandingkan
4. Klik **Jalankan A/B Testing**
5. Lihat hasil statistik, visualisasi, dan download CSV

### Notebook
File `ab_testing_analysis.ipynb` tersedia untuk eksplorasi mendalam di Jupyter/Colab.

---

## 📰 Literasi Keuangan

Halaman edukasi yang menyajikan:
- Snapshot ekonomi Indonesia (literasi keuangan, IHSG, BI Rate, inflasi)
- Berita & insight terkini (saham, ekonomi, lifestyle)
- Tips keuangan praktis (50/30/20, dana darurat, reksa dana)
- Kamus istilah keuangan
- **Referensi resmi dari OJK & Bank Indonesia**

---

## 📁 Dataset

Dataset yang digunakan:
- `centsaver_master_relabelling.csv` — Data transaksi dengan label micro-spending

Kolom wajib:
- `date` / `transaction_date`: Tanggal transaksi
- `amount`: Nominal pengeluaran
- `category`: Kategori transaksi
- `label`: 1 = micro transaction, 0 = non-micro
- `type`: income / expense

---

## 👥 Tim

**Capstone Team — DBS Foundation Coding Camp 2026**
- Data Science & AI Engineering Track

---

## 📝 Referensi

- Otoritas Jasa Keuangan & BPS. (2024). *National Survey On Financial Literacy And Inclusion 2024 Findings.* [OJK.go.id](https://www.ojk.go.id/en/berita-dan-kegiatan/siaran-pers/Pages/OJK-And-Statistics-Indonesia-Present-National-Survey-On-Financial-Literacy-And-Inclusion-2024-Findings.aspx)
- Otoritas Jasa Keuangan & BPS. (2025). *Survei Nasional Literasi dan Inklusi Keuangan (SNLIK) 2025.* [OJK.go.id](https://www.ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/OJK-dan-BPS-Umumkan-Hasil-Survei-Nasional-Literasi-Dan-Inklusi-Keuangan-SNLIK-Tahun-2025.aspx)
- Bank Indonesia. *Statistik Kebijakan Moneter.* [BI.go.id](https://www.bi.go.id/id/statistik/default.aspx)

---

## ⚠️ Catatan

- Modul **Product Analytics** (A/B Testing) ditujukan untuk **tim internal** (Data Scientist & Product Manager), bukan end-user.
- TensorFlow model memerlukan environment dengan library terinstall. Jika tidak tersedia, aplikasi akan berjalan dalam **mode dummy** dengan fallback prediction.
