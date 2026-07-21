import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(
    page_title="Advanced Smart Building Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
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
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
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


st.title("⚡ Advanced Smart Building Energy Analytics & Optimization")
st.markdown("""
**Comprehensive energy management platform** - Real-time monitoring, predictive analytics, 
anomaly detection, aur cost optimization ke liye. Aapke building ke har zone ka detailed analysis!
""")


st.sidebar.header("🎛️ Control Panel")
st.sidebar.markdown("---")

# Zone selection
zones_list = ["All Zones", "Floor 1: HVAC System", "Floor 2: Lighting", "Floor 3: Offices", "Server Room", "Basement: Backup Systems"]
selected_zone = st.sidebar.selectbox("Select Building Zone", zones_list)

# Date range filter
st.sidebar.markdown("**📅 Time Range Selection**")
date_range = st.sidebar.date_input(
    "Select date range",
    value=(datetime(2026, 1, 1), datetime(2026, 7, 1)),
    min_value=datetime(2026, 1, 1),
    max_value=datetime(2026, 7, 1)
)

# Aggregation level
aggregation_type = st.sidebar.radio(
    "Data Aggregation Level",
    ["Hourly", "Daily", "Weekly", "Monthly"]
)

# Advanced filters
st.sidebar.markdown("**🔍 Advanced Filters**")
show_anomalies = st.sidebar.checkbox("Anomaly Detection Enable karein", value=True)
show_forecast = st.sidebar.checkbox("Predictive Forecast Dikhayein", value=True)
cost_per_kwh = st.sidebar.number_input("Cost per kWh (₹)", value=8.5, min_value=0.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Advanced analytics se energy wastage identify karein aur costs reduce karein!")


@st.cache_data
def generate_realistic_energy_data():
    """Realistic energy consumption data for different zones"""
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-01-01", end="2026-07-01", freq="1H")
    
    # Base data
    n_hours = len(timestamps)
    
    # Different consumption patterns for each zone
    data = pd.DataFrame({
        "Timestamp": timestamps,
        "Hour": timestamps.hour,
        "Day_of_Week": timestamps.dayofweek,
        "Month": timestamps.month
    })
    
    # Floor 1: HVAC (sine wave pattern - peak during morning/evening)
    hvac_base = 150 + 40 * np.sin(np.linspace(0, 50, n_hours))
    hvac_noise = np.random.normal(0, 8, n_hours)
    hvac_pattern = np.where(
        data["Hour"].isin([6, 7, 8, 9, 17, 18, 19, 20]),
        hvac_base * 1.3 + hvac_noise,
        hvac_base * 0.8 + hvac_noise
    )
    
    # Floor 2: Lighting (peak during business hours)
    lighting_pattern = np.where(
        data["Hour"].isin(range(8, 18)),
        np.random.normal(80, 10, n_hours),
        np.random.normal(20, 5, n_hours)
    )
    
    # Floor 3: Offices (variable, peaks during business hours)
    office_pattern = np.where(
        data["Hour"].isin(range(8, 18)),
        np.random.normal(120, 15, n_hours),
        np.random.normal(40, 8, n_hours)
    )
    
    # Server Room (constant high load)
    server_pattern = np.random.normal(200, 20, n_hours)
    
    # Basement: Backup Systems (very low, spike during testing)
    basement_pattern = np.random.normal(15, 3, n_hours)
    basement_pattern[::504] *= 5  # Weekly spike
    
    # Add data to dataframe
    data["HVAC"] = np.maximum(hvac_pattern, 50)
    data["Lighting"] = np.maximum(lighting_pattern, 10)
    data["Offices"] = np.maximum(office_pattern, 20)
    data["Server_Room"] = np.maximum(server_pattern, 100)
    data["Backup_Systems"] = np.maximum(basement_pattern, 5)
    
    # Add temperature correlation
    data["Temperature_C"] = 20 + 8 * np.sin(np.linspace(0, 50, n_hours)) + np.random.normal(0, 1, n_hours)
    
    return data

# Load data
df_full = generate_realistic_energy_data()


def filter_and_aggregate_data(df, start_date, end_date, agg_type):
    """Filter data by date range and aggregate"""
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

# Apply filters
df = filter_and_aggregate_data(df_full, date_range[0], date_range[1], aggregation_type)

# Get selected zone data
def get_zone_data(df, zone_name):
    """Extract specific zone consumption"""
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


def detect_anomalies(data, column="Power_Consumption_kW", threshold=2):
    """Detect anomalies using Z-score"""
    z_scores = np.abs(stats.zscore(data[column].dropna()))
    anomaly_mask = z_scores > threshold
    
    anomalies = data[column].copy()
    anomalies[~data[column].index.isin(data[column][anomaly_mask].index)] = np.nan
    
    return anomalies

# ============================================================================
# FORECASTING FUNCTION
# ============================================================================
def forecast_power(df, periods=72, column="Power_Consumption_kW"):
    """Simple exponential smoothing forecast"""
    from scipy.ndimage import uniform_filter1d
    
    # Moving average for smoothing
    window = 24
    smoothed = uniform_filter1d(df[column].values, size=window, mode='nearest')
    
    # Simple trend calculation
    recent_data = smoothed[-48:]
    trend = (recent_data[-1] - recent_data[0]) / len(recent_data)
    
    # Generate forecast
    last_timestamp = df["Timestamp"].iloc[-1]
    forecast_timestamps = pd.date_range(start=last_timestamp, periods=periods+1, freq='H')[1:]
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
st.markdown("<div class='header-style'>📊 Key Performance Metrics</div>", unsafe_allow_html=True)

# Calculate metrics
avg_consumption = df["Power_Consumption_kW"].mean()
peak_consumption = df["Power_Consumption_kW"].max()
min_consumption = df["Power_Consumption_kW"].min()
total_energy_kwh = df["Power_Consumption_kW"].sum() * (1 if aggregation_type == "Hourly" else 24)
estimated_cost = total_energy_kwh * cost_per_kwh
energy_std_dev = df["Power_Consumption_kW"].std()

# Display metrics in 4 columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Average Load",
        value=f"{avg_consumption:.2f} kW",
        delta=f"Std Dev: ±{energy_std_dev:.2f}"
    )

with col2:
    st.metric(
        label="Peak Load",
        value=f"{peak_consumption:.2f} kW",
        delta=f"Min: {min_consumption:.2f} kW"
    )

with col3:
    st.metric(
        label="Total Energy Used",
        value=f"{total_energy_kwh:.0f} kWh",
        delta=f"Period: {aggregation_type}"
    )

with col4:
    st.metric(
        label="Estimated Cost",
        value=f"₹{estimated_cost:,.0f}",
        delta=f"@ ₹{cost_per_kwh}/kWh"
    )


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📈 Trend Analysis", "🔍 Anomalies", "🎯 Forecast", "📊 Distribution", "🔗 Correlation", "💰 Cost Analysis"]
)

with tab1:
    st.subheader("Interactive Power Consumption Trend")
    
    # Main line chart with zone data
    fig_trend = go.Figure()
    
    # Add actual consumption line
    fig_trend.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["Power_Consumption_kW"],
        mode='lines',
        name='Actual Consumption',
        line=dict(color='#0066cc', width=2),
        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>Power:</b> %{y:.2f} kW<extra></extra>'
    ))
    
    # Add moving average
    df["MA_24h"] = df["Power_Consumption_kW"].rolling(window=24, min_periods=1).mean()
    fig_trend.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["MA_24h"],
        mode='lines',
        name='24-Hour Moving Avg',
        line=dict(color='#ff6b6b', width=2, dash='dash'),
        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>MA:</b> %{y:.2f} kW<extra></extra>'
    ))
    
    fig_trend.update_layout(
        title=f"Energy Consumption Trend - {selected_zone} ({aggregation_type} Data)",
        xaxis_title="Timeline",
        yaxis_title="Power Consumption (kW)",
        hovermode="x unified",
        template="plotly_white",
        height=500,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255, 255, 255, 0.8)")
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Statistics box
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.info(f"**Peak Time:** {df.loc[df['Power_Consumption_kW'].idxmax(), 'Timestamp'].strftime('%Y-%m-%d %H:%M')}")
    with col_stat2:
        st.info(f"**Low Time:** {df.loc[df['Power_Consumption_kW'].idxmin(), 'Timestamp'].strftime('%Y-%m-%d %H:%M')}")


with tab2:
    st.subheader("🔍 Anomaly Detection & Alert System")
    
    if show_anomalies:
        # Detect anomalies
        anomalies = detect_anomalies(df, threshold=2)
        anomaly_count = anomalies.notna().sum()
        
        # Display anomaly chart
        fig_anomaly = go.Figure()
        
        fig_anomaly.add_trace(go.Scatter(
            x=df["Timestamp"],
            y=df["Power_Consumption_kW"],
            mode='lines',
            name='Normal Consumption',
            line=dict(color='#0066cc', width=2),
            hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>Power:</b> %{y:.2f} kW<extra></extra>'
        ))
        
        fig_anomaly.add_trace(go.Scatter(
            x=df["Timestamp"],
            y=anomalies,
            mode='markers',
            name='Anomaly Detected',
            marker=dict(size=10, color='red', symbol='diamond'),
            hovertemplate='<b>Anomaly at:</b> %{x|%Y-%m-%d %H:%M}<br><b>Power:</b> %{y:.2f} kW<extra></extra>'
        ))
        
        fig_anomaly.update_layout(
            title="Anomaly Detection in Power Consumption",
            xaxis_title="Timeline",
            yaxis_title="Power (kW)",
            hovermode="x unified",
            template="plotly_white",
            height=500
        )
        
        st.plotly_chart(fig_anomaly, use_container_width=True)
        
        # Anomaly summary
        if anomaly_count > 0:
            st.markdown(f"""
            <div class='warning-box'>
            <strong>⚠️ {anomaly_count} Anomalies Detected!</strong><br>
            Ye unusual power spikes ho sakte hain jo investigation karte hain. 
            Check karein ki kya equipment malfunction ya unexpected load surge hua hai.
            </div>
            """, unsafe_allow_html=True)
            
            # Show anomaly details
            anomaly_times = df[anomalies.notna()][["Timestamp", "Power_Consumption_kW"]]
            if len(anomaly_times) > 0:
                st.write("**Anomaly Details:**")
                st.dataframe(
                    anomaly_times.rename(columns={"Power_Consumption_kW": "Power (kW)"}),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.markdown("""
            <div class='success-box'>
            <strong>✅ No Anomalies Detected</strong><br>
            Power consumption normal range mein hai!
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Anomaly detection enable karein sidebar se")


with tab3:
    st.subheader("🎯 72-Hour Power Consumption Forecast")
    
    if show_forecast:
        # Generate forecast
        forecast_df = forecast_power(df, periods=72)
        
        # Combine actual and forecast
        fig_forecast = go.Figure()
        
        # Historical data
        fig_forecast.add_trace(go.Scatter(
            x=df["Timestamp"][-240:],  # Last 10 days
            y=df["Power_Consumption_kW"][-240:],
            mode='lines',
            name='Historical Data',
            line=dict(color='#0066cc', width=2),
            hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>Power:</b> %{y:.2f} kW<extra></extra>'
        ))
        
        # Forecast
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Timestamp"],
            y=forecast_df["Forecast"],
            mode='lines',
            name='Forecast',
            line=dict(color='#ffc107', width=2, dash='dash'),
            hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M}<br><b>Forecast:</b> %{y:.2f} kW<extra></extra>'
        ))
        
        # Confidence bands
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Timestamp"],
            y=forecast_df["Upper_Bound"],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["Timestamp"],
            y=forecast_df["Lower_Bound"],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            name='Confidence Range (±15%)',
            fillcolor='rgba(255, 193, 7, 0.2)',
            hoverinfo='skip'
        ))
        
        fig_forecast.update_layout(
            title="72-Hour Predictive Forecast with Confidence Interval",
            xaxis_title="Timeline",
            yaxis_title="Power (kW)",
            hovermode="x unified",
            template="plotly_white",
            height=500,
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(255, 255, 255, 0.8)")
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Forecast summary
        forecast_avg = forecast_df["Forecast"].mean()
        forecast_peak = forecast_df["Forecast"].max()
        forecast_cost = forecast_df["Forecast"].sum() * cost_per_kwh * 3  # 72 hours = 3 days
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.metric("Avg Forecast Load", f"{forecast_avg:.2f} kW")
        with col_f2:
            st.metric("Peak Forecast", f"{forecast_peak:.2f} kW")
        with col_f3:
            st.metric("Est. Cost (72h)", f"₹{forecast_cost:,.0f}")
    else:
        st.info("Forecast enable karein sidebar se")


with tab4:
    st.subheader("📊 Power Consumption Distribution")
    
    col_dist1, col_dist2 = st.columns(2)
    
    with col_dist1:
        # Histogram
        fig_hist = px.histogram(
            df,
            x="Power_Consumption_kW",
            nbins=30,
            title="Power Consumption Distribution",
            labels={"Power_Consumption_kW": "Power (kW)", "count": "Frequency"},
            color_discrete_sequence=["#0066cc"]
        )
        fig_hist.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_dist2:
        # Box plot by hour of day
        fig_box = px.box(
            df,
            x="Hour",
            y="Power_Consumption_kW",
            title="Power Variation by Hour of Day",
            labels={"Hour": "Hour of Day", "Power_Consumption_kW": "Power (kW)"},
            color_discrete_sequence=["#ff6b6b"]
        )
        fig_box.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_box, use_container_width=True)


with tab5:
    st.subheader("🔗 Energy-Temperature Correlation")
    
    col_corr1, col_corr2 = st.columns(2)
    
    with col_corr1:
        # Scatter plot
        fig_scatter = px.scatter(
            df,
            x="Temperature_C",
            y="Power_Consumption_kW",
            title="Power vs Temperature Correlation",
            labels={"Temperature_C": "Temperature (°C)", "Power_Consumption_kW": "Power (kW)"},
            opacity=0.6,
            color_discrete_sequence=["#0066cc"]
        )
        
        # Add trendline
        z = np.polyfit(df["Temperature_C"].dropna(), df["Power_Consumption_kW"].dropna(), 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df["Temperature_C"].min(), df["Temperature_C"].max(), 100)
        fig_scatter.add_trace(go.Scatter(x=x_trend, y=p(x_trend), mode='lines', name='Trend', line=dict(color='red', dash='dash')))
        
        fig_scatter.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_corr2:
        # Correlation stats
        correlation = df["Temperature_C"].corr(df["Power_Consumption_kW"])
        
        st.info(f"""
        **Correlation Coefficient:** {correlation:.3f}
        
        • {abs(correlation):.1%} strength ka relationship hai
        • {'Positive' if correlation > 0 else 'Negative'} correlation
        • Agar temperature badhega to power {'badhega' if correlation > 0 else 'kam hoga'}
        """)
        
        # Daily average comparison
        daily_stats = df.groupby(df["Timestamp"].dt.date).agg({
            "Power_Consumption_kW": "mean",
            "Temperature_C": "mean"
        }).reset_index()
        
        st.write("**Daily Averages:**")
        st.dataframe(
            daily_stats.rename(columns={
                "Timestamp": "Date",
                "Power_Consumption_kW": "Avg Power (kW)",
                "Temperature_C": "Avg Temp (°C)"
            }),
            use_container_width=True,
            hide_index=True
        )

with tab6:
    st.subheader("💰 Cost Analysis & Savings Opportunity")
    
    col_cost1, col_cost2 = st.columns([2, 1])
    
    with col_cost1:
        # Cost breakdown by hour
        df["Cost"] = df["Power_Consumption_kW"] * cost_per_kwh
        hourly_cost = df.groupby(df["Timestamp"].dt.hour)["Cost"].mean().reset_index()
        
        fig_cost = px.bar(
            hourly_cost,
            x="Timestamp",
            y="Cost",
            title="Average Hourly Cost Distribution",
            labels={"Timestamp": "Hour of Day", "Cost": "Avg Cost (₹)"},
            color="Cost",
            color_continuous_scale="RdYlGn_r"
        )
        fig_cost.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_cost, use_container_width=True)
    
    with col_cost2:
        # Cost by hour ranking
        hourly_cost_sorted = hourly_cost.sort_values("Cost", ascending=False)
        st.write("**Most Expensive Hours:**")
        for idx, row in hourly_cost_sorted.head(5).iterrows():
            st.write(f"🕐 {int(row['Timestamp']):02d}:00 - ₹{row['Cost']:.2f}")

st.markdown("---")
st.markdown("<div class='header-style'>💡 AI-Powered Optimization Recommendations</div>", unsafe_allow_html=True)

# Calculate savings opportunities
peak_hours = df.groupby(df["Timestamp"].dt.hour)["Power_Consumption_kW"].mean()
peak_hour = peak_hours.idxmax()
low_hour = peak_hours.idxmin()
peak_power = peak_hours.max()
low_power = peak_hours.min()

potential_savings_percent = ((peak_power - low_power) / peak_power) * 100
potential_savings_rs = (peak_power - low_power) * 24 * 30 * cost_per_kwh

recommendations = []

# Recommendation 1: Load Shifting
recommendations.append({
    "priority": "🔴 HIGH",
    "title": "Load Shifting Strategy",
    "description": f"{peak_hour}:00-{peak_hour+2}:00 ke beech peak load hota hai. "
                  f"Heavy operations ko off-peak hours ({low_hour}:00-{low_hour+2}:00) mein shift karein.",
    "savings": f"₹{potential_savings_rs*0.3:,.0f}/month"
})

# Recommendation 2: Thermal Management
temp_correlation = df["Temperature_C"].corr(df["Power_Consumption_kW"])
if abs(temp_correlation) > 0.5:
    recommendations.append({
        "priority": "🟡 MEDIUM",
        "title": "Thermal Regulation Upgrade",
        "description": "HVAC system ki efficiency improve karein. Smart thermostats lagayein jo temperature ko automatically control karein.",
        "savings": f"₹{potential_savings_rs*0.2:,.0f}/month"
    })

# Recommendation 3: Anomaly Handling
anomaly_count = detect_anomalies(df, threshold=2).notna().sum()
if anomaly_count > 0:
    recommendations.append({
        "priority": "🔴 HIGH",
        "title": "Address Anomalies",
        "description": f"{anomaly_count} unusual power spikes detected. Equipment inspection karein aur faults fix karein.",
        "savings": f"₹{potential_savings_rs*0.15:,.0f}/month"
    })

# Recommendation 4: Peak Shaving
recommendations.append({
    "priority": "🟡 MEDIUM",
    "title": "Peak Shaving with Battery Storage",
    "description": "Battery energy storage system install karein jо peak hours mein load handle kare aur grid se demand reduce kare.",
    "savings": f"₹{potential_savings_rs*0.25:,.0f}/month"
})

# Display recommendations
for i, rec in enumerate(recommendations, 1):
    with st.container():
        col_rec1, col_rec2 = st.columns([0.15, 0.85])
        with col_rec1:
            st.markdown(f"### {rec['priority']}")
        with col_rec2:
            st.markdown(f"### {i}. {rec['title']}")
        
        st.write(rec['description'])
        st.success(f"**Potential Savings: {rec['savings']}**")
        st.markdown("---")


st.markdown("---")
st.markdown("<div class='header-style'>📥 Data Export & Download</div>", unsafe_allow_html=True)

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    # Export filtered data
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📊 Download Filtered Data (CSV)",
        data=csv_data,
        file_name=f"energy_data_{selected_zone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col_exp2:
    # Export forecast
    if show_forecast:
        forecast_df_temp = forecast_power(df, periods=72)
        csv_forecast = forecast_df_temp.to_csv(index=False)
        st.download_button(
            label="📈 Download Forecast (CSV)",
            data=csv_forecast,
            file_name=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col_exp3:
    # Export summary report
    summary_text = f"""
SMART BUILDING ENERGY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ZONE: {selected_zone}
PERIOD: {date_range[0]} to {date_range[1]}
AGGREGATION: {aggregation_type}

=== KEY METRICS ===
Average Consumption: {avg_consumption:.2f} kW
Peak Consumption: {peak_consumption:.2f} kW
Minimum Consumption: {min_consumption:.2f} kW
Total Energy Used: {total_energy_kwh:.0f} kWh
Estimated Cost: ₹{estimated_cost:,.0f}

=== ANOMALIES ===
Anomalies Detected: {detect_anomalies(df, threshold=2).notna().sum()}

=== FORECAST ===
72-Hour Average Forecast: {forecast_power(df, periods=72)['Forecast'].mean():.2f} kW

=== TEMPERATURE ===
Avg Temperature: {df['Temperature_C'].mean():.2f}°C
Correlation with Power: {df['Temperature_C'].corr(df['Power_Consumption_kW']):.3f}

=== RECOMMENDATIONS ===
"""
    for rec in recommendations[:3]:
        summary_text += f"\n{rec['title']}: {rec['savings']}"
    
    st.download_button(
        label="📄 Download Summary Report",
        data=summary_text,
        file_name=f"energy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )


st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 30px;'>
    <p>⚡ <strong>Smart Building Energy Analytics System v2.0</strong></p>
    <p>Real-time monitoring • Predictive Analytics • Cost Optimization</p>
    <p style='font-size: 12px;'>Data updated every hour | Next update: {}</p>
</div>
""".format((datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')), unsafe_allow_html=True)
