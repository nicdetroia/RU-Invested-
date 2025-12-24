import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

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

BASE_MAJORS = {
    # RBS / SAS / SOE / SEBS / EJB / everything bucketed
    "BAIT": {"base": 88713, "growth": 0.07, "risk": 0.12, "top_bonus": 15000},
    "Finance": {"base": 76500, "growth": 0.06, "risk": 0.15, "top_bonus": 20000},
    "Accounting": {"base": 68000, "growth": 0.04, "risk": 0.06, "top_bonus": 5000},
    "Computer Science (SAS)": {"base": 101661, "growth": 0.08, "risk": 0.18, "top_bonus": 12000},
    "Engineering (ECE/CS/ME)": {"base": 93310, "growth": 0.06, "risk": 0.10, "top_bonus": 10000},
    "Nursing": {"base": 78000, "growth": 0.04, "risk": 0.07, "top_bonus": 5000},
    "Biology / Pre-Health": {"base": 52000, "growth": 0.05, "risk": 0.12, "top_bonus": 4000},
    "Public Health / Social Work": {"base": 51000, "growth": 0.03, "risk": 0.10, "top_bonus": 3000},
    "Education": {"base": 54000, "growth": 0.03, "risk": 0.05, "top_bonus": 3000},
    "Psychology / Liberal Arts": {"base": 54000, "growth": 0.03, "risk": 0.12, "top_bonus": 2000},
}

st.set_page_config(page_title="The Rutgers Major ROI Calculator", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetric"] { 
        background-color: #ffffff; 
        border: 1px solid #cc0033; 
        border-radius: 10px; 
        padding: 15px; 
    }
    [data-testid="stMetricValue"] { 
        color: #cc0033 !important; 
        font-weight: bold; 
    }
    .main { background-color: #fdfdfd; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Rutgers Major ROI Calculator")
st.write("v4.0 | 2025-26 Academic Year Data | Major + Experience + Side Income")

with st.sidebar:
    st.header("🏫 University Profile")
    residency = st.radio("Residency Status", ["NJ Resident", "Out-of-State"])
    
    major_options = list(BASE_MAJORS.keys()) + ["Custom Major / Input My Own"]
    major_choice = st.selectbox("Your Major Track", major_options)

    custom_major_params = None
    if major_choice == "Custom Major / Input My Own":
        st.subheader("Custom Major Assumptions")
        custom_base = st.number_input("Expected Starting Salary ($)", 30000, 200000, 65000, step=5000)
        custom_growth = st.slider("Annual Salary Growth (%)", 0.0, 15.0, 5.0, step=0.5) / 100
        custom_risk = st.slider("Salary Volatility (Risk)", 0.0, 0.40, 0.15, step=0.01)
        custom_bonus = st.number_input("Top Bonus / Upside Potential ($)", 0, 50000, 5000, step=1000)
        custom_major_params = {
            "base": custom_base,
            "growth": custom_growth,
            "risk": custom_risk,
            "top_bonus": custom_bonus
        }

    st.header("💸 Financial Aid")
    income_bracket = st.select_slider("Family Income Bracket", 
                                      options=["<$65k (Scarlet Guarantee)", "$65k-$100k", 
                                               "$100k-$150k", ">$150k"])
    scholarships = st.number_input("Annual Scarlet Promise/Merit Aid ($)", 0, 30000, 2000, step=500)

    st.header("🏠 Lifestyle & Work")
    housing = st.selectbox("Housing Choice", list(RUTGERS_COSTS["Housing"].keys()))
    meal_plan = st.selectbox("Dining Plan", list(RUTGERS_COSTS["Meal Plan"].keys()))
    side_income = st.number_input(
        "Average Annual Take-Home While in School (jobs, resell, internships) ($)",
        0, 60000, 0, step=1000
    )

left, right = st.columns([2, 1])

with left:
    st.subheader("📈 Experience & Career Capital")

    # Internships & Work Experience
    st.markdown("**Internships & Work Experience**")
    n_internships = st.number_input("How many internships / major work experiences will you have by graduation?",
                                    0, 10, 1)

    internship_tiers = ["Campus / Local", "Regional / Statewide", "Fortune 500 / Big 4",
                        "Top Tech / Quant / Tier-1"]

    internships = []
    for i in range(n_internships):
        with st.expander(f"Internship / Role #{i+1}", expanded=(i == 0)):
            company = st.text_input(f"Company #{i+1}", key=f"int_company_{i}")
            role = st.text_input(f"Role / Title #{i+1}", key=f"int_role_{i}")
            tier = st.selectbox(
                f"Company Tier #{i+1}", 
                internship_tiers, 
                index=0, 
                key=f"int_tier_{i}"
            )
            internships.append({"company": company, "role": role, "tier": tier})

    st.markdown("**Certifications & Technical Credentials**")
    n_certs = st.number_input("Number of certifications (e.g., BMC, CompTIA, AWS, CPA exams in progress)", 
                              0, 15, 0)
    cert_impact_levels = ["Low (nice-to-have)", "Medium (relevant)", "High (directly career-changing)"]
    certs = []
    for i in range(n_certs):
        with st.expander(f"Certification #{i+1}", expanded=False):
            cert_name = st.text_input(f"Certification Name #{i+1}", key=f"cert_name_{i}")
            cert_impact = st.selectbox(
                f"Impact Level #{i+1}", 
                cert_impact_levels, 
                index=1, 
                key=f"cert_impact_{i}"
            )
            certs.append({"name": cert_name, "impact": cert_impact})

    st.markdown("**Volunteer & Leadership Roles**")
    n_vol = st.number_input("Volunteer / leadership positions (clubs, orgs, nonprofits)", 0, 20, 0)
    leadership_levels = ["Member / Volunteer", "Coordinator / E-Board", "President / Founder"]
    volunteering = []
    for i in range(n_vol):
        with st.expander(f"Volunteer / Leadership Role #{i+1}", expanded=False):
            org = st.text_input(f"Organization #{i+1}", key=f"vol_org_{i}")
            title = st.text_input(f"Title / Position #{i+1}", key=f"vol_title_{i}")
            level = st.selectbox(
                f"Leadership Level #{i+1}",
                leadership_levels,
                index=0,
                key=f"vol_level_{i}"
            )
            volunteering.append({"org": org, "title": title, "level": level})


with right:
    st.subheader("🔧 Model Settings")
    time_horizon = st.slider("Career Horizon (years after graduation)", 5, 20, 10)
    discount_rate = st.slider("Discount Rate (time value of money)", 0.0, 15.0, 8.0, step=0.5) / 100
    sims = st.slider("Number of Monte Carlo Simulations", 500, 10000, 3000, step=500)

def compute_experience_boost(internships, certs, volunteering):
    """
    Returns a multiplicative boost on starting salary, e.g. 0.25 = +25%
    """
    boost = 0.0

    tier_weights = {
        "Campus / Local": 0.03,
        "Regional / Statewide": 0.05,
        "Fortune 500 / Big 4": 0.08,
        "Top Tech / Quant / Tier-1": 0.12
    }
    for item in internships:
        t = item.get("tier")
        boost += tier_weights.get(t, 0.0)
    cert_weights = {
        "Low (nice-to-have)": 0.01,
        "Medium (relevant)": 0.03,
        "High (directly career-changing)": 0.05
    }
    for c in certs:
        boost += cert_weights.get(c.get("impact"), 0.0)

    # Volunteer / leadership weights
    leadership_weights = {
        "Member / Volunteer": 0.005,
        "Coordinator / E-Board": 0.015,
        "President / Founder": 0.03
    }
    for v in volunteering:
        boost += leadership_weights.get(v.get("level"), 0.0)

    # Cap total boost so it doesn't go insane
    boost = min(boost, 0.60)  # max +60% starting salary boost
    return boost

def calculate_rutgers_roi():
    # 1. Yearly Outlay
    tuition = RUTGERS_COSTS["Tuition"][residency]
    fees = RUTGERS_COSTS["Mandatory Fees"]
    room_board = RUTGERS_COSTS["Housing"][housing] + RUTGERS_COSTS["Meal Plan"][meal_plan]

    if residency == "NJ Resident" and income_bracket == "<$65k (Scarlet Guarantee)":
        tuition_net = 0  # Scarlet Guarantee covers remaining tuition/fees
    elif residency == "NJ Resident" and income_bracket == "$65k-$100k":
        tuition_net = tuition * 0.5
    else:
        tuition_net = tuition

    gross_cost = tuition_net + fees + room_board
    total_yearly_cost = max(gross_cost - scholarships - side_income, 0)
    total_4yr_debt = total_yearly_cost * 4

    if major_choice == "Custom Major / Input My Own":
        stats = custom_major_params
        major_label = "Custom Major"
    else:
        stats = BASE_MAJORS[major_choice]
        major_label = major_choice

    exp_boost = compute_experience_boost(internships, certs, volunteering)

    npv_results = []

    for _ in range(sims):
        # Starting Salary with Major-specific volatility
        start = np.random.normal(stats['base'], stats['base'] * stats['risk'])
        # Apply experience boost
        start = max(start * (1 + exp_boost), 0)

        career_cashflow = 0
        current_sal = start

        for y in range(time_horizon):
            # Simple "take-home" assumption (e.g., 75% after taxes/expenses)
            take_home = current_sal * 0.75
            career_cashflow += take_home / ((1 + discount_rate) ** y)
            current_sal *= (1 + stats['growth'])

        npv_results.append(career_cashflow - total_4yr_debt)

    return np.array(npv_results), total_4yr_debt, major_label, exp_boost, total_yearly_cost

results, debt, major_label, exp_boost, yearly_cost = calculate_rutgers_roi()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Estimated Net Cost per Year", f"${int(yearly_cost):,}")
with c2:
    st.metric("Estimated 4-Year Cost", f"${int(debt):,}")
with c3:
    median_gain = int(np.median(results))
    st.metric(f"Median {time_horizon}-Year Net Gain", f"${median_gain:,}")
with c4:
    if debt <= 0:
        roi_text = "Debt-Free"
    else:
        roi_text = f"{round(np.median(results) / debt, 2)}x"
    st.metric("ROI Efficiency", roi_text)

st.divider()

summary_df = pd.DataFrame({
    "Category": [
        "Residency",
        "Major Track",
        "Experience Boost on Starting Salary",
        "Simulated Career Horizon (years)",
        "Discount Rate",
        "Annual Net Cost",
        "Total 4-Year Cost"
    ],
    "Value": [
        residency,
        major_label,
        f"+{round(exp_boost * 100, 1)}%",
        time_horizon,
        f"{round(discount_rate * 100, 1)}%",
        f"${int(yearly_cost):,}",
        f"${int(debt):,}"
    ]
})
st.subheader("Scenario Snapshot")
st.table(summary_df)

st.divider()

fig = go.Figure()
fig.add_trace(go.Violin(
    x=results,
    line_color='#cc0033',
    name='ROI Range',
    box_visible=True,
    meanline_visible=True
))
fig.update_layout(
    title=f"Probability Distribution of Career Value (NPV) over {time_horizon} Years",
    xaxis_title="Net Profit ($)",
    template="none"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Risk & Range")
st.write(f"**5th percentile:** ${int(np.percentile(results, 5)):,}")
st.write(f"**Median:** ${int(np.percentile(results, 50)):,}")
st.write(f"**95th percentile:** ${int(np.percentile(results, 95)):,}")
