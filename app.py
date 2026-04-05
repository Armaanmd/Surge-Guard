import streamlit as st
import folium
from folium.plugins import HeatMap, AntPath
from streamlit_folium import st_folium
from data_manager import get_full_report, predict_exhaustion, calculate_distance, SEARCHABLE_AREAS, get_priority_requests
from datetime import datetime
import pandas as pd
# In app.py
from data_manager import (
    get_full_report, 
    predict_exhaustion, 
    calculate_distance, 
    SEARCHABLE_AREAS, 
    get_priority_requests,
    get_stock_alerts  # <--- ADD THIS
)   

# --- CONFIG ---
st.set_page_config(page_title="Surge-Guard Dashboard", layout="wide", page_icon="🛡️")

# --- NAVIGATION ---
st.sidebar.title("🛡️ Surge-Guard Menu")
page = st.sidebar.radio("Go to", [
    "🌍 Global Market View", 
    "🏠 Personal Monitor", 
    "🛺 Auto-Driver Hub", 
    "🏛️ Governance Command",
    "📦 Distribution Manager"
])

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
    alerts = get_stock_alerts(all_stations)
    if alerts:
        with st.expander("🔔 Live Supply Alerts", expanded=True):
            for a in alerts:
                if a['level'] == "ERROR":
                    st.error(a['msg'])
                else:
                    st.warning(a['msg'])
    if tension > 50 and my_station:
        st.warning(f"🚨 **High Tension Alert:** Prices include a ₹{my_station['surge']} surge due to scarcity.")
    if my_station:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹{my_station['price']}", f"+₹{my_station['surge']}")
        c2.metric("Dealer Stock", f"{my_station['stock']} Units")
        c3.metric("Next Arrival", my_station['arrival'])
        c4.metric("Market Status", my_station['action'])
        st.info(f"📞 **Distributor:** {my_station['distributor']} | **Contact:** {my_station['contact']}")

    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    heat_data = [[s['lat'], s['lon'], 1000 - s['stock']] for s in all_stations if s['brand'] == user_brand]
    HeatMap(heat_data, radius=25, blur=15).add_to(m)
    st_folium(m, width="100%", height=450, key="market_map")
    
    st.subheader(f"🔄 Alternatives in {user_loc}")
    alts = [s for s in all_stations if s['location'] == user_loc and s['brand'] != user_brand]
    st.dataframe(alts, use_container_width=True)

# --- PAGE 2: PERSONAL MONITOR ---
elif page == "🏠 Personal Monitor":
    st.title("🏠 Smart Personal LPG Monitor")
    num_cyl = st.sidebar.number_input("Cylinders Ordered", 1, 5, 1)
    family_size = st.sidebar.number_input("Family Members", 1, 15, 4)
    book_date = st.sidebar.date_input("Last Booking Date", datetime.now())
    ex_date, days_left = predict_exhaustion(book_date, family_size, num_cyl)
    
    if days_left <= 5: st.error(f"🚨 **CRITICAL:** Gas finishing in {days_left} days!")
    else: st.success(f"✅ **SAFE:** Supply lasts until {ex_date.strftime('%d %b, %Y')}.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Usage:** {round(family_size * 0.12, 2)} kg/day")
        st.write(f"**Exhaustion Date:** {ex_date.strftime('%A, %d %B %Y')}")
    with c2:
        total_days = (num_cyl * 14.2) / (family_size * 0.12)
        st.progress(max(0.0, min(1.0, days_left / total_days)))

# --- PAGE 3: AUTO-DRIVER HUB ---
elif page == "🛺 Auto-Driver Hub":
    st.title("🛺 Auto-Rickshaw Quick Refill Finder")
    st.sidebar.markdown("### 📍 Your Current Stand")
    selected_area_name = st.sidebar.selectbox("Where are you now?", list(SEARCHABLE_AREAS.keys()))
    
    driver_lat = SEARCHABLE_AREAS[selected_area_name]['lat']
    driver_lon = SEARCHABLE_AREAS[selected_area_name]['lon']

    auto_stations = []
    for s in all_stations:
        if "Medical" not in s['loc_type']:
            s_copy = s.copy()
            s_copy['dist'] = calculate_distance(driver_lat, driver_lon, s['lat'], s['lon'])
            auto_stations.append(s_copy)
    
    smooth = sorted([s for s in auto_stations if s['wait_time'] <= 15 and s['stock'] > 100], key=lambda x: x['dist'])
    jammed = sorted([s for s in auto_stations if s['wait_time'] > 30], key=lambda x: x['wait_time'], reverse=True)

    col1, col2 = st.columns([2, 1])
    with col2:
        st.subheader("🚦 Pit-Stop Logic")
        st.info(f"Showing distances from **{selected_area_name}**")
        if smooth:
            st.success(f"✅ **BEST PICK:** {smooth[0]['location']}\n\n{smooth[0]['dist']} km away | {smooth[0]['wait_time']} min wait")
            if st.button("🚀 Navigate to Best Station"):
                st.session_state.auto_nav = smooth[0]
        if jammed:
            st.error(f"⚠️ **AVOID:** {jammed[0]['location']} ({jammed[0]['wait_time']}m wait)")

    with col1:
        m_auto = folium.Map(location=[driver_lat, driver_lon], zoom_start=13)
        folium.Marker([driver_lat, driver_lon], tooltip="YOUR STAND", icon=folium.Icon(color='blue', icon='star')).add_to(m_auto)
        for s in auto_stations:
            color = 'red' if s['wait_time'] > 30 else 'orange' if s['wait_time'] > 15 else 'green'
            folium.Marker([s['lat'], s['lon']], popup=f"{s['location']} ({s['dist']}km)", icon=folium.Icon(color=color)).add_to(m_auto)
        if 'auto_nav' in st.session_state:
            nav = st.session_state.auto_nav
            AntPath(locations=[[driver_lat, driver_lon], [nav['lat'], nav['lon']]], color="green", weight=5).add_to(m_auto)
        st_folium(m_auto, width="100%", height=400, key="auto_map")

    st.subheader("📋 Nearby Stations (Sorted by Distance)")
    auto_df = pd.DataFrame(auto_stations)[['location', 'brand', 'dist', 'wait_time', 'stock', 'price']]
    auto_df.columns = ['Station', 'Brand', 'Distance (km)', 'Wait (Min)', 'Stock', 'Price']
    st.dataframe(auto_df.sort_values('Distance (km)'), use_container_width=True)

# --- PAGE 4: GOVERNANCE COMMAND ---
elif page == "🏛️ Governance Command":
    st.title("🏛️ Admin: Priority Supply Optimizer")
    if 'show_route' not in st.session_state: st.session_state.show_route = False

    critical = min(all_stations, key=lambda x: x['backup_pct'] if "Medical" in x['loc_type'] else 100)
    surplus = max(all_stations, key=lambda x: x['backup_pct'] if "Commercial" in x['loc_type'] else 0)

    col1, col2 = st.columns(2)
    col1.metric("Critical Site Backup", f"{critical['backup_pct']}%", delta="- Critical", delta_color="inverse")
    col2.metric("Surplus Site Backup", f"{surplus['backup_pct']}%", delta="Available")

    if st.button("🚀 Calculate Emergency Redistribution"):
        st.session_state.show_route = True

    m_gov = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    gov_heat = [[s['lat'], s['lon'], 100 - s['backup_pct']] for s in all_stations]
    HeatMap(gov_heat, radius=30, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m_gov)

    if st.session_state.show_route:
        folium.Marker([critical['lat'], critical['lon']], icon=folium.Icon(color='red')).add_to(m_gov)
        folium.Marker([surplus['lat'], surplus['lon']], icon=folium.Icon(color='blue')).add_to(m_gov)
        AntPath(locations=[[surplus['lat'], surplus['lon']], [critical['lat'], critical['lon']]], color="blue", weight=6).add_to(m_gov)

    st_folium(m_gov, width="100%", height=500, key="gov_map_final")
    st.dataframe(all_stations, use_container_width=True)

# --- PAGE 5: DISTRIBUTION MANAGER ---
elif page == "📦 Distribution Manager":
    st.title("📦 Bulk Priority Allocation Manager")
    st.subheader("📩 Incoming Emergency Requests")
    low_stock_sites = [s for s in all_stations if s['stock'] < 300]
    
    if low_stock_sites:
        for site in low_stock_sites:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"📌 **{site['location']}** ({site['brand']}) requests emergency refill. Current: **{site['stock']} units**")
            if col_b.button(f"Approve Refill", key=f"btn_{site['location']}_{site['brand']}"):
                st.toast(f"Refill dispatched to {site['location']}!")
    else:
        st.success("No emergency refill requests at this time.")
    
    st.divider()
    st.markdown("### Decision Support for Authorized Distributors")
    
    req_data = get_priority_requests()
    df_req = pd.DataFrame(req_data)

    # Performance Charts
    st.subheader("📊 Demand vs. Fulfillment by Sector")
    chart_df = df_req.set_index('Sector')[['Requested Units', 'Allocated Units']]
    st.bar_chart(chart_df)

    # Detailed Table
    st.subheader("📋 Priority Allocation Ledger")
    def highlight_priority(val):
        if isinstance(val, int):
            if val == 1: return 'color: red; font-weight: bold'
            if val == 2: return 'color: orange; font-weight: bold'
        return 'color: black'
    
    # Using .style.map for modern Pandas compatibility
    st.dataframe(df_req.style.map(highlight_priority, subset=['Priority']), use_container_width=True)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Regional Demand", f"{df_req['Requested Units'].sum()} Units")
    c2.metric("Total Priority Allocation", f"{df_req['Allocated Units'].sum()} Units")
    c3.metric("Stock Gap", f"-{df_req['Gap'].sum()} Units", delta_color="inverse")
