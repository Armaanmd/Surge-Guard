import random
import math
from datetime import datetime, timedelta
import streamlit as st

# User-friendly area mapping
SEARCHABLE_AREAS = {
    "Majestic (City Center)": {"lat": 12.9767, "lon": 77.5713},
    "Koramangala": {"lat": 12.9352, "lon": 77.6245},
    "Whitefield": {"lat": 12.9698, "lon": 77.7500},
    "Jayanagar": {"lat": 12.9300, "lon": 77.5833},
    "MG Road": {"lat": 12.9733, "lon": 77.6117},
    "Yeshwanthpur": {"lat": 13.0250, "lon": 77.5484},
    "Electronic City": {"lat": 12.8452, "lon": 77.6632}
}

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@st.cache_data
def get_full_report(tension_level):
    base_domestic = 915.50
    locations = [
        {"name": "Kamanahalli", "lat": 13.0158, "lon": 77.6378, "type": "Residential"},
        {"name": "Indiranagar", "lat": 12.9719, "lon": 77.6412, "type": "Commercial (Hotel)"},
        {"name": "Victoria Hospital", "lat": 12.9634, "lon": 77.5746, "type": "Medical (Critical)"},
        {"name": "Hebbal", "lat": 13.0354, "lon": 77.5988, "type": "Residential"}
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
            backup_pct = max(5, random.randint(10, 95) - (tension_level // 3))
            stock = max(0, random.randint(400, 800) - (tension_level * 5))
            if "Hospital" in loc['name']: stock += 1000
            
            days_to_arrival = random.randint(1, 3) + (tension_level // 25)
            arrival_date = (datetime.now() + timedelta(days=days_to_arrival)).strftime("%d %b")
            
            surge_charge = tension_level * 0.45
            price = base_domestic + surge_charge
            
            wait_time = random.randint(5, 20) + (tension_level // 2)
            if stock < 200: wait_time += 25
            
            entry = {
                "location": loc['name'], "lat": loc['lat'], "lon": loc['lon'], "loc_type": loc['type'],
                "brand": b['brand'], "contact": b['contact'], "distributor": b['distributor'],
                "stock": int(stock), "backup_pct": backup_pct, "arrival": arrival_date, 
                "price": round(price, 2), "surge": round(surge_charge, 2),
                "wait_time": int(wait_time)
            }
            
            if entry['stock'] < 100 or backup_pct < 20: entry['action'] = "🚨 OUT OF STOCK"
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

def get_priority_requests():
    sectors = [
        {"type": "Medical (Critical)", "priority": 1, "demand": 150, "icon": "🏥"},
        {"type": "Heavy Industry", "priority": 2, "demand": 200, "icon": "🏭"},
        {"type": "College Hostels", "priority": 2, "demand": 80, "icon": "🏫"},
        {"type": "Govt Canteens", "priority": 3, "demand": 60, "icon": "🍱"},
        {"type": "Restaurants", "priority": 4, "demand": 120, "icon": "🍕"},
        {"type": "Small Retailers", "priority": 5, "demand": 40, "icon": "🏪"}
    ]
    
    requests = []
    for s in sectors:
        requested = s['demand'] + random.randint(-10, 20)
        allocation_pct = max(0.5, 1.1 - (s['priority'] * 0.12)) 
        allocated = int(requested * allocation_pct)
        
        requests.append({
            "Sector": f"{s['icon']} {s['type']}",
            "Priority": s['priority'],
            "Requested Units": requested,
            "Allocated Units": allocated,
            "Gap": requested - allocated
        })
    return requests
