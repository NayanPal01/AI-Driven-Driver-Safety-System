import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# Streamlit page setup
st.set_page_config(page_title="Driver Drowsiness Dashboard", layout="wide")
st.title("🚗 Driver Drowsiness Analysis (All-Time)")

# 🔁 Refresh every 5 seconds
st_autorefresh(interval=5000, limit=None, key="refresh")

try:
    df = pd.read_csv("alert_log.csv", usecols=["Timestamp", "Status"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
    df.dropna(subset=["Timestamp"], inplace=True)
    df = df[df["Status"].isin(["Drowsy !", "SLEEPING !!!"])]

    if df.empty:
        st.warning("⚠️ No drowsy or sleepy data yet.")
    else:
        df["Hour"] = df["Timestamp"].dt.hour
        hourly_counts = df["Hour"].value_counts().sort_index()
        hourly_ranges = hourly_counts.rename(index=lambda h: f"{h:02d}:00–{h:02d}:59")
        top3 = hourly_ranges.sort_values(ascending=False).head(3)

        # Chart
        st.subheader("📊 Drowsiness Events by Hour (Auto-Updated)")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(hourly_ranges.index, hourly_ranges.values, color='darkorange')
        ax.set_xlabel("Time Range")
        ax.set_ylabel("Event Count")
        ax.set_title("Driver Drowsiness Frequency by Hour")
        ax.grid(True, axis='y')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Top 3
        st.subheader("🔥 Top 3 Hours")
        st.table(top3.reset_index().rename(columns={"index": "Time Range", "Hour": "Count"}))

        # Download buttons
        st.download_button("⬇ Full Hourly CSV", hourly_ranges.to_csv().encode(), "drowsy_hourly_all.csv", "text/csv")
        st.download_button("⬇ Top 3 CSV", top3.to_csv().encode(), "drowsy_top3_all.csv", "text/csv")

except Exception as e:
    st.error(f"❌ Error: {e}")
