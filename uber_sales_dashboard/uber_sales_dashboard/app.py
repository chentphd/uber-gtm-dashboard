import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uber for Business · Sales Performance Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Uber brand palette ────────────────────────────────────────────────────────
UBER_BLACK   = "#000000"
UBER_WHITE   = "#FFFFFF"
UBER_GREEN   = "#06C167"
UBER_GREY    = "#F6F6F6"
UBER_MID     = "#EEEEEE"
UBER_TEXT    = "#1A1A1A"
UBER_ACCENT  = "#276EF1"   # Uber blue for secondary charts
REGION_COLORS = {
    "US&Can":  "#06C167",
    "Europe":  "#276EF1",
    "LatAm":   "#FF6B35",
    "APACx":   "#9B59B6",
    "India":   "#F1C40F",
    "MEA":     "#E74C3C",
}

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #FFFFFF; }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: #000000 !important;
      color: white !important;
  }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stMultiSelect > div > div {
      background: #1a1a1a !important;
      border: 1px solid #333 !important;
  }
  [data-testid="stSidebar"] label { color: #aaa !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

  /* Top header bar */
  .uber-header {
      background: #000000;
      padding: 20px 32px;
      margin: -1rem -1rem 1.5rem -1rem;
      display: flex;
      align-items: center;
      gap: 16px;
  }
  .uber-logo { font-size: 2rem; font-weight: 700; color: white; letter-spacing: -1px; }
  .uber-subtitle { font-size: 0.95rem; color: #aaa; margin-top: 2px; }
  .uber-badge {
      background: #06C167;
      color: black;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 20px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
  }

  /* KPI cards */
  .kpi-card {
      background: #FFFFFF;
      border: 1px solid #E5E5E5;
      border-radius: 12px;
      padding: 20px 24px;
      transition: box-shadow 0.2s;
  }
  .kpi-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
  .kpi-label { font-size: 0.72rem; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
  .kpi-value { font-size: 2rem; font-weight: 700; color: #000; line-height: 1.1; }
  .kpi-delta-pos { font-size: 0.82rem; color: #06C167; font-weight: 600; margin-top: 4px; }
  .kpi-delta-neg { font-size: 0.82rem; color: #E74C3C; font-weight: 600; margin-top: 4px; }
  .kpi-sub { font-size: 0.78rem; color: #999; margin-top: 2px; }

  /* Section headers */
  .section-header {
      font-size: 1.25rem;
      font-weight: 700;
      color: #000;
      border-left: 4px solid #06C167;
      padding-left: 12px;
      margin: 2rem 0 1rem 0;
  }
  .section-sub {
      font-size: 0.85rem;
      color: #666;
      margin-top: -0.75rem;
      margin-bottom: 1rem;
      padding-left: 16px;
  }

  /* Insight callout */
  .insight-box {
      background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
      border-left: 4px solid #06C167;
      border-radius: 10px;
      padding: 16px 20px;
      margin: 12px 0;
  }
  .insight-box .insight-title { color: #06C167; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
  .insight-box .insight-text { color: white; font-size: 0.9rem; margin-top: 4px; }

  /* Warning insight */
  .warning-box {
      background: #FFF8F0;
      border-left: 4px solid #FF6B35;
      border-radius: 10px;
      padding: 16px 20px;
      margin: 12px 0;
  }
  .warning-box .insight-title { color: #FF6B35; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }
  .warning-box .insight-text { color: #333; font-size: 0.9rem; margin-top: 4px; }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] { background: #F6F6F6; border-radius: 8px; padding: 4px; }
  .stTabs [data-baseweb="tab"] { border-radius: 6px; font-weight: 500; }
  .stTabs [aria-selected="true"] { background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }

  /* Plotly chart border */
  .stPlotlyChart { border: 1px solid #eee; border-radius: 10px; overflow: hidden; }

  /* Footer */
  .dashboard-footer {
      border-top: 1px solid #eee;
      margin-top: 3rem;
      padding-top: 1rem;
      font-size: 0.75rem;
      color: #bbb;
      text-align: center;
  }
</style>
""", unsafe_allow_html=True)


# ── Data loading & cleaning ───────────────────────────────────────────────────
@st.cache_data
def load_and_clean():
    xl = pd.ExcelFile("sales_data.xlsx")

    # ── Leaderboard ──────────────────────────────────────────────────────────
    lb = pd.read_excel(xl, sheet_name="Leaderboard", header=0)
    lb = lb.drop(columns=["Unnamed: 0"], errors="ignore")
    lb = lb.dropna(subset=["Account Executive Name"])
    lb.columns = lb.columns.str.strip()

    # Normalise ramp status capitalisation
    lb["Tenure based ramp status"] = lb["Tenure based ramp status"].str.strip().str.title()

    # Normalise status
    lb["Status as of 12/31"] = lb["Status as of 12/31"].str.strip().str.lower()

    # Numeric quotas → fill NA with 0
    for col in ["H2'21 NB Quota", "H2'21 CO Quota", "H2 Total Quota"]:
        lb[col] = pd.to_numeric(lb[col], errors="coerce").fillna(0)

    # Rename for convenience
    lb = lb.rename(columns={
        "Account Executive Name": "AE",
        "Mega Region": "Mega_Region",
        "H2'21 NB Quota": "NB_Quota",
        "H2'21 CO Quota": "CO_Quota",
        "H2 Total Quota": "Total_Quota",
        "Tenure based ramp status": "Ramp_Status",
        "Status as of 12/31": "AE_Status",
    })

    # ── Attainment Query Data ────────────────────────────────────────────────
    aq = pd.read_excel(xl, sheet_name="Attainment Query Data", header=0)
    aq = aq.dropna(subset=["Opportunity owner (Account Executive)"])
    aq.columns = aq.columns.str.strip()

    aq = aq.rename(columns={
        "Opportunity owner (Account Executive)": "AE",
        "Mega region": "Mega_Region",
        "NB GB (USD)": "NB_GB",
        "CO GB (USD)": "CO_GB",
        "Total $GB (USD)": "Total_GB",
        "Customer Use Case": "Use_Case",
    })

    # Parse dates
    aq["Close Date"] = pd.to_datetime(aq["Close Date"], errors="coerce")
    aq["Month"] = aq["Close Date"].dt.to_period("M").astype(str)
    aq["Quarter"] = aq["Close Date"].dt.to_period("Q").astype(str)

    # Fill numeric NAs
    for col in ["NB_GB", "CO_GB", "Total_GB"]:
        aq[col] = pd.to_numeric(aq[col], errors="coerce").fillna(0)

    # Product normalise
    aq["Product"] = aq["Product"].str.strip().str.lower()

    # Classify Recurring vs Non-Recurring
    recurring_products = {"travel", "eats", "central"}
    aq["Product_Type"] = aq["Product"].apply(
        lambda p: "Recurring" if p in recurring_products else "Non-Recurring"
    )

    # Product display labels
    product_labels = {
        "travel": "Travel",
        "eats": "Eats",
        "central": "Central",
        "gift card": "Gift Card",
        "eats vouchers": "Eats Vouchers",
        "vouchers": "Vouchers",
    }
    aq["Product_Label"] = aq["Product"].map(product_labels).fillna(aq["Product"].str.title())

    # ── Merge to compute attainment ──────────────────────────────────────────
    # Aggregate actual GB per AE from the transaction data
    actuals = aq.groupby("AE").agg(
        NB_GB_Actual=("NB_GB", "sum"),
        CO_GB_Actual=("CO_GB", "sum"),
        Deals=("Unique Dashboard ID", "nunique"),
    ).reset_index()
    actuals["Total_GB_Actual"] = actuals["NB_GB_Actual"] + actuals["CO_GB_Actual"]

    merged = lb.merge(actuals, on="AE", how="left")
    merged[["NB_GB_Actual", "CO_GB_Actual", "Total_GB_Actual", "Deals"]] = (
        merged[["NB_GB_Actual", "CO_GB_Actual", "Total_GB_Actual", "Deals"]].fillna(0)
    )

    # Attainment rates
    merged["NB_Attainment"] = merged.apply(
        lambda r: r["NB_GB_Actual"] / r["NB_Quota"] if r["NB_Quota"] > 0 else np.nan, axis=1
    )
    merged["CO_Attainment"] = merged.apply(
        lambda r: r["CO_GB_Actual"] / r["CO_Quota"] if r["CO_Quota"] > 0 else np.nan, axis=1
    )
    merged["Total_Attainment"] = merged.apply(
        lambda r: r["Total_GB_Actual"] / r["Total_Quota"] if r["Total_Quota"] > 0 else np.nan, axis=1
    )

    # Performance tier
    def tier(att):
        if pd.isna(att):
            return "No Quota"
        elif att >= 1.25:
            return "Exceptional (≥125%)"
        elif att >= 1.0:
            return "On Target (100–124%)"
        elif att >= 0.75:
            return "Near Target (75–99%)"
        elif att >= 0.5:
            return "Below Target (50–74%)"
        else:
            return "At Risk (<50%)"

    merged["Perf_Tier"] = merged["Total_Attainment"].apply(tier)

    return lb, aq, merged


lb, aq, merged = load_and_clean()

REGIONS   = sorted(merged["Mega_Region"].dropna().unique())
CHANNELS  = sorted(merged["Channel"].dropna().unique())
PRODUCTS  = sorted(aq["Product_Label"].dropna().unique())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 24px 0'>
      <div style='font-size:1.5rem;font-weight:700;color:white'>Uber</div>
      <div style='font-size:0.75rem;color:#888;margin-top:2px'>for Business · Sales Ops</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Filters**")

    sel_regions = st.multiselect(
        "Mega Region",
        options=REGIONS,
        default=REGIONS,
    )
    sel_channels = st.multiselect(
        "Channel",
        options=CHANNELS,
        default=CHANNELS,
    )
    sel_ramp = st.multiselect(
        "Ramp Status",
        options=sorted(merged["Ramp_Status"].dropna().unique()),
        default=sorted(merged["Ramp_Status"].dropna().unique()),
    )
    sel_status = st.selectbox(
        "AE Status",
        options=["All", "active", "inactive"],
        index=0,
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem;color:#666;line-height:1.6'>
      <b style='color:#06C167'>H2'21 Performance</b><br>
      Jul – Dec 2021<br>
      Semi-Annual Cycle<br>
      Gross Bookings Basis
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
filt = merged.copy()
if sel_regions:
    filt = filt[filt["Mega_Region"].isin(sel_regions)]
if sel_channels:
    filt = filt[filt["Channel"].isin(sel_channels)]
if sel_ramp:
    filt = filt[filt["Ramp_Status"].isin(sel_ramp)]
if sel_status != "All":
    filt = filt[filt["AE_Status"] == sel_status]

aq_filt = aq[aq["Mega_Region"].isin(sel_regions)] if sel_regions else aq
if sel_channels:
    aq_filt = aq_filt[aq_filt["Channel"].isin(sel_channels)]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='uber-header'>
  <div>
    <div class='uber-logo'>Uber for Business</div>
    <div class='uber-subtitle'>Sales Pipeline &amp; Performance Dashboard &nbsp;·&nbsp; H2 2021</div>
  </div>
  <div class='uber-badge'>H2 '21</div>
</div>
""", unsafe_allow_html=True)

# ── Top KPIs ─────────────────────────────────────────────────────────────────
active_filt = filt[filt["AE_Status"] == "active"]
total_nb_actual    = filt["NB_GB_Actual"].sum()
total_co_actual    = filt["CO_GB_Actual"].sum()
total_nb_quota     = filt["NB_Quota"].sum()
total_co_quota     = filt["CO_Quota"].sum()
total_quota        = filt["Total_Quota"].sum()
total_actual       = filt["Total_GB_Actual"].sum()
overall_att        = total_actual / total_quota if total_quota > 0 else 0
nb_att             = total_nb_actual / total_nb_quota if total_nb_quota > 0 else 0
pct_on_target      = (filt["Total_Attainment"] >= 1.0).sum() / max(len(filt[filt["Total_Attainment"].notna()]), 1) * 100
total_deals        = aq_filt["Unique Dashboard ID"].nunique()

c1, c2, c3, c4, c5, c6 = st.columns(6)

def kpi_card(col, label, value, sub="", delta=None, delta_pos=True):
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-pos" if delta_pos else "kpi-delta-neg"
        delta_html = f"<div class='{cls}'>{delta}</div>"
    col.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}</div>
      {delta_html}
      <div class='kpi-sub'>{sub}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(c1, "Total GB Actual",   f"${total_actual/1e6:.1f}M", f"Quota: ${total_quota/1e6:.1f}M")
kpi_card(c2, "Overall Attainment", f"{overall_att:.0%}", f"{len(filt)} AEs included",
         delta=f"{'▲' if overall_att>=1 else '▼'} vs 100% target", delta_pos=overall_att>=1)
kpi_card(c3, "NB GB Actual",       f"${total_nb_actual/1e6:.1f}M", f"NB Quota: ${total_nb_quota/1e6:.1f}M",
         delta=f"{nb_att:.0%} NB Attainment", delta_pos=nb_att>=1)
kpi_card(c4, "CO GB Actual",       f"${total_co_actual/1e6:.1f}M", f"CO Quota: ${total_co_quota/1e6:.1f}M")
kpi_card(c5, "% On/Above Target",  f"{pct_on_target:.0f}%", "AEs ≥100% attainment",
         delta="↑ Higher = Better", delta_pos=pct_on_target>=50)
kpi_card(c6, "Total Deals",        f"{total_deals:,}", "Unique opps closed")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Performance Distribution",
    "🎯 Performance Optimization",
    "🔄 Product & Incentives",
    "💡 Sales Strategy",
    "⚙️ Scalability & Automation",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 · PERFORMANCE DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("<div class='section-header'>AE Performance by Mega Region</div>", unsafe_allow_html=True)
    #st.markdown("<div class='section-sub'>What → So What → Now What framework applied to attainment distributions</div>", unsafe_allow_html=True)

    # ── Row 1: Attainment by Region ──────────────────────────────────────────
    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        reg_perf = (
            filt.groupby("Mega_Region")
            .agg(
                AE_Count=("AE", "count"),
                NB_Actual=("NB_GB_Actual", "sum"),
                CO_Actual=("CO_GB_Actual", "sum"),
                NB_Quota=("NB_Quota", "sum"),
                CO_Quota=("CO_Quota", "sum"),
                Total_Actual=("Total_GB_Actual", "sum"),
                Total_Quota=("Total_Quota", "sum"),
            )
            .reset_index()
        )
        reg_perf["Attainment"] = reg_perf["Total_Actual"] / reg_perf["Total_Quota"].replace(0, np.nan)
        reg_perf["NB_Att"] = reg_perf["NB_Actual"] / reg_perf["NB_Quota"].replace(0, np.nan)
        reg_perf = reg_perf.sort_values("Attainment", ascending=True)

        fig = go.Figure()
        colors = [REGION_COLORS.get(r, UBER_ACCENT) for r in reg_perf["Mega_Region"]]
        fig.add_trace(go.Bar(
            y=reg_perf["Mega_Region"],
            x=reg_perf["Attainment"] * 100,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}%" for v in reg_perf["Attainment"] * 100],
            textposition="outside",
            customdata=np.stack([
                reg_perf["AE_Count"],
                reg_perf["Total_Actual"] / 1e6,
                reg_perf["Total_Quota"] / 1e6,
            ], axis=-1),
            hovertemplate="<b>%{y}</b><br>Attainment: %{x:.1f}%<br>AEs: %{customdata[0]}<br>Actual: $%{customdata[1]:.2f}M<br>Quota: $%{customdata[2]:.2f}M<extra></extra>",
        ))
        fig.add_vline(x=100, line_dash="dot", line_color=UBER_GREEN, line_width=2,
                      annotation_text="100% Target", annotation_position="top")
        fig.update_layout(
            title="Total Attainment % by Mega Region",
            xaxis_title="Attainment (%)",
            yaxis_title="",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=340,
            margin=dict(l=10, r=80, t=50, b=40),
            font=dict(family="Inter", size=12),
            xaxis=dict(gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Performance tier donut
        tier_order = [
            "Exceptional (≥125%)", "On Target (100–124%)",
            "Near Target (75–99%)", "Below Target (50–74%)", "At Risk (<50%)", "No Quota"
        ]
        tier_colors_map = {
            "Exceptional (≥125%)":    "#06C167",
            "On Target (100–124%)":   "#2ECC71",
            "Near Target (75–99%)":   "#F39C12",
            "Below Target (50–74%)":  "#E67E22",
            "At Risk (<50%)":         "#E74C3C",
            "No Quota":               "#BDC3C7",
        }
        tier_counts = filt["Perf_Tier"].value_counts().reindex(tier_order).fillna(0)
        fig2 = go.Figure(go.Pie(
            labels=tier_counts.index,
            values=tier_counts.values,
            hole=0.45,
            marker_colors=[tier_colors_map[t] for t in tier_counts.index],
            textinfo="percent+label",
            textfont_size=10,
            hovertemplate="<b>%{label}</b><br>%{value} AEs (%{percent})<extra></extra>",
        ))
        fig2.update_layout(
            title="AE Performance Tier Distribution",
            height=340,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            annotations=[dict(text=f"<b>{len(filt)}</b><br>AEs", x=0.5, y=0.5,
                              font_size=14, showarrow=False)],
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Individual AE scatter ─────────────────────────────────────────
    st.markdown("<div class='section-header' style='margin-top:1rem'>Individual AE Attainment — NB vs CO</div>", unsafe_allow_html=True)

    ae_plot = filt[filt["Total_Quota"] > 0].copy()
    ae_plot["NB_Att_pct"]    = ae_plot["NB_Attainment"].fillna(0) * 100
    ae_plot["Total_Att_pct"] = ae_plot["Total_Attainment"].fillna(0) * 100

    fig3 = px.scatter(
        ae_plot,
        x="NB_GB_Actual",
        y="CO_GB_Actual",
        color="Mega_Region",
        size="Total_GB_Actual",
        size_max=40,
        color_discrete_map=REGION_COLORS,
        hover_name="AE",
        hover_data={
            "NB_GB_Actual": ":.0f",
            "CO_GB_Actual": ":.0f",
            "Total_Att_pct": ":.1f",
            "Channel": True,
            "Ramp_Status": True,
        },
        labels={
            "NB_GB_Actual": "NB GB (USD)",
            "CO_GB_Actual": "CO GB (USD)",
            "Total_Att_pct": "Total Attainment (%)",
        },
        title="NB vs CO Gross Bookings — Bubble = Total Actual GB",
    )
    fig3.update_layout(
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        yaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        legend_title="Mega Region",
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Insights ──────────────────────────────────────────────────────────────
    best_region = reg_perf.dropna(subset=["Attainment"]).sort_values("Attainment", ascending=False).iloc[0]
    worst_region = reg_perf.dropna(subset=["Attainment"]).sort_values("Attainment").iloc[0]
    pct_below = (filt["Total_Attainment"] < 0.75).sum() / max(len(filt[filt["Total_Attainment"].notna()]), 1) * 100

    c1i, c2i = st.columns(2)
    with c1i:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🏆 Key Insight · Top Region</div>
          <div class='insight-text'>
            <b>{best_region['Mega_Region']}</b> leads with <b>{best_region['Attainment']:.0%}</b> attainment across
            {int(best_region['AE_Count'])} AEs — indicating strong quota calibration and market penetration.
            Scale their playbooks cross-regionally.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2i:
        st.markdown(f"""
        <div class='warning-box'>
          <div class='insight-title'>⚠️ Action Required · Lagging Region</div>
          <div class='insight-text'>
            <b>{worst_region['Mega_Region']}</b> sits at <b>{worst_region['Attainment']:.0%}</b> attainment.
            <b>{pct_below:.0f}%</b> of AEs (filtered) are below 75% — consider quota recalibration,
            targeted coaching, or territory restructuring.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Region Detail Table ───────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Region Summary Table</div>", unsafe_allow_html=True)
    display_reg = reg_perf[["Mega_Region", "AE_Count", "NB_Actual", "CO_Actual", "Total_Actual", "Total_Quota", "Attainment"]].copy()
    display_reg.columns = ["Region", "# AEs", "NB Actual ($)", "CO Actual ($)", "Total Actual ($)", "Total Quota ($)", "Attainment"]
    for col in ["NB Actual ($)", "CO Actual ($)", "Total Actual ($)", "Total Quota ($)"]:
        display_reg[col] = display_reg[col].apply(lambda x: f"${x:,.0f}")
    display_reg["Attainment"] = display_reg["Attainment"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    st.dataframe(display_reg.reset_index(drop=True), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 · PERFORMANCE OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='section-header'>Right-Sizing Performance Distributions</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Identifying where quota calibration, coaching, or structural changes are needed</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Attainment histogram
        hist_data = filt[filt["Total_Attainment"].notna() & (filt["Total_Quota"] > 0)]["Total_Attainment"] * 100
        fig_hist = px.histogram(
            hist_data,
            nbins=20,
            color_discrete_sequence=[UBER_GREEN],
            title="Distribution of AE Total Attainment",
            labels={"value": "Attainment (%)", "count": "# AEs"},
        )
        fig_hist.add_vline(x=100, line_dash="dot", line_color="black", line_width=2,
                           annotation_text="100% Target")
        fig_hist.add_vline(x=float(hist_data.mean()), line_dash="dash",
                           line_color=UBER_ACCENT, line_width=1.5,
                           annotation_text=f"Mean: {hist_data.mean():.0f}%",
                           annotation_position="top left")
        fig_hist.update_layout(
            height=350, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            xaxis=dict(gridcolor="#f0f0f0"),
            yaxis=dict(gridcolor="#f0f0f0", title="# AEs"),
            showlegend=False,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        # Boxplot by region
        box_data = filt[filt["Total_Attainment"].notna() & (filt["Total_Quota"] > 0)].copy()
        box_data["Att_pct"] = box_data["Total_Attainment"] * 100
        fig_box = px.box(
            box_data,
            x="Mega_Region",
            y="Att_pct",
            color="Mega_Region",
            color_discrete_map=REGION_COLORS,
            title="Attainment Spread by Region (Box Plot)",
            labels={"Att_pct": "Attainment (%)", "Mega_Region": ""},
            points="all",
        )
        fig_box.add_hline(y=100, line_dash="dot", line_color="black", line_width=1.5)
        fig_box.update_layout(
            height=350, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            showlegend=False,
            yaxis=dict(gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Quota vs Actual by Channel ────────────────────────────────────────────
    st.markdown("<div class='section-header'>Quota vs Actual by Channel</div>", unsafe_allow_html=True)

    ch_perf = (
        filt.groupby("Channel")
        .agg(
            AE_Count=("AE", "count"),
            Avg_Quota=("Total_Quota", "mean"),
            Avg_Actual=("Total_GB_Actual", "mean"),
            Total_Quota=("Total_Quota", "sum"),
            Total_Actual=("Total_GB_Actual", "sum"),
        )
        .reset_index()
    )
    ch_perf["Attainment"] = ch_perf["Total_Actual"] / ch_perf["Total_Quota"].replace(0, np.nan)

    fig_ch = go.Figure()
    fig_ch.add_trace(go.Bar(
        name="Avg Quota",
        x=ch_perf["Channel"],
        y=ch_perf["Avg_Quota"],
        marker_color=UBER_MID,
        marker_line_color="#999",
        marker_line_width=1,
    ))
    fig_ch.add_trace(go.Bar(
        name="Avg Actual GB",
        x=ch_perf["Channel"],
        y=ch_perf["Avg_Actual"],
        marker_color=UBER_GREEN,
    ))
    fig_ch.update_layout(
        barmode="group",
        title="Average Quota vs Actual GB by Channel",
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        yaxis=dict(gridcolor="#f0f0f0", title="USD ($)"),
        xaxis_title="Channel",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_ch, use_container_width=True)

    # ── Ramp Status Analysis ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Attainment by Ramp Status</div>", unsafe_allow_html=True)
    ramp_data = filt[filt["Total_Attainment"].notna() & (filt["Total_Quota"] > 0)].copy()
    ramp_data["Att_pct"] = ramp_data["Total_Attainment"] * 100
    ramp_agg = ramp_data.groupby("Ramp_Status")["Att_pct"].agg(["mean", "median", "count"]).reset_index()
    ramp_agg.columns = ["Ramp Status", "Mean Att %", "Median Att %", "# AEs"]
    ramp_agg = ramp_agg.sort_values("Mean Att %", ascending=False)

    fig_ramp = px.bar(
        ramp_agg,
        x="Ramp Status",
        y="Mean Att %",
        color="Ramp Status",
        text=[f"{v:.0f}%" for v in ramp_agg["Mean Att %"]],
        title="Mean Attainment % by Ramp Status",
        color_discrete_sequence=[UBER_GREEN, UBER_ACCENT, "#FF6B35", "#E74C3C"],
    )
    fig_ramp.add_hline(y=100, line_dash="dot", line_color="black")
    fig_ramp.update_layout(
        height=320, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        showlegend=False,
        yaxis=dict(gridcolor="#f0f0f0", title="Mean Attainment (%)"),
    )
    st.plotly_chart(fig_ramp, use_container_width=True)

    # Optimization insights
    mean_att = hist_data.mean() if len(hist_data) > 0 else 0
    median_att = hist_data.median() if len(hist_data) > 0 else 0

    c1o, c2o, c3o = st.columns(3)
    with c1o:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>📐 Quota Calibration</div>
          <div class='insight-text'>
            Mean attainment of <b>{mean_att:.0f}%</b> vs median of <b>{median_att:.0f}%</b> signals
            right-skew — a handful of top performers inflate the mean.
            Recommend tightening quota bands for outlier AEs and re-baseline for partially ramped reps.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2o:
        no_quota_count = (filt["Ramp_Status"] == "No Quota").sum()
        st.markdown(f"""
        <div class='warning-box'>
          <div class='insight-title'>🎯 No-Quota AEs</div>
          <div class='insight-text'>
            <b>{no_quota_count}</b> AEs carry no quota — likely onboarding.
            Establish milestone-based ramp quotas (e.g. 25% / 50% / 75% over 3 half-cycles)
            to accelerate time-to-full contribution and improve pipeline visibility.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c3o:
        exceptional_pct = (filt["Perf_Tier"] == "Exceptional (≥125%)").sum() / max(len(filt[filt["Perf_Tier"] != "No Quota"]), 1) * 100
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🚀 Accelerator Design</div>
          <div class='insight-text'>
            <b>{exceptional_pct:.0f}%</b> of quota-bearing AEs exceed 125%.
            Tiered accelerators (e.g. 1.2× at 100%, 1.5× at 120%, 2× at 150%) reward
            high performers and create upside that self-funds through incremental GB.
          </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 · PRODUCT & INCENTIVES
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div class='section-header'>Recurring vs Non-Recurring Product Mix</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Are AEs focused on the right mix? How should incentives be adjusted?</div>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        type_agg = aq_filt.groupby("Product_Type").agg(
            NB_GB=("NB_GB", "sum"),
            CO_GB=("CO_GB", "sum"),
            Deals=("Unique Dashboard ID", "nunique"),
        ).reset_index()
        type_agg["Total_GB"] = type_agg["NB_GB"] + type_agg["CO_GB"]

        fig_type = go.Figure(go.Pie(
            labels=type_agg["Product_Type"],
            values=type_agg["Total_GB"],
            hole=0.55,
            marker_colors=[UBER_GREEN, UBER_ACCENT],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total GB: $%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig_type.update_layout(
            title="Total GB by Product Type",
            height=340,
            paper_bgcolor="white",
            font=dict(family="Inter", size=12),
            annotations=[dict(text="GB Split", x=0.5, y=0.5, font_size=13, showarrow=False)],
            showlegend=True,
        )
        st.plotly_chart(fig_type, use_container_width=True)

    with col_p2:
        prod_agg = aq_filt.groupby(["Product_Label", "Product_Type"]).agg(
            NB_GB=("NB_GB", "sum"),
            CO_GB=("CO_GB", "sum"),
            Deals=("Unique Dashboard ID", "nunique"),
        ).reset_index()
        prod_agg["Total_GB"] = prod_agg["NB_GB"] + prod_agg["CO_GB"]
        prod_agg = prod_agg.sort_values("Total_GB", ascending=True)

        fig_prod = px.bar(
            prod_agg,
            y="Product_Label",
            x="Total_GB",
            color="Product_Type",
            orientation="h",
            color_discrete_map={"Recurring": UBER_GREEN, "Non-Recurring": UBER_ACCENT},
            title="Total GB by Product",
            text=[f"${v/1e3:.0f}K" for v in prod_agg["Total_GB"]],
            labels={"Total_GB": "Total GB (USD)", "Product_Label": ""},
        )
        fig_prod.update_layout(
            height=340,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            xaxis=dict(gridcolor="#f0f0f0"),
            legend_title="Product Type",
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    # ── Product mix by region ─────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Product Mix by Region</div>", unsafe_allow_html=True)

    reg_prod = aq_filt.groupby(["Mega_Region", "Product_Type"])["Total_GB"].sum().reset_index()
    reg_prod_pivot = reg_prod.pivot(index="Mega_Region", columns="Product_Type", values="Total_GB").fillna(0)
    reg_prod_pivot["Total"] = reg_prod_pivot.sum(axis=1)
    if "Recurring" in reg_prod_pivot.columns:
        reg_prod_pivot["Recurring_Pct"] = reg_prod_pivot["Recurring"] / reg_prod_pivot["Total"] * 100
    else:
        reg_prod_pivot["Recurring_Pct"] = 0
    reg_prod_pivot = reg_prod_pivot.reset_index().sort_values("Recurring_Pct", ascending=False)

    fig_mix = go.Figure()
    if "Recurring" in reg_prod_pivot.columns:
        fig_mix.add_trace(go.Bar(
            name="Recurring",
            x=reg_prod_pivot["Mega_Region"],
            y=reg_prod_pivot["Recurring"],
            marker_color=UBER_GREEN,
        ))
    if "Non-Recurring" in reg_prod_pivot.columns:
        fig_mix.add_trace(go.Bar(
            name="Non-Recurring",
            x=reg_prod_pivot["Mega_Region"],
            y=reg_prod_pivot["Non-Recurring"],
            marker_color=UBER_ACCENT,
        ))
    fig_mix.update_layout(
        barmode="stack",
        title="Recurring vs Non-Recurring GB by Region (Stacked)",
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        yaxis=dict(gridcolor="#f0f0f0", title="Total GB (USD)"),
        xaxis_title="",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_mix, use_container_width=True)

    # ── Monthly product trend ─────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Product Revenue Trend (Monthly)</div>", unsafe_allow_html=True)

    monthly_prod = aq_filt.groupby(["Month", "Product_Label"])["Total_GB"].sum().reset_index()
    fig_trend = px.line(
        monthly_prod,
        x="Month",
        y="Total_GB",
        color="Product_Label",
        markers=True,
        title="Monthly GB by Product",
        labels={"Total_GB": "Total GB (USD)", "Month": ""},
    )
    fig_trend.update_layout(
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        yaxis=dict(gridcolor="#f0f0f0"),
        xaxis=dict(tickangle=-45),
        legend_title="Product",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── Incentive recommendations ─────────────────────────────────────────────
    rec_nb = type_agg[type_agg["Product_Type"] == "Recurring"]["NB_GB"].sum() if len(type_agg) > 0 else 0
    non_rec_nb = type_agg[type_agg["Product_Type"] == "Non-Recurring"]["NB_GB"].sum() if len(type_agg) > 0 else 0
    rec_pct = rec_nb / max(rec_nb + non_rec_nb, 1) * 100

    st.markdown("<div class='section-header'>Incentive Design Recommendations</div>", unsafe_allow_html=True)
    c1p, c2p, c3p = st.columns(3)
    with c1p:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🔁 Recurring First</div>
          <div class='insight-text'>
            Recurring products (Travel, Eats, Central) represent <b>{rec_pct:.0f}%</b> of NB GB
            but generate compounding CO value in future halves.
            Boost recurring quota weight to <b>60–70%</b> and apply a <b>1.3× multiplier</b>
            on recurring deals to shift AE focus.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2p:
        st.markdown(f"""
        <div class='warning-box'>
          <div class='insight-title'>🎁 Non-Recurring Risk</div>
          <div class='insight-text'>
            Gift Cards and Vouchers inflate NB attainment without generating reliable CO.
            Cap non-recurring credit at <b>30% of NB quota</b> or apply a
            <b>0.7× discount factor</b> to non-recurring GB in attainment calculations.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c3p:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>📈 CO Incentive Design</div>
          <div class='insight-text'>
            CO attainment reflects prior-half deal quality. Introduce a
            <b>CO Health Bonus</b> — AEs whose H1 deals generate ≥80% expected CO
            in H2 earn a 5–10% base bonus. This rewards sustainable deal structuring.
          </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 · SALES STRATEGY TRADEOFFS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div class='section-header'>Sales Strategy Tradeoffs</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Should high-cost AEs focus on smaller, non-recurring deals? Can those lead to larger opportunities?</div>", unsafe_allow_html=True)

    # Deal size distribution
    col_s1, col_s2 = st.columns([1, 1])

    with col_s1:
        deal_size = aq_filt.groupby("Unique Dashboard ID").agg(
            NB_GB=("NB_GB", "sum"),
            Product_Type=("Product_Type", "first"),
            Mega_Region=("Mega_Region", "first"),
        ).reset_index()
        deal_size = deal_size[deal_size["NB_GB"] > 0]

        fig_ds = px.histogram(
            deal_size,
            x="NB_GB",
            color="Product_Type",
            nbins=40,
            log_x=True,
            color_discrete_map={"Recurring": UBER_GREEN, "Non-Recurring": UBER_ACCENT},
            title="Deal Size Distribution (NB GB, Log Scale)",
            labels={"NB_GB": "NB GB per Deal (USD)", "count": "# Deals"},
        )
        fig_ds.update_layout(
            height=360, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            yaxis=dict(gridcolor="#f0f0f0"),
            legend_title="Product Type",
        )
        st.plotly_chart(fig_ds, use_container_width=True)

    with col_s2:
        # Average deal size by product
        avg_deal = aq_filt[aq_filt["NB_GB"] > 0].groupby("Product_Label")["NB_GB"].agg(["mean", "median", "count"]).reset_index()
        avg_deal.columns = ["Product", "Mean Deal ($)", "Median Deal ($)", "# Deals"]
        avg_deal = avg_deal.sort_values("Mean Deal ($)", ascending=True)

        fig_avg = go.Figure()
        fig_avg.add_trace(go.Bar(
            y=avg_deal["Product"],
            x=avg_deal["Mean Deal ($)"],
            name="Mean",
            orientation="h",
            marker_color=UBER_GREEN,
            text=[f"${v:,.0f}" for v in avg_deal["Mean Deal ($)"]],
            textposition="outside",
        ))
        fig_avg.add_trace(go.Bar(
            y=avg_deal["Product"],
            x=avg_deal["Median Deal ($)"],
            name="Median",
            orientation="h",
            marker_color=UBER_ACCENT,
            text=[f"${v:,.0f}" for v in avg_deal["Median Deal ($)"]],
            textposition="outside",
        ))
        fig_avg.update_layout(
            barmode="group",
            title="Mean vs Median Deal Size by Product",
            height=360, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            xaxis=dict(gridcolor="#f0f0f0", title="NB GB (USD)"),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_avg, use_container_width=True)

    # ── AE productivity analysis ──────────────────────────────────────────────
    st.markdown("<div class='section-header'>AE Productivity: Deals vs GB (Efficiency Quadrant)</div>", unsafe_allow_html=True)

    ae_prod = aq_filt.groupby("AE").agg(
        Deals=("Unique Dashboard ID", "nunique"),
        NB_GB=("NB_GB", "sum"),
    ).reset_index()
    ae_prod["GB_per_Deal"] = ae_prod["NB_GB"] / ae_prod["Deals"].replace(0, np.nan)
    ae_prod = ae_prod.merge(filt[["AE", "Mega_Region", "Channel", "Total_Attainment"]], on="AE", how="left")

    med_deals = ae_prod["Deals"].median()
    med_gb    = ae_prod["NB_GB"].median()

    def quadrant(row):
        h = row["Deals"] >= med_deals
        v = row["NB_GB"] >= med_gb
        if h and v:     return "High Volume + High GB (Stars)"
        elif not h and v:  return "Low Volume + High GB (Whales)"
        elif h and not v:  return "High Volume + Low GB (Grinders)"
        else:              return "Low Volume + Low GB (At Risk)"

    ae_prod["Quadrant"] = ae_prod.apply(quadrant, axis=1)
    quad_colors = {
        "High Volume + High GB (Stars)":    UBER_GREEN,
        "Low Volume + High GB (Whales)":    UBER_ACCENT,
        "High Volume + Low GB (Grinders)":  "#F39C12",
        "Low Volume + Low GB (At Risk)":    "#E74C3C",
    }

    fig_quad = px.scatter(
        ae_prod,
        x="Deals",
        y="NB_GB",
        color="Quadrant",
        color_discrete_map=quad_colors,
        hover_name="AE",
        hover_data={"Channel": True, "Mega_Region": True, "GB_per_Deal": ":.0f"},
        title="AE Efficiency Quadrant (Deals vs NB GB)",
        labels={"Deals": "# Deals Closed", "NB_GB": "NB GB (USD)"},
        size_max=20,
    )
    fig_quad.add_vline(x=med_deals, line_dash="dot", line_color="#bbb",
                       annotation_text=f"Median: {med_deals:.0f} deals")
    fig_quad.add_hline(y=med_gb, line_dash="dot", line_color="#bbb",
                       annotation_text=f"Median: ${med_gb:,.0f}")
    fig_quad.update_layout(
        height=440, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", y=-0.15, title=""),
    )
    st.plotly_chart(fig_quad, use_container_width=True)

    # Strategic insights
    stars   = (ae_prod["Quadrant"] == "High Volume + High GB (Stars)").sum()
    whales  = (ae_prod["Quadrant"] == "Low Volume + High GB (Whales)").sum()
    grind   = (ae_prod["Quadrant"] == "High Volume + Low GB (Grinders)").sum()
    at_risk = (ae_prod["Quadrant"] == "Low Volume + Low GB (At Risk)").sum()

    c1s, c2s = st.columns(2)
    with c1s:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>💡 Strategic Tradeoff Analysis</div>
          <div class='insight-text'>
            <b>{grind}</b> AEs are "Grinders" — high deal volume, low GB per deal.
            Many chase Non-Recurring (gift cards, vouchers) that pad NB count without building CO pipeline.
            These AEs should be redirected toward fewer, larger recurring deals —
            even one Travel or Central deal can outperform 10 voucher deals.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2s:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🐋 Whale Strategy</div>
          <div class='insight-text'>
            <b>{whales}</b> "Whale" AEs drive large GB from few deals — high ROI but concentration risk.
            Non-recurring deals <i>can</i> serve as land-and-expand entry points: a gift card
            trial frequently converts to an Eats program or Travel subscription at renewal.
            Track conversion rates from non-recurring to recurring per AE to quantify this pathway.
          </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 · SCALABILITY & AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("<div class='section-header'>Scalability & Automation Roadmap</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>How to automate and scale this analysis end-to-end</div>", unsafe_allow_html=True)

    # Pipeline Architecture Diagram (text-based)
    st.markdown("""
    <div style='background:#000;border-radius:12px;padding:24px 32px;margin-bottom:1.5rem;'>
      <div style='color:#06C167;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px'>
        Proposed Automated Analytics Architecture
      </div>
      <div style='font-family:monospace;color:white;font-size:0.85rem;line-height:2'>
        Salesforce CRM → <span style='color:#06C167'>Fivetran / Airbyte</span> → Snowflake DW<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        dbt (data models: attainment, product mix, AE productivity)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style='color:#276EF1'>Looker / Tableau / Streamlit</span> (Real-time dashboards)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style='color:#F39C12'>AI/ML Layer</span>: Quota forecasting · Churn signals · Rep coaching alerts<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        Slack / Email Digest → Sales Directors &amp; VP (Weekly automated)</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Automation roadmap cards
    col_a1, col_a2, col_a3 = st.columns(3)

    with col_a1:
        st.markdown("""
        <div class='kpi-card' style='border-top:3px solid #06C167'>
          <div class='kpi-label'>Phase 1 — Foundation (0–3 mo)</div>
          <div style='font-size:0.85rem;color:#333;margin-top:8px;line-height:1.8'>
            ✅ Salesforce → Snowflake via Fivetran<br>
            ✅ dbt models for attainment & quotas<br>
            ✅ This Streamlit dashboard (auto-refresh)<br>
            ✅ Weekly Slack digest to leadership<br>
            ✅ Anomaly detection on GB drops
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a2:
        st.markdown("""
        <div class='kpi-card' style='border-top:3px solid #276EF1'>
          <div class='kpi-label'>Phase 2 — Intelligence (3–6 mo)</div>
          <div style='font-size:0.85rem;color:#333;margin-top:8px;line-height:1.8'>
            🤖 ML quota forecasting (XGBoost)<br>
            🤖 AE churn / disengagement model<br>
            🤖 Product upsell propensity scoring<br>
            🤖 Territory optimization algorithm<br>
            🤖 CO revenue prediction per AE
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a3:
        st.markdown("""
        <div class='kpi-card' style='border-top:3px solid #FF6B35'>
          <div class='kpi-label'>Phase 3 — Scale (6–12 mo)</div>
          <div style='font-size:0.85rem;color:#333;margin-top:8px;line-height:1.8'>
            🚀 Self-serve analytics (natural language)<br>
            🚀 Real-time deal scoring in Salesforce<br>
            🚀 Automated quota setting (annual)<br>
            🚀 AI coaching recommendations per rep<br>
            🚀 Executive QBR auto-generation
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Automation metrics ────────────────────────────────────────────────────
    st.markdown("<div class='section-header' style='margin-top:1.5rem'>Current Pipeline Metrics (Automatable KPIs)</div>", unsafe_allow_html=True)

    auto_col1, auto_col2 = st.columns([1.5, 1])

    with auto_col1:
        monthly_gb = aq_filt.groupby("Month").agg(
            NB_GB=("NB_GB", "sum"),
            CO_GB=("CO_GB", "sum"),
            Deals=("Unique Dashboard ID", "nunique"),
        ).reset_index()
        monthly_gb["Total_GB"] = monthly_gb["NB_GB"] + monthly_gb["CO_GB"]

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=monthly_gb["Month"],
            y=monthly_gb["NB_GB"],
            name="NB GB",
            marker_color=UBER_GREEN,
        ))
        fig_monthly.add_trace(go.Bar(
            x=monthly_gb["Month"],
            y=monthly_gb["CO_GB"],
            name="CO GB",
            marker_color=UBER_ACCENT,
        ))
        fig_monthly.add_trace(go.Scatter(
            x=monthly_gb["Month"],
            y=monthly_gb["Deals"],
            name="# Deals",
            yaxis="y2",
            line=dict(color="#FF6B35", width=2.5),
            marker=dict(size=6),
        ))
        fig_monthly.update_layout(
            barmode="stack",
            title="Monthly NB + CO GB with Deal Volume Trend",
            height=380,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            yaxis=dict(gridcolor="#f0f0f0", title="GB (USD)"),
            yaxis2=dict(title="# Deals", overlaying="y", side="right", showgrid=False),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with auto_col2:
        st.markdown("""
        <div class='insight-box' style='margin-top:0'>
          <div class='insight-title'>⚙️ Where AI Fits</div>
          <div class='insight-text' style='line-height:1.9'>
            <b>Quota Setting:</b> Train on historical GB, ramp curves, market size<br>
            <b>Churn Detection:</b> Flag AEs with declining engagement 6 wks early<br>
            <b>Deal Prioritization:</b> Score inbound leads by conversion probability<br>
            <b>CO Prediction:</b> Forecast next-half CO from current deal structure<br>
            <b>Natural Language:</b> "What is US&Can NB attainment vs last half?"
          </div>
        </div>
        <div class='warning-box'>
          <div class='insight-title'>📋 Data Quality Requirements</div>
          <div class='insight-text' style='line-height:1.9'>
            276 rows missing Mega Region in raw data → fix at Salesforce entry level<br>
            Ramp status inconsistency ("partially" vs "Partially") → governed picklist<br>
            Recommend weekly automated data quality Slack alert to Sales Ops
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tech stack table ──────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Recommended Tech Stack</div>", unsafe_allow_html=True)
    tech_df = pd.DataFrame({
        "Layer": ["Source", "Ingestion", "Storage", "Transformation", "Visualization", "AI/ML", "Orchestration", "Alerting"],
        "Tool": ["Salesforce CRM", "Fivetran / Airbyte", "Snowflake", "dbt Core", "Streamlit / Looker", "Python (scikit-learn, XGBoost)", "Airflow / Prefect", "Slack API / PagerDuty"],
        "Purpose": [
            "CRM: opportunities, accounts, AE data",
            "Automated CDC sync to data warehouse",
            "Scalable columnar DW for analytics",
            "SQL-based modular data transformations",
            "Dashboards for Sales Directors / VP",
            "Quota forecasting, churn, propensity models",
            "Schedule dbt runs & model retraining",
            "Anomaly alerts & weekly digests",
        ],
        "Priority": ["Now", "Now", "Now", "Now", "Now", "Phase 2", "Phase 2", "Phase 2"],
    })
    st.dataframe(tech_df, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='dashboard-footer'>
  Uber for Business · Sales Operations · H2 2021 Performance Analysis ·
  Built with Streamlit + Plotly · Data: Salesforce Attainment Export
</div>
""", unsafe_allow_html=True)
