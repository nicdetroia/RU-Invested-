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

BASE_MAJORS = {
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

# --- UI CONFIG ---
st.set_page_config(page_title="The Rutgers Major ROI Calculator", layout="wide")

# ---- SESSION STATE INIT ----
if "parsed_internships" not in st.session_state:
    st.session_state["parsed_internships"] = []
if "parsed_certs" not in st.session_state:
    st.session_state["parsed_certs"] = []
if "parsed_volunteering" not in st.session_state:
    st.session_state["parsed_volunteering"] = []

# --- GLOBAL CSS: BLACK / WHITE / RUTGERS RED ---
st.markdown("""
    <style>
    /* Global background + text */
    html, body,
    [data-testid="stAppViewContainer"],
    .main, .block-container {
        background-color: #050505 !important;
        color: #f9fafb !important;
    }

    /* Sidebar: slightly lighter black */
    div[data-testid="stSidebar"] {
        background-color: #0b0b0b !important;
        color: #f9fafb !important;
    }
    div[data-testid="stSidebar"] * {
        color: #f9fafb !important;
    }

    /* All text in main area white by default */
    h1, h2, h3, h4, h5, h6,
    p, label, span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] * {
        color: #f9fafb !important;
    }

    /* Inputs */
    .stTextArea textarea,
    .stTextInput input {
        background-color: #111111 !important;
        color: #f9fafb !important;
        border-radius: 6px;
        border: 1px solid #374151 !important;
    }

    .stNumberInput input,
    .stSlider,
    .stSelectbox,
    .stRadio {
        color: #f9fafb !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #0b0b0b !important;
        border: 1px solid #cc0033;
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stMetricLabel"] {
        color: #e5e7eb !important;
    }
    [data-testid="stMetricValue"] {
        color: #cc0033 !important;
        font-weight: bold;
    }

    /* Buttons */
    .stButton button {
        background-color: #cc0033 !important;
        color: #f9fafb !important;
        border-radius: 8px;
        border: none;
    }
    .stButton button:hover {
        background-color: #e00036 !important;
    }

    /* Tables */
    .stTable, .stTable table {
        color: #f9fafb !important;
        background-color: #050505 !important;
    }
    .stTable tbody tr:nth-child(even) {
        background-color: #111111 !important;
    }
    .stTable tbody tr:nth-child(odd) {
        background-color: #050505 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TITLE ---
st.title("🛡️ Rutgers Major ROI Calculator")
st.write("v6.1 | Black & white with Rutgers red – text-only resume import")

# --- SIDEBAR: PROFILE / COSTS ---
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
    income_bracket = st.select_slider(
        "Family Income Bracket", 
        options=[
            "<$65k (Scarlet Guarantee)",
            "$65k-$100k",
            "$100k-$150k",
            ">$150k"
        ]
    )
    scholarships = st.number_input("Annual Scarlet Promise/Merit Aid ($)", 0, 30000, 2000, step=500)

    st.header("🏠 Lifestyle & Work")
    housing = st.selectbox("Housing Choice", list(RUTGERS_COSTS["Housing"].keys()))
    meal_plan = st.selectbox("Dining Plan", list(RUTGERS_COSTS["Meal Plan"].keys()))
    side_income = st.number_input(
        "Average Annual Take-Home While in School (jobs, resell, internships) ($)",
        0, 60000, 0, step=1000
    )

# --- PARSING HELPERS ---

def extract_text_from_file(uploaded_file):
    """
    Text-only. If user uploads PDF, we refuse and tell them to paste text.
    """
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        st.warning("PDF parsing is disabled here. Export your LinkedIn/resume text and paste it below.")
        return ""
    # fallback: try decode anyway
    try:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception:
        st.warning("Could not read this file as text. Paste your resume content instead.")
        return ""

def guess_tier_from_line(line: str) -> str:
    line_lower = line.lower()
    top_keywords = ["google", "meta", "amazon", "microsoft", "goldman", "j.p. morgan", "jp morgan",
                    "citadel", "hft", "stripe", "quant", "faang"]
    big4_keywords = ["deloitte", "pwc", "pricewaterhouse", "ey ", "ernst & young", "kpmg"]
    regional_keywords = ["bank", "hospital", "rutgers", "state", "regional", "corp", "inc", "llc"]

    if any(k in line_lower for k in top_keywords):
        return "Top Tech / Quant / Tier-1"
    if any(k in line_lower for k in big4_keywords):
        return "Fortune 500 / Big 4"
    if any(k in line_lower for k in regional_keywords):
        return "Regional / Statewide"
    return "Campus / Local"

def parse_resume_text(text: str):
    internships = []
    certs = []
    volunteering = []

    if not text:
        return internships, certs, volunteering

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    section = None

    for line in lines:
        lower = line.lower()

        # Section detection
        if "experience" in lower and "no experience" not in lower:
            section = "exp"
            continue
        if "work history" in lower or "professional experience" in lower:
            section = "exp"
            continue
        if "certification" in lower or "certifications" in lower or "licenses" in lower:
            section = "cert"
            continue
        if "volunteer" in lower or "leadership" in lower or "activities" in lower:
            section = "vol"
            continue

        # Experience
        if section == "exp":
            if len(line) < 10:
                continue
            if " - " in line:
                parts = line.split(" - ", 1)
            elif " | " in line:
                parts = line.split(" | ", 1)
            else:
                parts = [line, ""]
            company = parts[0].strip()
            role = parts[1].strip() if len(parts) > 1 else ""
            tier = guess_tier_from_line(line)
            internships.append({"company": company, "role": role, "tier": tier})
            continue

        # Certifications
        if section == "cert":
            if len(line) < 4:
                continue
            certs.append({"name": line, "impact": "Medium (relevant)"})
            continue

        # Volunteering / leadership
        if section == "vol":
            if len(line) < 4:
                continue
            if " - " in line:
                parts = line.split(" - ", 1)
            elif " | " in line:
                parts = line.split(" | ", 1)
            else:
                parts = [line, ""]
            org = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else ""
            volunteering.append({"org": org, "title": title, "level": "Member / Volunteer"})

    return internships, certs, volunteering

# --- MAIN LAYOUT ---
left, right = st.columns([2.2, 0.8])

with left:
    # IMPORT
    st.subheader("🔗 Import from LinkedIn / Resume (Optional)")

    uploaded_file = st.file_uploader(
        "Upload a .txt export of your resume / LinkedIn (PDFs not parsed here)",
        type=["txt", "pdf"]
    )
    resume_text_manual = st.text_area(
        "…or paste your resume / LinkedIn text here",
        height=150,
        placeholder="Paste your Experience, Certifications, Activities sections here…"
    )

    if st.button("Parse & Autofill from Resume/LinkedIn"):
        raw_text = ""
        if uploaded_file is not None:
            raw_text = extract_text_from_file(uploaded_file)
        elif resume_text_manual.strip():
            raw_text = resume_text_manual
        else:
            st.warning("Provide a text file or paste your resume content first.")
        
        if raw_text:
            ints, cs, vols = parse_resume_text(raw_text)
            st.session_state["parsed_internships"] = ints
            st.session_state["parsed_certs"] = cs
            st.session_state["parsed_volunteering"] = vols
            st.success(
                f"Parsed {len(ints)} experiences, {len(cs)} certifications, {len(vols)} volunteer roles."
            )

    # EXPERIENCE
    st.subheader("📈 Experience & Career Capital")

    st.markdown("**Internships & Work Experience**")
    internship_tiers = [
        "Campus / Local",
        "Regional / Statewide",
        "Fortune 500 / Big 4",
        "Top Tech / Quant / Tier-1"
    ]

    parsed_ints = st.session_state.get("parsed_internships", [])
    default_n_int = max(1, len(parsed_ints)) if parsed_ints else 1

    n_internships = st.number_input(
        "How many internships / major work experiences will you have by graduation?",
        0, 10, default_n_int
    )

    internships = []
    for i in range(n_internships):
        with st.expander(f"Internship / Role #{i+1}", expanded=(i == 0)):
            parsed = parsed_ints[i] if i < len(parsed_ints) else {}
            default_company = parsed.get("company", "")
            default_role = parsed.get("role", "")
            default_tier = parsed.get("tier", internship_tiers[0])

            company = st.text_input(
                f"Company #{i+1}",
                value=default_company,
                key=f"int_company_{i}"
            )
            role = st.text_input(
                f"Role / Title #{i+1}",
                value=default_role,
                key=f"int_role_{i}"
            )
            tier = st.selectbox(
                f"Company Tier #{i+1}",
                internship_tiers,
                index=internship_tiers.index(default_tier) if default_tier in internship_tiers else 0,
                key=f"int_tier_{i}"
            )
            internships.append({"company": company, "role": role, "tier": tier})

    st.markdown("**Certifications & Technical Credentials**")
    parsed_certs = st.session_state.get("parsed_certs", [])
    default_n_certs = len(parsed_certs)

    cert_impact_levels = ["Low (nice-to-have)", "Medium (relevant)", "High (directly career-changing)"]

    n_certs = st.number_input(
        "Number of certifications (e.g., BMC, CompTIA, AWS, CPA exams in progress)",
        0, 15, default_n_certs
    )

    certs = []
    for i in range(n_certs):
        with st.expander(f"Certification #{i+1}", expanded=False):
            parsed = parsed_certs[i] if i < len(parsed_certs) else {}
            default_name = parsed.get("name", "")
            default_impact = parsed.get("impact", "Medium (relevant)")

            cert_name = st.text_input(
                f"Certification Name #{i+1}",
                value=default_name,
                key=f"cert_name_{i}"
            )
            cert_impact = st.selectbox(
                f"Impact Level #{i+1}",
                cert_impact_levels,
                index=cert_impact_levels.index(default_impact) if default_impact in cert_impact_levels else 1,
                key=f"cert_impact_{i}"
            )
            certs.append({"name": cert_name, "impact": cert_impact})

    st.markdown("**Volunteer & Leadership Roles**")
    parsed_vols = st.session_state.get("parsed_volunteering", [])
    default_n_vol = len(parsed_vols)

    leadership_levels = ["Member / Volunteer", "Coordinator / E-Board", "President / Founder"]

    n_vol = st.number_input(
        "Volunteer / leadership positions (clubs, orgs, nonprofits)",
        0, 20, default_n_vol
    )

    volunteering = []
    for i in range(n_vol):
        with st.expander(f"Volunteer / Leadership Role #{i+1}", expanded=False):
            parsed = parsed_vols[i] if i < len(parsed_vols) else {}
            default_org = parsed.get("org", "")
            default_title = parsed.get("title", "")
            default_level = parsed.get("level", "Member / Volunteer")

            org = st.text_input(
                f"Organization #{i+1}",
                value=default_org,
                key=f"vol_org_{i}"
            )
            title = st.text_input(
                f"Title / Position #{i+1}",
                value=default_title,
                key=f"vol_title_{i}"
            )
            level = st.selectbox(
                f"Leadership Level #{i+1}",
                leadership_levels,
                index=leadership_levels.index(default_level) if default_level in leadership_levels else 0,
                key=f"vol_level_{i}"
            )
            volunteering.append({"org": org, "title": title, "level": level})

with right:
    st.subheader("🔧 Model Settings")
    time_horizon = st.slider("Career Horizon (years after graduation)", 5, 20, 10)
    discount_rate = st.slider("Discount Rate (time value of money)", 0.0, 15.0, 8.0, step=0.5) / 100
    sims = st.slider("Number of Monte Carlo Simulations", 500, 10000, 3000, step=500)

# --- EXPERIENCE BOOST ENGINE ---
def compute_experience_boost(internships, certs, volunteering):
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

    leadership_weights = {
        "Member / Volunteer": 0.005,
        "Coordinator / E-Board": 0.015,
        "President / Founder": 0.03
    }
    for v in volunteering:
        boost += leadership_weights.get(v.get("level"), 0.0)

    return min(boost, 0.60)

# --- CORE CALC ENGINE ---
def calculate_rutgers_roi():
    tuition = RUTGERS_COSTS["Tuition"][residency]
    fees = RUTGERS_COSTS["Mandatory Fees"]
    room_board = RUTGERS_COSTS["Housing"][housing] + RUTGERS_COSTS["Meal Plan"][meal_plan]

    if residency == "NJ Resident" and income_bracket == "<$65k (Scarlet Guarantee)":
        tuition_net = 0
    elif residency == "NJ Resident" and income_bracket == "$65k-$100k":
        tuition_net = tuition * 0.5
    else:
        tuition_net = tuition

    gross_cost = tuition_net + fees + room_board
    total_yearly_cost = max(gross_cost - scholarships - side_income, 0)
    total_4yr_cost = total_yearly_cost * 4

    if major_choice == "Custom Major / Input My Own":
        stats = custom_major_params
        major_label = "Custom Major"
    else:
        stats = BASE_MAJORS[major_choice]
        major_label = major_choice

    exp_boost = compute_experience_boost(internships, certs, volunteering)

    npv_results = []
    for _ in range(sims):
        start = np.random.normal(stats["base"], stats["base"] * stats["risk"])
        start = max(start * (1 + exp_boost), 0)

        career_cashflow = 0
        current_sal = start

        for y in range(time_horizon):
            take_home = current_sal * 0.75
            career_cashflow += take_home / ((1 + discount_rate) ** y)
            current_sal *= (1 + stats["growth"])

        npv_results.append(career_cashflow - total_4yr_cost)

    return np.array(npv_results), total_4yr_cost, major_label, exp_boost, total_yearly_cost

# --- RUN MODEL ---
results, debt, major_label, exp_boost, yearly_cost = calculate_rutgers_roi()

# --- METRICS ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Estimated Net Cost per Year", f"${int(yearly_cost):,}")
with c2:
    st.metric("Estimated 4-Year Cost", f"${int(debt):,}")
with c3:
    median_gain = int(np.median(results))
    st.metric(f"Median {time_horizon}-Year Net Gain", f"${median_gain:,}")
with c4:
    roi_text = "Debt-Free" if debt <= 0 else f"{round(np.median(results) / debt, 2)}x"
    st.metric("ROI Efficiency", roi_text)

st.divider()

# --- SNAPSHOT TABLE ---
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

# --- DISTRIBUTION PLOT (BLACK THEME) ---
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
    template="plotly_dark",
    plot_bgcolor="#050505",
    paper_bgcolor="#050505",
    font_color="#f9fafb",
    xaxis=dict(color="#f9fafb"),
    yaxis=dict(color="#f9fafb")
)
st.plotly_chart(fig, use_container_width=True)

# --- RISK STATS ---
st.subheader("Risk & Range")
st.write(f"**5th percentile:** ${int(np.percentile(results, 5)):,}")
st.write(f"**Median:** ${int(np.percentile(results, 50)):,}")
st.write(f"**95th percentile:** ${int(np.percentile(results, 95)):,}")
