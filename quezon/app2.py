import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Quezon Agri-Price Radar", page_icon="🌾", layout="wide"
)

# Locate CSV in the same folder as app2.py
DATA_PATH = Path(__file__).parent / "quezon_crop_price_surges.csv"
df = pd.read_csv(DATA_PATH)

# Load data
# df = pd.read_csv("quezon_crop_price_surges.csv")
# df["Date"] = pd.to_datetime(df["Date"])

st.title("🌾 Quezon Agri-Commodity Price Shock & Anomaly Radar")
st.caption(
    "Automated early-warning tripwire system detecting regional farmgate price spikes and supply disruptions."
)
st.divider()

# Sidebar Crop Selector
crop_list = df["Commodity"].unique().tolist()
selected_crop = st.sidebar.selectbox("Select Commodity", crop_list)

crop_df = df[df["Commodity"] == selected_crop].sort_values("Date").reset_index()
latest = crop_df.iloc[-1]
prev_price = latest["price_lag_1m"]

# KPI Header
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Latest Farmgate Price", f"₱{latest['Farmgate_Price_PHP']:.2f}/kg")

with kpi2:
    delta_mom = latest["mom_pct_change"]
    st.metric(
        "Month-over-Month Velocity",
        f"{delta_mom:+.1f}%",
        delta=f"{delta_mom:+.1f}%",
        delta_color="inverse",
    )

with kpi3:
    st.metric("Rolling 12M Normal Baseline", f"₱{latest['rolling_12m_mean']:.2f}/kg")

with kpi4:
    if latest["is_surge"]:
        st.error("🚨 STATUS: SURGE ALERT")
    else:
        st.success("🟢 STATUS: STABLE")

# Anomaly Time-Series Plot
st.subheader(f"Price Trajectory & Detected Shocks: {selected_crop}")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(
    crop_df["Date"],
    crop_df["Farmgate_Price_PHP"],
    label="Farmgate Price (₱/kg)",
    color="#1f77b4",
    lw=1.6,
)
ax.plot(
    crop_df["Date"],
    crop_df["rolling_12m_mean"],
    label="12-Month Rolling Mean",
    color="#ff7f0e",
    linestyle="--",
    alpha=0.7,
)

# Highlight Red Alerts
surges = crop_df[crop_df["is_surge"]]
ax.scatter(
    surges["Date"],
    surges["Farmgate_Price_PHP"],
    color="#d62728",
    s=45,
    zorder=5,
    label="Shock Event (Z >= 2.0 or MoM >= 35%)",
)

ax.set_ylabel("PHP / kg")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend(loc="upper left")
st.pyplot(fig)

# Table of Past Crises
st.subheader("Historical Shock Events Log")
st.caption("Periods where farmgate margins experienced severe supply tightening or post-storm shortages.")
surge_table = surges[
    ["Date", "Farmgate_Price_PHP", "mom_pct_change", "z_score"]
].sort_values("Date", ascending=False)
st.dataframe(
    surge_table.rename(
        columns={
            "Farmgate_Price_PHP": "Price (₱/kg)",
            "mom_pct_change": "MoM Change (%)",
            "z_score": "Z-Score",
        }
    ),
    use_container_width=True,
)
