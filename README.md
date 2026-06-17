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

Open http://localhost:8501 and upload `demo_loan_data.csv` to see it in action.


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
