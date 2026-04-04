import random

def get_station_data(tension_level):
    """
    Step 1: The Foundation
    Simulates the 'Digital Twin' of Bengaluru's LPG supply.
    tension_level: 0-100 (0 = Peace, 100 = Crisis)
    """
    # Define our 'Digital Twin' Nodes with coordinates
    stations = [
        {"name": "Kamanahalli LPG Junction", "lat": 13.0158, "lon": 77.6378, "type": "Auto-LPG", "priority": 2},
        {"name": "Indiranagar Supply Co.", "lat": 12.9719, "lon": 77.6412, "type": "Commercial", "priority": 3},
        {"name": "Victoria Hospital Depot", "lat": 12.9634, "lon": 77.5746, "type": "Critical", "priority": 1},
        {"name": "Hebbal Main Station", "lat": 13.0354, "lon": 77.5988, "type": "Auto-LPG", "priority": 2},
        {"name": "Koramangala Energy Hub", "lat": 12.9352, "lon": 77.6245, "type": "Mixed", "priority": 2}
    ]

    for s in stations:
        # Stock depletes as tension rises (Starting max stock is 3000L)
        s['stock'] = max(0, 3000 - (tension_level * 28))
        
        # Wait times increase (Base 15 mins + tension-based delay)
        s['wait_time'] = 15 + (tension_level // 2)
        
        # April 2026 Price Logic (Base ₹82.50/L + crisis surcharge)
        s['price'] = round(82.50 + (tension_level * 0.45), 2)

    return stations

def allocate_resources(stations):
    """
    Step 2: The Prioritization Algorithm
    Identifies 'Critical' nodes and suggests emergency actions.
    """
    plan = []
    for s in stations:
        # EMERGENCY: Critical stations (Hospitals) with low stock
        if s['priority'] == 1 and s['stock'] < 1000:
            status = "🚨 EMERGENCY REFILL REQUIRED"
        # WARNING: Auto-LPG stations with high wait times
        elif s['type'] == "Auto-LPG" and s['wait_time'] > 50:
            status = "⚠️ HIGH TRAFFIC - DIVERT DRIVERS"
        else:
            status = "✅ STABLE"
            
        plan.append(status)
    
    return plan

def get_full_report(tension_level):
    """
    Step 3: The Master Sync
    This is the ONLY function Person B needs to call in app.py.
    """
    stations = get_station_data(tension_level)
    actions = allocate_resources(stations)
    
    # Merge the action status into the station dictionary
    for i in range(len(stations)):
        stations[i]['action'] = actions[i]
        
    return stations

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Simulate a high-tension scenario (85%)
    final_data = get_full_report(85)
    
    print("--- MASTER SYNC TEST (Crisis at 85%) ---")
    for s in final_data:
        print(f"Location: {s['name']}")
        print(f"  Stock: {s['stock']}L | Price: ₹{s['price']}")
        print(f"  Status: {s['action']}")
        print("-" * 30)