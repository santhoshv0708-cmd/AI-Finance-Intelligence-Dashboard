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

.main{
    background-color:#f5f7fa;
}

[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#1e3c72,#2a5298);
}

[data-testid="stSidebar"] *{
    color:white;
}

.dashboard-title{
    text-align:center;
    color:#1e3c72;
    font-size:42px;
    font-weight:bold;
}

.kpi-card{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.15);
    text-align:center;
    margin-bottom:10px;
}

.footer{
    text-align:center;
    color:gray;
    padding:10px;
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
except:
    pass

st.markdown("""
<h1 class='dashboard-title'>
💰 Company Expense & Budget Variance Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown("""
### Monitor budgets, identify overspending and uncover financial insights.
""")

st.info(
"""
Welcome to the Expense & Budget Variance Dashboard.

Use the filters in the sidebar to analyze department spending,
budget utilization and overspending trends.
"""
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv(
        "cleaned_budget_data.csv"
    )

df = load_data()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("🔍 Filters")

department = st.sidebar.multiselect(
    "Department",
    options=df["Department"].unique(),
    default=df["Department"].unique()
)

category = st.sidebar.multiselect(
    "Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_df = df[
    (df["Department"].isin(department))
    &
    (df["Category"].isin(category))
]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_budget = filtered_df["Budget Amount"].sum()

total_actual = filtered_df["Actual Amount"].sum()

total_variance = filtered_df["Variance"].sum()

overspending_percent = (
    filtered_df[filtered_df["Variance"] > 0].shape[0]
    /
    filtered_df.shape[0]
) * 100

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='kpi-card'>
    <h4>Total Budget</h4>
    <h2>${total_budget:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card'>
    <h4>Total Actual</h4>
    <h2>${total_actual:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card'>
    <h4>Total Variance</h4>
    <h2>${total_variance:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card'>
    <h4>Overspending %</h4>
    <h2>{overspending_percent:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

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
        filtered_df.groupby("Department")
        [["Budget Amount", "Actual Amount"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        dept_summary,
        x="Department",
        y=["Budget Amount", "Actual Amount"],
        barmode="group",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📂 Budget vs Actual by Category")

    cat_summary = (
        filtered_df.groupby("Category")
        [["Budget Amount", "Actual Amount"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        cat_summary,
        x="Category",
        y=["Budget Amount", "Actual Amount"],
        barmode="group",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# ANALYSIS TAB
# --------------------------------------------------

with tab2:

    st.subheader("⚠ Top 10 Overspending Areas")

    top_over = (
        filtered_df.groupby(
            ["Department", "Category"]
        )["Variance"]
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
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    if "Month" in filtered_df.columns:

        st.subheader("📈 Monthly Trend")

        monthly = (
            filtered_df.groupby("Month")
            [["Budget Amount", "Actual Amount"]]
            .sum()
            .reset_index()
        )

        fig = px.line(
            monthly,
            x="Month",
            y=["Budget Amount", "Actual Amount"],
            markers=True,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    if "Status" in filtered_df.columns:

        st.subheader("🥧 Budget Status Distribution")

        status_count = (
            filtered_df["Status"]
            .value_counts()
            .reset_index()
        )

        status_count.columns = [
            "Status",
            "Count"
        ]

        fig = px.pie(
            status_count,
            names="Status",
            values="Count"
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
        filtered_df.groupby("Department")
        ["Variance"]
        .sum()
        .idxmax()
    )

    highest_over_cat = (
        filtered_df.groupby("Category")
        ["Variance"]
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

    csv = filtered_df.to_csv(
        index=False
    )

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
""", unsafe_allow_html=True)

