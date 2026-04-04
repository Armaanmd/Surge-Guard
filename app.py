import streamlit as st
import folium
from streamlit_folium import st_folium
from data_manager import get_full_report, predict_exhaustion
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Surge-Guard Dashboard", layout="wide", page_icon="🛡️")

# --- NAVIGATION ---
st.sidebar.title("🛡️ Surge-Guard Menu")
page = st.sidebar.radio("Go to", ["🌍 Global Market View", "🏠 Personal Monitor"])

# --- PAGE 1: GLOBAL MARKET VIEW ---
if page == "🌍 Global Market View":
    # Sidebar for Page 1
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Settings")
    user_brand = st.sidebar.selectbox("LPG Brand", ["Indane", "HP Gas", "Bharat Gas"])
    user_loc = st.sidebar.selectbox("Select Area", ["Kamanahalli", "Indiranagar", "Hebbal", "Victoria Hospital"])
    tension = st.sidebar.slider("Crisis Tension Level", 0, 100, 30)

    # Data logic
    all_stations = get_full_report(tension)
    my_station = next((s for s in all_stations if s['brand'] == user_brand and s['location'] == user_loc), None)

    st.title("🌍 Bengaluru LPG Market Intelligence")
    st.write(f"Showing live data for **{user_brand}** in **{user_loc}** during a **{tension}%** crisis level.")

    # Market Cards
    if my_station:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹{my_station['price']}")
        c2.metric("Dealer Stock", f"{my_station['stock']} Units")
        c3.metric("Next Arrival", my_station['arrival'])
        c4.metric("Market Status", my_station['action'])
        st.info(f"📞 **Distributor:** {my_station['distributor']} | **Contact:** {my_station['contact']}")

    # Map
    st.markdown("---")
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    for s in all_stations:
        if s['brand'] == user_brand:
            color = "red" if s['stock'] < 100 else "orange" if s['stock'] < 400 else "green"
            folium.Marker([s['lat'], s['lon']], tooltip=s['location'], icon=folium.Icon(color=color)).add_to(m)
    st_folium(m, width="100%", height=450, key="market_map")

    # Alternatives
    st.subheader(f"🔄 Price & Stock Alternatives in {user_loc}")
    alts = [s for s in all_stations if s['location'] == user_loc and s['brand'] != user_brand]
    st.dataframe(alts, use_container_width=True)

# --- PAGE 2: PERSONAL MONITOR ---
elif page == "🏠 Personal Monitor":
    # Sidebar for Page 2
    st.sidebar.markdown("---")
    st.sidebar.subheader("Household Config")
    num_cyl = st.sidebar.number_input("Cylinders Ordered", min_value=1, max_value=5, value=1)
    family_size = st.sidebar.number_input("Family Members", min_value=1, max_value=15, value=4)
    book_date = st.sidebar.date_input("Last Booking Date", datetime.now())

    st.title("🏠 Smart Personal LPG Monitor")
    st.write("Track your household consumption and get predictive alerts.")

    # Calculation logic
    ex_date, days_left = predict_exhaustion(book_date, family_size, num_cyl)

    # Big Alert Banner
    if days_left <= 5:
        st.error(f"🚨 **CRITICAL:** Your gas is expected to finish in {days_left} days! Please book now.")
    elif days_left <= 12:
        st.warning(f"⚠️ **WARNING:** You have about {days_left} days left. Keep an eye on local stock.")
    else:
        st.success(f"✅ **SAFE:** Your supply should last until {ex_date.strftime('%d %b, %Y')}.")

    # Detailed Stats
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Booking Overview")
        st.write(f"**Cylinders in Reserve:** {num_cyl}")
        st.write(f"**Calculated Daily Usage:** {round(family_size * 0.12, 2)} kg/day")
        st.write(f"**Expected Exhaustion Date:** {ex_date.strftime('%A, %d %B %Y')}")
    
    with col2:
        st.subheader("Usage Progress")
        # Visualizing the burn rate
        total_days = (num_cyl * 14.2) / (family_size * 0.12)
        progress_per = max(0.0, min(1.0, days_left / total_days))
        st.progress(progress_per)
        st.write(f"{int(progress_per * 100)}% of supply remaining")

    st.info("💡 **Pro-Tip:** Based on your current usage, booking your next cylinder 7 days before exhaustion ensures you never run out during a crisis.")
