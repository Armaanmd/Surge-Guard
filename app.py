import streamlit as st
import folium
from folium.plugins import HeatMap, AntPath
from streamlit_folium import st_folium
from data_manager import get_full_report, predict_exhaustion
from datetime import datetime
import random

# --- CONFIG ---
st.set_page_config(page_title="Surge-Guard Dashboard", layout="wide", page_icon="🛡️")

# --- NAVIGATION ---
st.sidebar.title("🛡️ Surge-Guard Menu")
page = st.sidebar.radio("Go to", ["🌍 Global Market View", "🏠 Personal Monitor", "🏛️ Governance Command"])

# --- GLOBAL DATA ---
tension = st.sidebar.slider("Crisis Tension Level", 0, 100, 30)
all_stations = get_full_report(tension)

# --- PAGE 1: GLOBAL MARKET VIEW ---
if page == "🌍 Global Market View":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Settings")
    user_brand = st.sidebar.selectbox("LPG Brand", ["Indane", "HP Gas", "Bharat Gas"])
    user_loc = st.sidebar.selectbox("Select Area", ["Kamanahalli", "Indiranagar", "Hebbal", "Victoria Hospital"])

    my_station = next((s for s in all_stations if s['brand'] == user_brand and s['location'] == user_loc), None)

    st.title("🌍 Bengaluru LPG Market Intelligence")
    
    if tension > 50:
        st.warning(f"🚨 **High Tension Alert:** Prices include a ₹{my_station['surge']} surge due to scarcity.")

    if my_station:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹{my_station['price']}", f"+₹{my_station['surge']}")
        c2.metric("Dealer Stock", f"{my_station['stock']} Units")
        c3.metric("Next Arrival", my_station['arrival'])
        c4.metric("Market Status", my_station['action'])
        st.info(f"📞 **Distributor:** {my_station['distributor']} | **Contact:** {my_station['contact']}")

    st.markdown("### 🗺️ Scarcity Heatmap")
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    heat_data = [[s['lat'], s['lon'], 1000 - s['stock']] for s in all_stations if s['brand'] == user_brand]
    HeatMap(heat_data, radius=25, blur=15).add_to(m)
    
    for s in all_stations:
        if s['brand'] == user_brand:
            color = "red" if s['stock'] < 100 else "orange" if s['stock'] < 400 else "green"
            folium.Marker([s['lat'], s['lon']], tooltip=s['location'], icon=folium.Icon(color=color)).add_to(m)
    
    st_folium(m, width="100%", height=450, key="market_map")

    st.subheader(f"🔄 Alternatives in {user_loc}")
    alts = [s for s in all_stations if s['location'] == user_loc and s['brand'] != user_brand]
    st.dataframe(alts, use_container_width=True)

# --- PAGE 2: PERSONAL MONITOR ---
elif page == "🏠 Personal Monitor":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Household Config")
    num_cyl = st.sidebar.number_input("Cylinders Ordered", min_value=1, max_value=5, value=1)
    family_size = st.sidebar.number_input("Family Members", min_value=1, max_value=15, value=4)
    book_date = st.sidebar.date_input("Last Booking Date", datetime.now())

    st.title("🏠 Smart Personal LPG Monitor")
    ex_date, days_left = predict_exhaustion(book_date, family_size, num_cyl)

    if days_left <= 5:
        st.error(f"🚨 **CRITICAL:** Your gas is expected to finish in {days_left} days!")
        if st.button("⚡ Quick Refill Booking"):
            st.success(f"Booking ID: SG-{random.randint(1000,9999)} Confirmed.")
            st.balloons()
    elif days_left <= 12:
        st.warning(f"⚠️ **WARNING:** {days_left} days remaining. Stock is low in your area.")
    else:
        st.success(f"✅ **SAFE:** Your supply lasts until {ex_date.strftime('%d %b, %Y')}.")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Booking Overview")
        st.write(f"**Cylinders:** {num_cyl} | **Usage:** {round(family_size * 0.12, 2)} kg/day")
        st.write(f"**Exhaustion Date:** {ex_date.strftime('%A, %d %B %Y')}")
    with c2:
        st.subheader("Usage Progress")
        total_days = (num_cyl * 14.2) / (family_size * 0.12)
        progress = max(0.0, min(1.0, days_left / total_days))
        st.progress(progress)
        st.write(f"{int(progress * 100)}% of supply remaining")

# --- PAGE 3: GOVERNANCE COMMAND ---
elif page == "🏛️ Governance Command":
    st.title("🏛️ Admin: Priority Supply Optimizer")
    
    # Initialize session state for the routing trigger
    if 'show_route' not in st.session_state:
        st.session_state.show_route = False

    # Priority Logic Calculation
    critical = min(all_stations, key=lambda x: x['backup_pct'] if "Medical" in x['loc_type'] else 100)
    surplus = max(all_stations, key=lambda x: x['backup_pct'] if "Commercial" in x['loc_type'] else 0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Critical Site Backup", f"{critical['backup_pct']}%", delta="- Critical", delta_color="inverse")
        st.write(f"**Target:** {critical['location']} ({critical['loc_type']})")
    with col2:
        st.metric("Surplus Site Backup", f"{surplus['backup_pct']}%", delta="Available")
        st.write(f"**Source:** {surplus['location']} ({surplus['loc_type']})")

    st.markdown("---")
    
    # Button to trigger the route
    if st.button("🚀 Calculate Emergency Redistribution"):
        st.session_state.show_route = True

    # Build the Map
    m_gov = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    
    # Add Heatmap
    gov_heat = [[s['lat'], s['lon'], 100 - s['backup_pct']] for s in all_stations]
    HeatMap(gov_heat, radius=30, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m_gov)

    # If button was clicked, add the route and info
    if st.session_state.show_route:
        st.subheader("🤖 AI Routing: Emergency Divert Active")
        st.info(f"Directing emergency supply from **{surplus['location']}** to **{critical['location']}**.")
        
        # Add Markers
        folium.Marker([critical['lat'], critical['lon']], popup="TARGET: Hospital", icon=folium.Icon(color='red', icon='plus')).add_to(m_gov)
        folium.Marker([surplus['lat'], surplus['lon']], popup="SOURCE: Hotel", icon=folium.Icon(color='blue', icon='arrow-up')).add_to(m_gov)
        
        # The Blue AntPath
        AntPath(
            locations=[[surplus['lat'], surplus['lon']], [critical['lat'], critical['lon']]],
            delay=1000, color="blue", pulse_color="cyan", weight=6
        ).add_to(m_gov)

    # Display the Map
    st_folium(m_gov, width="100%", height=500, key="gov_map_final")
    
    st.markdown("### Regional Data Overview")
    st.dataframe(all_stations, use_container_width=True)
