import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 1. THE MOCK DATA (Integration Point) ---
def get_simulated_data(tension):
    # This simulates what Person A will eventually provide
    return [
        {"name": "Kamanahalli HP", "lat": 13.0158, "lon": 77.6378, "stock_level": 2000 - (tension*15), "type": "Auto-LPG", "priority": "High", "wait_time": 20},
        {"name": "Indiranagar Indane", "lat": 12.9719, "lon": 77.6412, "stock_level": 1200 - (tension*10), "type": "Domestic", "priority": "Medium", "wait_time": 45},
        {"name": "Hebbal PSU", "lat": 13.0354, "lon": 77.5988, "stock_level": 400 - (tension*5), "type": "Auto-LPG", "priority": "High", "wait_time": 120},
        {"name": "Victoria Hospital (Critical)", "lat": 12.9634, "lon": 77.5744, "stock_level": 3000, "type": "Critical-Care", "priority": "Emergency", "wait_time": 5}
    ]

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Surge-Guard Dashboard", layout="wide")

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.title("🛡️ Surge-Guard Controls")
tension = st.sidebar.slider("Geopolitical Tension", 0, 100, 20)
show_auto = st.sidebar.toggle("Show Auto-LPG Stations Only")

st.sidebar.markdown("---")
st.sidebar.write("### 📍 Map Legend")
st.sidebar.write("🟢 **Stable:** > 1500L")
st.sidebar.write("🟠 **Warning:** 500L - 1500L")
st.sidebar.write("🔴 **Critical:** < 500L")

# --- 4. HEADER & NEWS TICKER ---
st.title("🛡️ Surge-Guard: Bengaluru LPG Digital Twin")

if tension > 70:
    st.error("⚠️ EMERGENCY: Strait of Hormuz closure confirmed. Bengaluru reserves at 48-hour limit.")
elif tension > 40:
    st.warning("⚡ ALERT: Commercial LPG prices hiked by ₹195.50. Expect longer queues.")
else:
    st.success("✅ Supply Chain Stable: Tankers arriving at Mangalore Port on schedule.")

# --- 5. DATA FETCHING ---
stations = get_simulated_data(tension)

# --- 6. MAP BUILDING (LIGHT MODE) ---
def draw_map(data):
    # CHANGED: 'tiles="OpenStreetMap"' for maximum light-mode readability
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="OpenStreetMap")
    
    for s in data:
        # Toggle Logic
        if show_auto and s['type'] != "Auto-LPG":
            continue
            
        # Color Logic
        if s['stock_level'] < 500: color = "red"
        elif s['stock_level'] < 1500: color = "orange"
        else: color = "green"
            
        # NEW: Icon Logic (Car for Auto, Home for others, Star for Hospital)
        if s['type'] == "Auto-LPG":
            icon_name = "car"
        elif s['type'] == "Critical-Care":
            icon_name = "plus-sign"
        else:
            icon_name = "home"
            
        folium.Marker(
            [s['lat'], s['lon']],
            popup=f"<b>{s['name']}</b><br>Stock: {int(s['stock_level'])}L<br>Wait: {s['wait_time']}m",
            icon=folium.Icon(color=color, icon=icon_name)
        ).add_to(m)
        # This automatically fits the map view to show all your markers
    m.fit_bounds(m.get_bounds())
    return m

# --- 7. RENDER MAP ---
map_obj = draw_map(stations)
st_folium(map_obj, width=1200, height=500)

# --- 8. LIVE CITY ANALYTICS (NEW) ---
st.markdown("---")
st.subheader("📊 Live City Analytics")
col1, col2, col3 = st.columns(3)

with col1:
    panic_val = "High" if tension > 60 else "Moderate" if tension > 30 else "Low"
    st.metric("Estimated Panic Level", panic_val, delta="Reduced by 12%" if tension < 50 else "+5%")

with col2:
    avg_wait = sum(s['wait_time'] for s in stations) // len(stations)
    st.metric("Avg. Queue Time", f"{avg_wait} Mins")

with col3:
    st.write("**City Resource Load**")
    st.progress(tension / 100)