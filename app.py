import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Pipeline Intelligence | Bose Abubakre",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #F7F8FA; }
  [data-testid="stSidebar"] { background: #032D60; }
  [data-testid="stSidebar"] * { color: #FFFFFF !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label { color: #A8C5E8 !important; font-size:12px; letter-spacing:0.05em; text-transform:uppercase; }
  .metric-card {
    background: white; border-radius: 10px; padding: 18px 20px;
    border-left: 4px solid #00A1E0; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  .metric-val { font-size: 28px; font-weight: 700; color: #032D60; line-height:1; margin-bottom:4px; }
  .metric-lbl { font-size: 12px; color: #6B7280; letter-spacing:0.04em; text-transform:uppercase; }
  .metric-delta { font-size: 12px; font-weight:600; margin-top:4px; }
  .delta-up { color: #16A34A; }
  .delta-down { color: #DC2626; }
  .section-header { font-size:14px; font-weight:700; color:#032D60; letter-spacing:0.06em; text-transform:uppercase; margin:8px 0 12px; border-bottom:2px solid #00A1E0; padding-bottom:6px; }
  .insight-box { background:#E6F5FB; border-left:3px solid #00A1E0; border-radius:4px; padding:10px 14px; margin:8px 0; font-size:13px; color:#032D60; }
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Synthetic Data Generation ─────────────────────────────────────────────────
@st.cache_data
def generate_data():
    random.seed(42)
    np.random.seed(42)

    reps = ["Jordan M.", "Taylor R.", "Priya S.", "Marcus L.", "Aisha K.", "Devon C.", "Mei W.", "Carlos B."]
    products = ["Sales Cloud", "Service Cloud", "Marketing Cloud", "Commerce Cloud", "Platform"]
    regions = ["West", "East", "Central", "South"]
    stages = ["Prospecting", "Qualification", "Needs Analysis", "Value Proposition", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    stage_order = {s: i for i, s in enumerate(stages)}
    win_probs = {"Prospecting": 0.08, "Qualification": 0.18, "Needs Analysis": 0.28,
                 "Value Proposition": 0.42, "Proposal": 0.58, "Negotiation": 0.75,
                 "Closed Won": 1.0, "Closed Lost": 0.0}

    rows = []
    base = datetime(2026, 1, 1)
    for i in range(320):
        stage = random.choices(stages, weights=[30,25,20,15,20,15,45,35])[0]
        rep = random.choice(reps)
        product = random.choices(products, weights=[35,25,15,10,15])[0]
        region = random.choice(regions)
        amount = int(np.random.lognormal(10.8, 0.6))
        amount = max(10000, min(500000, amount))
        create_date = base + timedelta(days=random.randint(0, 270))
        close_date = create_date + timedelta(days=random.randint(14, 180))
        cycle_days = (close_date - create_date).days
        quarter = f"Q{(create_date.month - 1) // 3 + 1} 2026"
        rows.append({
            "opp_id": f"OPP-{1000+i}",
            "rep": rep,
            "product": product,
            "region": region,
            "stage": stage,
            "stage_order": stage_order[stage],
            "amount": amount,
            "win_prob": win_probs[stage],
            "weighted_amount": amount * win_probs[stage],
            "create_date": create_date,
            "close_date": close_date,
            "cycle_days": cycle_days,
            "quarter": quarter,
        })

    df = pd.DataFrame(rows)

    # Monthly actuals vs forecast
    months = pd.date_range("2026-01-01", periods=10, freq="MS")
    monthly = []
    for i, m in enumerate(months):
        actual = int(np.random.normal(1_200_000 + i * 80_000, 150_000))
        forecast = int(actual * np.random.uniform(0.88, 1.12))
        monthly.append({"month": m, "actual": max(0, actual), "forecast": max(0, forecast)})
    monthly_df = pd.DataFrame(monthly)

    return df, monthly_df

df, monthly_df = generate_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔵 Sales Intelligence")
    st.markdown("**Powered by Bose Abubakre**")
    st.markdown("---")

    quarter_opts = ["All"] + sorted(df["quarter"].unique().tolist())
    sel_quarter = st.selectbox("Quarter", quarter_opts)

    region_opts = ["All"] + sorted(df["region"].unique().tolist())
    sel_region = st.selectbox("Region", region_opts)

    product_opts = ["All"] + sorted(df["product"].unique().tolist())
    sel_product = st.selectbox("Product", product_opts)

    rep_opts = ["All"] + sorted(df["rep"].unique().tolist())
    sel_rep = st.selectbox("Sales Rep", rep_opts)

    st.markdown("---")
    st.markdown("**About this dashboard**")
    st.markdown("Built to demonstrate sales analytics capabilities for Salesforce Sales Strategy team. Data is synthetic.")
    st.markdown("📧 bosedeabuba@gmail.com")
    st.markdown("🔗 [GitHub](https://github.com/bosede-coder)")

# ── Filter data ───────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_quarter != "All": fdf = fdf[fdf["quarter"] == sel_quarter]
if sel_region != "All": fdf = fdf[fdf["region"] == sel_region]
if sel_product != "All": fdf = fdf[fdf["product"] == sel_product]
if sel_rep != "All": fdf = fdf[fdf["rep"] == sel_rep]

won = fdf[fdf["stage"] == "Closed Won"]
lost = fdf[fdf["stage"] == "Closed Lost"]
open_opps = fdf[~fdf["stage"].isin(["Closed Won", "Closed Lost"])]
total_pipeline = open_opps["amount"].sum()
won_revenue = won["amount"].sum()
win_rate = len(won) / max(1, len(won) + len(lost)) * 100
avg_cycle = won["cycle_days"].mean() if len(won) > 0 else 0
weighted_pipeline = open_opps["weighted_amount"].sum()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Sales Pipeline Intelligence Dashboard")
st.markdown("*Real-time visibility into pipeline health, rep performance, and revenue forecasting*")
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val">${won_revenue/1e6:.1f}M</div>
        <div class="metric-lbl">Closed Won Revenue</div>
        <div class="metric-delta delta-up">↑ 18% vs prior period</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card" style="border-left-color:#7B61FF;">
        <div class="metric-val">${total_pipeline/1e6:.1f}M</div>
        <div class="metric-lbl">Open Pipeline</div>
        <div class="metric-delta delta-up">↑ {len(open_opps)} opportunities</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card" style="border-left-color:#16A34A;">
        <div class="metric-val">{win_rate:.0f}%</div>
        <div class="metric-lbl">Win Rate</div>
        <div class="metric-delta delta-up">↑ 3pts vs target</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card" style="border-left-color:#F59E0B;">
        <div class="metric-val">${weighted_pipeline/1e6:.1f}M</div>
        <div class="metric-lbl">Weighted Forecast</div>
        <div class="metric-delta delta-up">Prob-adjusted pipeline</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="metric-card" style="border-left-color:#EF4444;">
        <div class="metric-val">{avg_cycle:.0f}d</div>
        <div class="metric-lbl">Avg Sales Cycle</div>
        <div class="metric-delta delta-down">↓ 8d improvement</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Funnel + Forecast ──────────────────────────────────────────────────
col1, col2 = st.columns([1, 1.6])

with col1:
    st.markdown('<div class="section-header">Pipeline Funnel by Stage</div>', unsafe_allow_html=True)
    funnel_stages = ["Prospecting", "Qualification", "Needs Analysis", "Value Proposition", "Proposal", "Negotiation"]
    funnel_data = []
    for s in funnel_stages:
        cnt = len(fdf[fdf["stage"] == s])
        amt = fdf[fdf["stage"] == s]["amount"].sum()
        funnel_data.append({"Stage": s, "Count": cnt, "Amount": amt})
    fdf_funnel = pd.DataFrame(funnel_data)

    fig_funnel = go.Figure(go.Funnel(
        y=fdf_funnel["Stage"],
        x=fdf_funnel["Count"],
        textinfo="value+percent initial",
        marker=dict(color=["#032D60","#0B5FAB","#00A1E0","#4CC9F0","#7B61FF","#A78BFA"]),
        connector=dict(line=dict(color="#E5E7EB", width=1)),
    ))
    fig_funnel.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12),
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Revenue: Actual vs Forecast (2026)</div>', unsafe_allow_html=True)
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Bar(
        x=monthly_df["month"].dt.strftime("%b"),
        y=monthly_df["forecast"],
        name="Forecast",
        marker_color="#E5E7EB",
        width=0.4,
    ))
    fig_forecast.add_trace(go.Bar(
        x=monthly_df["month"].dt.strftime("%b"),
        y=monthly_df["actual"],
        name="Actual",
        marker_color="#00A1E0",
        width=0.4,
    ))
    fig_forecast.add_trace(go.Scatter(
        x=monthly_df["month"].dt.strftime("%b"),
        y=monthly_df["actual"].rolling(3, min_periods=1).mean(),
        name="3-Month Trend",
        line=dict(color="#032D60", width=2.5, dash="dot"),
        mode="lines",
    ))
    fig_forecast.update_layout(
        barmode="overlay",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", size=12),
        yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#F3F4F6"),
        xaxis=dict(gridcolor="#F3F4F6"),
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

# ── Row 2: Rep performance + Product mix ─────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-header">Rep Performance: Win Rate vs Revenue</div>', unsafe_allow_html=True)
    rep_won = df[df["stage"]=="Closed Won"].groupby("rep").agg(revenue=("amount","sum"), won=("opp_id","count")).reset_index()
    rep_total = df[df["stage"].isin(["Closed Won","Closed Lost"])].groupby("rep").agg(total=("opp_id","count")).reset_index()
    rep_perf = rep_won.merge(rep_total, on="rep")
    rep_perf["win_rate"] = rep_perf["won"] / rep_perf["total"] * 100
    rep_perf["avg_deal"] = rep_perf["revenue"] / rep_perf["won"]

    fig_rep = px.scatter(
        rep_perf, x="win_rate", y="revenue", size="avg_deal", text="rep",
        color="win_rate",
        color_continuous_scale=["#E0F2FE","#00A1E0","#032D60"],
        labels={"win_rate": "Win Rate (%)", "revenue": "Total Revenue Won"},
    )
    fig_rep.update_traces(textposition="top center", textfont_size=10)
    fig_rep.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        paper_bgcolor="white", plot_bgcolor="white",
        coloraxis_showscale=False,
        yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#F3F4F6"),
        xaxis=dict(gridcolor="#F3F4F6"),
        font=dict(family="Inter, sans-serif", size=11),
    )
    st.plotly_chart(fig_rep, use_container_width=True)

with col4:
    st.markdown('<div class="section-header">Pipeline by Product & Stage</div>', unsafe_allow_html=True)
    prod_stage = fdf[~fdf["stage"].isin(["Closed Won","Closed Lost"])].groupby(["product","stage"])["amount"].sum().reset_index()
    fig_prod = px.bar(
        prod_stage, x="product", y="amount", color="stage",
        color_discrete_sequence=["#032D60","#0B5FAB","#00A1E0","#4CC9F0","#7B61FF","#A78BFA"],
        labels={"amount": "Pipeline Value", "product": "Product"},
    )
    fig_prod.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#F3F4F6"),
        xaxis=dict(gridcolor="#F3F4F6"),
        font=dict(family="Inter, sans-serif", size=11),
        barmode="stack",
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# ── Row 3: Cycle time + Regional heatmap ─────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-header">Sales Cycle Time by Product</div>', unsafe_allow_html=True)
    cycle_data = df[df["stage"]=="Closed Won"].groupby("product")["cycle_days"].agg(["mean","median","std"]).reset_index()
    cycle_data.columns = ["product","mean","median","std"]
    cycle_data = cycle_data.sort_values("mean", ascending=True)
    fig_cycle = go.Figure()
    fig_cycle.add_trace(go.Bar(
        y=cycle_data["product"], x=cycle_data["mean"],
        orientation="h", name="Avg Days",
        marker_color="#00A1E0",
        error_x=dict(type="data", array=cycle_data["std"], color="#9CA3AF", thickness=1.5),
    ))
    fig_cycle.add_trace(go.Scatter(
        y=cycle_data["product"], x=cycle_data["median"],
        mode="markers", name="Median",
        marker=dict(color="#032D60", size=8, symbol="diamond"),
    ))
    fig_cycle.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=280,
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(title="Days", gridcolor="#F3F4F6"),
        font=dict(family="Inter, sans-serif", size=11),
    )
    st.plotly_chart(fig_cycle, use_container_width=True)

with col6:
    st.markdown('<div class="section-header">Win Rate by Region & Product</div>', unsafe_allow_html=True)
    heat = df[df["stage"].isin(["Closed Won","Closed Lost"])].copy()
    heat["won_flag"] = (heat["stage"] == "Closed Won").astype(int)
    pivot = heat.groupby(["region","product"])["won_flag"].mean().unstack().fillna(0) * 100
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=["#E0F2FE","#00A1E0","#032D60"],
        labels=dict(color="Win Rate %"),
        text_auto=".0f",
    )
    fig_heat.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=280,
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=11),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🤖 AI-Generated Pipeline Insights</div>', unsafe_allow_html=True)
top_rep = df[df["stage"]=="Closed Won"].groupby("rep")["amount"].sum().idxmax()
top_product = df[df["stage"]=="Closed Won"].groupby("product")["amount"].sum().idxmax()
stalled = open_opps[open_opps["cycle_days"] > 90]

ins1, ins2, ins3 = st.columns(3)
with ins1:
    st.markdown(f'<div class="insight-box">🏆 <strong>Top Performer:</strong> {top_rep} leads in closed revenue. Consider pairing with reps in Negotiation-stage deals to accelerate close.</div>', unsafe_allow_html=True)
with ins2:
    st.markdown(f'<div class="insight-box">📦 <strong>{top_product}</strong> drives the most closed revenue. Pipeline coverage in Proposal stage is strong — prioritize moving to Negotiation.</div>', unsafe_allow_html=True)
with ins3:
    st.markdown(f'<div class="insight-box">⚠️ <strong>{len(stalled)} opportunities</strong> have been open 90+ days without closing. Review and qualify out or escalate to accelerate.</div>', unsafe_allow_html=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
with st.expander("🔍 View Raw Pipeline Data"):
    display_cols = ["opp_id","rep","product","region","stage","amount","win_prob","weighted_amount","cycle_days","quarter"]
    st.dataframe(
        fdf[display_cols].sort_values("amount", ascending=False),
        use_container_width=True,
        height=300,
    )

st.markdown("---")
st.markdown("*Built by [Bose Abubakre](https://github.com/bosede-coder) · PhD Geology · MBA · AI Product Owner · Data is synthetic and for demonstration purposes.*")
