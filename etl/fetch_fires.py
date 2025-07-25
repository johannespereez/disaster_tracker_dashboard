import pandas as pd

def fetch_fire_data():
    # This is the NASA FIRMS MODIS Global 24h fire data hosted via FIRMS-AWS mirror
    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"
    
    try:
        df = pd.read_csv(url)
        df = df[["latitude", "longitude", "acq_date", "acq_time", "brightness", "confidence", "frp"]]
        df.to_csv("data/fires.csv", index=False)
        print("✅ Fire data saved to data/fires.csv")
    except Exception as e:
        print(f"❌ Failed to fetch fire data: {e}")

if __name__ == "__main__":
    fetch_fire_data()
