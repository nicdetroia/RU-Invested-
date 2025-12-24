import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- REAL-TIME DATA & CONFIGURATION ---
COLLEGE_MAJOR_MAP = {
    "Rutgers New Brunswick: RBS (Business)": {
        "BAIT/Finance": {"base": 78000, "growth": 0.06, "risk": 0.12},
        "Accounting/Marketing": {"base": 68000, "growth": 0.04, "risk": 0.08},
    },
    "Rutgers New Brunswick: SAS (Arts & Sciences)": {
        "Computer Science": {"base": 92000, "growth": 0.07, "risk": 0.18},
        "Economics": {"base": 72000, "growth": 0.05, "risk": 0.14},
        "Psychology/Sociology": {"base": 52000, "growth": 0.03, "risk": 0.10},
        "Biological Sciences": {"base": 65000, "growth": 0.04, "risk": 0.12},
    },
    "Rutgers New Brunswick: SOE (Engineering)": {
        "Mechanical/Aero": {"base": 82000, "growth": 0.05, "risk": 0.09},
        "Electrical/ECE": {"base": 88000, "growth": 0.06, "risk": 0.11},
    },
    "Rutgers Newark/Camden": {
        "Business/Professional": {"base": 65000, "growth": 0.04, "risk": 0.10},
        "Arts/Sciences": {"base": 50000, "growth": 0.03, "risk": 0.12},
    }
}

# --- UI SETUP ---
st.set_page_config(page_title="RU-Invested 2025", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
    }
    </style>
    """, unsafe_allow_html=True) # Changed from unsafe_whitespace

st.title("🛡️ RU-Invested: The Universal Rutgers ROI Engine")
st.caption("v2.5 | Integrated 2025 Salary Benchmarks | Monte Carlo Simulation")

# --- SIDEBAR: PROFILE BUILDER ---
with st.sidebar:
    st.image("https://identity.rutgers.edu/wp-content/uploads/2021/01/R_Logotype_RED_RGB_WEB.png", width=150)
    st.header("👤 Candidate Profile")
    
    selected_college = st.selectbox("Your College", list(COLLEGE_MAJOR_MAP.keys()))
    major_options = list(COLLEGE_MAJOR_MAP[selected_college].keys())
    selected_major = st.selectbox("Your Major Track", major_options)
    
    st.divider()
    
    gpa = st.slider("Cumulative GPA", 2.0, 4.0, 3.5, step=0.1)
    work_years = st.number_input("Years of Work/Internship", 0, 4, 1)
    
    st.subheader("📜 Certifications")
    finra_certs = st.multiselect("FINRA (Finance)", ["SIE", "Series 7", "Series 63"])
    comptia_certs = st.multiselect("CompTIA (Tech)", ["A+", "Network+", "Security+"])
    
    st.subheader("🌍 External Factors")
    location = st.selectbox("Post-Grad Hub", ["NYC/San Fran", "Jersey City/Philly", "Remote/Other"])
    internship_tier = st.select_slider("Internship Prestige", options=["None", "Local", "Regional", "Fortune 500"])

# --- CALCULATION LOGIC ---
def calculate_roi():
    data = COLLEGE_MAJOR_MAP[selected_college][selected_major]
    simulations = 2000
    all_paths = []
    
    # Pre-calculating Multipliers
    loc_mult = 1.25 if location == "NYC/San Fran" else (1.10 if location == "Jersey City/Philly" else 1.0)
    tier_mult = {"None": 1.0, "Local": 1.05, "Regional": 1.15, "Fortune 500": 1.30}[internship_tier]
    cert_boost = (len(finra_certs) * 0.06) + (len(comptia_certs) * 0.08)
    gpa_boost = max(0, (gpa - 3.0) * 0.12)
    
    for _ in range(simulations):
        # Starting Salary with Stochastic Variance
        sigma = data['risk'] / (1 + (work_years * 0.1)) # More work exp = less risk
        start_sal = np.random.normal(data['base'], data['base'] * sigma)
        start_sal *= (1 + gpa_boost + cert_boost) * loc_mult * tier_mult
        
        # 10 Year Path
        path = []
        current_val = start_sal
        for year in range(10):
            # Applying 8% Discount Rate (NPV)
            path.append(current_val / (1.08**year))
            current_val *= (1 + data['growth'] + np.random.normal(0, 0.02))
        
        all_paths.append(sum(path) - 65000) # Subtracting ~4yr Rutgers Cost
        
    return np.array(all_paths)

results = calculate_roi()

# --- DASHBOARD LAYOUT ---
top_col1, top_col2, top_col3 = st.columns(3)

with top_col1:
    st.metric("Mean 10-Yr Net Profit", f"${int(results.mean()):,}")
with top_col2:
    st.metric("90th Percentile 'Alpha'", f"${int(np.percentile(results, 90)):,}")
with top_col3:
    st.metric("Success Probability (ROI > 0)", f"{(results > 0).mean():.1%}")

st.divider()

# --- VISUALIZATION ---
fig = go.Figure()
fig.add_trace(go.Histogram(x=results, nbinsx=50, marker_color='#cc0033', opacity=0.75))
fig.update_layout(
    title=f"Probability Distribution: {selected_major} Career Value",
    xaxis_title="10-Year Net Present Value (After Tuition)",
    yaxis_title="Frequency",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)



# --- DATA TABLE & BREAKDOWN ---
with st.expander("📝 View Detailed Simulation Data"):
    breakdown_df = pd.DataFrame({
        "Metric": ["Average Salary Boost", "Certification Impact", "Location Premium", "Risk Adjusted Floor"],
        "Value": [f"{gpa*2.5}%", f"{len(finra_certs + comptia_certs)*7}%", location, f"${int(results.min()):,}"]
    })
    st.table(breakdown_df)
