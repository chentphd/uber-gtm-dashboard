import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Uber GTM Dashboard",
    layout="wide"
)

# ---------------------------
# UBER STYLE
# ---------------------------
st.markdown("""
<style>
.stMetric {
    background-color: #F6F6F6;
    padding: 12px;
    border-radius: 10px;
}
h1, h2, h3 {
    color: black;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# TITLE
# ---------------------------
st.title("🚗 Uber GTM Sales Performance Dashboard")

# ---------------------------
# LOAD DATA (EXCEL WITH 2 TABS)
# ---------------------------
@st.cache_data
def load_data():
    file = "Sales Data Set (1) (3) (3).xlsx"
    
    leaderboard = pd.read_excel(file, sheet_name="Leaderboard")
    attainment = pd.read_excel(file, sheet_name="Attainment Query Data")
    
    return leaderboard, attainment

leaderboard_df, df = load_data()

# ---------------------------
# STANDARDIZE COLUMN NAMES (IMPORTANT)
# ---------------------------
df.columns = df.columns.str.lower().str.replace(" ", "_")

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("Filters")

region_col = "mega_region" if "mega_region" in df.columns else df.columns[0]
product_col = "product_type" if "product_type" in df.columns else df.columns[1]

regions = st.sidebar.multiselect(
    "Mega Region",
    options=df[region_col].dropna().unique(),
    default=df[region_col].dropna().unique()
)

products = st.sidebar.multiselect(
    "Product Type",
    options=df[product_col].dropna().unique(),
    default=df[product_col].dropna().unique()
)

filtered_df = df[
    (df[region_col].isin(regions)) &
    (df[product_col].isin(products))
]

# ---------------------------
# KPI CALCULATIONS
# ---------------------------
gb_col = "gross_bookings"
quota_col = "quota"

# fallback if column names differ
if gb_col not in df.columns:
    gb_col = df.columns[2]

if quota_col not in df.columns:
    quota_col = df.columns[3]

total_gb = filtered_df[gb_col].sum()
total_quota = filtered_df[quota_col].sum()
attainment = total_gb / total_quota if total_quota != 0 else 0

# recurring %
recurring_pct = 0
if "product_type" in df.columns:
    recurring_pct = (
        filtered_df[filtered_df["product_type"].str.lower().str.contains("recurring")][gb_col].sum()
        / total_gb
    ) * 100 if total_gb > 0 else 0

# ---------------------------
# KPI DISPLAY
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Gross Bookings", f"${total_gb:,.0f}")
col2.metric("Quota Attainment", f"{attainment*100:.1f}%")
col3.metric("Recurring Revenue %", f"{recurring_pct:.1f}%")

# ---------------------------
# DISTRIBUTION
# ---------------------------
st.subheader("AE Performance Distribution")

filtered_df["attainment_ratio"] = filtered_df[gb_col] / filtered_df[quota_col]

fig = px.histogram(
    filtered_df,
    x="attainment_ratio",
    nbins=20,
    title="Quota Attainment Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# REGION PERFORMANCE
# ---------------------------
st.subheader("Performance by Region")

region_perf = filtered_df.groupby(region_col).agg({
    gb_col: "sum",
    quota_col: "sum"
}).reset_index()

region_perf["attainment"] = region_perf[gb_col] / region_perf[quota_col]

fig2 = px.bar(
    region_perf,
    x=region_col,
    y="attainment",
    title="Quota Attainment by Region"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# PRODUCT MIX
# ---------------------------
if "product_type" in df.columns:
    st.subheader("Product Mix")

    product_mix = filtered_df.groupby("product_type")[gb_col].sum().reset_index()

    fig3 = px.pie(
        product_mix,
        names="product_type",
        values=gb_col,
        title="Recurring vs Non-Recurring"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# LEADERBOARD (BONUS USING 2ND TAB)
# ---------------------------
st.subheader("Top Performers")

if not leaderboard_df.empty:
    st.dataframe(leaderboard_df.head(10))

# ---------------------------
# KEY INSIGHT (CRITICAL FOR INTERVIEW)
# ---------------------------
st.subheader("Key Insight")

st.info("""
Performance is skewed across regions, with a small percentage of AEs driving a disproportionate share of Gross Bookings. 
Additionally, reliance on non-recurring revenue suggests potential misalignment in incentive structures toward short-term gains.
""")