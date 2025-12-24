import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- 2025-2026 RUTGERS DATA REPOSITORY ---
RUTGERS_COSTS = {
    "Tuition": {"NJ Resident": 16356, "Out-of-State": 34981},
    "Mandatory Fees": 3891,
    "Housing": {
        "Livingston/SoJo Truth Apts": 12248,
        "Easton Ave Apts": 11166,
        "Traditional Dorm (Double)": 10328,
        "Off-Campus/Commuter": 0
    },
    "Meal Plan": {"Scarlet Unlimited": 7534, "150-Meal Plan": 6418, "None/Off-Campus": 0}
}

RBS_SALARIES = {
    "BAIT": {"base": 88713, "growth": 0.07, "risk": 0.12, "top_bonus": 15000},
    "Finance": {"base": 76500, "growth": 0.06, "risk": 0.15, "top_bonus": 20000},
    "Accounting": {"base": 68000, "growth": 0.04, "risk": 0.06, "top_bonus": 5000},
    "Computer Science (SAS)": {"base": 101661, "growth": 0.08, "risk": 0.18, "top_bonus": 12000},
    "Engineering (ECE/CS)": {"base": 93310, "growth": 0.06, "risk": 0.10, "top_bonus": 10000},
    "Psychology/Liberal Arts": {"base": 54000, "growth": 0.03, "risk": 0.12, "top_bonus": 2000}
}

# --- UI CONFIG ---
st.set_page_config(page_title="The Rutgers Major Calculator", layout="wide")

# Custom CSS for that "High-Finance" Look
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #ffffff; border: 1px solid #cc0033; border-radius: 10px; padding: 15px; }
    [data-testid="stMetricValue"] { color: #cc0033 !important; font-weight: bold; }
    .main { background-color: #fdfdfd; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Rutgers Major ROI Calculator")
st.write("v3.0 | 2025-26 Academic Year Data")

# --- SIDEBAR: RUTGERS SPECIFICS ---
with st.sidebar:
    st.header("🏫 University Profile")
    residency = st.radio("Residency Status", ["NJ Resident", "Out-of-State"])
    major = st.selectbox("Your Major Track", list(RBS_SALARIES.keys()))
    
    st.header("💸 Financial Aid")
    income_bracket = st.select_slider("Family Income Bracket", 
                                     options=["<$65k (Scarlet Guarantee)", "$65k-$100k", "$100k-$150k", ">$150k"])
    scholarships = st.number_input("Annual Scarlet Promise/Merit Aid ($)", 0, 30000, 2000)

    st.header("🏠 Lifestyle")
    housing = st.selectbox("Housing Choice", list(RUTGERS_COSTS["Housing"].keys()))
    meal_plan = st.selectbox("Dining Plan", list(RUTGERS_COSTS["Meal Plan"].keys()))

# --- CALCULATION ENGINE ---
def calculate_rutgers_roi():
    # 1. Calculate Yearly Outlay
    tuition = RUTGERS_COSTS["Tuition"][residency]
    fees = RUTGERS_COSTS["Mandatory Fees"]
    room_board = RUTGERS_COSTS["Housing"][housing] + RUTGERS_COSTS["Meal Plan"][meal_plan]
    
    # 2. Scarlet Guarantee Logic
    if residency == "NJ Resident" and income_bracket == "<$65k (Scarlet Guarantee)":
        tuition_net = 0 # Scarlet Guarantee covers remaining tuition/fees
    elif residency == "NJ Resident" and income_bracket == "$65k-$100k":
        tuition_net = tuition * 0.5
    else:
        tuition_net = tuition
        
    total_yearly_cost = tuition_net + fees + room_board - scholarships
    total_4yr_debt = total_yearly_cost * 4
    
    # 3. Career Simulation (Monte Carlo)
    stats = RBS_SALARIES[major]
    sims = 3000
    npv_results = []
    
    for _ in range(sims):
        # Starting Salary with Major-specific volatility
        start = np.random.normal(stats['base'], stats['base'] * stats['risk'])
        
        # 10 Year NPV
        career_cashflow = 0
        current_sal = start
        for y in range(10):
            career_cashflow += current_sal / (1.08**y) # 8% Discount Rate
            current_sal *= (1 + stats['growth'])
        
        npv_results.append(career_cashflow - total_4yr_debt)
        
    return np.array(npv_results), total_4yr_debt

# --- DISPLAY ---
results, debt = calculate_rutgers_roi()

c1, c2, c3 = st.columns(3)
with c1: st.metric("Estimated 4-Year Cost", f"${int(debt):,}")
with c2: st.metric("Median 10-Year Net Gain", f"${int(np.median(results)):,}")
with c3: st.metric("ROI Efficiency", f"{round(np.median(results)/debt, 2)}x")

st.divider()

# Probability Distribution Chart
fig = go.Figure()
fig.add_trace(go.Violin(x=results, line_color='#cc0033', name='ROI Range', box_visible=True, meanline_visible=True))
fig.update_layout(title="Probability Distribution of Career Value (NPV)", xaxis_title="Net Profit ($)", template="none")
st.plotly_chart(fig, use_container_width=True)
