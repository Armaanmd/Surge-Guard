import random
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data
def get_full_report(tension_level):
    base_domestic = 915.50
    locations = [
        {"name": "Kamanahalli", "lat": 13.0158, "lon": 77.6378},
        {"name": "Indiranagar", "lat": 12.9719, "lon": 77.6412},
        {"name": "Victoria Hospital", "lat": 12.9634, "lon": 77.5746},
        {"name": "Hebbal", "lat": 13.0354, "lon": 77.5988}
    ]
    brands = [
        {"brand": "Indane", "contact": "1800-233-3555", "distributor": "V L Gramin Vitrak"},
        {"brand": "HP Gas", "contact": "1800-233-4000", "distributor": "Himu Distributors"},
        {"brand": "Bharat Gas", "contact": "1800-22-4344", "distributor": "Sree LPG Pvt Ltd"}
    ]
    
    full_data = []
    for loc in locations:
        for b in brands:
            random.seed(loc['name'] + b['brand'])
            stock = max(0, random.randint(400, 800) - (tension_level * 5))
            if "Hospital" in loc['name']: stock += 1000
            
            days_to_arrival = random.randint(1, 3) + (tension_level // 25)
            arrival_date = (datetime.now() + timedelta(days=days_to_arrival)).strftime("%d %b")
            
            # Feature 1: Explicit Surge Calculation
            surge_charge = tension_level * 0.45
            price = base_domestic + surge_charge
            
            entry = {
                "location": loc['name'], "lat": loc['lat'], "lon": loc['lon'],
                "brand": b['brand'], "contact": b['contact'], "distributor": b['distributor'],
                "stock": int(stock), "arrival": arrival_date, "price": round(price, 2),
                "surge": round(surge_charge, 2),
                "type": "Critical" if "Hospital" in loc['name'] else "Standard"
            }
            if entry['stock'] < 100: entry['action'] = "🚨 OUT OF STOCK"
            elif entry['stock'] < 300: entry['action'] = "⚠️ CRITICAL LOW"
            else: entry['action'] = "✅ AVAILABLE"
            full_data.append(entry)
    return full_data

def predict_exhaustion(booking_date, family_size, num_cylinders=1):
    total_capacity = 14.2 * num_cylinders
    daily_usage = family_size * 0.12 
    days_it_lasts = total_capacity / daily_usage
    
    exhaustion_date = booking_date + timedelta(days=int(days_it_lasts))
    days_left = (exhaustion_date - datetime.now().date()).days
    return exhaustion_date, days_left
