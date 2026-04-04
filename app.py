import streamlit as st
import folium
from streamlit_folium import st_folium
from data_manager import get_full_report, predict_exhaustion
from datetime import datetime

st.set_page_config(page_title="Surge-Guard: Smart LPG Monitor", layout="wide", page_icon="🛡️")

# --- SIDEBAR ---
st.sidebar.title("🛡️ Surge-Guard")
with st.sidebar.expander("👤 User Profile", expanded=True):
    user_brand = st.selectbox("Your LPG Brand", ["Indane", "HP Gas", "Bharat Gas"])
    user_loc = st.selectbox("Your Area", ["Kamanahalli", "Indiranagar", "Hebbal", "Victoria Hospital"])

with st.sidebar.expander("⚙️ Admin Simulation"):
    tension = st.slider("Crisis Tension Level", 0, 100, 30)

# --- NEW FEATURE: HOUSEHOLD MONITOR INPUTS ---
st.sidebar.markdown("---")
st.sidebar.subheader("🏠 Household Monitor")
last_booking = st.sidebar.date_input("Last Cylinder Delivery", datetime.now())
family_members = st.sidebar.number_input("Family Size", min_value=1, max_value=15, value=4)

# --- DATA FETCHING ---
all_stations = get_full_report(tension)
current_user_data = [s for s in all_stations if s['brand'] == user_brand and s['location'] == user_loc]
my_station = current_user_data[0] if current_user_data else None

# --- HEADER ---
st.title("🛡️ Surge-Guard: Personal LPG Assistant")

# --- FEATURE: SMART PREDICTION CARDS ---
st.subheader("📊 My Household Insights")
ex_date, days_left = predict_exhaustion(last_booking, family_members)

p1, p2, p3 = st.columns(3)
with p1:
    st.metric("Expected Exhaustion", ex_date.strftime("%d %b, %Y"))
with p2:
    color = "normal" if days_left > 7 else "inverse"
    st.metric("Days Remaining", f"{days_left} Days", delta="-1 Day" if days_left < 10 else None, delta_color=color)
with p3:
    if days_left <= 5:
        st.error("🚨 ACTION REQUIRED: Book Cylinder Now!")
    elif days_left <= 10:
        st.warning("⚠️ Reminder: Refill booking opens in 2 days.")
    else:
        st.success("✅ Stock Healthy: No immediate booking needed.")

# --- FEATURE: LOCAL AVAILABILITY ---
st.markdown("---")
st.subheader(f"📍 Market Status for {user_brand} in {user_loc}")
if my_station:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Current Price", f"₹{my_station['price']}")
    with c2: st.metric("Dealer Stock", f"{my_station['stock']} Units")
    with c3: st.metric("Next Supply", my_station['arrival'])
    with c4: st.metric("Availability", my_station['action'])
    st.info(f"📞 **Distributor:** {my_station['distributor']} | **Contact:** {my_station['contact']}")

# --- MAP SECTION ---
st.markdown("---")
st.subheader("🗺️ Neighborhood Availability Map")
m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="OpenStreetMap")
for s in all_stations:
    if s['brand'] == user_brand:
        color = "red" if s['stock'] < 100 else "orange" if s['stock'] < 400 else "green"
        folium.Marker([s['lat'], s['lon']], 
                      popup=f"Stock: {s['stock']}", 
                      tooltip=f"{s['location']}",
                      icon=folium.Icon(color=color, icon="info-sign")).add_to(m)
st_folium(m, width="100%", height=400, key="main_map")

# --- ALTERNATIVES TABLE ---
st.markdown("---")
st.subheader(f"🔄 Alternatives in {user_loc}")
alts = [s for s in all_stations if s['location'] == user_loc and s['brand'] != user_brand]
st.dataframe(alts, use_container_width=True)
