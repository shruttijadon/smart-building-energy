import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Smart Building Energy Profiling",
    page_icon="⚡",
    layout="wide"
)

# App Title & Overview 
st.title("⚡ Smart Building Energy Profiling & Analytics")
st.markdown("""
This web application provides real-time and historical power consumption analysis across different building zones 
to optimize energy efficiency, lower baseline costs, and detect operational anomalies.
""")

# Sidebar Navigation Controls
st.sidebar.header("Profiling Controls")
zone = st.sidebar.selectbox(
    "Select Building Zone", 
    ["All Zones", "Floor 1: HVAC", "Floor 2: Lighting", "Server Room"]
)

# Simulated Sensor Data Generation
@st.cache_data
def load_energy_data():
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-01-01", end="2026-07-01", period=4344)
    data = pd.DataFrame({
        "Timestamp": timestamps,
        "Power_Consumption_kW": np.random.normal(120, 15, size=len(timestamps)) + np.sin(np.linspace(0, 50, len(timestamps))) * 30,
        "Temperature_C": np.random.normal(24, 2, size=len(timestamps))
    })
    return data

df = load_energy_data()

# Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Average Power Load", value=f"{df['Power_Consumption_kW'].mean():.1f} kW")
with col2:
    st.metric(label="Peak Load Recorded", value=f"{df['Power_Consumption_kW'].max():.1f} kW")
with col3:
    st.metric(label="Total Tracked Hours", value=len(df))

st.markdown("---")

# Visualizations Section
st.subheader("📈 Power Consumption Trend Analysis")
st.line_chart(df.set_index("Timestamp")[["Power_Consumption_kW"]])
st.caption(f"Figure: Hourly energy consumption profile for {zone}.")

st.subheader("💡 Efficiency & Optimization Recommendations")
st.markdown("""
* **Load Shifting:** Shift heavy HVAC operations to off-peak hours to reduce baseline demand charges.
* **Automated Shut-downs:** Implement occupancy-based sensor cut-offs for lighting on Floor 2 during low-traffic windows.
* **Thermal Regulation:** Maintain server room cooling thresholds dynamically based on ambient external temperature metrics.
""")
