# 📊 Automated EDA Report Generator

> Upload any CSV or Excel file → get a full exploratory data analysis report in seconds — with a one-click PDF download.

**Live demo:** `streamlit run app.py`

---

## What it does

| Feature | Detail |
|---|---|
| **Auto EDA** | Detects dtypes, missing values, cardinality, distributions |
| **Correlation heatmap** | Seaborn diverging heatmap for all numeric columns |
| **Missing value chart** | Color-coded bar chart (red >30%, amber >10%) |
| **Outlier detection** | IQR method per numeric column |
| **Skewness flag** | Flags columns needing log/sqrt transforms |
| **PDF export** | One-click downloadable report with all charts + insights |
| **Excel support** | Works with `.csv`, `.xlsx`, `.xls` |

---

## Stack

- **Python 3.10+**
- **Streamlit** — UI and file upload
- **Pandas / NumPy** — data wrangling
- **Matplotlib / Seaborn** — visualizations
- **fpdf2** — PDF report generation
- **ydata-profiling** — extended profiling (optional)

---

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/eda-report-generator.git
cd eda-report-generator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Open http://localhost:8501 and upload `demo_loan_data.csv` to see it in action.

---

## Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. Click **Deploy** — you get a public URL in ~60 seconds

---

## Project structure

```
eda-report-generator/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── demo_loan_data.csv      # Sample dataset (500 rows, 11 columns)
└── README.md
```

---

## Business impact

- Saves analysts **2–4 hours** of manual EDA per new dataset
- Generates consistent, shareable PDF reports for stakeholders
- Works on any structured dataset — no code changes needed
- Plugs into any data team's pre-modelling workflow

---

## What I learned building this

- Building **production-ready Streamlit apps** (not just notebooks)
- Generating **programmatic PDF reports** with charts embedded
- Writing **reusable data quality checks** (outliers, skewness, missing values)
- Designing tools that **non-technical stakeholders** can actually use

---

*Built as a portfolio project to demonstrate tool-building skills beyond notebook analysis.*
