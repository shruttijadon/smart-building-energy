
Smart Building Energy Analytics & Optimization Platform

B.Tech Minor Project - A comprehensive dashboard built with Streamlit and Plotly to track, analyze, and forecast power consumption across different building zones.

---

 Project Overview

Smart buildings leverage advanced IoT sensors, automated HVAC controls, and real-time data analytics to drastically reduce energy waste and lower operational costs. By continuously monitoring power consumption patterns across different building zones—such as offices, server rooms, and lighting grids—facility managers can identify efficiency bottlenecks, detect sudden load anomalies, and automatically adjust systems in response to ambient temperature changes. Integrating predictive forecasting models further empowers building operators to shift heavy energy workloads to off-peak hours, ensuring a sustainable, cost-effective, and environmentally friendly infrastructure for the future.

---

Key Features

* **Multi-Zone Monitoring:** Track power usage across HVAC systems, lighting, offices, server rooms, and basement backup systems.
* **Statistical Anomaly Detection:** Automatically detects sudden power spikes and anomalies using rolling standard deviation thresholds.
* **Short-Term Predictive Forecasting:** Forecasts power load for the next 72 hours using exponential smoothing trends.
* **Cost Optimization & Rate Calculator:** Calculates real-time electricity expenses based on custom customizable tariffs (₹ per kWh).
* **Interactive Visualizations:** Powered by Plotly for dynamic trends, boxplots, histograms, and temperature-load correlation scatter plots.
* **Data Export:** Download filtered datasets, 3-day forecast CSVs, and text summaries instantly.

 Tech Stack

* **Frontend & Dashboard:** [Streamlit](https://streamlit.io/)
* **Data Manipulation & Analysis:** Python, Pandas, NumPy
* **Data Visualization:** Plotly Express & Graph Objects

---

 Installation & Running Locally



1. **Repository Clone Karein:**
   ```bash
   git clone <your-repository-url>
   cd smart-building-energy
