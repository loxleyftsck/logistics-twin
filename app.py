from flask import Flask, jsonify, render_template, request
import os
import time
import json
import math
import html
import requests
import numpy as np
import traceback
from threading import Lock
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
# Pastikan tsp_agent.py sudah berisi 5 Class Agent (Base, QL, Sarsa, MC, TD, Dyna)
from tsp_agent import QLearningAgent, SarsaAgent, MonteCarloAgent, TDLambdaAgent, DynaQAgent, TSPBaseAgent

# Flask App Configuration (V5.6 - Production Ready)
app = Flask(__name__, template_folder='templates', static_folder='static')

# V5.6: CORS Headers for secure cross-origin requests
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Configure specific domains in production
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# P0 Security Fix #1: Request Size Limit (prevent OOM)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# P0 Security Fix #2: Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# --- HAVERSINE DISTANCE HELPER (For Disaster Radius Calculation) ---
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# --- 1. DATA: 25 INDUSTRIAL NODES (SUPPLY CHAIN MAP) ---
# Emojis digunakan sebagai "Tag" untuk pewarnaan otomatis di Frontend
cities_data = {
    # --- JABODETABEK & JABAR (PRODUCTION) ---
    0:  {"name": "Tg. Priok Port ⚓", "lat": -6.1096, "lon": 106.8837},
    1:  {"name": "Jakarta City 🏢", "lat": -6.2088, "lon": 106.8456},
    2:  {"name": "Cikarang Dry Port 🏭", "lat": -6.2863, "lon": 107.1601},
    3:  {"name": "Karawang KIIC ⚙️", "lat": -6.3575, "lon": 107.2917},
    4:  {"name": "Bandung Teknopolis 🏢", "lat": -6.9175, "lon": 107.6191},
    5:  {"name": "Serang/Merak ⚓", "lat": -6.1104, "lon": 106.1634},

    # --- PANTURA CORRIDOR (MAIN ARTERY) ---
    6:  {"name": "Cirebon Port ⚓", "lat": -6.7320, "lon": 108.5523},
    7:  {"name": "Tegal 📍", "lat": -6.8797, "lon": 109.1256},
    8:  {"name": "Pekalongan 📍", "lat": -6.8898, "lon": 109.6746},
    9:  {"name": "Batang KITB 🏗️", "lat": -6.9133, "lon": 110.2033},
    10: {"name": "Semarang Tg Emas ⚓", "lat": -6.9472, "lon": 110.4356},

    # --- CENTRAL & SOUTH (FAILOVER/MARKET) ---
    11: {"name": "Purwokerto 📍", "lat": -7.4245, "lon": 109.2302},
    12: {"name": "Cilacap Ind. 🏭", "lat": -7.7279, "lon": 109.0077},
    13: {"name": "Yogyakarta 🏢", "lat": -7.7955, "lon": 110.3695},
    14: {"name": "Solo 🏢", "lat": -7.5755, "lon": 110.8243},
    15: {"name": "Madiun 📍", "lat": -7.6298, "lon": 111.5176},
    16: {"name": "Tasikmalaya 📍", "lat": -7.3274, "lon": 108.2207},

    # --- EAST JAVA HUB (DISTRIBUTION) ---
    17: {"name": "Tuban Industrial 🏭", "lat": -6.8976, "lon": 112.0642},
    18: {"name": "Bojonegoro 📍", "lat": -7.1502, "lon": 111.8818},
    19: {"name": "Surabaya Tg Perak ⚓", "lat": -7.2023, "lon": 112.7308},
    20: {"name": "Sidoarjo Waru 🏢", "lat": -7.3621, "lon": 112.7373},
    21: {"name": "Mojokerto Ngoro 🏭", "lat": -7.5583, "lon": 112.6120},
    22: {"name": "Pasuruan PIER ⚙️", "lat": -7.6181, "lon": 112.8711},
    23: {"name": "Probolinggo 📍", "lat": -7.7543, "lon": 113.2159},
    24: {"name": "Malang 🏢", "lat": -7.9666, "lon": 112.6326}
}

# --- 2. CLEANUP & INIT ---
if os.path.exists("q_table.npy"):
    try:
        os.remove("q_table.npy")
        print(">>> Memory Wiped (New Map Loaded)")
    except: pass

print(">>> Initializing Physics (OSRM Shared Matrix)...")
# Fetch Matrix 1x untuk dipakai ramai-ramai
base_physics = TSPBaseAgent(cities_data)
shared_matrix = base_physics.dist_matrix

# V5.0: Backup original matrix for disaster recovery (P0 Fix #2: Deep Copy)
base_matrix = shared_matrix.copy()

print(">>> Spawning THE FULL GRID (5 Agents)...")
agents = {
    'QL-Bot': QLearningAgent(cities_data, dist_matrix=shared_matrix, name="QL-Bot", color="blue"),
    'Sarsa-Bot': SarsaAgent(cities_data, dist_matrix=shared_matrix, name="Sarsa-Bot", color="green"),
    'MC-Bot': MonteCarloAgent(cities_data, dist_matrix=shared_matrix, name="MC-Bot", color="red"),
    'TD-Bot': TDLambdaAgent(cities_data, dist_matrix=shared_matrix, name="TD-Bot", color="orange"),
    'Dyna-Bot': DynaQAgent(cities_data, dist_matrix=shared_matrix, name="Dyna-Bot", color="purple")
}

# V5.0: Thread Lock for Safe Concurrent Access (P0 Fix #1)
lock = Lock()

# V5.4: Implement Real Economy Constants
PRICE_DIESEL = 15000   # Rp / Liter
PRICE_ELECTRIC = 2500  # Rp / kWh
DRIVER_WAGE_KM = 3000  # Rp / KM (Labor + Maintenance)

# V5.0: Disaster Management State
active_disasters = []  # List of {id, lat, lon, type, radius, multiplier}
disaster_id_counter = 0
DISASTER_LIMIT = 10  # P0 Fix #3: DoS Prevention

# V5.1: Severity-Based Disaster Configuration
SEVERITY_LEVELS = {
    1: {
        'name': 'Genangan',
        'description': 'Light flooding - high vehicles can pass',
        'multiplier': 1.2,
        'color': '#ffc107',  # Yellow
        'icon': '🌧️',
        'passable': True  # V5.1: Can pass with minor penalty
    },
    2: {
        'name': 'Banjir Sedang',
        'description': 'Moderate flood - significant delays',
        'multiplier': 2.5,  # V5.1: Increased from 2.0 for better differentiation
        'color': '#ff6f00',  # Orange
        'icon': '🌊',
        'passable': True  # V5.1: Can pass with heavy penalty
    },
    3: {
        'name': 'Longsor/Putus',
        'description': 'Road blocked - complete avoidance',
        'multiplier': 100.0,
        'color': '#b71c1c',  # Dark Red
        'icon': '🚫',
        'passable': False  # V5.1: Complete blockage
    }
}

# V5.1: Disaster Types (now just categories, severity determines impact)
DISASTER_TYPES = ['flood', 'quake', 'landslide']

# V5.4: Fleet Economy Configuration (Real Efficiency Model)
VEHICLES = {
    'diesel': {'label': 'Diesel Heavy', 'co2': 2.6, 'efficiency': 3.0, 'fuel': 'diesel', 'icon': 'bi-truck'}, # 3 km/L
    'hybrid': {'label': 'Hybrid Wingbox', 'co2': 1.8, 'efficiency': 5.0, 'fuel': 'diesel', 'icon': 'bi-battery-half'}, # 5 km/L
    'ev': {'label': 'Electric Semi', 'co2': 0.0, 'efficiency': 1.0, 'fuel': 'electric', 'icon': 'bi-lightning-charge'}, # 1 km/kWh (300kWh pack / 300km)
    'lng': {'label': 'LNG Truck', 'co2': 1.2, 'efficiency': 3.5, 'fuel': 'diesel', 'icon': 'bi-droplet'} # Simplified as diesel-equivalent for now or add LNG price later
}

CARGO = {
    'general': {'label': 'General Goods 📦', 'multiplier': 1.0, 'baseRevenue': 25000000},
    'cold': {'label': 'Cold Chain ❄️', 'multiplier': 1.8, 'baseRevenue': 65000000},
    'danger': {'label': 'Hazardous ☣️', 'multiplier': 2.5, 'baseRevenue': 85000000},
    'express': {'label': 'Express ⚡', 'multiplier': 1.5, 'baseRevenue': 45000000},
    # V5.3: Humanitarian Cargo
    'humanitarian': {
        'label': '🚑 Bantuan Bencana', 
        'multiplier': 0.5,        # Low commercial value
        'baseRevenue': 15000000,  # Flat rate (Rp 15jt)
        'reputation': 100,        # +100 Karma per delivery
        'is_emergency': True
    }
}

# V5.0.1: Disaster Type Configuration (Fix NameError)
DISASTER_TYPES_INFO = {
    'flood': {
        'name': 'Flood',
        'moves': False,
        'velocity': [0, 0],
        'decays': True,
        'decay_rate': 0.5,
        'default_lifetime': 300,
        'icon': '🌊'
    },
    'quake': {
        'name': 'Earthquake',
        'moves': False,
        'velocity': [0, 0],
        'decays': False,
        'decay_rate': 0,
        'default_lifetime': None,
        'icon': '🏚️'
    },
    'landslide': {
        'name': 'Landslide',
        'moves': False,
        'velocity': [0, 0],
        'decays': False,
        'decay_rate': 0,
        'default_lifetime': None,
        'icon': '🪨'
    },
    'storm': {
        'name': 'Storm',
        'moves': True,
        'velocity': [0.01, 0],  # Moving east ~1km/100 episodes
        'decays': False,
        'decay_rate': 0,
        'default_lifetime': 500,
        'icon': '⛈️'
    }
}

# V5.3: Global State
global_reputation = 0  # Starts at 0, max 1000

# V4.9.1: Fleet Configuration (matches frontend defaults)
fleet_config = {
    'QL-Bot': {'v': 'diesel', 'c': 'general'},
    'Sarsa-Bot': {'v': 'lng', 'c': 'general'},  # V4.9.1: LNG demonstration
    'MC-Bot': {'v': 'diesel', 'c': 'danger'},
    'TD-Bot': {'v': 'ev', 'c': 'express'},
    'Dyna-Bot': {'v': 'hybrid', 'c': 'cold'}
}

# V5.2: Weather System - Behavior Presets
WEATHER_PRESETS = {
    'storm': {
        'moves': True,
        'velocity': [0.01, 0],      # [lon, lat] degrees per episode (~1km East)
        'decays': False,
        'decay_rate': 0,
        'default_lifetime': 500      # Episodes before expiry
    },
    'flood': {
        'moves': False,
        'velocity': [0, 0],
        'decays': True,
        'decay_rate': 0.5,           # km per episode
        'default_lifetime': 300
    },
    'quake': {
        'moves': False,
        'velocity': [0, 0],
        'decays': False,
        'decay_rate': 0,
        'default_lifetime': None     # Permanent until cleared
    },
    'landslide': {
        'moves': False,
        'velocity': [0, 0],
        'decays': True,
        'decay_rate': 0.2,           # Slower decay than flood
        'default_lifetime': 400
    }
}

top_records = []
total_episodes = 0

# --- 3. API ENDPOINTS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns system status and key metrics.
    """
    return jsonify({
        "status": "healthy",
        "version": "V5.6.1",
        "agents": len(agents),
        "cities": len(cities_data),
        "disasters": len(active_disasters),
        "episodes": total_episodes,
        "uptime": "running",
        "features": ["CORS", "Rate-Limiting", "Multi-Stage-Docker", "OSRM-Proxy"]
    }), 200

# V5.6: OSRM Proxy Endpoint with Timeout
@app.route('/api/route', methods=['POST'])
@limiter.limit("100 per minute")
def get_osrm_route():
    """
    Proxy endpoint for OSRM routing with timeout protection.
    Prevents hanging requests to external OSRM service.
    """
    try:
        coords = request.json.get('coords')
        if not coords:
            return jsonify({"error": "Missing coordinates"}), 400
        
        # Call OSRM with 5-second timeout
        osrm_url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"
        response = requests.get(osrm_url, timeout=5)
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "OSRM service error"}), response.status_code
            
    except requests.Timeout:
        return jsonify({"error": "Route service timeout"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_cities')
def get_cities():
    simple_data = {info['name']: [info['lat'], info['lon']] for _, info in cities_data.items()}
    return jsonify(simple_data)

@app.route('/api/reset')
def reset_sim():
    # V5.4: Use SimulationManager
    sim_manager.reset()
    
    # Reset Physics
    global shared_matrix
    shared_matrix[:] = base_matrix.copy()
    
    for agent in agents:
        agent.q_table.clear()
        agent.epsilon = 1.0
        agent.dist_matrix = shared_matrix 
        if hasattr(agent, 'e_traces'): agent.e_traces.clear()
        if hasattr(agent, 'model'): agent.model.clear()
    return jsonify({"status": "reset"})

# --- V5.4 REFACTOR: SIMULATION MANAGER ---
class SimulationManager:
    def __init__(self):
        self.reputation = 0
        self.disasters = []
        self.total_episodes = 0
        self.top_records = []
        
        # State Guards
        self.lock = Lock()
        
    def reset(self):
        self.reputation = 0
        self.disasters = []
        self.total_episodes = 0
        self.top_records = []
        global disaster_id_counter, active_disasters
        disaster_id_counter = 0
        active_disasters = [] # Sync with legacy global for now
        
    def update_physics(self):
        """Encapsulated Physics Update"""
        global shared_matrix, active_disasters
        
        # Sync disasters from global to internal state
        self.disasters = active_disasters
        
        # P0 Fix #9: Start from clean slate
        shared_matrix[:] = base_matrix.copy()
        
        # Apply disasters
        for disaster in self.disasters:
            lat = disaster['lat']
            lon = disaster['lon']
            radius = disaster['radius']
            multiplier = disaster['multiplier']
            
            # Optimization: Pre-calc affected cities
            affected_cities = []
            for city_id, city_data in cities_data.items():
                d = haversine_distance(lat, lon, city_data['lat'], city_data['lon'])
                if d <= radius: affected_cities.append(city_id)
            
            # V5.1: Graduated Severity Penalties
            severity = disaster.get('severity', 2)  # Default to L2
            num_cities = len(cities_data)
            
            if severity == 1:
                # L1: Only penalize roads FULLY inside zone (both endpoints affected)
                for city_i in affected_cities:
                    for city_j in affected_cities:
                        if city_i != city_j:
                            dist_ij = shared_matrix[city_i][city_j]
                            dist_ji = shared_matrix[city_j][city_i]
                            shared_matrix[city_i][city_j] = min(dist_ij * multiplier, 100000)
                            shared_matrix[city_j][city_i] = min(dist_ji * multiplier, 100000)
            
            elif severity == 2:
                # L2: Penalize any road TOUCHING zone (one endpoint affected)
                for city_i in affected_cities:
                    for city_j in range(num_cities):
                        if city_i != city_j:
                            dist_ij = shared_matrix[city_i][city_j]
                            dist_ji = shared_matrix[city_j][city_i]
                            shared_matrix[city_i][city_j] = min(dist_ij * multiplier, 100000)
                            shared_matrix[city_j][city_i] = min(dist_ji * multiplier, 100000)
            
            else:  # severity == 3
                # L3: Complete blockage (100x multiplier creates effective closure)
                for city_i in affected_cities:
                    for city_j in range(num_cities):
                        if city_i != city_j:
                            dist_ij = shared_matrix[city_i][city_j]
                            dist_ji = shared_matrix[city_j][city_i]
                            shared_matrix[city_i][city_j] = min(dist_ij * multiplier, 100000)
                            shared_matrix[city_j][city_i] = min(dist_ji * multiplier, 100000)
                     
        # Propagate to agents
        for agent in agents:
            agent.dist_matrix = shared_matrix
            
    def update_disasters_lifecycle(self):
        """Encapsulated Lifecycle Logic"""
        global active_disasters
        
        # Sync from global
        self.disasters = active_disasters
        
        expired_ids = []
        modified = False
        
        for d in self.disasters:
            d['age'] += 1
            if d.get('is_moving', False):
                d['lon'] += d['velocity'][0]
                d['lat'] += d['velocity'][1]
                modified = True
                
            if d.get('is_decaying', False):
                d['radius'] = max(10, d['radius'] - d['decay_rate'])
                modified = True
                if d['radius'] <= 10: expired_ids.append(d['id'])
                
            lifetime = d.get('lifetime')
            if lifetime and d['age'] >= lifetime:
                expired_ids.append(d['id'])
                
        if expired_ids:
             self.disasters = [d for d in self.disasters if d['id'] not in expired_ids]
             active_disasters = self.disasters  # Sync back to global
             modified = True
             
        if modified:
            self.update_physics()
            
        return len(expired_ids)

# Initialize Singleton
sim_manager = SimulationManager()

# Legacy recalculate_physics definition removed (Moved to SimManager)

# V5.2: Temporal Disaster System - Update Function
def update_disasters():
    """
    Update disaster positions and properties based on lifecycle.
    Called after each training episode to simulate temporal evolution.
    Returns: Number of disasters expired
    """
    global active_disasters
    
    disasters_modified = False
    expired_disasters = []
    
    for disaster in active_disasters:
        disaster['age'] += 1
        
        # V5.2: Movement Logic (storms drift East)
        if disaster.get('is_moving', False):
            velocity = disaster.get('velocity', [0, 0])
            disaster['lon'] += velocity[0]  # East/West movement
            disaster['lat'] += velocity[1]  # North/South movement
            disasters_modified = True
            
            # Boundary check: Keep disaster within Java region
            disaster['lat'] = max(-9.0, min(-5.0, disaster['lat']))
            disaster['lon'] = max(105.0, min(115.0, disaster['lon']))
        
        # V5.2: Decay Logic (floods recede)
        if disaster.get('is_decaying', False):
            decay_rate = disaster.get('decay_rate', 0)
            disaster['radius'] = max(10, disaster['radius'] - decay_rate)
            disasters_modified = True
            
            # Auto-remove if shrunk to minimum
            if disaster['radius'] <= 10:
                expired_disasters.append(disaster['id'])
                print(f">>> Disaster {disaster['id']} ({disaster['type']}) expired (shrunk to minimum)")
        
# --- LEGACY FUNCTIONS REMOVED (Moved to SimulationManager) ---
# recalculate_physics and update_disasters logic is now inside SimulationManager
# For backward compatibility during refactor transition:
def recalculate_physics(): sim_manager.update_physics()
def update_disasters(): return sim_manager.update_disasters_lifecycle()

# --- V5.0/5.2: DISASTER API ENDPOINTS ---

@app.route('/api/train')
@limiter.limit("30 per minute")  # P0 Security: Rate limit training endpoint
def train_step():
    try:
        global total_episodes # Legacy global
        
        # Batch Size Kecil agar Browser tidak lag dengan 5 agen
        batch_size = 5 
        
        routes_data = []
        with lock:
            for agent_name, agent in agents.items():
                # Get current fleet config
                conf = fleet_config.get(agent_name, {'v': 'diesel', 'c': 'general'})
                cargo_type = conf['c']
                cargo_props = CARGO.get(cargo_type, CARGO['general'])
                
                # Determine Objective (V5.3)
                objective = 'time' if cargo_type == 'humanitarian' else 'profit'
                
                # Train one episode
                agent.train_episode(objective=objective)
                
                # Get best route & stats
                dist, route_indices = agent.get_best_route_distance()
                path_names = [cities_data[idx]['name'] for idx in route_indices] if route_indices else []
                
                # V5.4: Real Cost Calculation
                vehicle_props = VEHICLES.get(conf['v'], VEHICLES['diesel'])
                efficiency = vehicle_props.get('efficiency', 3.0)
                fuel_type = vehicle_props.get('fuel', 'diesel')
                fuel_price = PRICE_ELECTRIC if fuel_type == 'electric' else PRICE_DIESEL
                
                fuel_needed = dist / efficiency
                fuel_cost = fuel_needed * fuel_price
                labor_cost = dist * DRIVER_WAGE_KM
                total_cost = (fuel_cost + labor_cost) * cargo_props['multiplier']
                
                revenue = cargo_props['baseRevenue']
                profit = revenue - total_cost
                
                # V5.3: Reputation Update
                if cargo_type == 'humanitarian':
                    sim_manager.reputation += cargo_props.get('reputation', 0)
                    if sim_manager.reputation > 1000: sim_manager.reputation = 1000
                
                routes_data.append({
                    'agent': agent_name,
                    'episode': total_episodes, 
                    'distance': round(dist, 2),
                    'cost': round(total_cost, 0),
                    'profit': round(profit, 0),
                    'epsilon': round(agent.epsilon, 4),
                    'color': agent.color,
                    'path': path_names,  # Changed from 'route' to 'path' for V4.9.1 frontend
                    'cargo': cargo_type
                })
                
                # Hall of Fame Logic
                rounded_dist = round(dist, 2)
                is_duplicate = False
                for r in sim_manager.top_records:
                    if abs(r['distance'] - rounded_dist) < 0.01:
                        is_duplicate = True
                        break
                
                if not is_duplicate and rounded_dist > 0:
                    if len(sim_manager.top_records) < 5 or rounded_dist < sim_manager.top_records[-1]['distance']:
                        sim_manager.top_records.append({'agent': agent.name, 'distance': rounded_dist, 'rank': 0})
                        sim_manager.top_records.sort(key=lambda x: x['distance'])
                        sim_manager.top_records = sim_manager.top_records[:5]
                        for i, rec in enumerate(sim_manager.top_records): rec['rank'] = i + 1
        
        total_episodes += 1
        
        # Temporal Disaster Cycle
        expired = sim_manager.update_disasters_lifecycle()

        return jsonify({
            'routes': routes_data,
            'best_routes': sim_manager.top_records,
            'episode': total_episodes,
            'disasters_expired': expired,
            'reputation': sim_manager.reputation
        })

    except Exception as e:
        # 🚨 V5.0.1: LOUD ERROR LOGGING (Red Team Hardening)
        print(f"\n{'='*60}")
        print(f"🚨 CRITICAL ERROR IN /api/train")
        print(f"Episode: {total_episodes}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*60}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__,
            'status': 'failed',
            'routes': [],
            'message': 'Training loop crashed. Check server logs for full traceback.'
        }), 500

@app.route('/api/sabotage', methods=['POST'])
def sabotage():
    data = request.json
    city_from = data.get('from')
    city_to = data.get('to')
    status = data.get('status')
    
    id_from, id_to = None, None
    for pid, info in cities_data.items():
        if info['name'] == city_from: id_from = pid
        if info['name'] == city_to: id_to = pid
            
    if id_from is not None and id_to is not None:
        for agent in agents:
            agent.set_road_status(id_from, id_to, status)
        return jsonify({"status": "success", "message": f"Sabotage {status} applied!"})
    
    return jsonify({"status": "error", "message": "City not found"}), 400

# --- V5.0: DISASTER API ENDPOINTS ---

@app.route('/api/disaster', methods=['POST'])
def create_disaster():
    """
    Create a disaster zone with severity levels (V5.1).
    Implements all P0 validation fixes + severity system.
    """
    global disaster_id_counter, active_disasters
    
    try:
        data = request.json
        
        # P0 Fix #3: DoS Prevention - Disaster Limit
        if len(active_disasters) >= DISASTER_LIMIT:
            return jsonify({
                "status": "error", 
                "message": f"Disaster limit reached ({DISASTER_LIMIT} max). Clear some disasters first."
            }), 429
        
        # Extract parameters
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))
        disaster_type = data.get('type', 'flood').lower()  # flood/quake/landslide
        severity = int(data.get('severity', 2))  # V5.1: Default to level 2
        radius = float(data.get('radius', 50))
        
        # P0 Fix #5: Coordinate Validation (Java region bounds)
        if not (-9.0 <= lat <= -5.0 and 105.0 <= lon <= 115.0):
            return jsonify({
                "status": "error",
                "message": "Coordinates outside Java region (-9 to -5 lat, 105 to 115 lon)"
            }), 400
        
        # V5.1: Severity Validation
        if severity not in SEVERITY_LEVELS:
            return jsonify({
                "status": "error",
                "message": f"Invalid severity level. Must be one of: {list(SEVERITY_LEVELS.keys())}"
            }), 400
            
        # V5.2: Create disaster using Type Config & Severity
        sev_info = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS[2])
        severity_config = sev_info  # Alias for compatibility
        type_info = DISASTER_TYPES_INFO.get(disaster_type, DISASTER_TYPES_INFO['flood'])
        
        disaster = {
            'id': disaster_id_counter,
            'lat': lat,
            'lon': lon,
            'type': disaster_type,
            'severity': severity,
            'severity_name': sev_info['name'],
            'radius': radius,
            'multiplier': sev_info['multiplier'],
            'color': sev_info['color'],
            'icon': sev_info['icon'],
            
            # Lifecycle
            'age': 0,
            'spawn_episode': total_episodes,
            'is_moving': type_info['moves'],
            'velocity': type_info['velocity'],
            'is_decaying': type_info['decays'],
            'decay_rate': type_info['decay_rate'],
            'lifetime': type_info['default_lifetime']
        }
        
        active_disasters.append(disaster)
        disaster_id_counter += 1
        
        # Update Physics
        sim_manager.update_physics()
        
        lifecycle_info = ""
        if type_info['moves']:
            lifecycle_info += f" [Moving {type_info['velocity'][0]*100:.1f}km/100ep]"
        if type_info['decays']:
            lifecycle_info += f" [Decaying {type_info['decay_rate']}km/ep]"
        if type_info['default_lifetime']:
            lifecycle_info += f" [TTL: {type_info['default_lifetime']}ep]"
        
        print(f">>> Disaster Created: {severity_config['name']} ({disaster_type.upper()}) at ({lat:.2f}, {lon:.2f}), radius {radius}km{lifecycle_info}")
        
        return jsonify({
            "status": "success",
            "disaster": disaster,
            "message": f"{severity_config['icon']} {severity_config['name']} created!"
        })
        
    except (ValueError, TypeError) as e:
        return jsonify({
            "status": "error",
            "message": f"Invalid data format: {str(e)}"
        }), 400

@app.route('/api/disaster', methods=['DELETE'])
def clear_disasters():
    """
    Clear all active disasters and restore original physics.
    """
    global active_disasters, disaster_id_counter
    
    count = len(active_disasters)
    active_disasters = []
    disaster_id_counter = 0
    
    # Reset physics to original state
    shared_matrix[:] = base_matrix.copy()
    
    # P0 Fix #1: Force propagate to agents
    for agent in agents:
        agent.dist_matrix = shared_matrix
    
    print(f">>> All Disasters Cleared ({count} removed)")
    
    return jsonify({
        "status": "success",
        "message": f"Cleared {count} disaster(s)",
        "active_count": 0
    })

@app.route('/api/disasters', methods=['GET'])
def get_disasters():
    """
    Get list of active disasters.
    """
    return jsonify({
        "disasters": active_disasters,
        "count": len(active_disasters),
        "limit": DISASTER_LIMIT
    })

@app.route('/api/update_config', methods=['POST'])
def update_config():
    global cities_data, agents, top_records, total_episodes, shared_matrix
    
    try:
        new_data = request.json.get('cities')
        if not new_data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Konversi keys JSON (string) kembali ke integer jika perlu
        # Rebuild dictionary dengan keys integer
        cleaned_cities = {}
        for k, v in new_data.items():
            # P0 Security Fix #3: Sanitize inputs (prevent XSS)
            cleaned_cities[int(k)] = {
                'name': html.escape(str(v['name'])[:50]),  # Max 50 chars, escape HTML
                'lat': max(-90, min(90, float(v['lat']))),  # Clamp latitude range
                'lon': max(-180, min(180, float(v['lon'])))  # Clamp longitude range
            }
            
        # 1. Update Global Data
        cities_data = cleaned_cities
        
        # 2. Reset Memory
        if os.path.exists("q_table.npy"):
            os.remove("q_table.npy")
            
        # 3. Re-Fetch OSRM Matrix (Berat, tapi perlu)
        print(">>> Re-initializing Physics (New Map)...")
        base_physics = TSPBaseAgent(cities_data)
        shared_matrix = base_physics.dist_matrix
        
        # 4. Re-Spawn Agents
        agents = [
            QLearningAgent(cities_data, dist_matrix=shared_matrix, name="QL-Bot", color="blue"),
            SarsaAgent(cities_data, dist_matrix=shared_matrix, name="Sarsa-Bot", color="green"),
            MonteCarloAgent(cities_data, dist_matrix=shared_matrix, name="MC-Bot", color="red"),
            TDLambdaAgent(cities_data, dist_matrix=shared_matrix, name="TD-Bot", color="orange"),
            DynaQAgent(cities_data, dist_matrix=shared_matrix, name="Dyna-Bot", color="purple")
        ]
        
        # 5. Reset Stats
        top_records = []
        total_episodes = 0
        
        return jsonify({"status": "success", "message": "Map Updated! Simulation Reset."})
        
    except Exception as e:
        print(f"Config Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- V4.9: BRAIN PERSISTENCE (SAVE/LOAD Q-TABLE) ---

@app.route('/api/save_brain')
def save_brain():
    """
    Serialize Q-tables to JSON format for persistent storage.
    Includes metadata for validation on load.
    """
    dump = {
        'version': '4.9',
        'num_cities': len(cities_data),
        'episodes': total_episodes,
        'agents': {}
    }
    
    for agent in agents:
        q_data = {}
        # Convert tuple state keys to string for JSON compatibility
        for state, actions in agent.q_table.items():
            key = f"{state[0]}|{state[1]}"  # "city_id|visited_mask"
            q_data[key] = dict(actions)
        
        dump['agents'][agent.name] = {
            'q_table': q_data,
            'epsilon': agent.epsilon
        }
    
    print(f">>> BRAIN SAVED: {len(dump['agents'])} agents, Episode {total_episodes}")
    return jsonify(dump)


@app.route('/api/load_brain', methods=['POST'])
def load_brain():
    """
    Restore Q-tables from JSON with validation.
    Hardening: city count, epsilon range, Q-table size.
    """
    global total_episodes
    
    try:
        data = request.json
        
        # VALIDATION #1: City Count Compatibility
        saved_cities = data.get('num_cities', 0)
        if saved_cities != len(cities_data):
            return jsonify({
                "msg": f"Brain incompatible! Saved for {saved_cities} cities, current map has {len(cities_data)} cities."
            }), 400
        
        # VALIDATION #2: Version Check (optional warning)
        saved_version = data.get('version', 'unknown')
        if saved_version != '4.9':
            print(f">>> WARNING: Loading brain from version {saved_version}")
        
        # Restore episode counter
        total_episodes = data.get('episodes', 0)
        
        for agent in agents:
            if agent.name not in data.get('agents', {}):
                continue
            
            saved_data = data['agents'][agent.name]
            
            # VALIDATION #3: Epsilon Clamping (0.01-1.0 range)
            raw_epsilon = saved_data.get('epsilon', 1.0)
            agent.epsilon = max(0.01, min(1.0, raw_epsilon))
            
            # VALIDATION #4: Q-table Size Limit (prevent memory bomb)
            q_table_data = saved_data.get('q_table', {})
            if len(q_table_data) > 100000:
                return jsonify({
                    "msg": f"{agent.name} Q-table too large ({len(q_table_data)} states, max 100k)"
                }), 400
            
            # Clear existing Q-table
            agent.q_table.clear()
            
            # Restore Q-values
            for key_str, actions in q_table_data.items():
                try:
                    # Parse "city|mask" back to tuple (city_id, visited_mask)
                    parts = key_str.split('|')
                    city_id = int(parts[0])
                    mask = int(parts[1])
                    
                    # VALIDATION #5: State Range Check (skip invalid states)
                    if city_id >= len(cities_data):
                        continue  # Skip states for cities that don't exist
                    
                    state = (city_id, mask)
                    
                    # Restore actions
                    for action_str, value in actions.items():
                        action = int(action_str)
                        agent.q_table[state][action] = float(value)
                        
                except (ValueError, IndexError) as e:
                    print(f">>> Skipping corrupt state: {key_str}")
                    continue
        
        print(f">>> BRAIN RESTORED: Episode {total_episodes}, {len(agents)} agents loaded")
    except KeyError as e:
        return jsonify({"msg": f"Invalid brain file format: missing {str(e)}"}), 400
    except Exception as e:
        print(f">>> LOAD FAILED: {str(e)}")
        return jsonify({"msg": f"Load failed: {str(e)}"}), 500


# --- P0: INTERPRETABILITY & WHAT-IF FEATURES ---

@app.route('/api/explain/<agent_name>', methods=['GET'])
def explain_decision(agent_name):
    """
    P0.1: Decision Explanation - Interpretability Feature
    Returns why agent chose current route based on Q-values
    """
    try:
        # agents is a dictionary, access directly by key
        if agent_name not in agents:
            return jsonify({"error": "Agent not found"}), 404
        
        target_agent = agents[agent_name]
        
        # Get current state (assuming start from city 0)
        start_city = 0
        mask = 1 << start_city
        state = (start_city, mask)
        
        # Get valid actions (cities not yet visited)
        valid_actions = [city for city in range(len(cities_data)) if not (mask & (1 << city))]
        
        # If Q-table empty, agent is still exploring
        if not target_agent.q_table or state not in target_agent.q_table:
            return jsonify({
                "agent": agent_name,
                "status": "exploring",
                "message": "Agent still exploring - insufficient training data",
                "epsilon": round(target_agent.epsilon, 4),
                "actions": []
            })
        
        # Get Q-values for valid actions
        q_values = []
        total_q_magnitude = 0
        for action in valid_actions:
            q_val = target_agent.q_table[state].get(action, 0.0)
            city_name = cities_data[action]['name']
            q_values.append({
                "city_id": action,
                "city_name": city_name,
                "q_value": round(q_val, 2)
            })
            total_q_magnitude += abs(q_val)
        
        # Sort by Q-value descending
        q_values.sort(key=lambda x: x['q_value'], reverse=True)
        
        # Calculate percentages for top 3
        top_3 = q_values[:3]
        for item in top_3:
            if total_q_magnitude > 0:
                item['percentage'] = round((abs(item['q_value']) / total_q_magnitude) * 100, 1)
            else:
                item['percentage'] = 33.3  # Equal if all zeros
        
        # Decision factors (simple heuristic based on Q-value magnitude)
        best_q = top_3[0]['q_value'] if top_3 else 0
        factors = []
        if best_q > 500:
            factors.append({"factor": "Short distance", "weight": 60})
            factors.append({"factor": "Low cost", "weight": 40})
        elif best_q > 200:
            factors.append({"factor": "Moderate distance", "weight": 50})
            factors.append({"factor": "Disaster avoidance", "weight": 30})
            factors.append({"factor": "Cost efficiency", "weight": 20})
        else:
            factors.append({"factor": "Exploration", "weight": 70})
            factors.append({"factor": "Unknown route", "weight": 30})
        
        return jsonify({
            "agent": agent_name,
            "status": "trained",
            "current_epsilon": round(target_agent.epsilon, 4),
            "top_routes": top_3,
            "decision_factors": factors,
            "total_states_explored": len(target_agent.q_table)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/disaster_impact', methods=['POST'])
def calculate_disaster_impact():
    """
    P0.2: Disaster Impact Calculator - What-If Scenario Feature
    Simulates disaster without mutating state (preview mode)
    """
    try:
        data = request.json
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))
        severity = int(data.get('severity', 2))
        radius = float(data.get('radius', 50))
        
        # Validate inputs
        if severity not in SEVERITY_LEVELS:
            return jsonify({"error": "Invalid severity level"}), 400
        
        # Calculate affected cities
        affected_cities = []
        for city_id, city_data in cities_data.items():
            dist = haversine_distance(lat, lon, city_data['lat'], city_data['lon'])
            if dist <= radius:
                affected_cities.append({
                    "id": city_id,
                    "name": city_data['name'],
                    "distance_from_disaster": round(dist, 1)
                })
        
        # Simulate impact on current routes (read-only)
        sev_info = SEVERITY_LEVELS[severity]
        multiplier = sev_info['multiplier']
        
        # Calculate cost increase for each agent's current route
        route_impacts = []
        total_affected_routes = 0

        # agents is already a dictionary
        for agent_name, agent in agents.items():
            dist, route = agent.get_best_route_distance()
            
            # Check if route passes through affected zone
            is_affected = False
            for city_id in route:
                if any(city_id == ac['id'] for ac in affected_cities):
                    is_affected = True
                    break
            
            if is_affected:
                total_affected_routes += 1
                original_cost = dist * 8000  # Base cost estimate
                impacted_cost = dist * 8000 * multiplier
                cost_increase = impacted_cost - original_cost
                
                route_impacts.append({
                    "agent": agent_name,
                    "original_distance": round(dist, 1),
                    "cost_increase": round(cost_increase, 0),
                    "cost_increase_pct": round(((multiplier - 1) * 100), 1),
                    "affected_cities": [ac['name'] for ac in affected_cities if ac['id'] in route]
                })
        
        # Find alternate routes (simplified - just show count)
        alternate_options = len(cities_data) - len(affected_cities)
        
        return jsonify({
            "disaster_preview": {
                "severity": severity,
                "severity_name": sev_info['name'],
                "icon": sev_info['icon'],
                "multiplier": multiplier,
                "radius": radius,
                "location": {"lat": lat, "lon": lon}
            },
            "impact_summary": {
                "affected_cities_count": len(affected_cities),
                "affected_cities": [ac['name'] for ac in affected_cities],
                "routes_affected": f"{total_affected_routes}/{len(agents)}",
                "alternate_routes_available": alternate_options
            },
            "agent_impacts": route_impacts,
            "recommendation": "High impact - consider alternate routing" if total_affected_routes >= 3 else "Moderate impact - monitor situation"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agent_comparison', methods=['GET'])
def get_agent_comparison():
    """
    P0.3: Agent Comparison - Policy Comparison Feature
    Aggregates metrics for side-by-side agent analysis
    """
    try:
        comparison_data = []
        
        # agents is already a dictionary
        for agent_name, agent in agents.items():
            # Get current fleet config
            conf = fleet_config.get(agent_name, {'v': 'diesel', 'c': 'general'})
            vehicle = VEHICLES.get(conf['v'], VEHICLES['diesel'])
            cargo = CARGO.get(conf['c'], CARGO['general'])
            
            # Calculate metrics
            dist, route = agent.get_best_route_distance()
            
            # Cost calculation
            efficiency = vehicle.get('efficiency', 3.0)
            fuel_type = vehicle.get('fuel', 'diesel')
            fuel_price = PRICE_ELECTRIC if fuel_type == 'electric' else PRICE_DIESEL
            
            fuel_needed = dist / efficiency
            fuel_cost = fuel_needed * fuel_price
            labor_cost = dist * DRIVER_WAGE_KM
            total_cost = (fuel_cost + labor_cost) * cargo['multiplier']
            
            # Revenue & Profit
            revenue = cargo['baseRevenue']
            profit = revenue - total_cost
            
            # CO2 calculation
            co2_per_km = vehicle.get('co2', 2.6)
            total_co2 = dist * co2_per_km
            
            # Route diversity (unique states in Q-table)
            unique_routes = len(agent.q_table)
            
            # Convergence (estimated from epsilon)
            convergence_pct = round((1.0 - agent.epsilon) * 100, 1)
            
            comparison_data.append({
                "agent": agent_name,
                "color": agent.color,
                "vehicle": vehicle['label'],
                "cargo": cargo['label'],
                "metrics": {
                    "avg_profit": round(profit, 0),
                    "avg_distance": round(dist, 1),
                    "avg_co2": round(total_co2, 1),
                    "avg_cost": round(total_cost, 0),
                    "route_diversity": unique_routes,
                    "convergence": f"{convergence_pct}%"
                },
                "ranking": {
                    "profit": 0,  # Will be calculated after sorting
                    "green": 0,
                    "cost": 0
                }
            })
        
        # Calculate rankings
        # Profit ranking (highest = best)
        profit_sorted = sorted(comparison_data, key=lambda x: x['metrics']['avg_profit'], reverse=True)
        for rank, item in enumerate(profit_sorted, 1):
            next(a for a in comparison_data if a['agent'] == item['agent'])['ranking']['profit'] = rank
        
        # Green ranking (lowest CO2 = best)
        green_sorted = sorted(comparison_data, key=lambda x: x['metrics']['avg_co2'])
        for rank, item in enumerate(green_sorted, 1):
            next(a for a in comparison_data if a['agent'] == item['agent'])['ranking']['green'] = rank
        
        # Cost ranking (lowest = best)
        cost_sorted = sorted(comparison_data, key=lambda x: x['metrics']['avg_cost'])
        for rank, item in enumerate(cost_sorted, 1):
            next(a for a in comparison_data if a['agent'] == item['agent'])['ranking']['cost'] = rank
        
        # Determine overall winner
        best_profit = profit_sorted[0]
        best_green = green_sorted[0]
        best_cost = cost_sorted[0]
        
        return jsonify({
            "comparison": comparison_data,
            "winners": {
                "most_profitable": best_profit['agent'],
                "most_green": best_green['agent'],
                "lowest_cost": best_cost['agent']
            },
            "episode": total_episodes,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 JAVA LOGISTICS TWIN V5.4 - PRODUCTION READY")
    print("="*60)
    print(f"📍 Industrial Nodes: {len(cities_data)}")
    print(f"🤖 Active Agents: {len(agents)}")
    print(f"🧠 Save/Load: ENABLED (with validation)")
    print(f"🌦️ Dynamic Weather: Moving Storms + Receding Floods")
    print(f"🔍 NEW: Decision Explanation + Impact Preview + Agent Comparison")
    print("="*60 + "\n")
    
    # Production-safe configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    if debug_mode:
        print("⚠️  WARNING: Running in DEBUG mode (for development only)")
    else:
        print("✅ Running in PRODUCTION mode (debug disabled)")
    
    app.run(debug=debug_mode, host=host, port=port)
