# DisasterTracker Dashboard

A real-time disaster response dashboard for visualizing earthquakes and wildfires, built with Python, Streamlit, and Folium.

## Features

- Live tracking of earthquakes and fires using public data
- Interactive map with filters by magnitude, confidence, and event type
- Country-specific date range selection
- Earthquake forecasting using historical trends
- Expandable view of raw data

python -m venv venv
venv\Scripts\activate        # On Windows
# or
source venv/bin/activate     # On Mac/Linux
pip install -r requirements.txt
disastertracker/
├── app.py                     # Main Streamlit dashboard
├── etl/
│   ├── fetch_earthquakes.py   # Earthquake data collection and preprocessing
│   └── fetch_fires.py         # Fire data collection
├── data/
│   ├── earthquakes.csv        # Cleaned and enriched earthquake data
│   └── fires.csv              # Cleaned fire data
├── requirements.txt
└── README.md

Data Sources
Earthquakes: USGS (United States Geological Survey)

Fires: NASA FIRMS (Fire Information for Resource Management System)

Notes
Earthquake forecasting is performed using ARIMA models (statsmodels)

The dashboard works fully offline once data CSVs are generated

Filters for magnitude, confidence, country, and date are available in the sidebar

This project is provided for educational and portfolio use
