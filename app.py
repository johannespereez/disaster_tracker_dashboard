import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium import Element
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

st.set_page_config(layout="wide")
st.title("Disaster Response Dashboard")
st.caption("Live earthquake and fire tracking (USGS & NASA FIRMS)")

# === Load and clean earthquake data ===
eq_df = pd.read_csv("data/earthquakes.csv")
eq_df["time"] = pd.to_datetime(eq_df["time"], errors="coerce")
eq_df = eq_df.dropna(subset=["latitude", "longitude", "magnitude", "time", "country"])

# === Load and clean fire data ===
fire_df = pd.read_csv("data/fires.csv")
fire_df = fire_df.dropna(subset=["latitude", "longitude", "confidence"])
fire_df["latitude"] = pd.to_numeric(fire_df["latitude"], errors="coerce")
fire_df["longitude"] = pd.to_numeric(fire_df["longitude"], errors="coerce")
fire_df["confidence"] = pd.to_numeric(fire_df["confidence"], errors="coerce")
fire_df = fire_df.dropna(subset=["latitude", "longitude", "confidence"])

# === Sidebar Filters ===
st.sidebar.header("Filters")
min_mag = st.sidebar.slider("Minimum Earthquake Magnitude", 0.0, 10.0, 3.0, 0.1)
min_conf = st.sidebar.slider("Minimum Fire Confidence", 0, 100, 50, 1)
view_option = st.sidebar.selectbox("Display", ["Both", "Earthquakes", "Fires"])

# Handle date filter safely
if not eq_df.empty:
    start_date = eq_df["time"].min().date()
    end_date = eq_df["time"].max().date()
else:
    start_date = end_date = pd.Timestamp.today().date()

date_range = st.sidebar.date_input("Date Range", [start_date, end_date])
country_options = eq_df["country"].dropna().unique().tolist()
country_filter = st.sidebar.selectbox("Country (for Forecast)", ["All"] + sorted(country_options))

# === Apply Filters ===
eq_filtered = eq_df[
    (eq_df["magnitude"] >= min_mag) &
    (eq_df["time"].dt.date >= date_range[0]) &
    (eq_df["time"].dt.date <= date_range[1])
]

if country_filter != "All":
    eq_filtered = eq_filtered[eq_filtered["country"] == country_filter]

fire_filtered = fire_df[fire_df["confidence"] >= min_conf]

st.write(f"Earthquakes after filter: {eq_filtered.shape[0]}")
st.write(f"Fires after filter: {fire_filtered.shape[0]}")

# === Map Center ===
avg_lat = eq_filtered["latitude"].mean() if not eq_filtered.empty else 0
avg_lon = eq_filtered["longitude"].mean() if not eq_filtered.empty else 0

m = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)

# === Earthquake Markers ===
if view_option in ["Both", "Earthquakes"]:
    for _, row in eq_filtered.iterrows():
        icon = folium.Icon(color="red", icon="glyphicon glyphicon-exclamation-sign", prefix="glyphicon")
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            tooltip=f"Magnitude {row['magnitude']} - {row['place']}",
            icon=icon
        ).add_to(m)

# === Fire Markers ===
if view_option in ["Both", "Fires"]:
    fire_limited = fire_filtered.head(1000)
    for _, row in fire_limited.iterrows():
        icon = folium.Icon(color="orange", icon="fa-fire", prefix="fa")
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            tooltip=f"Brightness: {row.get('brightness', '')}, Confidence: {row['confidence']}%",
            icon=icon
        ).add_to(m)

# Add debug marker
folium.Marker([14.5995, 120.9842], tooltip="Manila").add_to(m)

# === Legend ===
legend_html = """
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
<div style="position: fixed; bottom: 50px; left: 50px; width: 160px; background-color: white; border:2px solid gray; z-index:9999; font-size:14px; padding: 10px;">
    <b>Legend</b><br>
    <i class="fa fa-fire" style="color:orange"></i> Fire<br>
    <i class="glyphicon glyphicon-exclamation-sign" style="color:red"></i> Earthquake<br>
    <span style="color:gray;">Manila (test)</span>
</div>
"""
m.get_root().html.add_child(Element(legend_html))

# === Show Map ===
st.subheader("Live Map")
st_data = st_folium(m, width=1200, height=600)

# === Forecasting ===
st.subheader("Earthquake Forecast (Next 7 Days)")
forecast_df = eq_df.copy()
if country_filter != "All":
    forecast_df = forecast_df[forecast_df["country"] == country_filter]

forecast_df["date"] = forecast_df["time"].dt.date
daily_counts = forecast_df.groupby("date").size().reset_index(name="count")
daily_counts = daily_counts.sort_values("date")

if len(daily_counts) >= 14:
    try:
        model = ARIMA(daily_counts["count"], order=(2, 1, 2))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=7)
        future_dates = pd.date_range(start=daily_counts["date"].max() + timedelta(days=1), periods=7)
        forecast_df = pd.DataFrame({"date": future_dates, "count": forecast})
        combined_df = pd.concat([daily_counts, forecast_df], ignore_index=True)

        st.line_chart(combined_df.set_index("date"))
    except Exception as e:
        st.warning(f"Forecasting failed: {e}")
else:
    st.info("Not enough data to generate a 7-day forecast.")

# === Raw Data ===
with st.expander("View Raw Data"):
    if view_option in ["Both", "Earthquakes"]:
        st.write("Earthquakes", eq_filtered)
    if view_option in ["Both", "Fires"]:
        st.write("Fires", fire_filtered)
