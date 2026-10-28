
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Expense & Budget Dashboard",
    page_icon="💰",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3c72, #2a5298);
}

[data-testid="stSidebar"] * {
    color: white;
}

.dashboard-title {
    text-align: center;
    color: #1e3c72;
    font-size: 42px;
    font-weight: bold;
}

.kpi-card,
div.kpi-card,
.stMarkdown .kpi-card,
[data-testid="stMarkdownContainer"] .kpi-card {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #111827 !important;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
    text-align: center;
    margin-bottom: 10px;
    min-height: 125px;
    box-sizing: border-box;
}

.kpi-card *,
.stMarkdown .kpi-card *,
[data-testid="stMarkdownContainer"] .kpi-card * {
    color: #111827 !important;
    opacity: 1 !important;
}

.kpi-card h4,
.stMarkdown .kpi-card h4,
[data-testid="stMarkdownContainer"] .kpi-card h4 {
    color: #1e3c72 !important;
    margin: 0 0 12px 0 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    text-align: center !important;
}

.kpi-card h2,
.stMarkdown .kpi-card h2,
[data-testid="stMarkdownContainer"] .kpi-card h2 {
    color: #111827 !important;
    margin: 0 !important;
    font-size: clamp(20px, 2vw, 28px) !important;
    font-weight: 700 !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    text-align: center !important;
    line-height: 1.3 !important;
}

.footer {
    text-align: center;
    color: gray;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

try:
    st.image(
        "assets/finance_banner.jpg",
        use_container_width=True
    )
except Exception:
    pass

st.markdown("""
<h1 class="dashboard-title">
💰 Company Expense & Budget Variance Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown("""
### Monitor budgets, identify overspending and uncover financial insights.
""")

st.info("""
Welcome to the Expense & Budget Variance Dashboard.

Use the filters in the sidebar to analyze department spending,
budget utilization and overspending trends.
""")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("cleaned_budget_data.csv")


df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔍 Filters")

department = st.sidebar.multiselect(
    "Department",
    options=sorted(df["Department"].dropna().unique()),
    default=sorted(df["Department"].dropna().unique())
)

category = st.sidebar.multiselect(
    "Category",
    options=sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique())
)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_df = df[
    (df["Department"].isin(department))
    & (df["Category"].isin(category))
]

if filtered_df.empty:
    st.warning(
        "No data matches the selected filters. "
        "Please select at least one department and category."
    )
    st.stop()

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_budget = filtered_df["Budget Amount"].sum()
total_actual = filtered_df["Actual Amount"].sum()
total_variance = filtered_df["Variance"].sum()

overspending_percent = (
    filtered_df[filtered_df["Variance"] > 0].shape[0]
    / len(filtered_df)
) * 100

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)


def render_kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-card"
             style="background-color:#ffffff !important;
                    color:#111827 !important;">
            <h4 style="color:#1e3c72 !important;">
                {title}
            </h4>
            <h2 style="color:#111827 !important;">
                {value}
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )


with col1:
    render_kpi_card("Total Budget", f"${total_budget:,.2f}")

with col2:
    render_kpi_card("Total Actual", f"${total_actual:,.2f}")

with col3:
    render_kpi_card("Total Variance", f"${total_variance:,.2f}")

with col4:
    render_kpi_card("Overspending %", f"{overspending_percent:.2f}%")

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    ["📊 Overview", "📈 Analysis", "💡 Insights"]
)

# --------------------------------------------------
# OVERVIEW TAB
# --------------------------------------------------

with tab1:
    st.subheader("🏢 Budget vs Actual by Department")

    dept_summary = (
        filtered_df.groupby("Department")[
            ["Budget Amount", "Actual Amount"]
        ]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        dept_summary,
        x="Department",
        y=["Budget Amount", "Actual Amount"],
        barmode="group",
        template="plotly_white",
        title="Budget vs Actual by Department"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📂 Budget vs Actual by Category")

    cat_summary = (
        filtered_df.groupby("Category")[
            ["Budget Amount", "Actual Amount"]
        ]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        cat_summary,
        x="Category",
        y=["Budget Amount", "Actual Amount"],
        barmode="group",
        template="plotly_white",
        title="Budget vs Actual by Category"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# ANALYSIS TAB
# --------------------------------------------------

with tab2:
    st.subheader("⚠ Top 10 Overspending Areas")

    top_over = (
        filtered_df.groupby(["Department", "Category"])["Variance"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_over,
        x="Variance",
        y="Department",
        color="Category",
        orientation="h",
        template="plotly_white",
        title="Top Overspending Areas"
    )

    st.plotly_chart(fig, use_container_width=True)

    if "Month" in filtered_df.columns:
        st.subheader("📈 Monthly Trend")

        monthly = (
            filtered_df.groupby("Month")[
                ["Budget Amount", "Actual Amount"]
            ]
            .sum()
            .reset_index()
        )

        fig = px.line(
            monthly,
            x="Month",
            y=["Budget Amount", "Actual Amount"],
            markers=True,
            template="plotly_white",
            title="Monthly Budget vs Actual"
        )

        st.plotly_chart(fig, use_container_width=True)

    if "Status" in filtered_df.columns:
        st.subheader("🥧 Budget Status Distribution")

        status_count = (
            filtered_df["Status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Count")
        )

        fig = px.pie(
            status_count,
            names="Status",
            values="Count",
            title="Budget Status Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# INSIGHTS TAB
# --------------------------------------------------

with tab3:
    st.subheader("🏆 Department Ranking")

    dept_rank = (
        filtered_df.groupby("Department")["Variance"]
        .sum()
        .reset_index()
        .sort_values("Variance")
    )

    st.dataframe(
        dept_rank,
        use_container_width=True
    )

    highest_over_dept = (
        filtered_df.groupby("Department")["Variance"]
        .sum()
        .idxmax()
    )

    highest_over_cat = (
        filtered_df.groupby("Category")["Variance"]
        .sum()
        .idxmax()
    )

    st.success(
        f"Highest Overspending Department: {highest_over_dept}"
    )

    st.warning(
        f"Highest Overspending Category: {highest_over_cat}"
    )

    st.subheader("⬇ Download Report")

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="Download Filtered Report",
        data=csv,
        file_name="expense_report.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown("""
<div class="footer">
    Company Expense & Budget Variance Dashboard
</div>
""", unsafe_allow_html=True)
