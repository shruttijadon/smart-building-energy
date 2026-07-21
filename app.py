import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Smart Building Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-style {
        color: #0066cc;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Smart Building Energy Analytics & Optimization Project")
st.markdown("""
**B.Tech Minor Project Dashboard** - Yeh platform building ke alag-alag zones ka power consumption 
track karne, anomalies detect karne, aur energy costs optimize karne ke liye banaya hai! 🚀
""")

st.sidebar.header("🎛️ Control Panel")
st.sidebar.markdown("---")

zones_list = [
    "All Zones", 
    "Floor 1: HVAC System", 
    "Floor 2: Lighting", 
    "Floor 3: Offices", 
    "Server Room", 
    "Basement: Backup Systems"
]
selected_zone = st.sidebar.selectbox("Building Zone Select Karo", zones_list)

st.sidebar.markdown("**📅 Date Range**")
date_range = st.sidebar.date_input(
    "Select range",
    value=(datetime(2026, 1, 1), datetime(2026, 7, 1)),
    min_value=datetime(2026, 1, 1),
    max_value=datetime(2026, 7, 1)
)

aggregation_type = st.sidebar.radio(
    "Data View Level",
    ["Hourly", "Daily", "Weekly", "Monthly"]
)

st.sidebar.markdown("**🔍 Analysis Options**")
show_anomalies = st.sidebar.checkbox("Show Anomalies (Spikes)", value=True)
show_forecast = st.sidebar.checkbox("Show 72h Forecast", value=True)
cost_per_kwh = st.sidebar.number_input("Electricity Rate (₹ per kWh)", value=8.5, min_value=0.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Left sidebar se zones aur filters change karke live graph update hote hue dekho!")

@st.cache_data
def generate_realistic_energy_data():
    np.random.seed(42)
    # Fixed frequency string from "1H" to "h" to resolve pandas compatibility error
    timestamps = pd.date_range(start="2026-01-01", end="2026-07-01", freq="h")
    n_hours = len(timestamps)
    
    data = pd.DataFrame({
        "Timestamp": timestamps,
        "Hour": timestamps.hour,
        "Day_of_Week": timestamps.dayofweek,
        "Month": timestamps.month
    })
    
    hvac_base = 150 + 40 * np.sin(np.linspace(0, 50, n_hours))
    hvac_noise = np.random.normal(0, 8, n_hours)
    hvac_pattern = np.where(
        data["Hour"].isin([6, 7, 8, 9, 17, 18, 19, 20]),
        hvac_base * 1.3 + hvac_noise,
        hvac_base * 0.8 + hvac_noise
    )
    
    lighting_pattern = np.where(
        data["Hour"].isin(range(8, 18)),
        np.random.normal(80, 10, n_hours),
        np.random.normal(20, 5, n_hours)
    )
    
    office_pattern = np.where(
        data["Hour"].isin(range(8, 18)),
        np.random.normal(120, 15, n_hours),
        np.random.normal(40, 8, n_hours)
    )
    
    server_pattern = np.random.normal(200, 20, n_hours)
    
    basement_pattern = np.random.normal(15, 3, n_hours)
    basement_pattern[::504] *= 5
    
    data["HVAC"] = np.maximum(hvac_pattern, 50)
    data["Lighting"] = np.maximum(lighting_pattern, 10)
    data["Offices"] = np.maximum(office_pattern, 20)
    data["Server_Room"] = np.maximum(server_pattern, 100)
    data["Backup_Systems"] = np.maximum(basement_pattern, 5)
    
    data["Temperature_C"] = 20 + 8 * np.sin(np.linspace(0, 50, n_hours)) + np.random.normal(0, 1, n_hours)
    
    return data

df_full = generate_realistic_energy_data()

def filter_and_aggregate_data(df, start_date, end_date, agg_type):
    df_filtered = df[(df["Timestamp"].dt.date >= start_date) & 
                     (df["Timestamp"].dt.date <= end_date)].copy()
    
    if agg_type == "Hourly":
        return df_filtered
    elif agg_type == "Daily":
        df_filtered = df_filtered.set_index("Timestamp").resample("D").mean().reset_index()
    elif agg_type == "Weekly":
        df_filtered = df_filtered.set_index("Timestamp").resample("W").mean().reset_index()
    elif agg_type == "Monthly":
        df_filtered = df_filtered.set_index("Timestamp").resample("M").mean().reset_index()
    
    return df_filtered

df = filter_and_aggregate_data(df_full, date_range[0], date_range[1], aggregation_type)

def get_zone_data(df, zone_name):
    zone_mapping = {
        "Floor 1: HVAC System": "HVAC",
        "Floor 2: Lighting": "Lighting",
        "Floor 3: Offices": "Offices",
        "Server Room": "Server_Room",
        "Basement: Backup Systems": "Backup_Systems"
    }
    
    if zone_name == "All Zones":
        df["Power_Consumption_kW"] = df[["HVAC", "Lighting", "Offices", "Server_Room", "Backup_Systems"]].sum(axis=1)
    else:
        df["Power_Consumption_kW"] = df[zone_mapping[zone_name]]
    
    return df

df = get_zone_data(df, selected_zone)

def detect_anomalies_simple(data, column="Power_Consumption_kW", threshold_multiplier=2.5):
    mean_val = data[column].mean()
    std_val = data[column].std()
    
    upper_threshold = mean_val + (threshold_multiplier * std_val)
    lower_threshold = mean_val - (threshold_multiplier * std_val)
    
    anomalies = data[column].copy()
    normal_mask = (anomalies > lower_threshold) & (anomalies < upper_threshold)
    anomalies[normal_mask] = np.nan
    
    return anomalies, upper_threshold, lower_threshold

def forecast_power_simple(df, periods=72, column="Power_Consumption_kW"):
    window = 24
    data_array = df[column].values
    smoothed = np.convolve(data_array, np.ones(window)/window, mode='valid')
    
    recent_data = smoothed[-48:] if len(smoothed) >= 48 else smoothed
    trend = (recent_data[-1] - recent_data[0]) / len(recent_data) if len(recent_data) > 0 else 0
    
    last_timestamp = df["Timestamp"].iloc[-1]
    # Fixed frequency string here as well from "H" to "h" for safety
    forecast_timestamps = pd.date_range(start=last_timestamp, periods=periods+1, freq='h')[1:]
    forecast_values = recent_data[-1] + trend * np.arange(1, periods+1)
    forecast_values = np.maximum(forecast_values, df[column].min())
    
    forecast_df = pd.DataFrame({
        "Timestamp": forecast_timestamps,
        "Forecast": forecast_values,
        "Upper_Bound": forecast_values * 1.15,
        "Lower_Bound": forecast_values * 0.85
    })
    
    return forecast_df

st.markdown("---")
st.markdown("<div class='header-style'>📊 Quick Performance Overview</div>", unsafe_allow_html=True)

avg_consumption = df["Power_Consumption_kW"].mean()
peak_consumption = df["Power_Consumption_kW"].max()
min_consumption = df["Power_Consumption_kW"].min()
total_energy_kwh = df["Power_Consumption_kW"].sum() * (1 if aggregation_type == "Hourly" else 24)
estimated_cost = total_energy_kwh * cost_per_kwh
energy_std_dev = df["Power_Consumption_kW"].std()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Average Load", value=f"{avg_consumption:.2f} kW", delta=f"±{energy_std_dev:.2f} std")
with col2:
    st.metric(label="Peak Load", value=f"{peak_consumption:.2f} kW", delta=f"Min: {min_consumption:.2f} kW")
with col3:
    st.metric(label="Total Energy Used", value=f"{total_energy_kwh:.0f} kWh", delta=f"{aggregation_type} View")
with col4:
    st.metric(label="Estimated Bill", value=f"₹{estimated_cost:,.0f}", delta=f"@ ₹{cost_per_kwh}/kWh")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trend Analysis", 
    "🔍 Anomalies", 
    "🎯 Forecast", 
    "📊 Distribution", 
    "🔗 Temperature Impact", 
    "💰 Cost Breakdown"
])

with tab1:
    st.subheader("Power Consumption Line Chart")
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["Power_Consumption_kW"],
        mode='lines',
        name='Actual Power',
        line=dict(color='#0066cc', width=2),
        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>Power:</b> %{y:.2f} kW<extra></extra>'
    ))
    
    df["MA_24h"] = df["Power_Consumption_kW"].rolling(window=24, min_periods=1).mean()
    fig_trend.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["MA_24h"],
        mode='lines',
        name='24h Moving Average',
        line=dict(color='#ff6b6b', width=2, dash='dash'),
        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>MA:</b> %{y:.2f} kW<extra></extra>'
    ))
    
    fig_trend.update_layout(
        title=f"Consumption Trend for {selected_zone}",
        xaxis_title="Timeline",
        yaxis_title="Power (kW)",
        hovermode="x unified",
        template="plotly_white",
        height=450
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"⚡ Max Load Recorded At: {df.loc[df['Power_Consumption_kW'].idxmax(), 'Timestamp'].strftime('%Y-%m-%d %H:%M')}")
    with c2:
        st.info(f"💤 Min Load Recorded At: {df.loc[df['Power_Consumption_kW'].idxmin(), 'Timestamp'].strftime('%Y-%m-%d %H:%M')}")

with tab2:
    st.subheader("Sudden Power Spikes & Anomalies")
    
    if show_anomalies:
        anomalies, upper_thresh, lower_thresh = detect_anomalies_simple(df, threshold_multiplier=2.5)
        anomaly_count = anomalies.notna().sum()
        
        fig_anomaly = go.Figure()
        
        fig_anomaly.add_trace(go.Scatter(
            x=df["Timestamp"],
            y=df["Power_Consumption_kW"],
            mode='lines',
            name='Normal Range',
            line=dict(color='#0066cc', width=1.5)
        ))
        
        fig_anomaly.add_hline(y=upper_thresh, line_dash="dash", line_color="orange", annotation_text="Upper Limit")
        
        fig_anomaly.add_trace(go.Scatter(
            x=df["Timestamp"],
            y=anomalies,
            mode='markers',
            name='Anomaly Found',
            marker=dict(size=9, color='red', symbol='diamond')
        ))
        
        fig_anomaly.update_layout(
            title="Statistical Outlier Detection (2.5 Std Dev)",
            xaxis_title="Timeline",
            yaxis_title="Power (kW)",
            template="plotly_white",
            height=450
        )
        
        st.plotly_chart(fig_anomaly, use_container_width=True)
        
        if anomaly_count > 0:
            st.markdown(f"""
            <div class='warning-box'>
            <strong>⚠️ Total {anomaly_count} potential anomalies detect hue hain!</strong><br>
            Ye spikes kisi equipment failure ya sudden heavy load ki taraf ishara kar sakte hain.
            </div>
            """, unsafe_allow_html=True)
            
            anomaly_df = df[anomalies.notna()][["Timestamp", "Power_Consumption_kW"]]
            st.dataframe(anomaly_df.rename(columns={"Power_Consumption_kW": "Spike Power (kW)"}), use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            <div class='success-box'>
            <strong>✅ Sab kuch normal hai!</strong><br>
            Koi bada power anomaly nahi mila is time period mein.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sidebar se 'Anomaly Detection Enable' checkbox tick karo.")

with tab3:
    st.subheader("Next 72 Hours Power Forecast")
    
    if show_forecast:
        forecast_df = forecast_power_simple(df, periods=72)
        
        fig_forecast = go.Figure()
        
        fig_forecast.add_trace(go.Scatter(
            x=df["Timestamp"][-240:],
            y=df["Power_Consumption_kW"][-240:],
            mode='lines',
            name='Past Data',
            line=dict(color='#0066cc', width=2)
        ))
        
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Timestamp"],
            y=forecast_df["Forecast"],
            mode='lines',
            name='Predicted Trend',
            line=dict(color='#ffc107', width=2, dash='dash')
        ))
        
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Timestamp"],
            y=forecast_df["Upper_Bound"],
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Timestamp"],
            y=forecast_df["Lower_Bound"],
            fill='tonexty',
            line_color='rgba(0,0,0,0)',
            name='Confidence Band',
            fillcolor='rgba(255, 193, 7, 0.2)',
            hoverinfo='skip'
        ))
        
        fig_forecast.update_layout(
            title="Short-term Exponential Smoothing Forecast",
            xaxis_title="Timeline",
            yaxis_title="Power (kW)",
            template="plotly_white",
            height=450
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        f_avg = forecast_df["Forecast"].mean()
        f_peak = forecast_df["Forecast"].max()
        f_cost = forecast_df["Forecast"].sum() * cost_per_kwh * 3
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.metric("Expected Avg Load", f"{f_avg:.2f} kW")
        with col_f2:
            st.metric("Expected Peak Load", f"{f_peak:.2f} kW")
        with col_f3:
            st.metric("Projected Cost (3 Days)", f"₹{f_cost:,.0f}")
    else:
        st.info("Sidebar se 'Predictive Forecast' enable karo.")

with tab4:
    st.subheader("Load Spread & Hourly Distribution")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_hist = px.histogram(
            df, x="Power_Consumption_kW", nbins=30,
            title="Load Frequency Histogram",
            labels={"Power_Consumption_kW": "Power (kW)"},
            color_discrete_sequence=["#0066cc"]
        )
        fig_hist.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col_d2:
        fig_box = px.box(
            df, x="Hour", y="Power_Consumption_kW",
            title="Hourly Variations (Boxplot)",
            labels={"Hour": "Hour of Day", "Power_Consumption_kW": "Power (kW)"},
            color_discrete_sequence=["#ff6b6b"]
        )
        fig_box.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_box, use_container_width=True)

with tab5:
    st.subheader("Ambient Temperature vs Energy Correlation")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_scatter = px.scatter(
            df, x="Temperature_C", y="Power_Consumption_kW",
            title="Temperature vs Load Correlation",
            labels={"Temperature_C": "Temp (°C)", "Power_Consumption_kW": "Power (kW)"},
            opacity=0.5, color_discrete_sequence=["#0066cc"]
        )
        
        z = np.polyfit(df["Temperature_C"].dropna(), df["Power_Consumption_kW"].dropna(), 1)
        p = np.poly1d(z)
        x_vals = np.linspace(df["Temperature_C"].min(), df["Temperature_C"].max(), 100)
        fig_scatter.add_trace(go.Scatter(x=x_vals, y=p(x_vals), mode='lines', name='Fit Trend', line=dict(color='red', dash='dash')))
        
        fig_scatter.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_c2:
        corr_val = df["Temperature_C"].corr(df["Power_Consumption_kW"])
        st.info(f"""
        **Statistical Insights:**
        - **Correlation Value:** {corr_val:.3f}
        - Yeh batata hai ki temperature badhne par building ka energy load kitna affect hota hai (jaise AC/HVAC load).
        """)
        
        daily_avg = df.groupby(df["Timestamp"].dt.date).agg({
            "Power_Consumption_kW": "mean",
            "Temperature_C": "mean"
        }).reset_index().tail(5)
        
        st.write("**Recent Days Average:**")
        st.dataframe(daily_avg.rename(columns={"Timestamp": "Date", "Power_Consumption_kW": "Avg Power", "Temperature_C": "Avg Temp"}), use_container_width=True, hide_index=True)

with tab6:
    st.subheader("Cost Optimization & Hourly Expenses")
    
    df["Cost"] = df["Power_Consumption_kW"] * cost_per_kwh
    hourly_cost = df.groupby(df["Timestamp"].dt.hour)["Cost"].mean().reset_index()
    
    col_cc1, col_cc2 = st.columns([2, 1])
    with col_cc1:
        fig_cost = px.bar(
            hourly_cost, x="Timestamp", y="Cost",
            title="Average Hourly Electricity Expense",
            labels={"Timestamp": "Hour", "Cost": "Cost (₹)"},
            color="Cost", color_continuous_scale="RdYlGn_r"
        )
        fig_cost.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_cost, use_container_width=True)
        
    with col_cc2:
        st.write("**Top 5 Costliest Hours:**")
        sorted_costs = hourly_cost.sort_values("Cost", ascending=False)
        for _, row in sorted_costs.head(5).iterrows():
            st.write(f"⏰ {int(row['Timestamp']):02d}:00 hrs ➔ ₹{row['Cost']:.2f}/hr")

st.markdown("---")
st.markdown("<div class='header-style'>💡 AI & Sensor Insights / Recommendations</div>", unsafe_allow_html=True)

peak_hours_mean = df.groupby(df["Timestamp"].dt.hour)["Power_Consumption_kW"].mean()
p_hour = peak_hours_mean.idxmax()
l_hour = peak_hours_mean.idxmin()
p_pow = peak_hours_mean.max()
l_pow = peak_hours_mean.min()
est_savings = (p_pow - l_pow) * 24 * 30 * cost_per_kwh

recs = [
    {
        "tag": "🔴 HIGH PRIORITY",
        "title": "Shift Heavy Operations to Off-Peak",
        "desc": f"Peak consumption usually {p_hour}:00 ke aas-pass hoti hai. Heavy machinery ya workloads ko off-peak hours ({l_hour}:00) mein shift karne se bill kam ho sakta hai.",
        "save": f"Estimated Savings: ₹{est_savings*0.3:,.0f} / month"
    },
    {
        "tag": "🟡 MEDIUM PRIORITY",
        "title": "HVAC Smart Automation",
        "desc": "Temperature aur power consumption mein high correlation hai. Building management systems (BMS) mein smart timers lagayein.",
        "save": f"Estimated Savings: ₹{est_savings*0.2:,.0f} / month"
    }
]

for r in recs:
    c_r1, c_r2 = st.columns([0.2, 0.8])
    with c_r1:
        st.markdown(f"**{r['tag']}**")
    with c_r2:
        st.markdown(f"**{r['title']}**")
    st.write(r['desc'])
    st.success(r['save'])
    st.markdown("---")

st.markdown("<div class='header-style'>📥 Export Clean Dataset & Reports</div>", unsafe_allow_html=True)
ex1, ex2, ex3 = st.columns(3)

with ex1:
    st.download_button(
        label="Download Filtered CSV",
        data=df.to_csv(index=False),
        file_name="smart_building_data.csv",
        mime="text/csv"
    )

with ex2:
    if show_forecast:
        fc_csv = forecast_power_simple(df, 72).to_csv(index=False)
        st.download_button(
            label="Download 72h Forecast CSV",
            data=fc_csv,
            file_name="energy_forecast.csv",
            mime="text/csv"
        )

with ex3:
    report_summary = f"Smart Building Report - Zone: {selected_zone}\nAvg Load: {avg_consumption:.2f}kW\nTotal Energy: {total_energy_kwh:.0f}kWh"
    st.download_button(
        label="Download Text Report",
        data=report_summary,
        file_name="energy_report.txt",
        mime="text/plain"
    )

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚡ <strong>Smart Building Energy Analytics Dashboard</strong> • Built with Streamlit & Plotly</p>
    <p>B.Tech Minor Project Work</p>
</div>
""", unsafe_allow_html=True)
