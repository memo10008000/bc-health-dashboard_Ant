import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="BC Health Authority Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for the high-fidelity header and pills
st.markdown("""
    <style>
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1E1E1E;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .header-subtitle {
        font-size: 1.1rem;
        color: #666666;
        font-style: italic;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    .alert-banner {
        background-color: #FFF0F0;
        border-left: 5px solid #FF4B4B;
        padding: 15px 20px;
        border-radius: 4px;
        margin-bottom: 30px;
    }
    .alert-title {
        color: #D32F2F;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .alert-content {
        color: #333333;
        font-size: 0.95rem;
    }
    
    /* Metrics Layout */
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 40px;
    }
    .metric-box {
        text-align: left;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #555555;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E1E1E;
        margin-bottom: 8px;
        line-height: 1.1;
    }
    .community-pill {
        display: inline-block;
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #C8E6C9;
    }
    hr {
        border-color: #E0E0E0;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Data Loaders
@st.cache_data
def load_data():
    return pd.read_csv("bc_health_indicators.csv")

@st.cache_data
def load_wait_times():
    return pd.read_csv("wait_times_mock.csv")

@st.cache_data
def load_opioids():
    return pd.read_csv("opioid_harms_mock.csv")

# Load all files safely
try:
    df_wait = load_wait_times()
    df_opioid = load_opioids()
except FileNotFoundError:
    st.error("Wait times or Opioid data files are missing.")
    st.stop()

# --- PRIMARY NAVIGATION ---
st.markdown("<style>div.row-widget.stRadio > div{flex-direction:row;} .stRadio label {font-size:1.1rem; font-weight:600;}</style>", unsafe_allow_html=True)
active_tab = st.radio(
    "Select View:", 
    ["🌎 Population Health Equity", "⏱️ BC Wait Times", "⚠️ Opioid Crisis"], 
    horizontal=True,
    label_visibility="collapsed"
)

# Sidebar
is_tab1 = (active_tab == "🌎 Population Health Equity")

st.sidebar.header("Data Source (Tab 1)")
uploaded_file = st.sidebar.file_uploader("Upload custom dataset (CSV)", type=['csv'], disabled=not is_tab1)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        st.stop()
else:
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("Data file not found. Please upload a CSV or ensure `bc_health_indicators.csv` is present in the directory.")
        st.stop()

st.sidebar.divider()
st.sidebar.header("Filters (Tab 1 Only)")
selected_ha = st.sidebar.selectbox("Select Health Authority", options=["All"] + list(df['health_authority'].unique()), disabled=not is_tab1)

if not is_tab1:
    st.sidebar.info("Filters and Dataset Uploads are only active on the Population Health Equity view.")

if selected_ha != "All":
    filtered_df = df[df['health_authority'] == selected_ha]
else:
    filtered_df = df

if filtered_df.empty:
    st.warning("No data available for the selected area.")
    st.stop()

# Pre-calculate Tab 1 Vulnerability for use in all tabs (specifically Tab 3 callout)
df_calc = filtered_df.copy()
max_doc = df_calc['pct_without_family_doctor'].max() or 1
max_opioid = df_calc['opioid_overdose_rate'].max() or 1
max_er = df_calc['er_visits_per_1000'].max() or 1
max_inc = df_calc['median_household_income'].max() or 1

df_calc['need_score'] = (
    (df_calc['pct_without_family_doctor'] / max_doc) * 1.5 +
    (df_calc['opioid_overdose_rate'] / max_opioid) * 2.0 +
    (df_calc['er_visits_per_1000'] / max_er) * 1.2 +
    (1.0 - (df_calc['median_household_income'] / max_inc)) * 1.0
)
df_calc['vulnerability_index'] = (df_calc['need_score'] / df_calc['need_score'].max()) * 100
top_community_global = df_calc.loc[df_calc['need_score'].idxmax()]

# ==========================================
# TAB 1: POPULATION HEALTH EQUITY
# ==========================================
if active_tab == "🌎 Population Health Equity":
    highest_er_comm = filtered_df.loc[filtered_df['er_visits_per_1000'].idxmax()]
    lowest_life_comm = filtered_df.loc[filtered_df['life_expectancy'].idxmin()]
    worst_gp_comm = filtered_df.loc[filtered_df['pct_without_family_doctor'].idxmax()]
    highest_opioid_comm = filtered_df.loc[filtered_df['opioid_overdose_rate'].idxmax()]

    display_area = selected_ha if selected_ha != "All" else "BC Provincial"
    num_chsas = len(filtered_df)
    
    np.random.seed(42)
    mock_pop = sum(np.random.randint(15000, 25000) for _ in range(num_chsas)) if 'population' not in filtered_df.columns else filtered_df['population'].sum()

    st.markdown(f"""
        <div class="header-title">{display_area} &bull; Population Health Equity Overview</div>
        <div class="header-subtitle">{num_chsas} Community Health Service Areas &bull; Population: {mock_pop:,}</div>
        <hr>
        
        <div class="alert-banner">
            <div class="alert-title">&#9888; HIGHEST PRIORITY COMMUNITY FLAGGED</div>
            <div class="alert-content">
                <strong>{top_community_global['chsa_name']}</strong> &mdash; Vulnerability Score: {top_community_global['vulnerability_index']:.1f}/100 
                &bull; {top_community_global['pct_without_family_doctor']:.1f}% without GP 
                &bull; Opioid rate: {top_community_global['opioid_overdose_rate']:.1f}/100k 
                &bull; Life expectancy: {top_community_global['life_expectancy']:.1f} yrs
            </div>
        </div>
        
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-title">Highest ER Pressure</div>
                <div class="metric-value">{highest_er_comm['er_visits_per_1000']:.0f}/1k</div>
                <div class="community-pill">&#8593; {highest_er_comm['chsa_name']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Lowest Life Expectancy</div>
                <div class="metric-value">{lowest_life_comm['life_expectancy']:.1f} yrs</div>
                <div class="community-pill">&#8593; {lowest_life_comm['chsa_name']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Worst GP Access Gap</div>
                <div class="metric-value">{worst_gp_comm['pct_without_family_doctor']:.1f}%</div>
                <div class="community-pill">&#8593; {worst_gp_comm['chsa_name']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Highest Opioid Rate</div>
                <div class="metric-value">{highest_opioid_comm['opioid_overdose_rate']:.1f}/100k</div>
                <div class="community-pill">&#8593; {highest_opioid_comm['chsa_name']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Access Gaps: % Without Family Doctor")
        bar_df = filtered_df.sort_values(by="pct_without_family_doctor", ascending=False).head(15)
        fig_bar = px.bar(
            bar_df, x="pct_without_family_doctor", y="chsa_name", orientation='h', 
            color="pct_without_family_doctor", color_continuous_scale="Reds",
            labels={"pct_without_family_doctor": "% Without", "chsa_name": "Community"}
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Wealth-Health Gap")
        fig_scatter = px.scatter(
            filtered_df, x="median_household_income", y="life_expectancy", color="health_authority",
            size="pct_without_family_doctor", hover_name="chsa_name",
            labels={"median_household_income": "Income ($)", "life_expectancy": "Life Expectancy"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_layout(margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Vulnerability Heatmap: Opioid Overdose Rates (Top 10)")
    top_10_opioid = filtered_df.sort_values(by="opioid_overdose_rate", ascending=False).head(10)
    fig_heat = go.Figure(data=go.Heatmap(
        z=[top_10_opioid['opioid_overdose_rate']], x=top_10_opioid['chsa_name'], y=["Opioid Overdose Rate (per 100k)"],
        colorscale='YlGnBu', text=[[f"{val:.1f}" for val in top_10_opioid['opioid_overdose_rate']]],
        texttemplate="%{text}", hoverinfo="x+z"
    ))
    fig_heat.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title="Community (CHSA)", height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.subheader("🤖 AI Synthesis Engine: Executive Briefing")
    briefing = f"Based on a multi-factorial algorithmic analysis of the dataset, the community of **{top_community_global['chsa_name']}** is identified as the strict highest priority target for the next public health outreach clinic. This specific region exhibits a critical localized intersection of systemic vulnerabilities, suffering from a severe primary care access gap ({top_community_global['pct_without_family_doctor']:.1f}% without a GP) compounded by a massive opioid overdose rate ({top_community_global['opioid_overdose_rate']:.1f} per 100,000). Deploying rapid, targeted clinical resources to {top_community_global['chsa_name']} is currently mathematically optimized to alleviate both severe demographic mortality and immense structural emergency room pressure."
    st.info(briefing)

# ==========================================
# TAB 2: BC WAIT TIMES
# ==========================================
elif active_tab == "⏱️ BC Wait Times":
    st.markdown('<div class="header-title">BC Wait Times</div><hr>', unsafe_allow_html=True)
    selected_procedure = st.selectbox("Select Procedure", df_wait['procedure'].unique())
    
    cur_year = df_wait['year'].max()
    df_bc_curr = df_wait[(df_wait['province'] == 'BC') & (df_wait['procedure'] == selected_procedure) & (df_wait['year'] == cur_year)]
    df_bc_2014 = df_wait[(df_wait['province'] == 'BC') & (df_wait['procedure'] == selected_procedure) & (df_wait['year'] == 2014)]
    
    if not df_bc_curr.empty and not df_bc_2014.empty:
        curr_rec = df_bc_curr.iloc[0]
        rec_2014 = df_bc_2014.iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Median Wait (Days)", f"{curr_rec['median_wait_days']}", delta=f"{curr_rec['median_wait_days'] - rec_2014['median_wait_days']} vs 2014", delta_color="inverse")
        col2.metric("Benchmark Target", f"{curr_rec['benchmark_days']} days", delta=f"{curr_rec['benchmark_days'] - curr_rec['median_wait_days']} gap", delta_color="normal")
        col3.metric("% Within Benchmark", f"{curr_rec['pct_within_benchmark']}%", delta=f"{curr_rec['pct_within_benchmark'] - rec_2014['pct_within_benchmark']}% vs 2014")
        col4.metric("Total Volume", f"{curr_rec['volume']:,}", delta=f"{curr_rec['volume'] - rec_2014['volume']:,} vs 2014")
    
    # Trend line chart: BC vs Nat Avg vs Benchmark
    df_proc = df_wait[(df_wait['procedure'] == selected_procedure)]
    df_bc_trend = df_proc[df_proc['province'] == 'BC']
    
    # Calculate National Average (excluding BC for 'Other Prov Avg' or including for National)
    df_nat = df_proc.groupby('year')['median_wait_days'].mean().reset_index()
    
    fig_trend = go.Figure()
    # Faint lines for all other provinces
    for prov in df_proc['province'].unique():
        if prov != 'BC':
            df_p = df_proc[df_proc['province'] == prov]
            fig_trend.add_trace(go.Scatter(x=df_p['year'], y=df_p['median_wait_days'], mode='lines', line=dict(color='lightgrey', width=1), name='Other Provs', showlegend=False))
            
    # National Average
    fig_trend.add_trace(go.Scatter(x=df_nat['year'], y=df_nat['median_wait_days'], mode='lines', line=dict(color='orange', width=3, dash='dash'), name='National Avg'))
    
    # BC
    fig_trend.add_trace(go.Scatter(x=df_bc_trend['year'], y=df_bc_trend['median_wait_days'], mode='lines', line=dict(color='blue', width=4), name='British Columbia'))
    
    # Benchmark Red Line
    benchmark_value = df_bc_trend['benchmark_days'].max()
    fig_trend.add_hline(y=benchmark_value, line_dash="solid", line_color="red", annotation_text="Benchmark")
    
    fig_trend.update_layout(title="Median Wait Days Trend (2014-2025)", xaxis_title="Year", yaxis_title="Days", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

    # Horizontal Bar: All procedures for BC latest year vs Benchmark
    df_bc_all_curr = df_wait[(df_wait['province'] == 'BC') & (df_wait['year'] == cur_year)].copy()
    
    # Color logic: Red if wait > benchmark, Amber if within 10%, Green if safely within
    def get_color(row):
        if row['median_wait_days'] > row['benchmark_days']: return 'red'
        elif row['benchmark_days'] - row['median_wait_days'] <= 10: return 'orange'
        return 'green'
        
    df_bc_all_curr['Status'] = df_bc_all_curr.apply(get_color, axis=1)
    
    fig_bar2 = px.bar(df_bc_all_curr, x='median_wait_days', y='procedure', orientation='h', color='Status', 
                      color_discrete_map={'red':'red', 'orange':'orange', 'green':'green'},
                      title=f"BC Procedure Performance (Current Year {cur_year})")
    fig_bar2.add_vline(x=0, line_dash="solid", line_color="red") # visual line
    fig_bar2.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar2, use_container_width=True)

# ==========================================
# TAB 3: OPIOID CRISIS
# ==========================================
elif active_tab == "⚠️ Opioid Crisis":
    st.markdown('<div class="header-title">Opioid Crisis Tracking</div><hr>', unsafe_allow_html=True)
    
    # Filter BC data and calculate YoY
    df_opioid_bc = df_opioid[df_opioid['province'] == 'BC']
    df_bc_yearly = df_opioid_bc.groupby('year').sum(numeric_only=True).reset_index()
    # Correct the rate_per_100k column by taking average over Quarters instead of Summing
    df_bc_yearly['rate_per_100k_deaths'] = df_opioid_bc.groupby('year')['rate_per_100k_deaths'].mean().values
    
    cur_yr = df_bc_yearly['year'].max()
    prev_yr = cur_yr - 1
    
    curr_yr_data = df_bc_yearly[df_bc_yearly['year'] == cur_yr].iloc[0]
    prev_yr_data = df_bc_yearly[df_bc_yearly['year'] == prev_yr].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toxicity Deaths", f"{curr_yr_data['apparent_opioid_toxicity_deaths']:,.0f}", delta=f"{curr_yr_data['apparent_opioid_toxicity_deaths'] - prev_yr_data['apparent_opioid_toxicity_deaths']:,.0f} YoY", delta_color="inverse")
    col2.metric("Hospitalizations", f"{curr_yr_data['opioid_hospitalizations']:,.0f}", delta=f"{curr_yr_data['opioid_hospitalizations'] - prev_yr_data['opioid_hospitalizations']:,.0f} YoY", delta_color="inverse")
    col3.metric("ED Visits", f"{curr_yr_data['opioid_ed_visits']:,.0f}", delta=f"{curr_yr_data['opioid_ed_visits'] - prev_yr_data['opioid_ed_visits']:,.0f} YoY", delta_color="inverse")
    col4.metric("Death Rate (per 100k)", f"{curr_yr_data['rate_per_100k_deaths']:.1f}", delta=f"{curr_yr_data['rate_per_100k_deaths'] - prev_yr_data['rate_per_100k_deaths']:.1f} YoY", delta_color="inverse")
    
    # Custom Crisis Alert tied to Tab 1
    st.markdown(f"""
        <div class="alert-banner" style="background-color: #FFF0F0; border-left: 5px solid darkred;">
            <div class="alert-title" style="color: darkred;">&#9888; PROVINCIAL IMPACT ALERT </div>
            <div class="alert-content" style="color: #333;">
                The surging provincial toxicity death rate directly impacts <strong>{top_community_global['chsa_name']}</strong>, 
                which we identified in our Equity Analysis as highly vulnerable. Funneling harm-reduction resources to 
                {top_community_global['chsa_name']} will directly address this rising curve.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Quarterly Harm Trends")
    # Stacked bar + dual-axis line chart
    df_opioid_bc = df_opioid_bc.copy()
    df_opioid_bc['period'] = df_opioid_bc['year'].astype(str) + " " + df_opioid_bc['quarter']
    
    # Create figure with secondary y-axis
    from plotly.subplots import make_subplots
    fig_harms = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_harms.add_trace(go.Bar(x=df_opioid_bc['period'], y=df_opioid_bc['opioid_ed_visits'], name="ED Visits"), secondary_y=False)
    fig_harms.add_trace(go.Bar(x=df_opioid_bc['period'], y=df_opioid_bc['opioid_hospitalizations'], name="Hospitalizations"), secondary_y=False)
    
    fig_harms.add_trace(go.Scatter(x=df_opioid_bc['period'], y=df_opioid_bc['apparent_opioid_toxicity_deaths'], name="Toxicity Deaths", mode="lines+markers", line=dict(color="red", width=3)), secondary_y=True)
    
    fig_harms.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_harms.update_yaxes(title_text="Healthcare Encounters (Bar)", secondary_y=False)
    fig_harms.update_yaxes(title_text="Toxicity Deaths (Line)", secondary_y=True)
    
    st.plotly_chart(fig_harms, use_container_width=True)

    # Provincial comparison bar in latest quarter
    st.subheader("Inter-Provincial Comparison (Death Rate per 100k)")
    cur_year = df_opioid['year'].max()
    df_latest_prov = df_opioid[(df_opioid['year'] == cur_year)].groupby('province')['rate_per_100k_deaths'].mean().reset_index()
    
    df_latest_prov['color'] = df_latest_prov['province'].apply(lambda x: 'BC' if x == 'BC' else 'Other')
    fig_prov = px.bar(df_latest_prov, x="rate_per_100k_deaths", y="province", color="color", 
                      color_discrete_map={'BC': 'blue', 'Other': 'lightgrey'}, orientation='h')
    fig_prov.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_prov, use_container_width=True)
