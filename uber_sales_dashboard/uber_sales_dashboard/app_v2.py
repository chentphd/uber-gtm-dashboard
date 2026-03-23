import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uber for Business · Sales Performance Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Uber brand palette ────────────────────────────────────────────────────────
UBER_BLACK  = "#000000"
UBER_WHITE  = "#FFFFFF"
UBER_GREEN  = "#06C167"
UBER_GREY   = "#F6F6F6"
UBER_MID    = "#EEEEEE"
UBER_TEXT   = "#1A1A1A"
UBER_ACCENT = "#276EF1"
REGION_COLORS = {
    "US&Can": "#06C167",
    "Europe": "#276EF1",
    "LatAm":  "#FF6B35",
    "APACx":  "#9B59B6",
    "India":  "#F1C40F",
    "MEA":    "#E74C3C",
}

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #FFFFFF; }

  [data-testid="stSidebar"] { background: #000000 !important; color: white !important; }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stMultiSelect > div > div {
      background: #1a1a1a !important; border: 1px solid #333 !important;
  }
  [data-testid="stSidebar"] label {
      color: #aaa !important; font-size: 0.75rem;
      text-transform: uppercase; letter-spacing: 0.05em;
  }
  /* All-selected pill */
  .all-selected-pill {
      background: #1a1a1a; border: 1px solid #06C167; border-radius: 20px;
      padding: 6px 14px; font-size: 0.78rem; color: #06C167 !important;
      font-weight: 600; display: inline-block; margin-bottom: 8px;
  }

  .uber-header {
      background: #000000; padding: 20px 32px;
      margin: -1rem -1rem 1.5rem -1rem;
      display: flex; align-items: center; gap: 16px;
  }
  .uber-logo { font-size: 2rem; font-weight: 700; color: white; letter-spacing: -1px; }
  .uber-subtitle { font-size: 0.95rem; color: #aaa; margin-top: 2px; }
  .uber-badge {
      background: #06C167; color: black; font-size: 0.7rem; font-weight: 700;
      padding: 3px 10px; border-radius: 20px;
      text-transform: uppercase; letter-spacing: 0.05em;
  }

  .kpi-card {
      background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 12px;
      padding: 20px 24px; transition: box-shadow 0.2s;
  }
  .kpi-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
  .kpi-label { font-size: 0.72rem; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
  .kpi-value { font-size: 2rem; font-weight: 700; color: #000; line-height: 1.1; }
  .kpi-delta-pos { font-size: 0.82rem; color: #06C167; font-weight: 600; margin-top: 4px; }
  .kpi-delta-neg { font-size: 0.82rem; color: #E74C3C; font-weight: 600; margin-top: 4px; }
  .kpi-sub { font-size: 0.78rem; color: #999; margin-top: 2px; }

  .section-header {
      font-size: 1.25rem; font-weight: 700; color: #000;
      border-left: 4px solid #06C167; padding-left: 12px; margin: 2rem 0 1rem 0;
  }
  .section-sub {
      font-size: 0.85rem; color: #666; margin-top: -0.75rem;
      margin-bottom: 1rem; padding-left: 16px;
  }

  .insight-box {
      background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
      border-left: 4px solid #06C167; border-radius: 10px;
      padding: 16px 20px; margin: 12px 0;
  }
  .insight-box .insight-title { color: #06C167; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
  .insight-box .insight-text { color: white; font-size: 0.9rem; margin-top: 4px; }

  .warning-box {
      background: #FFF8F0; border-left: 4px solid #FF6B35;
      border-radius: 10px; padding: 16px 20px; margin: 12px 0;
  }
  .warning-box .insight-title { color: #FF6B35; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }
  .warning-box .insight-text { color: #333; font-size: 0.9rem; margin-top: 4px; }

  .verdict-yes {
      background: #F0FFF7; border-left: 4px solid #06C167;
      border-radius: 10px; padding: 16px 20px; margin: 12px 0;
  }
  .verdict-no {
      background: #FFF0F0; border-left: 4px solid #E74C3C;
      border-radius: 10px; padding: 16px 20px; margin: 12px 0;
  }
  .verdict-no .insight-title { color: #E74C3C; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }
  .verdict-no .insight-text { color: #333; font-size: 0.9rem; margin-top: 4px; }

  .stTabs [data-baseweb="tab-list"] { background: #F6F6F6; border-radius: 8px; padding: 4px; }
  .stTabs [data-baseweb="tab"] { border-radius: 6px; font-weight: 500; }
  .stTabs [aria-selected="true"] { background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
  .stPlotlyChart { border: 1px solid #eee; border-radius: 10px; overflow: hidden; }
  .dashboard-footer {
      border-top: 1px solid #eee; margin-top: 3rem; padding-top: 1rem;
      font-size: 0.75rem; color: #bbb; text-align: center;
  }
</style>
""", unsafe_allow_html=True)


# ── Data loading & cleaning ───────────────────────────────────────────────────
@st.cache_data
def load_and_clean():
    xl = pd.ExcelFile("sales_data.xlsx")

    lb = pd.read_excel(xl, sheet_name="Leaderboard", header=0)
    lb = lb.drop(columns=["Unnamed: 0"], errors="ignore")
    lb = lb.dropna(subset=["Account Executive Name"])
    lb.columns = lb.columns.str.strip()
    lb["Tenure based ramp status"] = lb["Tenure based ramp status"].str.strip().str.title()
    lb["Status as of 12/31"] = lb["Status as of 12/31"].str.strip().str.lower()
    for col in ["H2'21 NB Quota", "H2'21 CO Quota", "H2 Total Quota"]:
        lb[col] = pd.to_numeric(lb[col], errors="coerce").fillna(0)
    lb = lb.rename(columns={
        "Account Executive Name": "AE",
        "Mega Region": "Mega_Region",
        "H2'21 NB Quota": "NB_Quota",
        "H2'21 CO Quota": "CO_Quota",
        "H2 Total Quota": "Total_Quota",
        "Tenure based ramp status": "Ramp_Status",
        "Status as of 12/31": "AE_Status",
    })

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
    aq["Close Date"] = pd.to_datetime(aq["Close Date"], errors="coerce")
    aq["Month"] = aq["Close Date"].dt.to_period("M").astype(str)
    aq["Quarter"] = aq["Close Date"].dt.to_period("Q").astype(str)
    for col in ["NB_GB", "CO_GB", "Total_GB"]:
        aq[col] = pd.to_numeric(aq[col], errors="coerce").fillna(0)
    aq["Product"] = aq["Product"].str.strip().str.lower()
    recurring_products = {"travel", "eats", "central"}
    aq["Product_Type"] = aq["Product"].apply(
        lambda p: "Recurring" if p in recurring_products else "Non-Recurring"
    )
    product_labels = {
        "travel": "Travel", "eats": "Eats", "central": "Central",
        "gift card": "Gift Card", "eats vouchers": "Eats Vouchers", "vouchers": "Vouchers",
    }
    aq["Product_Label"] = aq["Product"].map(product_labels).fillna(aq["Product"].str.title())

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
    merged["NB_Attainment"] = merged.apply(
        lambda r: r["NB_GB_Actual"] / r["NB_Quota"] if r["NB_Quota"] > 0 else np.nan, axis=1
    )
    merged["CO_Attainment"] = merged.apply(
        lambda r: r["CO_GB_Actual"] / r["CO_Quota"] if r["CO_Quota"] > 0 else np.nan, axis=1
    )
    merged["Total_Attainment"] = merged.apply(
        lambda r: r["Total_GB_Actual"] / r["Total_Quota"] if r["Total_Quota"] > 0 else np.nan, axis=1
    )

    def tier(att):
        if pd.isna(att):        return "No Quota"
        elif att >= 1.25:       return "Exceptional (≥125%)"
        elif att >= 1.0:        return "On Target (100–124%)"
        elif att >= 0.75:       return "Near Target (75–99%)"
        elif att >= 0.5:        return "Below Target (50–74%)"
        else:                   return "At Risk (<50%)"

    merged["Perf_Tier"] = merged["Total_Attainment"].apply(tier)
    return lb, aq, merged


lb, aq, merged = load_and_clean()

REGIONS    = sorted(merged["Mega_Region"].dropna().unique())
CHANNELS   = sorted(merged["Channel"].dropna().unique())
RAMP_OPTS  = sorted(merged["Ramp_Status"].dropna().unique())
TIER_OPTS  = ["All"] + [
    "Exceptional (≥125%)", "On Target (100–124%)", "Near Target (75–99%)",
    "Below Target (50–74%)", "At Risk (<50%)", "No Quota"
]

# ── Sidebar ── FIX #1 & #2: Smart "All Selected" display + new Perf Tier filter
def smart_multiselect(label, options, key):
    """Renders a checkbox for Select All + multiselect; shows pill when all selected."""
    all_key = f"__all_{key}"
    all_checked = st.checkbox(f"Select All — {label}", value=True, key=all_key)
    if all_checked:
        st.markdown(f"<div class='all-selected-pill'>✓ All {label} Selected</div>", unsafe_allow_html=True)
        return list(options)
    else:
        return st.multiselect(label, options=options, default=options, key=key)

with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 24px 0'>
      <div style='font-size:1.5rem;font-weight:700;color:white'>Uber</div>
      <div style='font-size:0.75rem;color:#888;margin-top:2px'>for Business · Sales Ops</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Filters**")

    sel_regions  = smart_multiselect("Mega Region",  REGIONS,   "regions")
    sel_channels = smart_multiselect("Channel",      CHANNELS,  "channels")
    sel_ramp     = smart_multiselect("Ramp Status",  RAMP_OPTS, "ramp")

    # FIX #2: AE Status (existing) + NEW Performance Tier filter
    sel_status = st.selectbox("AE Status", options=["All", "active", "inactive"], index=0)
    sel_tier   = st.selectbox("Performance Tier", options=TIER_OPTS, index=0)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem;color:#666;line-height:1.6'>
      <b style='color:#06C167'>H2'21 Performance</b><br>
      Jul – Dec 2021 · Semi-Annual Cycle<br>
      Gross Bookings Basis
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
filt = merged.copy()
if sel_regions:  filt = filt[filt["Mega_Region"].isin(sel_regions)]
if sel_channels: filt = filt[filt["Channel"].isin(sel_channels)]
if sel_ramp:     filt = filt[filt["Ramp_Status"].isin(sel_ramp)]
if sel_status != "All": filt = filt[filt["AE_Status"] == sel_status]
if sel_tier != "All":   filt = filt[filt["Perf_Tier"] == sel_tier]

aq_filt = aq.copy()
if sel_regions:  aq_filt = aq_filt[aq_filt["Mega_Region"].isin(sel_regions)]
if sel_channels: aq_filt = aq_filt[aq_filt["Channel"].isin(sel_channels)]

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

# ── Top KPIs ── FIX #3: CO GB Actual gets CO Attainment delta ─────────────────
total_nb_actual = filt["NB_GB_Actual"].sum()
total_co_actual = filt["CO_GB_Actual"].sum()
total_nb_quota  = filt["NB_Quota"].sum()
total_co_quota  = filt["CO_Quota"].sum()
total_quota     = filt["Total_Quota"].sum()
total_actual    = filt["Total_GB_Actual"].sum()
overall_att     = total_actual / total_quota if total_quota > 0 else 0
nb_att          = total_nb_actual / total_nb_quota if total_nb_quota > 0 else 0
co_att          = total_co_actual / total_co_quota if total_co_quota > 0 else 0
pct_on_target   = (filt["Total_Attainment"] >= 1.0).sum() / max(len(filt[filt["Total_Attainment"].notna()]), 1) * 100
total_deals     = aq_filt["Unique Dashboard ID"].nunique()

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

kpi_card(c1, "Total GB Actual",    f"${total_actual/1e6:.1f}M",    f"Quota: ${total_quota/1e6:.1f}M")
kpi_card(c2, "Overall Attainment", f"{overall_att:.0%}",           f"{len(filt)} AEs included",
         delta=f"{'▲' if overall_att>=1 else '▼'} vs 100% target", delta_pos=overall_att>=1)
kpi_card(c3, "NB GB Actual",       f"${total_nb_actual/1e6:.1f}M", f"NB Quota: ${total_nb_quota/1e6:.1f}M",
         delta=f"{nb_att:.0%} NB Attainment", delta_pos=nb_att>=1)
# FIX #3 — CO card now shows CO Attainment delta
kpi_card(c4, "CO GB Actual",       f"${total_co_actual/1e6:.1f}M", f"CO Quota: ${total_co_quota/1e6:.1f}M",
         delta=f"{co_att:.0%} CO Attainment" if total_co_quota > 0 else "No CO Quota Set",
         delta_pos=co_att>=1)
kpi_card(c5, "% On/Above Target",  f"{pct_on_target:.0f}%",        "AEs ≥100% attainment",
         delta="↑ Higher = Better", delta_pos=pct_on_target>=50)
kpi_card(c6, "Total Deals",        f"{total_deals:,}",             "Unique opps closed")

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

    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        reg_perf = (
            filt.groupby("Mega_Region").agg(
                AE_Count=("AE", "count"),
                NB_Actual=("NB_GB_Actual", "sum"),
                CO_Actual=("CO_GB_Actual", "sum"),
                NB_Quota=("NB_Quota", "sum"),
                CO_Quota=("CO_Quota", "sum"),
                Total_Actual=("Total_GB_Actual", "sum"),
                Total_Quota=("Total_Quota", "sum"),
            ).reset_index()
        )
        reg_perf["Attainment"] = reg_perf["Total_Actual"] / reg_perf["Total_Quota"].replace(0, np.nan)
        reg_perf["NB_Att"]     = reg_perf["NB_Actual"]    / reg_perf["NB_Quota"].replace(0, np.nan)
        reg_perf = reg_perf.sort_values("Attainment", ascending=True)

        fig = go.Figure()
        colors = [REGION_COLORS.get(r, UBER_ACCENT) for r in reg_perf["Mega_Region"]]
        fig.add_trace(go.Bar(
            y=reg_perf["Mega_Region"], x=reg_perf["Attainment"] * 100, orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}%" for v in reg_perf["Attainment"] * 100],
            textposition="outside",
            customdata=np.stack([reg_perf["AE_Count"], reg_perf["Total_Actual"]/1e6, reg_perf["Total_Quota"]/1e6], axis=-1),
            hovertemplate="<b>%{y}</b><br>Attainment: %{x:.1f}%<br>AEs: %{customdata[0]}<br>Actual: $%{customdata[1]:.2f}M<br>Quota: $%{customdata[2]:.2f}M<extra></extra>",
        ))
        fig.add_vline(x=100, line_dash="dot", line_color=UBER_GREEN, line_width=2,
                      annotation_text="100% Target", annotation_position="top")
        fig.update_layout(
            title="Total Attainment % by Mega Region", xaxis_title="Attainment (%)", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white", height=340,
            margin=dict(l=10, r=80, t=50, b=40), font=dict(family="Inter", size=12),
            xaxis=dict(gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # FIX #4 — Increased height + legend instead of inline labels for crowded pie
        tier_order = [
            "Exceptional (≥125%)", "On Target (100–124%)", "Near Target (75–99%)",
            "Below Target (50–74%)", "At Risk (<50%)", "No Quota"
        ]
        tier_colors_map = {
            "Exceptional (≥125%)":   "#06C167",
            "On Target (100–124%)":  "#2ECC71",
            "Near Target (75–99%)":  "#F39C12",
            "Below Target (50–74%)": "#E67E22",
            "At Risk (<50%)":        "#E74C3C",
            "No Quota":              "#BDC3C7",
        }
        tier_counts = filt["Perf_Tier"].value_counts().reindex(tier_order).fillna(0)
        fig2 = go.Figure(go.Pie(
            labels=tier_counts.index,
            values=tier_counts.values,
            hole=0.45,
            marker_colors=[tier_colors_map[t] for t in tier_counts.index],
            textinfo="percent",
            textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{value} AEs (%{percent})<extra></extra>",
        ))
        fig2.update_layout(
            title="AE Performance Tier Distribution",
            height=460,                          # ← FIX #4: was 340, now 460
            showlegend=True,                     # ← FIX #4: legend shows all tier labels
            legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=10)),
            margin=dict(l=0, r=160, t=50, b=10),
            paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            annotations=[dict(text=f"<b>{len(filt)}</b><br>AEs", x=0.38, y=0.5,
                              font_size=14, showarrow=False)],
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Individual AE scatter
    st.markdown("<div class='section-header' style='margin-top:1rem'>Individual AE Attainment — NB vs CO</div>", unsafe_allow_html=True)
    ae_plot = filt[filt["Total_Quota"] > 0].copy()
    ae_plot["Total_Att_pct"] = ae_plot["Total_Attainment"].fillna(0) * 100
    fig3 = px.scatter(
        ae_plot, x="NB_GB_Actual", y="CO_GB_Actual", color="Mega_Region",
        size="Total_GB_Actual", size_max=40, color_discrete_map=REGION_COLORS,
        hover_name="AE",
        hover_data={"NB_GB_Actual": ":.0f", "CO_GB_Actual": ":.0f",
                    "Total_Att_pct": ":.1f", "Channel": True, "Ramp_Status": True},
        labels={"NB_GB_Actual": "NB GB (USD)", "CO_GB_Actual": "CO GB (USD)",
                "Total_Att_pct": "Total Attainment (%)"},
        title="NB vs CO Gross Bookings — Bubble = Total Actual GB",
    )
    fig3.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        yaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        legend_title="Mega Region",
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Insights
    if len(reg_perf.dropna(subset=["Attainment"])) >= 2:
        best_region  = reg_perf.dropna(subset=["Attainment"]).sort_values("Attainment", ascending=False).iloc[0]
        worst_region = reg_perf.dropna(subset=["Attainment"]).sort_values("Attainment").iloc[0]
        pct_below    = (filt["Total_Attainment"] < 0.75).sum() / max(len(filt[filt["Total_Attainment"].notna()]), 1) * 100
        c1i, c2i = st.columns(2)
        with c1i:
            st.markdown(f"""
            <div class='insight-box'>
              <div class='insight-title'>🏆 Top Region</div>
              <div class='insight-text'>
                <b>{best_region['Mega_Region']}</b> leads with <b>{best_region['Attainment']:.0%}</b> attainment
                across {int(best_region['AE_Count'])} AEs. Scale their playbooks cross-regionally.
              </div>
            </div>""", unsafe_allow_html=True)
        with c2i:
            st.markdown(f"""
            <div class='warning-box'>
              <div class='insight-title'>⚠️ Lagging Region</div>
              <div class='insight-text'>
                <b>{worst_region['Mega_Region']}</b> sits at <b>{worst_region['Attainment']:.0%}</b>.
                <b>{pct_below:.0f}%</b> of AEs below 75% — consider quota recalibration or coaching.
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Region Summary Table</div>", unsafe_allow_html=True)
    display_reg = reg_perf[["Mega_Region","AE_Count","NB_Actual","CO_Actual","Total_Actual","Total_Quota","Attainment"]].copy()
    display_reg.columns = ["Region","# AEs","NB Actual ($)","CO Actual ($)","Total Actual ($)","Total Quota ($)","Attainment"]
    for col in ["NB Actual ($)","CO Actual ($)","Total Actual ($)","Total Quota ($)"]:
        display_reg[col] = display_reg[col].apply(lambda x: f"${x:,.0f}")
    display_reg["Attainment"] = display_reg["Attainment"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    st.dataframe(display_reg.reset_index(drop=True), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 · PERFORMANCE OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='section-header'>Right-Sizing Performance Distributions</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Identifying where quota calibration, coaching, or structural changes are needed</div>", unsafe_allow_html=True)

    # col_left, col_right = st.columns([1, 1])

    # with col_left:
    hist_data = filt[filt["Total_Attainment"].notna() & (filt["Total_Quota"] > 0)]["Total_Attainment"] * 100
    mean_val   = float(hist_data.mean())  if len(hist_data) > 0 else 0
    median_val = float(hist_data.median()) if len(hist_data) > 0 else 0

    fig_hist = px.histogram(
        hist_data, nbins=20,
        color_discrete_sequence=[UBER_GREEN],
        title="Distribution of AE Total Attainment",
        labels={"value": "Attainment (%)", "count": "# AEs"},
    )
    # FIX #5 — Separate annotations so they don't overlap
    # fig_hist.add_vline(x=100, line_dash="dot", line_color="black", line_width=2,
    #                     annotation_text="100% Target",
    #                     annotation_position="top right",
    #                     annotation=dict(font_size=11, bgcolor="white", bordercolor="black"))
    fig_hist.add_vline(x=mean_val, line_dash="dash", line_color=UBER_ACCENT, line_width=1.5,
                        annotation_text=f"Mean: {mean_val:.0f}%",
                        annotation_position="bottom right",
                        annotation=dict(font_size=10, bgcolor="#EBF2FF", bordercolor=UBER_ACCENT))
    fig_hist.add_vline(x=median_val, line_dash="dot", line_color="#FF6B35", line_width=1.5,
                        annotation_text=f"Median: {median_val:.0f}%",
                        annotation_position="top left",
                        annotation=dict(font_size=10, bgcolor="#FFF3EE", bordercolor="#FF6B35"))
    fig_hist.update_layout(
        height=380, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0", title="# AEs"),
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # with col_right:
    #     box_data = filt[filt["Total_Attainment"].notna() & (filt["Total_Quota"] > 0)].copy()
    #     box_data["Att_pct"] = box_data["Total_Attainment"] * 100
    #     fig_box = px.box(
    #         box_data, x="Mega_Region", y="Att_pct", color="Mega_Region",
    #         color_discrete_map=REGION_COLORS,
    #         title="Attainment Spread by Region",
    #         labels={"Att_pct": "Attainment (%)", "Mega_Region": ""},
    #         points="all",
    #     )
    #     fig_box.add_hline(y=100, line_dash="dot", line_color="black", line_width=1.5)
    #     fig_box.update_layout(
    #         height=380, plot_bgcolor="white", paper_bgcolor="white",
    #         font=dict(family="Inter", size=11), showlegend=False,
    #         yaxis=dict(gridcolor="#f0f0f0"),
    #     )
    #     st.plotly_chart(fig_box, use_container_width=True)

    # FIX #6 — Channel chart sorted by Avg_Actual descending
    # st.markdown("<div class='section-header'>Quota vs Actual by Channel</div>", unsafe_allow_html=True)
    # ch_perf = (
    #     filt.groupby("Channel").agg(
    #         AE_Count=("AE", "count"),
    #         Avg_Quota=("Total_Quota", "mean"),
    #         Avg_Actual=("Total_GB_Actual", "mean"),
    #         Total_Quota=("Total_Quota", "sum"),
    #         Total_Actual=("Total_GB_Actual", "sum"),
    #     ).reset_index()
    # )
    # ch_perf["Attainment"] = ch_perf["Total_Actual"] / ch_perf["Total_Quota"].replace(0, np.nan)
    # ch_perf = ch_perf.sort_values("Avg_Actual", ascending=False)   # ← FIX #6

    # fig_ch = go.Figure()
    # fig_ch.add_trace(go.Bar(
    #     name="Avg Quota", x=ch_perf["Channel"], y=ch_perf["Avg_Quota"],
    #     marker_color=UBER_MID, marker_line_color="#999", marker_line_width=1,
    # ))
    # fig_ch.add_trace(go.Bar(
    #     name="Avg Actual GB", x=ch_perf["Channel"], y=ch_perf["Avg_Actual"],
    #     marker_color=UBER_GREEN,
    # ))
    # fig_ch.update_layout(
    #     barmode="group",
    #     title="Average Quota vs Actual GB by Channel (sorted by Avg Actual, high→low)",
    #     height=360, plot_bgcolor="white", paper_bgcolor="white",
    #     font=dict(family="Inter", size=11),
    #     yaxis=dict(gridcolor="#f0f0f0", title="USD ($)"),
    #     xaxis=dict(title="Channel", categoryorder="array", categoryarray=ch_perf["Channel"].tolist()),
    #     legend=dict(orientation="h", y=1.1),
    # )
    # st.plotly_chart(fig_ch, use_container_width=True)

    # ── FIX #7 — Ramp Status: add GB Contribution chart ──────────────────────
    st.markdown("<div class='section-header'>Attainment & GB Contribution by Ramp Status</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Do No-Quota AEs generate meaningful GB despite having no formal quota?</div>", unsafe_allow_html=True)

    ramp_col1, ramp_col2 = st.columns(2)

    with ramp_col1:
        ramp_data = filt[filt["Total_Attainment"].notna() & (filt["Total_Quota"] > 0)].copy()
        ramp_data["Att_pct"] = ramp_data["Total_Attainment"] * 100
        ramp_agg = ramp_data.groupby("Ramp_Status")["Att_pct"].agg(["mean", "median", "count"]).reset_index()
        ramp_agg.columns = ["Ramp Status", "Mean Att %", "Median Att %", "# AEs"]
        ramp_agg = ramp_agg.sort_values("Mean Att %", ascending=False)

        fig_ramp = px.bar(
            ramp_agg, x="Ramp Status", y="Mean Att %", color="Ramp Status",
            text=[f"{v:.0f}%" for v in ramp_agg["Mean Att %"]],
            title="Mean Attainment % by Ramp Status (quota-bearing AEs only)",
            color_discrete_sequence=[UBER_GREEN, UBER_ACCENT, "#FF6B35", "#E74C3C"],
        )
        fig_ramp.add_hline(y=100, line_dash="dot", line_color="black")
        fig_ramp.update_layout(
            height=340, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11), showlegend=False,
            yaxis=dict(gridcolor="#f0f0f0", title="Mean Attainment (%)"),
        )
        st.plotly_chart(fig_ramp, use_container_width=True)

    with ramp_col2:
        # FIX #7 — GB value added by ramp status including No-Quota AEs
        ramp_gb = filt.groupby("Ramp_Status").agg(
            AE_Count=("AE", "count"),
            Total_GB=("Total_GB_Actual", "sum"),
            NB_GB=("NB_GB_Actual", "sum"),
            CO_GB=("CO_GB_Actual", "sum"),
        ).reset_index()
        ramp_gb["GB_per_AE"] = ramp_gb["Total_GB"] / ramp_gb["AE_Count"].replace(0, np.nan)
        ramp_gb = ramp_gb.sort_values("Total_GB", ascending=False)

        fig_ramp_gb = go.Figure()
        fig_ramp_gb.add_trace(go.Bar(
            name="NB GB", x=ramp_gb["Ramp_Status"], y=ramp_gb["NB_GB"] / 1e6,
            marker_color=UBER_GREEN,
            text=[f"${v:.1f}M" for v in ramp_gb["NB_GB"] / 1e6],
            textposition="inside",
        ))
        fig_ramp_gb.add_trace(go.Bar(
            name="CO GB", x=ramp_gb["Ramp_Status"], y=ramp_gb["CO_GB"] / 1e6,
            marker_color=UBER_ACCENT,
            text=[f"${v:.1f}M" for v in ramp_gb["CO_GB"] / 1e6],
            textposition="inside",
        ))
        fig_ramp_gb.add_trace(go.Scatter(
            name="GB / AE ($K)",
            x=ramp_gb["Ramp_Status"],
            y=ramp_gb["GB_per_AE"] / 1e3,
            yaxis="y2",
            mode="markers+lines",
            marker=dict(size=10, color="#FF6B35"),
            line=dict(color="#FF6B35", width=2),
        ))
        fig_ramp_gb.update_layout(
            barmode="stack",
            title="GB Contribution by Ramp Status (incl. No-Quota AEs)",
            height=340, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            yaxis=dict(gridcolor="#f0f0f0", title="Total GB ($M)"),
            yaxis2=dict(title="GB/AE ($K)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_ramp_gb, use_container_width=True)

    # ── FIX #8 — Full AE Leaderboard with Actual vs Quota ────────────────────
    st.markdown("<div class='section-header'>AE-Level Leaderboard: Actual vs Quota</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Full rep-level detail — sort any column; search by AE name using the filter above</div>", unsafe_allow_html=True)

    ae_table = filt[[
        "AE", "Mega_Region", "Channel", "Ramp_Status", "AE_Status",
        "NB_Quota", "NB_GB_Actual", "CO_Quota", "CO_GB_Actual",
        "Total_Quota", "Total_GB_Actual", "NB_Attainment", "CO_Attainment", "Total_Attainment", "Perf_Tier"
    ]].copy()

    ae_table = ae_table.rename(columns={
        "AE": "Rep", "Mega_Region": "Region", "Ramp_Status": "Ramp", "AE_Status": "Status",
        "NB_Quota": "NB Quota ($)", "NB_GB_Actual": "NB Actual ($)",
        "CO_Quota": "CO Quota ($)", "CO_GB_Actual": "CO Actual ($)",
        "Total_Quota": "Total Quota ($)", "Total_GB_Actual": "Total Actual ($)",
        "NB_Attainment": "NB Att %", "CO_Attainment": "CO Att %",
        "Total_Attainment": "Total Att %", "Perf_Tier": "Tier",
    })
    for col in ["NB Quota ($)", "NB Actual ($)", "CO Quota ($)", "CO Actual ($)", "Total Quota ($)", "Total Actual ($)"]:
        ae_table[col] = ae_table[col].apply(lambda x: f"${x:,.0f}")
    for col in ["NB Att %", "CO Att %", "Total Att %"]:
        ae_table[col] = ae_table[col].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
    ae_table = ae_table.sort_values("Total Actual ($)", ascending=False)

    st.dataframe(ae_table.reset_index(drop=True), use_container_width=True, hide_index=True, height=420)

    # Optimization insights
    mean_att   = hist_data.mean()   if len(hist_data) > 0 else 0
    median_att = hist_data.median() if len(hist_data) > 0 else 0
    c1o, c2o, c3o = st.columns(3)
    with c1o:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>📐 Quota Calibration</div>
          <div class='insight-text'>
            Mean <b>{mean_att:.0f}%</b> vs median <b>{median_att:.0f}%</b> signals right-skew —
            a few top performers inflate the mean. Tighten quota bands for outlier AEs.
          </div>
        </div>""", unsafe_allow_html=True)
    with c2o:
        no_quota_count = (filt["Ramp_Status"] == "No Quota").sum()
        no_quota_gb    = filt[filt["Ramp_Status"] == "No Quota"]["Total_GB_Actual"].sum()
        st.markdown(f"""
        <div class='warning-box'>
          <div class='insight-title'>🎯 No-Quota AEs</div>
          <div class='insight-text'>
            <b>{no_quota_count}</b> AEs carry no quota but collectively generate
            <b>${no_quota_gb/1e6:.1f}M</b> in GB — real revenue at risk of under-measurement.
            Establish milestone-based ramp quotas to capture and incentivise this output.
          </div>
        </div>""", unsafe_allow_html=True)
    with c3o:
        exceptional_pct = (filt["Perf_Tier"] == "Exceptional (≥125%)").sum() / max(len(filt[filt["Perf_Tier"] != "No Quota"]), 1) * 100
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🚀 Accelerator Design</div>
          <div class='insight-text'>
            <b>{exceptional_pct:.0f}%</b> of quota-bearing AEs exceed 125%.
            Tiered accelerators (1.2× at 100%, 1.5× at 120%, 2× at 150%) reward high performers
            and self-fund through incremental GB.
          </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 · PRODUCT & INCENTIVES
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div class='section-header'>Recurring vs Non-Recurring Product Mix</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Are AEs focused on the right mix? How should incentives be adjusted?</div>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        type_agg = aq_filt.groupby("Product_Type").agg(
            NB_GB=("NB_GB", "sum"), CO_GB=("CO_GB", "sum"),
            Deals=("Unique Dashboard ID", "nunique"),
        ).reset_index()
        type_agg["Total_GB"] = type_agg["NB_GB"] + type_agg["CO_GB"]

        fig_type = go.Figure(go.Pie(
            labels=type_agg["Product_Type"], values=type_agg["Total_GB"],
            hole=0.55, marker_colors=[UBER_GREEN, UBER_ACCENT],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total GB: $%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig_type.update_layout(
            title="Total GB by Product Type", height=340, paper_bgcolor="white",
            font=dict(family="Inter", size=12),
            annotations=[dict(text="GB Split", x=0.5, y=0.5, font_size=13, showarrow=False)],
            showlegend=True,
        )
        st.plotly_chart(fig_type, use_container_width=True)

    with col_p2:
        prod_agg = aq_filt.groupby(["Product_Label", "Product_Type"]).agg(
            NB_GB=("NB_GB", "sum"), CO_GB=("CO_GB", "sum"),
            Deals=("Unique Dashboard ID", "nunique"),
        ).reset_index()
        prod_agg["Total_GB"] = prod_agg["NB_GB"] + prod_agg["CO_GB"]
        prod_agg = prod_agg.sort_values("Total_GB", ascending=True)

        # FIX #9 — labels in $M not $K
        fig_prod = px.bar(
            prod_agg, y="Product_Label", x="Total_GB", color="Product_Type",
            orientation="h",
            color_discrete_map={"Recurring": UBER_GREEN, "Non-Recurring": UBER_ACCENT},
            title="Total GB by Product",
            text=[f"${v/1e6:.1f}M" for v in prod_agg["Total_GB"]],   # ← FIX #9
            labels={"Total_GB": "Total GB (USD)", "Product_Label": ""},
        )
        fig_prod.update_layout(
            height=340, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            xaxis=dict(gridcolor="#f0f0f0"),
            legend_title="Product Type",
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    # FIX #10 — Toggle between Recurring/NR stacked AND full product breakdown
    st.markdown("<div class='section-header'>Product Mix by Region</div>", unsafe_allow_html=True)
    breakdown_mode = st.radio(
        "View mode",
        ["Recurring vs Non-Recurring", "Full Product Breakdown"],
        horizontal=True,
        key="region_breakdown_mode",
    )

    if breakdown_mode == "Recurring vs Non-Recurring":
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
                name="Recurring", x=reg_prod_pivot["Mega_Region"],
                y=reg_prod_pivot["Recurring"] / 1e6, marker_color=UBER_GREEN,
                text=[f"${v:.1f}M" for v in reg_prod_pivot["Recurring"] / 1e6],
                textposition="inside",
            ))
        if "Non-Recurring" in reg_prod_pivot.columns:
            fig_mix.add_trace(go.Bar(
                name="Non-Recurring", x=reg_prod_pivot["Mega_Region"],
                y=reg_prod_pivot["Non-Recurring"] / 1e6, marker_color=UBER_ACCENT,
                text=[f"${v:.1f}M" for v in reg_prod_pivot["Non-Recurring"] / 1e6],
                textposition="inside",
            ))
        fig_mix.update_layout(
            barmode="stack",
            title="Recurring vs Non-Recurring GB by Region ($M)",
            height=380, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            yaxis=dict(gridcolor="#f0f0f0", title="Total GB ($M)"),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_mix, use_container_width=True)

    else:  # Full Product Breakdown
        reg_prod_full = aq_filt.groupby(["Mega_Region", "Product_Label"])["Total_GB"].sum().reset_index()
        product_color_map = {
            "Travel":        "#06C167",
            "Eats":          "#2ECC71",
            "Central":       "#27AE60",
            "Gift Card":     "#276EF1",
            "Eats Vouchers": "#5B9BF5",
            "Vouchers":      "#9B59B6",
        }
        fig_full = px.bar(
            reg_prod_full, x="Mega_Region", y="Total_GB", color="Product_Label",
            color_discrete_map=product_color_map,
            title="Full Product Breakdown by Mega Region ($)",
            labels={"Total_GB": "Total GB (USD)", "Mega_Region": "", "Product_Label": "Product"},
            text_auto=False,
        )
        fig_full.update_layout(
            barmode="stack", height=420, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            yaxis=dict(gridcolor="#f0f0f0", title="Total GB (USD)"),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_full, use_container_width=True)

    # Monthly product trend
    st.markdown("<div class='section-header'>Product Revenue Trend (Monthly)</div>", unsafe_allow_html=True)
    monthly_prod = aq_filt.groupby(["Month", "Product_Label"])["Total_GB"].sum().reset_index()
    fig_trend = px.line(
        monthly_prod, x="Month", y="Total_GB", color="Product_Label",
        markers=True, title="Monthly GB by Product",
        labels={"Total_GB": "Total GB (USD)", "Month": ""},
    )
    fig_trend.update_layout(
        height=360, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        yaxis=dict(gridcolor="#f0f0f0"),
        xaxis=dict(tickangle=-45), legend_title="Product",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Incentive recommendations
    rec_nb     = type_agg[type_agg["Product_Type"] == "Recurring"]["NB_GB"].sum()     if len(type_agg) > 0 else 0
    non_rec_nb = type_agg[type_agg["Product_Type"] == "Non-Recurring"]["NB_GB"].sum() if len(type_agg) > 0 else 0
    rec_pct    = rec_nb / max(rec_nb + non_rec_nb, 1) * 100

    st.markdown("<div class='section-header'>Incentive Design Recommendations</div>", unsafe_allow_html=True)
    c1p, c2p, c3p = st.columns(3)
    with c1p:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🔁 Recurring First</div>
          <div class='insight-text'>
            Recurring products represent <b>{rec_pct:.0f}%</b> of NB GB but generate
            compounding CO value. Boost recurring quota weight to <b>60–70%</b>
            and apply a <b>1.3× multiplier</b> on recurring deals.
          </div>
        </div>""", unsafe_allow_html=True)
    with c2p:
        st.markdown("""
        <div class='warning-box'>
          <div class='insight-title'>🎁 Non-Recurring Risk</div>
          <div class='insight-text'>
            Gift Cards and Vouchers inflate NB attainment without generating reliable CO.
            Cap non-recurring credit at <b>30% of NB quota</b> or apply a
            <b>0.7× discount factor</b> in attainment calculations.
          </div>
        </div>""", unsafe_allow_html=True)
    with c3p:
        st.markdown("""
        <div class='insight-box'>
          <div class='insight-title'>📈 CO Health Bonus</div>
          <div class='insight-text'>
            CO attainment reflects prior-half deal quality. AEs whose H1 deals generate
            ≥80% expected CO in H2 earn a <b>5–10% base bonus</b>.
            This rewards sustainable deal structuring.
          </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 · SALES STRATEGY TRADEOFFS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div class='section-header'>Sales Strategy Tradeoffs</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Should high-cost AEs focus on smaller, non-recurring deals? Can those lead to larger opportunities?</div>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([1, 1])

    with col_s1:
        # FIX #11 — Deal size histogram: manually bin log10 values → no blank chart
        deal_size = aq_filt.groupby("Unique Dashboard ID").agg(
            NB_GB=("NB_GB", "sum"),
            Product_Type=("Product_Type", "first"),
        ).reset_index()
        deal_size = deal_size[deal_size["NB_GB"] > 0].copy()

        # Pre-compute log10 and bin manually
        deal_size["log_nb"] = np.log10(deal_size["NB_GB"])
        bins = np.linspace(0, 7, 36)
        bin_labels = [f"${10**b:,.0f}" for b in (bins[:-1] + bins[1:]) / 2]

        def make_hist_trace(df_sub, name, color):
            counts, _ = np.histogram(df_sub["log_nb"], bins=bins)
            return go.Bar(
                x=[(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)],
                y=counts,
                name=name,
                marker_color=color,
                opacity=0.8,
            )

        fig_ds = go.Figure()
        for ptype, color in [("Recurring", UBER_GREEN), ("Non-Recurring", UBER_ACCENT)]:
            sub = deal_size[deal_size["Product_Type"] == ptype]
            if len(sub) > 0:
                fig_ds.add_trace(make_hist_trace(sub, ptype, color))

        tick_vals = [0, 1, 2, 3, 4, 5, 6]
        tick_text = ["$1", "$10", "$100", "$1K", "$10K", "$100K", "$1M"]
        fig_ds.update_layout(
            barmode="stack",
            title="Deal Size Distribution (NB GB, Log Scale)",
            xaxis=dict(
                tickvals=tick_vals, ticktext=tick_text,
                title="NB GB per Deal (USD)", gridcolor="#f0f0f0",
            ),
            yaxis=dict(title="# Deals", gridcolor="#f0f0f0"),
            height=380, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            legend_title="Product Type",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_ds, use_container_width=True)

    with col_s2:
        # FIX #12 — Increase height so all products fit
        avg_deal = aq_filt[aq_filt["NB_GB"] > 0].groupby("Product_Label")["NB_GB"].agg(["mean", "median", "count"]).reset_index()
        avg_deal.columns = ["Product", "Mean Deal ($)", "Median Deal ($)", "# Deals"]
        avg_deal = avg_deal.sort_values("Mean Deal ($)", ascending=True)

        fig_avg = go.Figure()
        fig_avg.add_trace(go.Bar(
            y=avg_deal["Product"], x=avg_deal["Mean Deal ($)"],
            name="Mean", orientation="h", marker_color=UBER_GREEN,
            text=[f"${v:,.0f}" for v in avg_deal["Mean Deal ($)"]],
            textposition="outside",
        ))
        fig_avg.add_trace(go.Bar(
            y=avg_deal["Product"], x=avg_deal["Median Deal ($)"],
            name="Median", orientation="h", marker_color=UBER_ACCENT,
            text=[f"${v:,.0f}" for v in avg_deal["Median Deal ($)"]],
            textposition="outside",
        ))
        fig_avg.update_layout(
            barmode="group",
            title="Mean vs Median Deal Size by Product",
            height=420,                          # ← FIX #12: was 360, now 420
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            xaxis=dict(gridcolor="#f0f0f0", title="NB GB (USD)"),
            yaxis=dict(tickfont=dict(size=12)),   # ← FIX #12: clear label sizing
            margin=dict(l=120, r=80, t=50, b=40),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_avg, use_container_width=True)

    # ── AE Efficiency Quadrant ────────────────────────────────────────────────
    st.markdown("<div class='section-header'>AE Productivity: Deals vs GB (Efficiency Quadrant)</div>", unsafe_allow_html=True)
    ae_prod = aq_filt.groupby("AE").agg(
        Deals=("Unique Dashboard ID", "nunique"), NB_GB=("NB_GB", "sum"),
    ).reset_index()
    ae_prod["GB_per_Deal"] = ae_prod["NB_GB"] / ae_prod["Deals"].replace(0, np.nan)
    ae_prod = ae_prod.merge(filt[["AE", "Mega_Region", "Channel", "Total_Attainment"]], on="AE", how="left")
    med_deals = ae_prod["Deals"].median()
    med_gb    = ae_prod["NB_GB"].median()

    def quadrant(row):
        h = row["Deals"] >= med_deals
        v = row["NB_GB"] >= med_gb
        if h and v:       return "High Volume + High GB (Stars)"
        elif not h and v: return "Low Volume + High GB (Whales)"
        elif h and not v: return "High Volume + Low GB (Grinders)"
        else:             return "Low Volume + Low GB (At Risk)"

    ae_prod["Quadrant"] = ae_prod.apply(quadrant, axis=1)
    quad_colors = {
        "High Volume + High GB (Stars)":   UBER_GREEN,
        "Low Volume + High GB (Whales)":   UBER_ACCENT,
        "High Volume + Low GB (Grinders)": "#F39C12",
        "Low Volume + Low GB (At Risk)":   "#E74C3C",
    }
    fig_quad = px.scatter(
        ae_prod, x="Deals", y="NB_GB", color="Quadrant",
        color_discrete_map=quad_colors, hover_name="AE",
        hover_data={"Channel": True, "Mega_Region": True, "GB_per_Deal": ":.0f"},
        title="AE Efficiency Quadrant (Deals vs NB GB)",
        labels={"Deals": "# Deals Closed", "NB_GB": "NB GB (USD)"},
    )
    fig_quad.add_vline(x=med_deals, line_dash="dot", line_color="#bbb",
                       annotation_text=f"Median: {med_deals:.0f} deals")
    fig_quad.add_hline(y=med_gb, line_dash="dot", line_color="#bbb",
                       annotation_text=f"Median: ${med_gb:,.0f}")
    fig_quad.update_layout(
        height=440, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", y=-0.15, title=""),
    )
    st.plotly_chart(fig_quad, use_container_width=True)

    # ── FIX #13 — Land-and-Expand Analysis + Data-Driven Verdict ─────────────
    st.markdown("<div class='section-header'>🔍 Land-and-Expand Analysis: Does Non-Recurring Lead to Recurring?</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Do accounts that start with Gift Cards / Vouchers eventually adopt Travel, Eats, or Central programs?</div>", unsafe_allow_html=True)

    # Account-level analysis
    acct_products = aq_filt.groupby("Salesforce Account ID")["Product_Type"].apply(set).reset_index()
    acct_products["Has_Recurring"]    = acct_products["Product_Type"].apply(lambda x: "Recurring" in x)
    acct_products["Has_NonRecurring"] = acct_products["Product_Type"].apply(lambda x: "Non-Recurring" in x)

    n_both    = (acct_products["Has_Recurring"] & acct_products["Has_NonRecurring"]).sum()
    n_nr_only = (acct_products["Has_NonRecurring"] & ~acct_products["Has_Recurring"]).sum()
    n_r_only  = (acct_products["Has_Recurring"] & ~acct_products["Has_NonRecurring"]).sum()
    total_accts = len(acct_products)

    # Chronological: accounts whose FIRST deal was Non-Recurring → did they ever get Recurring?
    aq_sorted = aq_filt.sort_values("Close Date")
    first_type_per_acct = aq_sorted.groupby("Salesforce Account ID")["Product_Type"].first().reset_index()
    first_type_per_acct.columns = ["Salesforce Account ID", "First_Product_Type"]
    all_types_per_acct  = aq_filt.groupby("Salesforce Account ID")["Product_Type"].apply(set).reset_index()
    all_types_per_acct.columns = ["Salesforce Account ID", "All_Types"]
    conv_df = first_type_per_acct.merge(all_types_per_acct, on="Salesforce Account ID")
    nr_starters = conv_df[conv_df["First_Product_Type"] == "Non-Recurring"]
    pct_converted = (nr_starters["All_Types"].apply(lambda x: "Recurring" in x)).mean() if len(nr_starters) > 0 else 0
    n_converted   = int((nr_starters["All_Types"].apply(lambda x: "Recurring" in x)).sum())

    # Per-AE conversion rate
    ae_conv = aq_filt.groupby("AE").apply(
        lambda df: pd.Series({
            "NR_Accounts": df[df["Product_Type"] == "Non-Recurring"]["Salesforce Account ID"].nunique(),
            "Both_Accounts": df.groupby("Salesforce Account ID")["Product_Type"].apply(
                lambda x: len(set(x)) == 2
            ).sum(),
        })
    ).reset_index()
    ae_conv["Conversion_Rate"] = ae_conv["Both_Accounts"] / ae_conv["NR_Accounts"].replace(0, np.nan)
    ae_conv = ae_conv.dropna(subset=["Conversion_Rate"]).sort_values("Conversion_Rate", ascending=False)

    lae_col1, lae_col2 = st.columns([1, 1])

    with lae_col1:
        # Sankey / Funnel: account portfolio breakdown
        funnel_labels = [
            "All Accounts",
            "Started Non-Recurring",
            f"Converted to Recurring ({pct_converted:.0%})",
            f"Stayed Non-Recurring Only ({1-pct_converted:.0%})",
        ]
        funnel_values = [
            total_accts,
            len(nr_starters),
            n_converted,
            len(nr_starters) - n_converted,
        ]
        funnel_colors = [UBER_ACCENT, "#F39C12", UBER_GREEN, "#E74C3C"]

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels,
            x=funnel_values,
            textinfo="value+percent initial",
            marker=dict(color=funnel_colors),
        ))
        fig_funnel.update_layout(
            title="Account Land-and-Expand Conversion Funnel",
            height=360, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with lae_col2:
        # Account portfolio pie
        fig_acct_pie = go.Figure(go.Pie(
            labels=["Non-Recurring Only", "Both Types (Converted)", "Recurring Only"],
            values=[n_nr_only, n_both, n_r_only],
            hole=0.5,
            marker_colors=["#E74C3C", UBER_GREEN, UBER_ACCENT],
            textinfo="percent+label",
            textfont_size=10,
        ))
        fig_acct_pie.update_layout(
            title="Account Portfolio: Product Type Mix",
            height=360, paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            showlegend=False,
            annotations=[dict(text=f"<b>{total_accts:,}</b><br>Accounts", x=0.5, y=0.5,
                              font_size=12, showarrow=False)],
        )
        st.plotly_chart(fig_acct_pie, use_container_width=True)

    # AE conversion rate bar chart
    st.markdown("<div class='section-header'>Per-AE Conversion Rate: Non-Recurring Accounts → Also Got Recurring</div>", unsafe_allow_html=True)
    top_converters = ae_conv[ae_conv["NR_Accounts"] >= 3].head(20)  # AEs with meaningful NR base
    if len(top_converters) > 0:
        top_converters = top_converters.merge(
            filt[["AE", "Mega_Region", "Channel"]].drop_duplicates(), on="AE", how="left"
        )
        fig_ae_conv = px.bar(
            top_converters.sort_values("Conversion_Rate", ascending=True),
            y="AE", x="Conversion_Rate",
            color="Mega_Region", color_discrete_map=REGION_COLORS,
            orientation="h",
            title="Top 20 AEs by Land-and-Expand Conversion Rate (min 3 NR accounts)",
            labels={"Conversion_Rate": "Conversion Rate", "AE": ""},
            text=[f"{v:.0%}" for v in top_converters.sort_values("Conversion_Rate", ascending=True)["Conversion_Rate"]],
        )
        fig_ae_conv.add_vline(x=pct_converted, line_dash="dot", line_color="black",
                              annotation_text=f"Avg: {pct_converted:.0%}")
        fig_ae_conv.update_layout(
            height=500, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            xaxis=dict(gridcolor="#f0f0f0", tickformat=".0%"),
            legend_title="Region",
        )
        st.plotly_chart(fig_ae_conv, use_container_width=True)

    # ── DATA-DRIVEN VERDICT ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📋 Verdict: Does the Land-and-Expand Strategy Work?</div>", unsafe_allow_html=True)

    verdict_col1, verdict_col2 = st.columns([1.2, 1])
    with verdict_col1:
        st.markdown(f"""
        <div class='verdict-no'>
          <div class='insight-title'>❌ Verdict: The Strategy Has Limited Effectiveness</div>
          <div class='insight-text' style='line-height:1.9'>
            <b>Only {pct_converted:.1%}</b> of accounts that started with Non-Recurring products
            (Gift Cards / Vouchers) went on to adopt a Recurring product (Travel, Eats, Central).<br><br>
            Of the <b>{len(nr_starters):,}</b> accounts that entered via Non-Recurring,
            only <b>{n_converted:,}</b> converted — meaning <b>{len(nr_starters)-n_converted:,}
            ({(1-pct_converted):.0%})</b> remained transactional with no upgrade path.<br><br>
            The data suggests Non-Recurring deals are primarily <b>one-off transactions</b>,
            not a reliable top-of-funnel for Recurring program adoption.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with verdict_col2:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>💡 What to Do Instead</div>
          <div class='insight-text' style='line-height:1.9'>
            <b>1. Segment the {n_converted:,} converted accounts</b> — identify what made them convert
            (deal size, use case, AE) and build an ideal customer profile for expansion.<br><br>
            <b>2. Redirect AE focus</b> — AEs spending >50% of deals on Non-Recurring
            are unlikely to build sustainable CO. Set a <b>max 30% non-recurring cap</b>.<br><br>
            <b>3. Structured follow-up</b> — for accounts with ≥2 non-recurring deals,
            trigger an automatic AE outreach to propose a Recurring program at the 60-day mark.<br><br>
            <b>4. Track conversion KPI</b> — make NR→Recurring conversion rate a quarterly
            Sales Ops metric reported to VP level.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Quadrant insight cards
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
            <b>{grind}</b> "Grinder" AEs are chasing high deal volume at low GB per deal.
            These AEs over-index on Non-Recurring and should be redirected to fewer, larger
            Recurring deals — one Travel deal can outperform 10 voucher deals in lifetime value.
          </div>
        </div>""", unsafe_allow_html=True)
    with c2s:
        st.markdown(f"""
        <div class='insight-box'>
          <div class='insight-title'>🐋 Whale Strategy</div>
          <div class='insight-text'>
            <b>{whales}</b> "Whale" AEs deliver large GB from few deals — high ROI but concentration risk.
            Pair each Whale with a targeted expansion plan for their top accounts.
            Non-recurring can still open doors, but only <b>{pct_converted:.0%}</b> of such accounts
            actually progress to Recurring — confirm intent before over-investing.
          </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 · SCALABILITY & AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("<div class='section-header'>Scalability & Automation Roadmap</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>How to automate and scale this analysis end-to-end</div>", unsafe_allow_html=True)

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
        Slack / Email Digest → Sales Directors &amp; VP (Weekly automated)
      </div>
    </div>
    """, unsafe_allow_html=True)

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
        </div>""", unsafe_allow_html=True)
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
        </div>""", unsafe_allow_html=True)
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
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header' style='margin-top:1.5rem'>Current Pipeline Metrics (Automatable KPIs)</div>", unsafe_allow_html=True)
    auto_col1, auto_col2 = st.columns([1.5, 1])

    with auto_col1:
        monthly_gb = aq_filt.groupby("Month").agg(
            NB_GB=("NB_GB", "sum"), CO_GB=("CO_GB", "sum"),
            Deals=("Unique Dashboard ID", "nunique"),
        ).reset_index()
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(x=monthly_gb["Month"], y=monthly_gb["NB_GB"], name="NB GB", marker_color=UBER_GREEN))
        fig_monthly.add_trace(go.Bar(x=monthly_gb["Month"], y=monthly_gb["CO_GB"], name="CO GB", marker_color=UBER_ACCENT))
        fig_monthly.add_trace(go.Scatter(
            x=monthly_gb["Month"], y=monthly_gb["Deals"], name="# Deals", yaxis="y2",
            line=dict(color="#FF6B35", width=2.5), marker=dict(size=6),
        ))
        fig_monthly.update_layout(
            barmode="stack", title="Monthly NB + CO GB with Deal Volume Trend",
            height=380, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            yaxis=dict(gridcolor="#f0f0f0", title="GB (USD)"),
            yaxis2=dict(title="# Deals", overlaying="y", side="right", showgrid=False),
            xaxis=dict(tickangle=-45), legend=dict(orientation="h", y=1.1),
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
            <b>NLP Query:</b> "What is US&Can NB attainment vs last half?"
          </div>
        </div>
        <div class='warning-box'>
          <div class='insight-title'>📋 Data Quality Requirements</div>
          <div class='insight-text' style='line-height:1.9'>
            276 rows missing Mega Region → fix at Salesforce entry level<br>
            Ramp status inconsistency → governed picklist<br>
            Weekly automated data quality alert to Sales Ops
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Recommended Tech Stack</div>", unsafe_allow_html=True)
    tech_df = pd.DataFrame({
        "Layer": ["Source","Ingestion","Storage","Transformation","Visualization","AI/ML","Orchestration","Alerting"],
        "Tool": ["Salesforce CRM","Fivetran / Airbyte","Snowflake","dbt Core","Streamlit / Looker",
                 "Python (scikit-learn, XGBoost)","Airflow / Prefect","Slack API / PagerDuty"],
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
        "Priority": ["Now","Now","Now","Now","Now","Phase 2","Phase 2","Phase 2"],
    })
    st.dataframe(tech_df, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='dashboard-footer'>
  Uber for Business · Sales Operations · H2 2021 Performance Analysis ·
  Built with Streamlit + Plotly · Data: Salesforce Attainment Export
</div>
""", unsafe_allow_html=True)
