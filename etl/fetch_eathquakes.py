import pandas as pd
import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import os

# === Fetch Data ===
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"
response = requests.get(URL)
with open("data/earthquakes_raw.csv", "wb") as f:
    f.write(response.content)

df = pd.read_csv("data/earthquakes_raw.csv")
df = df.dropna(subset=["latitude", "longitude", "time", "mag"])
df = df.rename(columns={"mag": "magnitude"})
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.dropna(subset=["time"])

# === Reverse Geocoding Setup ===
geolocator = Nominatim(user_agent="disaster_dashboard")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, error_wait_seconds=10.0)

# Optional: Use a local cache to avoid repeating geocoding
cache_file = "data/geocache.csv"
if os.path.exists(cache_file):
    geocache = pd.read_csv(cache_file)
else:
    geocache = pd.DataFrame(columns=["lat", "lon", "country"])

def lookup_country(lat, lon):
    cached = geocache[(geocache["lat"] == lat) & (geocache["lon"] == lon)]
    if not cached.empty:
        return cached.iloc[0]["country"]

    try:
        location = reverse((lat, lon), language="en", exactly_one=True)
        if location and location.raw and "address" in location.raw:
            country = location.raw["address"].get("country", None)
            # Cache the result
            new_row = pd.DataFrame([{"lat": lat, "lon": lon, "country": country}])
            geocache.loc[len(geocache)] = new_row.iloc[0]
            return country
    except:
        return None

# === Add Country ===
print("Adding country info... (may take a few minutes)")
df["country"] = df.apply(lambda row: lookup_country(round(row["latitude"], 2), round(row["longitude"], 2)), axis=1)

# Save geocache
geocache.drop_duplicates().to_csv(cache_file, index=False)

# Final columns
final_df = df[["time", "latitude", "longitude", "depth", "magnitude", "place", "country"]]
final_df = final_df.dropna(subset=["country"])

# Save
final_df.to_csv("data/earthquakes.csv", index=False)
print("Saved to data/earthquakes.csv")
