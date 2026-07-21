import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page ka setup aur title wagera yahan set kar rahe hain
st.set_page_config(
    page_title="Smart Building Energy Profiling",
    page_icon="⚡",
    layout="wide"
)

# App ka main header aur chota sa introduction
st.title("⚡ Smart Building Energy Profiling & Analytics")
st.markdown("""
Yeh web application alag-alag building zones ki real-time aur historical power consumption ko analyze karti hai, 
taaki energy bachayi ja sake, kharcha kam ho aur koi bhi problem jaldi pakdi ja sake.
""")

# Sidebar mein control options
st.sidebar.header("Profiling Controls")
zone = st.sidebar.selectbox(
    "Select Building Zone", 
    ["All Zones", "Floor 1: HVAC", "Floor 2: Lighting", "Server Room"]
)

# Simulated sensor data generate karne ka function
@st.cache_data
def load_energy_data():
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-01-01", end="2026-07-01", periods=4344)
    data = pd.DataFrame({
        "Timestamp": timestamps,
        "Power_Consumption_kW": np.random.normal(120, 15, size=len(timestamps)) + np.sin(np.linspace(0, 50, len(timestamps))) * 30,
        "Temperature_C": np.random.normal(24, 2, size=len(timestamps))
    })
    return data

df = load_energy_data()

# Upar 3 columns mein main numbers/metrics dikhane ke liye
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Average Power Load", value=f"{df['Power_Consumption_kW'].mean():.1f} kW")
with col2:
    st.metric(label="Peak Load Recorded", value=f"{df['Power_Consumption_kW'].max():.1f} kW")
with col3:
    st.metric(label="Total Tracked Hours", value=len(df))

st.markdown("---")

# Animated & Interactive Plotly Graph wala section
st.subheader("📈 Interactive Power Consumption Trend Analysis")

# Plotly ka use karke ek smooth aur animated line chart bana rahe hain
fig = px.line(
    df, 
    x="Timestamp", 
    y="Power_Consumption_kW", 
    title=f"Hourly Energy Trend ({zone})",
    labels={"Power_Consumption_kW": "Power Load (kW)", "Timestamp": "Timeline"}
)

# Graph ko thoda aur sleek aur modern look dene ke liye styling
fig.update_traces(line=dict(color="#0066cc", width=2))
fig.update_layout(
    xaxis_title="Timeline",
    yaxis_title="Power Consumption (kW)",
    hovermode="x unified",
    template="plotly_white"
)

# Streamlit par graph show karna
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Figure: Selected zone ({zone}) ke liye interactive aur animated energy consumption trend.")

# Efficiency badhane ke liye tips aur recommendations
st.subheader("💡 Efficiency & Optimization Recommendations")
st.markdown("""
* **Load Shifting:** Bhaari HVAC systems ko un ghanto mein chalayein jab bijli ka load kam hota hai taaki kharcha bache.
* **Automated Shut-downs:** Floor 2 par jahan log kam hote hain, wahan lightings ke liye occupancy sensors lagayein jo apne aap band ho jayein.
* **Thermal Regulation:** Server room ka temperature bahar ke mausam ke hisaab se dynamically control karein.
""")
