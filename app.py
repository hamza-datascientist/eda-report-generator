import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import io
import os
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EDA Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Top bar */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 0 1.5rem 0;
    border-bottom: 1.5px solid #1a1a2e;
    margin-bottom: 2rem;
}
.brand {
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #0f0f23;
}
.brand span { color: #5b5ef4; }
.badge {
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    background: #f0f0ff;
    color: #5b5ef4;
    border: 1px solid #c7c7ff;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 500;
}

/* Upload zone */
.upload-hint {
    text-align: center;
    padding: 0.5rem 0 1.5rem 0;
    color: #888;
    font-size: 0.85rem;
}

/* Metric cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 1.5rem 0;
}
.metric-card {
    background: #fafafa;
    border: 1px solid #e8e8f0;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
}
.metric-label {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 600;
    color: #0f0f23;
    line-height: 1;
}
.metric-sub {
    font-size: 0.72rem;
    color: #aaa;
    margin-top: 4px;
}

/* Section headers */
.section-header {
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    color: #5b5ef4;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e8e8f0;
}

/* Column insight cards */
.col-card {
    background: white;
    border: 1px solid #e8e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.col-card:hover { border-color: #c7c7ff; }
.col-name {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.85rem;
    color: #0f0f23;
}
.col-dtype {
    font-size: 0.7rem;
    background: #f0f0ff;
    color: #5b5ef4;
    padding: 1px 7px;
    border-radius: 10px;
    margin-left: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.col-stats {
    display: flex;
    gap: 18px;
    margin-top: 8px;
    flex-wrap: wrap;
}
.stat-item { font-size: 0.78rem; color: #666; }
.stat-item strong { color: #0f0f23; }

/* Alert flags */
.flag-warn {
    font-size: 0.75rem;
    color: #b45309;
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 6px;
    padding: 4px 10px;
    margin-top: 8px;
    display: inline-block;
}
.flag-ok {
    font-size: 0.75rem;
    color: #065f46;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 6px;
    padding: 4px 10px;
    margin-top: 8px;
    display: inline-block;
}

/* Chart containers */
.chart-wrap {
    background: white;
    border: 1px solid #e8e8f0;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_data(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(file)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type.")


def dtype_label(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif series.nunique() / max(len(series), 1) < 0.05:
        return "categorical"
    else:
        return "text"


def column_insights(df: pd.DataFrame) -> list[dict]:
    insights = []
    for col in df.columns:
        s = df[col]
        null_pct = s.isna().mean() * 100
        label = dtype_label(s)
        info = {
            "name": col,
            "dtype": label,
            "null_pct": null_pct,
            "unique": s.nunique(),
            "total": len(s),
        }
        if label == "numeric":
            info["mean"] = s.mean()
            info["std"] = s.std()
            info["min"] = s.min()
            info["max"] = s.max()
            # skew flag
            try:
                info["skew"] = s.skew()
            except Exception:
                info["skew"] = 0
            # outlier flag (IQR)
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            outliers = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
            info["outliers"] = int(outliers)
        insights.append(info)
    return insights


def build_flags(info: dict) -> list[str]:
    flags = []
    if info["null_pct"] > 30:
        flags.append(f"⚠ {info['null_pct']:.0f}% missing — consider dropping or imputing this column")
    elif info["null_pct"] > 5:
        flags.append(f"⚠ {info['null_pct']:.0f}% missing — median/mode imputation recommended")
    if info.get("outliers", 0) > 0:
        pct = info["outliers"] / info["total"] * 100
        flags.append(f"⚠ {info['outliers']} outliers ({pct:.1f}%) detected via IQR method")
    if abs(info.get("skew", 0)) > 1:
        flags.append(f"⚠ Skewness {info['skew']:.2f} — consider log or sqrt transform")
    if info["unique"] == info["total"] and info["dtype"] != "numeric":
        flags.append("⚠ All values unique — likely an ID column, not useful for modeling")
    if not flags:
        flags.append("✓ No major data quality issues detected")
    return flags


def fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def plot_distribution(s: pd.Series, col: str):
    fig, ax = plt.subplots(figsize=(5, 2.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")
    s_clean = s.dropna()
    ax.hist(s_clean, bins=30, color="#5b5ef4", alpha=0.85, edgecolor="white", linewidth=0.4)
    ax.set_title(col, fontsize=9, fontweight="600", color="#0f0f23", pad=6)
    ax.tick_params(labelsize=7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    fig.tight_layout()
    return fig


def plot_value_counts(s: pd.Series, col: str, top_n: int = 10):
    fig, ax = plt.subplots(figsize=(5, 2.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")
    vc = s.value_counts().head(top_n)
    colors = ["#5b5ef4"] + ["#c7c7ff"] * (len(vc) - 1)
    ax.barh(vc.index.astype(str), vc.values, color=colors, edgecolor="white", linewidth=0.4)
    ax.invert_yaxis()
    ax.set_title(col, fontsize=9, fontweight="600", color="#0f0f23", pad=6)
    ax.tick_params(labelsize=7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", alpha=0.3, linewidth=0.5)
    fig.tight_layout()
    return fig


def plot_correlation(df: pd.DataFrame):
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] < 2:
        return None
    corr = num_df.corr()
    n = len(corr)
    size = max(5, min(n * 0.7, 10))
    fig, ax = plt.subplots(figsize=(size, size * 0.8))
    fig.patch.set_facecolor("white")
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(
        corr, mask=mask, cmap=cmap, vmin=-1, vmax=1,
        annot=True, fmt=".2f", annot_kws={"size": 8},
        linewidths=0.5, linecolor="#f0f0f0",
        ax=ax, cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Correlation Matrix", fontsize=10, fontweight="600", color="#0f0f23", pad=10)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    return fig


def plot_missing(df: pd.DataFrame):
    null_pct = (df.isnull().mean() * 100).sort_values(ascending=False)
    null_pct = null_pct[null_pct > 0]
    if null_pct.empty:
        return None
    fig, ax = plt.subplots(figsize=(7, max(2.5, len(null_pct) * 0.4)))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")
    colors = ["#ef4444" if v > 30 else "#f59e0b" if v > 10 else "#5b5ef4" for v in null_pct]
    ax.barh(null_pct.index, null_pct.values, color=colors, edgecolor="white", linewidth=0.4)
    ax.invert_yaxis()
    ax.set_xlabel("% Missing", fontsize=8)
    ax.set_title("Missing Values by Column", fontsize=10, fontweight="600", color="#0f0f23", pad=8)
    ax.tick_params(labelsize=8)
    ax.axvline(30, color="#ef4444", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axvline(10, color="#f59e0b", linestyle="--", linewidth=0.8, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", alpha=0.3, linewidth=0.5)
    fig.tight_layout()
    return fig


def generate_pdf(df: pd.DataFrame, insights: list[dict], filename: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(91, 94, 244)
    pdf.cell(0, 10, "EDA Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"File: {filename}   |   Rows: {df.shape[0]}   |   Columns: {df.shape[1]}", ln=True)
    pdf.ln(4)
    pdf.set_draw_color(91, 94, 244)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Summary table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 15, 35)
    pdf.cell(0, 8, "Dataset Overview", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    num_cols = df.select_dtypes(include="number").shape[1]
    cat_cols = df.shape[1] - num_cols
    total_missing = df.isnull().sum().sum()
    dup_rows = df.duplicated().sum()
    stats = [
        ("Rows", f"{df.shape[0]:,}"),
        ("Columns", str(df.shape[1])),
        ("Numeric columns", str(num_cols)),
        ("Categorical columns", str(cat_cols)),
        ("Total missing values", str(total_missing)),
        ("Duplicate rows", str(dup_rows)),
    ]
    for label, val in stats:
        pdf.cell(80, 7, label, border=0)
        pdf.cell(0, 7, val, ln=True)
    pdf.ln(4)

    # Correlation heatmap
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] >= 2:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 15, 35)
        pdf.cell(0, 8, "Correlation Heatmap", ln=True)
        fig = plot_correlation(df)
        if fig:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
            buf.seek(0)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(buf.read())
                tmp_path = tmp.name
            pdf.image(tmp_path, w=180)
            os.unlink(tmp_path)
            plt.close(fig)
        pdf.ln(4)

    # Missing values chart
    fig_miss = plot_missing(df)
    if fig_miss:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 15, 35)
        pdf.cell(0, 8, "Missing Values", ln=True)
        buf = io.BytesIO()
        fig_miss.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        buf.seek(0)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(buf.read())
            tmp_path = tmp.name
        pdf.image(tmp_path, w=150)
        os.unlink(tmp_path)
        plt.close(fig_miss)
        pdf.ln(4)

    # Column-by-column
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 15, 35)
    pdf.cell(0, 8, "Column Analysis", ln=True)
    pdf.ln(2)

    for info in insights:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(91, 94, 244)
        pdf.cell(0, 7, info["name"], ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 5, f"Type: {info['dtype']}   |   Missing: {info['null_pct']:.1f}%   |   Unique: {info['unique']}", ln=True)
        if info["dtype"] == "numeric":
            pdf.cell(0, 5,
                f"Mean: {info.get('mean', 0):.2f}   Std: {info.get('std', 0):.2f}   "
                f"Min: {info.get('min', 0):.2f}   Max: {info.get('max', 0):.2f}",
                ln=True)
        for flag in build_flags(info):
            clean = flag.replace("⚠", "[!]").replace("✓", "[OK]")
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(130, 100, 0)
            if "[OK]" in clean:
                pdf.set_text_color(0, 100, 60)
            pdf.cell(0, 5, clean, ln=True)
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Helvetica", "", 9)
        pdf.ln(2)

    return bytes(pdf.output())


# ── UI ─────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="top-bar">
  <div class="brand">EDA<span>·</span>Report</div>
  <div class="badge">v1.0 · portfolio project</div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Upload your dataset")
st.markdown('<div class="upload-hint">Supports CSV and Excel files up to 200 MB</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["csv", "xlsx", "xls"], label_visibility="collapsed")

if uploaded is None:
    # Landing state
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **What this tool generates**
        - Dataset shape & data types
        - Missing value analysis
        - Distribution plots per column
        - Correlation heatmap
        - Outlier detection (IQR)
        - Downloadable PDF report
        """)
    with col2:
        st.markdown("""
        **Best used for**
        - First look at a new dataset
        - Pre-modelling sanity checks
        - Sharing findings with stakeholders
        - Spotting data quality issues fast
        """)
    with col3:
        st.markdown("""
        **Built with**
        - Python + Pandas
        - Streamlit
        - Matplotlib / Seaborn
        - fpdf2
        """)
    st.stop()

# ── Load data ──────────────────────────────────────────────────────────────────
try:
    df = load_data(uploaded)
except Exception as e:
    st.error(f"Could not load file: {e}")
    st.stop()

insights = column_insights(df)
num_cols_count = df.select_dtypes(include="number").shape[1]
total_missing = df.isnull().sum().sum()
dup_rows = df.duplicated().sum()
complete_pct = (1 - df.isnull().mean().mean()) * 100

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-label">Rows</div>
    <div class="metric-value">{df.shape[0]:,}</div>
    <div class="metric-sub">{uploaded.name}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Columns</div>
    <div class="metric-value">{df.shape[1]}</div>
    <div class="metric-sub">{num_cols_count} numeric</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Completeness</div>
    <div class="metric-value">{complete_pct:.0f}%</div>
    <div class="metric-sub">{total_missing:,} missing values</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Duplicates</div>
    <div class="metric-value">{dup_rows}</div>
    <div class="metric-sub">duplicate rows</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Data preview ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Preview</div>', unsafe_allow_html=True)
st.dataframe(df.head(10), use_container_width=True)

# ── Missing values ─────────────────────────────────────────────────────────────
fig_miss = plot_missing(df)
if fig_miss:
    st.markdown('<div class="section-header">Missing Values</div>', unsafe_allow_html=True)
    st.pyplot(fig_miss, use_container_width=False)
    plt.close(fig_miss)

# ── Correlation heatmap ────────────────────────────────────────────────────────
if num_cols_count >= 2:
    st.markdown('<div class="section-header">Correlation Matrix</div>', unsafe_allow_html=True)
    fig_corr = plot_correlation(df)
    if fig_corr:
        st.pyplot(fig_corr, use_container_width=False)
        plt.close(fig_corr)

# ── Column-by-column analysis ──────────────────────────────────────────────────
st.markdown('<div class="section-header">Column Analysis</div>', unsafe_allow_html=True)

for info in insights:
    flags = build_flags(info)
    has_warn = any("⚠" in f for f in flags)

    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        stats_html = ""
        if info["dtype"] == "numeric":
            stats_html = f"""
            <div class="col-stats">
              <span class="stat-item"><strong>{info.get('mean', 0):.2f}</strong> mean</span>
              <span class="stat-item"><strong>{info.get('std', 0):.2f}</strong> std</span>
              <span class="stat-item"><strong>{info.get('min', 0):.2f}</strong> min</span>
              <span class="stat-item"><strong>{info.get('max', 0):.2f}</strong> max</span>
              <span class="stat-item"><strong>{info.get('outliers', 0)}</strong> outliers</span>
            </div>"""
        else:
            stats_html = f"""
            <div class="col-stats">
              <span class="stat-item"><strong>{info['unique']}</strong> unique values</span>
              <span class="stat-item"><strong>{info['null_pct']:.1f}%</strong> missing</span>
            </div>"""

        flags_html = "".join(
            f'<span class="flag-{"warn" if "⚠" in f else "ok"}">{f}</span><br>'
            for f in flags
        )

        st.markdown(f"""
        <div class="col-card">
          <span class="col-name">{info['name']}</span>
          <span class="col-dtype">{info['dtype']}</span>
          <div style="font-size:0.75rem;color:#aaa;margin-top:4px">{info['null_pct']:.1f}% missing · {info['total']:,} rows</div>
          {stats_html}
          <div style="margin-top:8px">{flags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        s = df[info["name"]]
        if info["dtype"] == "numeric":
            fig = plot_distribution(s, info["name"])
        else:
            fig = plot_value_counts(s, info["name"])
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

# ── PDF Export ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)

with st.spinner("Building PDF report…"):
    pdf_bytes = generate_pdf(df, insights, uploaded.name)

report_name = uploaded.name.rsplit(".", 1)[0] + "_eda_report.pdf"
st.download_button(
    label="⬇ Download PDF Report",
    data=pdf_bytes,
    file_name=report_name,
    mime="application/pdf",
    use_container_width=False,
)

st.caption("EDA Report Generator · Built with Python + Streamlit · Portfolio project")
