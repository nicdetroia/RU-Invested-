import streamlit as st
import numpy as np
import plotly.express as px

st.title("🛡️ RU-Invested: Career ROI Tracker")
st.write("Calculate the Net Present Value of your Rutgers Degree.")

# Sidebar for Daily Inputs
with st.sidebar:
    st.header("Daily Stats")
    gpa = st.slider("Current GPA", 2.0, 4.0, 3.5)
    networking = st.number_input("Networking Events Attended", 0, 100, 5)
    internships = st.radio("Internships Secured", [0, 1, 2, 3])

# The Math Logic
tuition = 60000 
simulations = 5000

def run_simulation():
    outcomes = []
    for _ in range(simulations):
        # Volatility decreases as networking increases
        risk = max(0.05, 0.25 - (networking * 0.01))
        base = np.random.normal(75000, 75000 * risk)
        
        # GPA & Internship Premiums
        salary = base * (1 + (gpa - 3.0) * 0.1) * (1 + (internships * 0.15))
        
        # 10-Year NPV calculation
        pv = sum([salary * (1.03**t) / (1.08**t) for t in range(10)])
        outcomes.append(pv - tuition)
    return outcomes

results = run_simulation()

# Visuals
st.metric("Expected Net Profit (NPV)", f"${int(np.mean(results)):,}")
fig = px.histogram(results, nbins=50, title="Probability Distribution of Your Career Value",
                   labels={'value': 'Net Present Value ($)'}, color_discrete_sequence=['#cc0033']) # Rutgers Red
st.plotly_chart(fig)
