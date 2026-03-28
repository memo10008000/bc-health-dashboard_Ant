import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 2.2 Configure page
st.set_page_config(page_title="BC Health Authority Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for high-contrast and professional look
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E1E1E;
        color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #FF4B4B;
    }
    .metric-card h4 {
        margin: 0;
        font-size: 1.1rem;
        color: #CCCCCC;
    }
    .metric-card p {
        margin: 10px 0;
        font-size: 1rem;
    }
    .metric-card .highlight {
        color: #FF4B4B;
        font-weight: bold;
    }
    .metric-card h2 {
        margin: 0;
        font-size: 2rem;
        color: #FFFFFF;
    }
    .metric-card small {
        font-size: 1rem;
        color: #AAAAAA;
    }
    </style>
""", unsafe_allow_html=True)

st.title("BC Health Authority Population Health Dashboard")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("bc_health_indicators.csv")

# 1. Sidebar Upload & Filter
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload custom dataset (CSV)", type=['csv'])

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
st.sidebar.header("Filters")
selected_ha = st.sidebar.selectbox("Select Health Authority", options=["All"] + list(df['health_authority'].unique()))

if selected_ha != "All":
    filtered_df = df[df['health_authority'] == selected_ha]
else:
    filtered_df = df

if filtered_df.empty:
    st.warning("No data available for the selected area.")
    st.stop()

# 5. Visual 4 (Metrics): Highlight CHSA with highest er_visits_per_1000
highest_er = filtered_df.loc[filtered_df['er_visits_per_1000'].idxmax()]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Communities Analysed", value=len(filtered_df))
with col2:
    st.metric(label="Avg Life Expectancy", value=f"{filtered_df['life_expectancy'].mean():.1f} yrs")
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>Critical Operational Pressure</h4>
        <p>Highest ER Visits: <span class="highlight">{highest_er['chsa_name']}</span></p>
        <h2>{highest_er['er_visits_per_1000']:.1f} <small>per 1,000</small></h2>
    </div>
    """, unsafe_allow_html=True)

st.divider()

col_left, col_right = st.columns(2)

# 2. Visual 1 (Bar Chart): pct_without_family_doctor
with col_left:
    st.subheader("Access Gaps: % Without Family Doctor")
    # Sort top 15 for readability
    bar_df = filtered_df.sort_values(by="pct_without_family_doctor", ascending=False).head(15)
    fig_bar = px.bar(
        bar_df, 
        x="pct_without_family_doctor", 
        y="chsa_name", 
        orientation='h', 
        color="pct_without_family_doctor",
        color_continuous_scale="Reds",
        labels={"pct_without_family_doctor": "% Without", "chsa_name": "Community"}
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_bar, use_container_width=True)

# 3. Visual 2 (Scatter Plot): Wealth-Health Gap
with col_right:
    st.subheader("Wealth-Health Gap")
    fig_scatter = px.scatter(
        filtered_df,
        x="median_household_income",
        y="life_expectancy",
        color="health_authority",
        size="pct_without_family_doctor",
        hover_name="chsa_name",
        labels={
            "median_household_income": "Median Household Income ($)",
            "life_expectancy": "Life Expectancy (Years)"
        },
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    # Ensure layout fits dark/clinical theme
    fig_scatter.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_scatter, use_container_width=True)

# 4. Visual 3: Heatmap of Opioid Overdose Rate Top 10 vulnerable
st.subheader("Vulnerability Heatmap: Opioid Overdose Rates (Top 10)")
top_10_opioid = filtered_df.sort_values(by="opioid_overdose_rate", ascending=False).head(10)

fig_heat = go.Figure(data=go.Heatmap(
    z=[top_10_opioid['opioid_overdose_rate']],
    x=top_10_opioid['chsa_name'],
    y=["Opioid Overdose Rate (per 100k)"],
    colorscale='Magma',
    text=[[f"{val:.1f}" for val in top_10_opioid['opioid_overdose_rate']]],
    texttemplate="%{text}",
    hoverinfo="x+z"
))
fig_heat.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis_title="Community (CHSA)",
    height=250
)
st.plotly_chart(fig_heat, use_container_width=True)

# 6. AI Feature: 'Synthesis Engine'
st.divider()
st.subheader("AI Synthesis Engine: Needs Assessment")

def executive_briefing(data_df):
    """
    Logic-based scoring system:
    Calculates vulnerability based on high overdose rates, low doctor access, high ER limits, and low income.
    """
    if data_df.empty: return "No data available to formulate a briefing."
    
    # Normalize inputs for relative comparison within the selected set
    df_calc = data_df.copy()
    
    # Avoid division by zero
    max_doc = df_calc['pct_without_family_doctor'].max() or 1
    max_opioid = df_calc['opioid_overdose_rate'].max() or 1
    max_er = df_calc['er_visits_per_1000'].max() or 1
    max_inc = df_calc['median_household_income'].max() or 1
    
    df_calc["norm_pct_without_doc"] = df_calc['pct_without_family_doctor'] / max_doc
    df_calc["norm_opioid"] = df_calc['opioid_overdose_rate'] / max_opioid
    df_calc["norm_er"] = df_calc['er_visits_per_1000'] / max_er
    # Use inverted income so lower income increases the score
    df_calc["norm_income_inverted"] = 1.0 - (df_calc['median_household_income'] / max_inc)
    
    df_calc['need_score'] = (
        df_calc['norm_pct_without_doc'] * 1.5 +
        df_calc['norm_opioid'] * 2.0 +
        df_calc['norm_er'] * 1.2 +
        df_calc['norm_income_inverted'] * 1.0
    )
    
    top_community = df_calc.loc[df_calc['need_score'].idxmax()]
    
    briefing = f"The community that most urgently needs the next outreach clinic is **{top_community['chsa_name']}**. "
    briefing += f"This assessment is driven by an exceptionally high opioid overdose rate ({top_community['opioid_overdose_rate']:.1f}/100k) combined with significant primary care access gaps ({top_community['pct_without_family_doctor']:.1f}% without a family doctor). "
    briefing += f"Deploying targeted resources here will directly alleviate the compounded operational pressure seen in their emergency room visits ({top_community['er_visits_per_1000']:.1f} visits per 1,000) and lower local economic resilience (Median Income: ${top_community['median_household_income']:,.0f})."
    
    return briefing

st.info(executive_briefing(filtered_df), icon="💡")
