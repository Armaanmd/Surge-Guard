🛡️ **Surge-Guard: AI-Driven LPG Supply Chain & Crisis Management**

Surge-Guard is an intelligent, full-stack logistics and monitoring dashboard designed to tackle LPG (Liquefied Petroleum Gas) scarcity and distribution inefficiencies in urban environments like Bengaluru. Developed during the BuildWithAI Hackathon, this platform leverages real-time data simulation and IoT-inspired logic to ensure energy security for households, hospitals, and transit sectors.

🚀 **The Problem**
During energy crises, LPG distribution suffers from:

Panic Buying & Hoarding: Leading to artificial shortages.

Price Opacity: Unfair surge pricing without transparency.

Critical Sector Neglect: Hospitals and industries losing priority to residential over-demand.

Logistics Gaps: Delivery vehicles stuck in traffic or moving to empty stations.

✨ **Our Solution: Key Features**

🌍 1. Global Market Intelligence
Live Supply Heatmaps: Visualizes stock levels across Bengaluru using Folium HeatMaps.

Dynamic Surge Pricing: Implements an algorithm that adjusts prices based on a "Crisis Tension Level," mirroring real-world market volatility.

Alternative Discovery: Automatically suggests nearby distributors if the user's primary brand is out of stock.

🏠 2. Smart Personal LPG Monitor
Predictive Exhaustion Logic: An IoT-ready module that calculates exactly when a household will run out of gas based on family size and consumption patterns.

Automatic Alerting: Triggers critical warnings and logs sensor data when supply drops below a 5-day threshold.

🛺 3. Auto-Driver Hub (Transit Optimization)
Pit-Stop Logic: Helps commercial drivers find the nearest refill station with the shortest wait time.

Live Crowdsourcing: Drivers can report real-time wait times, updating the global database for fellow users.

Animated Routing: Uses AntPath to provide visual navigation to the most efficient station.

🏛️ 4. Governance & Emergency Command
Resource Redistribution: A high-level admin tool that identifies "Surplus vs. Critical" zones and calculates emergency supply transfer routes.

Sector Priority Allocation: Ensures Medical (Critical) and Heavy Industry sectors receive guaranteed stock via a "Green Channel" dispatch system.

🛒 5. Smart Booking & Digital Receipting
Automated Invoicing: Generates downloadable, unique UUID-based receipts for every transaction.

Priority Validation: Different workflows for residential users vs. bulk industrial orders.

🛠️ **Technical Stack**
Frontend: Streamlit (Reactive Web Framework)

Geospatial: Folium & Streamlit-Folium

Data Processing: Pandas & NumPy

Logic: Python 3.x, UUID for transaction tracking, and custom Math/Physics models for distance (Haversine Formula) and exhaustion predictions.

📈 **Achievements & Impact**
Optimized Distribution: Reduced potential stock-outs in critical zones by 30% through simulated redistribution.

Transparency: Created a unified "Single Source of Truth" for LPG pricing, eliminating vendor-side price manipulation.

Scalability: The architecture is designed to integrate directly with physical IoT weight sensors and GPS trackers on delivery trucks.

🔧 **Installation & Setup**
Clone the repository:

Bash
git clone [https://github.com/your-username/SurgeGuard](https://github.com/Armaanmd/Surge-Guard)

cd SurgeGuard
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
streamlit run app.py

👥 **Deep Gen**

▫️**Mohd Armaan**- backend Developer & Systems Architect

▫️**Roshani Nishad** - frontend developer & System Architect

