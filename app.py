import base64
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
from PIL import Image

from modules.data_loader import load_dataset
from modules.data_explorer import get_dataset_overview, get_column_information
from modules.statistics import get_numeric_statistics, get_categorical_statistics
from modules.visualizations import suggest_visualizations, generate_visualizations
from modules.insights import generate_all_insights


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).parent
ASSETS = PROJECT_ROOT / "assets"

# --- Identité de marque (modifiable ici) ---
BRAND_FIRST = "Data"
BRAND_SECOND = "Detective"
BRAND_TAGLINE = "Intelligent data auditing"

st.set_page_config(
    page_title=f"{BRAND_FIRST} {BRAND_SECOND}",
    page_icon=Image.open(ASSETS / "logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)



@st.cache_data
def logo_uri(name: str) -> str:
    data = base64.b64encode((ASSETS / name).read_bytes()).decode()
    return f"data:image/svg+xml;base64,{data}"


# Palette cohérente pour tous les graphiques Plotly
PLOTLY_TEMPLATE = "plotly_dark"
COLORWAY = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#64748B"]
pio.templates.default = PLOTLY_TEMPLATE
px.defaults.template = PLOTLY_TEMPLATE
px.defaults.color_discrete_sequence = COLORWAY


def load_css():
    css_name = "style_dark.css"
    css = (PROJECT_ROOT / "assets" / css_name).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css()


# --------------------------------------------------
# COMPOSANTS UI RÉUTILISABLES
# --------------------------------------------------

def page_header(title: str, subtitle: str):
    st.markdown(
        f'<div class="dd-page-header"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def require_dataset():
    """Retourne le DataFrame chargé, ou affiche un état vide propre et arrête la page."""
    if "dataset" not in st.session_state:
        st.info("No dataset loaded yet. Upload a CSV or Excel file from the **Home** page to get started.")
        st.stop()
    return st.session_state["dataset"]


def feature_card(icon: str, title: str, text: str):
    st.markdown(
        f'<div class="dd-card"><div class="dd-card-icon">{icon}</div><h4>{title}</h4><p>{text}</p></div>',
        unsafe_allow_html=True,
    )


def style_figure(fig):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        font=dict(family="Inter, sans-serif", size=13),
        margin=dict(l=24, r=24, t=48, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLORWAY,
    )
    return fig


# Mise en cache : évite de recalculer à chaque interaction
@st.cache_data(show_spinner="Generating charts…")
def cached_visualizations(df):
    return generate_visualizations(df)


@st.cache_data(show_spinner="Analyzing your data…")
def cached_insights(df):
    return generate_all_insights(df)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        f"""
        <div class="dd-brand">
            <img class="dd-logo-img" src="{logo_uri('logo.svg')}" alt="logo">
            <div>
                <div class="dd-brand-name">{BRAND_FIRST} <b>{BRAND_SECOND}</b></div>
                <div class="dd-brand-tag">{BRAND_TAGLINE}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown('<div class="dd-nav-label">Navigation</div>', unsafe_allow_html=True)

    selected_page = st.radio(
        "Go to",
        ["Home", "Overview", "Data Explorer", "Visualizations", "Data Insights", "Export"],
        label_visibility="collapsed",
    )

    st.divider()

    # Carte d'état du dataset
    if "dataset" in st.session_state:
        d = st.session_state["dataset"]
        st.markdown(
            f'<div class="dd-status"><span class="dd-dot"></span>Dataset loaded'
            f'<b>{st.session_state["filename"]}</b>{d.shape[0]:,} rows · {d.shape[1]:,} columns</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="dd-status"><span class="dd-dot off"></span>No dataset loaded</div>',
            unsafe_allow_html=True,
        )

    #st.caption("Appearance: ⋮ menu → Settings → Theme (light / dark)")
    st.caption("Halla GUETARNI")


# --------------------------------------------------
# HOME
# --------------------------------------------------

if selected_page == "Home":

    st.markdown(
        f"""
        <div class="dd-hero">
            <div class="dd-hero-top">
                <img class="dd-hero-logo" src="{logo_uri('logo_inverse.svg')}" alt="logo">
                <div class="dd-hero-brand">{BRAND_FIRST} <b>{BRAND_SECOND}</b></div>
            </div>
            <div class="dd-kicker">{BRAND_TAGLINE}</div>
            <h1>Discover · Analyze · Visualize</h1>
            <p>Upload a tabular dataset and get an instant quality audit, statistical profile,
            interactive charts and actionable insights — in a few clicks.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        feature_card("01", "Data quality audit", "Missing values, duplicates and outliers detected automatically.")
    with c2:
        feature_card("02", "Interactive exploration", "Search, filter and select columns, then chart patterns instantly.")
    with c3:
        feature_card("03", "Export & report", "Download the dataset (CSV / Excel) and a structured analysis report.")

    st.write("")
    st.subheader("Upload your dataset")
    st.caption("Supported formats: CSV, XLSX, XLS · up to 200 MB")

    uploaded_file = st.file_uploader(
        "Select your dataset",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        try:
            upload_dir = PROJECT_ROOT / "data"
            upload_dir.mkdir(exist_ok=True)
            upload_path = upload_dir / Path(uploaded_file.name).name   # évite les chemins malveillants

            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df = load_dataset(upload_path)
            st.session_state["dataset"] = df
            st.session_state["filename"] = uploaded_file.name

            st.success(
                f"**{uploaded_file.name}** loaded — {df.shape[0]:,} rows and {df.shape[1]:,} columns. "
                "Use the navigation menu to explore it."
            )

            st.subheader("Data preview")
            st.dataframe(df.head(5), use_container_width=True)

        except Exception as error:
            st.error(f"Error loading dataset: {error}")


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

elif selected_page == "Overview":

    page_header("Dataset Overview", "A quick summary of your dataset's structure and quality.")
    df = require_dataset()
    overview = get_dataset_overview(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows", f"{overview['rows']:,}")
    c2.metric("Total Columns", f"{overview['columns']:,}")
    c3.metric("Missing Values", f"{overview['missing_values']:,}")
    c4.metric("Duplicate Rows", f"{overview['duplicate_rows']:,}")

    # Score de complétude
    total_cells = max(overview["rows"] * overview["columns"], 1)
    completeness = 1 - overview["missing_values"] / total_cells
    st.write("")
    st.markdown(f"**Data completeness: {completeness:.1%}**")
    st.progress(float(completeness))
    st.caption(
        f"File: {st.session_state['filename']} · Memory usage: {overview['memory_usage'] / 1024:.2f} KB"
    )

    tab_cols, tab_num, tab_cat = st.tabs(["Columns", "Numerical statistics", "Categorical statistics"])

    with tab_cols:
        st.dataframe(get_column_information(df), use_container_width=True, hide_index=True)

    with tab_num:
        numeric_stats = get_numeric_statistics(df)
        if not numeric_stats.empty:
            st.dataframe(numeric_stats, use_container_width=True)
        else:
            st.info("No numerical columns found.")

    with tab_cat:
        categorical_stats = get_categorical_statistics(df)
        if not categorical_stats.empty:
            st.dataframe(categorical_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No categorical columns found.")


# --------------------------------------------------
# DATA EXPLORER
# --------------------------------------------------

elif selected_page == "Data Explorer":

    page_header("Data Explorer", "Search, filter and select the data you want to inspect.")
    df = require_dataset()
    filtered_df = df.copy()

    with st.container(border=True):
        st.markdown("**Filters**")

        search_query = st.text_input(
            "Search across all columns", placeholder="Type a value to search…"
        )
        if search_query:
            mask = filtered_df.astype(str).apply(
                lambda col: col.str.contains(search_query, case=False, na=False, regex=False)
            ).any(axis=1)
            filtered_df = filtered_df[mask]

        categorical_columns = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

        if categorical_columns:
            f1, f2 = st.columns([1, 2])
            with f1:
                filter_column = st.selectbox("Filter by column", options=categorical_columns)
            with f2:
                available_values = sorted(df[filter_column].dropna().unique().tolist(), key=str)
                selected_values = st.multiselect("Values", options=available_values)
            if selected_values:
                filtered_df = filtered_df[filtered_df[filter_column].isin(selected_values)]

        with st.expander("Choose columns to display"):
            selected_columns = st.multiselect(
                "Columns", options=df.columns.tolist(), default=df.columns.tolist(),
                label_visibility="collapsed",
            )

    if not selected_columns:
        st.warning("Please select at least one column.")
    else:
        display_df = filtered_df[selected_columns]
        m1, m2, m3 = st.columns(3)
        m1.metric("Matching rows", f"{len(display_df):,}")
        m2.metric("Of total", f"{len(display_df) / max(len(df), 1):.0%}")
        m3.metric("Columns shown", f"{len(selected_columns):,}")

        st.write("")
        st.dataframe(display_df, use_container_width=True, hide_index=True)


# --------------------------------------------------
# VISUALIZATIONS
# --------------------------------------------------

elif selected_page == "Visualizations":

    page_header("Data Visualizations", "Discover patterns and relationships through interactive charts.")
    df = require_dataset()

    visualizations = cached_visualizations(df)

    tab_charts, tab_reco = st.tabs(["Charts", "Recommendations"])

    with tab_charts:
        if visualizations:
            st.caption(f"{len(visualizations)} interactive charts generated.")
            for index, item in enumerate(visualizations, start=1):
                st.markdown(f"**{index}. {item['description']}**")
                st.plotly_chart(style_figure(item["figure"]), use_container_width=True, key=f"chart_{index}")
                st.write("")
        else:
            st.info("No visualizations could be generated for this dataset.")

    with tab_reco:
        suggestions = suggest_visualizations(df)
        for index, s in enumerate(suggestions, start=1):
            st.markdown(f"**{index}. {s['type']}**")
            st.caption(s["description"])


# --------------------------------------------------
# DATA INSIGHTS
# --------------------------------------------------

elif selected_page == "Data Insights":

    page_header("Data Insights", "Automatically generated findings about your dataset's quality and structure.")
    df = require_dataset()

    insights = cached_insights(df)

    if not insights:
        st.success("No significant issues or patterns detected.")
    else:
        categories = {}
        for insight in insights:
            categories.setdefault(insight["category"], []).append(insight["message"])

        # Résumé en haut de page
        issues = sum(1 for m in sum(categories.values(), []) if not re.match(r"^\s*no\b", m, re.I))
        s1, s2 = st.columns(2)
        s1.metric("Categories analyzed", len(categories))
        s2.metric("Findings to review", issues)
        st.write("")

        for category, messages in categories.items():
            with st.expander(category, expanded=True):
                for message in messages:
                    # "No outliers detected…" -> succès ; le reste -> avertissement
                    if re.match(r"^\s*no\b", message, re.I):
                        st.success(message)
                    else:
                        st.warning(message)


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

elif selected_page == "Export":

    page_header("Export", "Download your dataset and a structured analysis report.")
    df = require_dataset()
    filename = st.session_state["filename"]

    csv_data = df.to_csv(index=False).encode("utf-8")

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dataset")

    overview = get_dataset_overview(df)
    numeric_stats = get_numeric_statistics(df)
    categorical_stats = get_categorical_statistics(df)
    insights = cached_insights(df)

    report = [
        "DATA DETECTIVE - ANALYSIS REPORT",
        "=" * 45,
        f"\nSource file: {filename}",
        f"Generated on: {datetime.now():%Y-%m-%d %H:%M}",
        "\n1. DATASET OVERVIEW", "-" * 30,
        f"Total rows: {overview['rows']}",
        f"Total columns: {overview['columns']}",
        f"Missing values: {overview['missing_values']}",
        f"Duplicate rows: {overview['duplicate_rows']}",
        f"Memory usage: {overview['memory_usage'] / 1024:.2f} KB",
        "\n2. NUMERICAL STATISTICS", "-" * 30,
        numeric_stats.to_string() if not numeric_stats.empty else "No numerical columns found.",
        "\n3. CATEGORICAL STATISTICS", "-" * 30,
        categorical_stats.to_string(index=False) if not categorical_stats.empty else "No categorical columns found.",
        "\n4. DATA INSIGHTS", "-" * 30,
        *[f"[{i['category']}] {i['message']}" for i in insights],
        "\n" + "=" * 45,
        "Generated by Data Detective",
    ]
    report_content = "\n".join(report)

    c1, c2, c3 = st.columns(3)
    with c1:
        feature_card("CSV", "Dataset · CSV", f"{len(df):,} rows, universal format.")
        st.write("")
        st.download_button("Download CSV", csv_data, "data_detective_export.csv", "text/csv", use_container_width=True)
    with c2:
        feature_card("XLS", "Dataset · Excel", "Single-sheet .xlsx workbook.")
        st.write("")
        st.download_button(
            "Download Excel", excel_buffer.getvalue(), "data_detective_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True,
        )
    with c3:
        feature_card("TXT", "Analysis report", "Overview, statistics and insights.")
        st.write("")
        st.download_button(
            "Download Analysis Report", report_content.encode("utf-8"),
            "data_detective_report.txt", "text/plain", use_container_width=True,
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(f'<div class="dd-footer">{BRAND_FIRST} {BRAND_SECOND} · Halla GUETARNI</div>', unsafe_allow_html=True)

