import numpy as np
import random
import requests
import math
import time
import os
from collections import defaultdict

# === V5.7: Test Helper Functions (Module-Level) ===
# These standalone functions are required by test suite

def calculate_total_distance(route, distance_matrix):
    """
    Calculate total distance for a given route.
    
    Args:
        route: List of city indices representing the route
        distance_matrix: 2D array/matrix of distances
    
    Returns:
        float: Total distance of the route
    """
    total = 0.0
    for i in range(len(route) - 1):
        from_city, to_city = route[i], route[i + 1]
        total += distance_matrix[from_city][to_city]
    return total


def generate_random_route(num_cities):
    """
    Generate a random route visiting all cities exactly once.
    
    Args:
        num_cities: Number of cities to visit
    
    Returns:
        list: Random permutation of city indices
    """
    route = list(range(num_cities))
    random.shuffle(route)
    return route


def solve_tsp_genetic(distance_matrix, population_size=20, generations=50):
    """
    Solve TSP using a simple genetic algorithm.
    
    Args:
        distance_matrix: 2D array of distances
        population_size: Number of routes in population
        generations: Number of evolutionary generations
    
    Returns:
        dict: {'best_route': list, 'best_distance': float}
    """
    num_cities = len(distance_matrix)
    
    # Initialize population with random routes
    population = [generate_random_route(num_cities) for _ in range(population_size)]
    
    def fitness(route):
        # Return negative distance (we want to minimize)
        return -calculate_total_distance(route + [route[0]], distance_matrix)
    
    # Evolve population
    for gen in range(generations):
        # Sort by fitness (best first)
        population.sort(key=fitness, reverse=True)
        
        # Keep top 50% (elitism)
        survivors = population[:population_size // 2]
        
        # Create offspring
        offspring = []
        while len(offspring) < population_size - len(survivors):
            # Simple crossover: take first half from parent1, rest from parent2
            parent1, parent2 = random.sample(survivors, 2)
            cutpoint = num_cities // 2
            
            child = parent1[:cutpoint]
            for city in parent2:
                if city not in child:
                    child.append(city)
            offspring.append(child)
        
        population = survivors + offspring
    
    # Return best solution
    best_route = min(population, key=lambda r: calculate_total_distance(r + [r[0]], distance_matrix))
    best_distance = calculate_total_distance(best_route + [best_route[0]], distance_matrix)
    
    return {
        'best_route': best_route,
        'best_distance': best_distance
    }


def create_distance_matrix(cities):
    """
    Create distance matrix from city coordinates using Haversine formula.
    
    Args:
        cities: Dict mapping city_id -> {'lat': float, 'lon': float}
    
    Returns:
        numpy.ndarray: Distance matrix (km)
    """
    num_cities = len(cities)
    ids = sorted(cities.keys())
    matrix = np.zeros((num_cities, num_cities), dtype=np.float32)
    
    for i in range(num_cities):
        for j in range(num_cities):
            if i == j:
                continue
            
            city1 = cities[ids[i]]
            city2 = cities[ids[j]]
            
            # Haversine formula
            R = 6371  # Earth radius in km
            lat1, lon1 = math.radians(city1['lat']), math.radians(city1['lon'])
            lat2, lon2 = math.radians(city2['lat']), math.radians(city2['lon'])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
            c = 2 * math.asin(math.sqrt(a))
            
            matrix[i][j] = R * c
    
    return matrix


class TSPBaseAgent:
    def __init__(self, cities, dist_matrix=None, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.9995, **kwargs):
        self.cities = cities
        self.num_cities = len(cities)
        self.name = "BaseAgent"
        self.color = "gray"
        
        # Unique Seed: Agar agen tidak bergerak kembar identik
        seed_val = time.time() + id(self)
        random.seed(seed_val)
        
        # Physics: Distance Matrix (OSRM / Haversine)
        if dist_matrix is not None:
            self.dist_matrix = dist_matrix
            print(f"[{self.name}] Using Shared Distance Matrix.")
        else:
            self.dist_matrix = self.calculate_distance_matrix(cities)
            
        # Backup untuk fitur Sabotase (God Mode)
        self.original_distance_matrix = self.dist_matrix.copy()
            
        # Hyperparameters
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = 0.01
        
        # Q-Table: Dictionary of Dictionaries (Sparse Matrix)
        self.q_table = defaultdict(lambda: defaultdict(float))

    def calculate_distance_matrix(self, cities):
        """Fetch OSRM Matrix dengan Fallback ke Haversine"""
        # Urutkan berdasarkan index key (0, 1, 2...)
        ids = sorted(cities.keys())
        coords = []
        for i in ids:
            c = cities[i]
            coords.append(f"{c['lon']},{c['lat']}")
        
        coords_str = ";".join(coords)
        url = f"http://router.project-osrm.org/table/v1/driving/{coords_str}?annotations=distance"
        
        print(f"--- Fetching OSRM Matrix for {self.num_cities} cities ---")
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"OSRM Error {resp.status_code}. Fallback to Haversine.")
                return self.get_haversine_matrix(cities)
                
            data = resp.json()
            if data.get('code') != 'Ok':
                print(f"OSRM Logic Error: {data.get('code')}. Fallback.")
                return self.get_haversine_matrix(cities)
                
            # Konversi Meter ke KM
            distances = np.array(data['distances'], dtype=np.float32) / 1000.0 
            
            # Validasi Ukuran
            if distances.shape[0] != self.num_cities:
                 print(f"OSRM Shape Mismatch. Fallback.")
                 return self.get_haversine_matrix(cities)
            
            print(">>> SUCCESS: OSRM Real Distances Loaded.")
            return distances
            
        except Exception as e:
            print(f"OSRM Failed ({str(e)}). Using Haversine Fallback.")
            return self.get_haversine_matrix(cities)

    def get_haversine_matrix(self, cities):
        n = len(cities)
        ids = sorted(cities.keys())
        mat = np.zeros((n, n), dtype=np.float32)
        for i in range(n):
            for j in range(n):
                if i == j: continue
                c1 = cities[ids[i]]
                c2 = cities[ids[j]]
                # Haversine Formula
                R = 6371
                d_lat = math.radians(c2['lat'] - c1['lat'])
                d_lon = math.radians(c2['lon'] - c1['lon'])
                a = (math.sin(d_lat / 2) ** 2 +
                     math.cos(math.radians(c1['lat'])) * math.cos(math.radians(c2['lat'])) *
                     math.sin(d_lon / 2) ** 2)
                c = 2 * math.asin(math.sqrt(a))
                mat[i][j] = R * c
        return mat

    def get_valid_actions(self, mask):
        return [city for city in range(self.num_cities) if not (mask & (1 << city))]

    def get_state(self, current_city, mask):
        return (current_city, mask)

    def calculate_reward(self, dist, objective='profit'):
        # V5.3: Multi-Objective Reward Function
        if objective == 'time':
            # Reward: Negate distance (minimize dist = maximize -dist)
            # Assumption: Speed is constant, so dist ~ time.
            # Scaling: -dist to keep values manageable
            return -dist 
        else:
            # Reward: 1000/dist (Standard profit maximization proxy)
            return 1000.0 / dist if dist > 0 else 1000.0

    def choose_action(self, state, valid_actions):
        # Epsilon-Greedy Strategy
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        
        state_q = self.q_table[state]
        max_q = -float('inf')
        best_actions = []
        
        # Cari action dengan Q-value tertinggi
        for action in valid_actions:
            q = state_q.get(action, 0.0) # Default 0.0 might be issue for negative rewards?
            # V5.3: If rewards are negative (time objective), 0.0 is actually "good" (high).
            # We should initialize with -inf if possible, or handle sparse carefully.
            # But for sparse matrix, 0.0 is the default "unexplored". 
            # If all learned Qs are negative (e.g. -500), then 0.0 > -500. 
            # This makes agents optimistic about unknown states (Exploration). Good.
            
            if q > max_q:
                max_q = q
                best_actions = [action]
            elif q == max_q:
                best_actions.append(action)
        
        if not best_actions:
            return random.choice(valid_actions)
        return random.choice(best_actions)

    def train_episode(self, objective='profit'):
        """Akan di-override oleh Child Class"""
        raise NotImplementedError

    def train_loop(self, episodes):
        # ... (Existing implementation not used by API-driven logic)
        pass

    def get_route(self):
        """Extract rute terbaik berdasarkan Q-Table saat ini"""
        start_city = 0
        current_city = start_city
        mask = 1 << start_city
        route = [start_city]
        
        while True:
            state = self.get_state(current_city, mask)
            valid_actions = self.get_valid_actions(mask)
            if not valid_actions:
                route.append(start_city) # Kembali ke awal
                break
            
            best_action = None
            max_q = -float('inf')
            state_actions = self.q_table[state]
            
            for action in valid_actions:
                q = state_actions.get(action, -float('inf'))
                if q > max_q:
                    max_q = q
                    best_action = action
            
            if best_action is None: 
                best_action = valid_actions[0]
                
            current_city = best_action
            mask = mask | (1 << current_city)
            route.append(current_city)
            
        return route

    def calculate_route_dist(self, route):
        d = 0
        for k in range(len(route)-1):
            u, v = route[k], route[k+1]
            d += self.dist_matrix[u][v]
        return d

    def apply_two_opt(self, route):
        """Algoritma 'Setrika' Rute: Menghilangkan silang-silang"""
        best_route = route[:]
        best_dist = self.calculate_route_dist(best_route)
        improved = True
        
        # Batasi loop agar tidak terlalu berat di server
        max_iter = 50 
        iter_count = 0
        
        while improved and iter_count < max_iter:
            improved = False
            iter_count += 1
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route)):
                    if j - i == 1: continue
                    new_route = best_route[:]
                    new_route[i:j] = best_route[i:j][::-1] # Swap/Reverse segment
                    new_dist = self.calculate_route_dist(new_route)
                    if new_dist < best_dist:
                        best_route = new_route
                        best_dist = new_dist
                        improved = True
        return best_route

    def reinforce_route(self, route):
        """Memasukkan rute bagus (hasil 2-OPT) ke dalam Q-Table"""
        mask = 1 << route[0]
        for i in range(len(route)-1):
            curr, next_node = route[i], route[i+1]
            state = self.get_state(curr, mask)
            
            # Hitung reward pura-pura
            dist = self.dist_matrix[curr][next_node]
            reward = self.calculate_reward(dist)
            
            next_mask = mask | (1 << next_node)
            next_state = self.get_state(next_node, next_mask)
            
            # Update Q-Value (seolah-olah agen yang menemukannya)
            max_next_q = 0.0
            if i < len(route)-2:
                valid_next = self.get_valid_actions(next_mask)
                qs = [self.q_table[next_state].get(a, 0.0) for a in valid_next]
                if qs: max_next_q = max(qs)
            
            current_q = self.q_table[state][next_node]
            self.q_table[state][next_node] = current_q + self.alpha * (reward + (self.gamma * max_next_q) - current_q)
            
            mask = next_mask

    def get_best_route_distance(self):
        route = self.get_route()
        return self.calculate_route_dist(route), route

    def set_road_status(self, u, v, status):
        """Fitur God Mode: Blokir Jalan"""
        limit = 9999999.0
        if status == 'blocked':
            self.dist_matrix[u][v] = limit
            self.dist_matrix[v][u] = limit
        elif status == 'open':
            # Restore dari backup
            self.dist_matrix[u][v] = self.original_distance_matrix[u][v]
            self.dist_matrix[v][u] = self.original_distance_matrix[v][u]


# --- CHILD CLASS 1: Q-Learning ---
class QLearningAgent(TSPBaseAgent):
    def __init__(self, cities, **kwargs):
        super().__init__(cities, **kwargs)
        self.name = kwargs.get('name', 'QL-Bot')
        self.color = kwargs.get('color', 'blue')

    def train_episode(self, objective='profit'):
        # Q-Learning (Off-Policy): Max Q(s', a')
        start_city = 0
        current_city = start_city
        mask = 1 << start_city
        done = False
        
        while not done:
            state = self.get_state(current_city, mask)
            valid_actions = self.get_valid_actions(mask)
            
            if not valid_actions:
                done = True
                continue
            
            action = self.choose_action(state, valid_actions)
            dist = self.dist_matrix[current_city][action]
            reward = self.calculate_reward(dist, objective=objective)
            
            next_city = action
            next_mask = mask | (1 << next_city)
            next_state = self.get_state(next_city, next_mask)
            
            # Cari Max Q di next state
            next_valid = self.get_valid_actions(next_mask)
            if not next_valid:
                 # Terminal step (kembali ke start)
                 max_next_q = self.q_table[next_state].get(start_city, 0.0)
            else:
                 vals = [self.q_table[next_state].get(a, 0.0) for a in next_valid]
                 max_next_q = max(vals) if vals else 0.0
            
            # Rumus Update
            current_q = self.q_table[state][action]
            self.q_table[state][action] = current_q + self.alpha * (reward + (self.gamma * max_next_q) - current_q)
            
            current_city = next_city
            mask = next_mask


# --- CHILD CLASS 2: SARSA ---
class SarsaAgent(TSPBaseAgent):
    def __init__(self, cities, **kwargs):
        super().__init__(cities, **kwargs)
        self.name = kwargs.get('name', 'Sarsa-Bot')
        self.color = kwargs.get('color', 'green')

    def train_episode(self, objective='profit'):
        # SARSA (On-Policy): Pilih a' sekarang juga
        start_city = 0
        current_city = start_city
        mask = 1 << start_city
        
        state = self.get_state(current_city, mask)
        valid_actions = self.get_valid_actions(mask)
        if not valid_actions: return
        
        # Pilih Action Awal
        action = self.choose_action(state, valid_actions)
        done = False
        
        while not done:
            dist = self.dist_matrix[current_city][action]
            reward = self.calculate_reward(dist, objective=objective)
            
            next_city = action
            next_mask = mask | (1 << next_city)
            next_state = self.get_state(next_city, next_mask)
            next_valid = self.get_valid_actions(next_mask)
            
            target_q = 0.0
            if not next_valid:
                done = True
            else:
                # Pilih Next Action A' (On-Policy)
                next_action = self.choose_action(next_state, next_valid)
                target_q = self.q_table[next_state].get(next_action, 0.0)
                
            current_q = self.q_table[state][action]
            self.q_table[state][action] = current_q + self.alpha * (reward + (self.gamma * target_q) - current_q)
            
            if not done:
                current_city = next_city
                mask = next_mask
                action = next_action
                state = next_state


# --- CHILD CLASS 3: Monte Carlo ---
class MonteCarloAgent(TSPBaseAgent):
    def __init__(self, cities, **kwargs):
        super().__init__(cities, **kwargs)
        self.name = kwargs.get('name', 'MC-Bot')
        self.color = kwargs.get('color', 'red')
        self.episode_memory = []  # Ingatan jangka pendek per episode

    def train_episode(self, objective='profit'):
        # Monte Carlo: First-Visit MC Control
        # 1. Generate Episode sampai selesai
        start_city = 0
        current_city = start_city
        mask = 1 << start_city
        self.episode_memory = []  # Reset memory
        
        # --- Generate Trajectory (Jalan dulu sampai mentok) ---
        while True:
            state = self.get_state(current_city, mask)
            valid_actions = self.get_valid_actions(mask)
            
            if not valid_actions:
                # Terminal step: Balik ke Jakarta
                dist = self.dist_matrix[current_city][start_city]
                reward = self.calculate_reward(dist, objective=objective)
                self.episode_memory.append((state, start_city, reward))
                break
            
            action = self.choose_action(state, valid_actions)
            dist = self.dist_matrix[current_city][action]
            reward = self.calculate_reward(dist, objective=objective)
            
            self.episode_memory.append((state, action, reward))
            
            current_city = action
            mask = mask | (1 << current_city)
            
        # --- Belajar di Akhir (Update Q-Table) ---
        G = 0  # Return (Total Reward)
        # Loop mundur dari langkah terakhir ke awal
        for state, action, reward in reversed(self.episode_memory):
            G = self.gamma * G + reward
            
            # Update Rumus MC: Q(s,a) = Q(s,a) + alpha * (G - Q(s,a))
            current_q = self.q_table[state][action]
            self.q_table[state][action] = current_q + self.alpha * (G - current_q)


# --- CHILD CLASS 4: TD(Lambda) Agent ---
class TDLambdaAgent(TSPBaseAgent):
    def __init__(self, cities, lambda_val=0.7, **kwargs):
        super().__init__(cities, **kwargs)
        self.name = kwargs.get('name', 'TD-Bot')
        self.color = kwargs.get('color', 'orange') # Warna Oranye
        self.lambda_val = lambda_val
        self.e_traces = defaultdict(lambda: defaultdict(float))

    def train_episode(self, objective='profit'):
        # Sarsa(Lambda) Implementation
        self.e_traces.clear() # Reset jejak ingatan tiap episode
        
        start_city = 0
        current_city = start_city
        mask = 1 << start_city
        
        state = self.get_state(current_city, mask)
        valid_actions = self.get_valid_actions(mask)
        if not valid_actions: return
        
        action = self.choose_action(state, valid_actions)
        done = False
        
        while not done:
            dist = self.dist_matrix[current_city][action]
            reward = self.calculate_reward(dist, objective=objective)
            
            next_city = action
            next_mask = mask | (1 << next_city)
            next_state = self.get_state(next_city, next_mask)
            next_valid = self.get_valid_actions(next_mask)
            
            current_q = self.q_table[state][action]
            
            target = reward
            if not next_valid:
                done = True
            else:
                next_action = self.choose_action(next_state, next_valid)
                next_q = self.q_table[next_state][next_action]
                target += self.gamma * next_q
            
            # Hitung Error (Delta)
            delta = target - current_q
            
            # Naikkan Trace untuk state saat ini (Accumulating Trace)
            self.e_traces[state][action] += 1
            
            # Update SEMUA state yang punya jejak (Trace > 0)
            # Ini yang bikin dia "ingat masa lalu"
            # Optimization: Loop hanya pada trace yang aktif
            for s, a_dict in list(self.e_traces.items()):
                for a, trace_val in list(a_dict.items()):
                    self.q_table[s][a] += self.alpha * delta * trace_val
                    # Decay trace
                    self.e_traces[s][a] *= self.gamma * self.lambda_val
                    # Hapus trace yang sudah terlalu kecil (hemat memori)
                    if self.e_traces[s][a] < 0.001:
                        del self.e_traces[s][a]
                        
            if not done:
                current_city = next_city
                mask = next_mask
                state = next_state
                action = next_action


# --- CHILD CLASS 5: Dyna-Q Agent ---
class DynaQAgent(TSPBaseAgent):
    def __init__(self, cities, planning_steps=5, **kwargs):
        super().__init__(cities, **kwargs)
        self.name = kwargs.get('name', 'Dyna-Bot')
        self.color = kwargs.get('color', 'purple') # Warna Ungu
        self.planning_steps = planning_steps # Seberapa sering dia melamun
        self.model = {} # Ingatan Dunia: (s,a) -> (r, s')
        self.model_keys = [] # List kunci untuk sampling cepat

    def train_episode(self, objective='profit'):
        # Q-Learning + Planning
        start_city = 0
        current_city = start_city
        mask = 1 << start_city
        done = False
        
        while not done:
            state = self.get_state(current_city, mask)
            valid_actions = self.get_valid_actions(mask)
            
            if not valid_actions:
                done = True
                continue
            
            action = self.choose_action(state, valid_actions)
            dist = self.dist_matrix[current_city][action]
            reward = self.calculate_reward(dist, objective=objective)
            
            next_city = action
            next_mask = mask | (1 << next_city)
            next_state = self.get_state(next_city, next_mask)
            
            # 1. Direct RL (Q-Learning Update)
            next_valid = self.get_valid_actions(next_mask)
            max_next_q = 0.0
            if next_valid:
                 vals = [self.q_table[next_state].get(a, 0.0) for a in next_valid]
                 max_next_q = max(vals) if vals else 0.0
            
            current_q = self.q_table[state][action]
            self.q_table[state][action] = current_q + self.alpha * (reward + (self.gamma * max_next_q) - current_q)
            
            # 2. Model Learning (Hafalkan dunia)
            if (state, action) not in self.model:
                self.model_keys.append((state, action)) # Simpan key buat random choice
            self.model[(state, action)] = (reward, next_state)
            
            # 3. Planning (Imajinasi)
            # Ulangi pengalaman masa lalu secara acak
            self.run_planning()
            
            current_city = next_city
            mask = next_mask

    def run_planning(self):
        if not self.model_keys: return
        
        # Lakukan update tambahan di kepala (Simulasi)
        for _ in range(self.planning_steps):
            # Ambil pengalaman acak
            s, a = random.choice(self.model_keys)
            r, next_s = self.model[(s, a)]
            
            # Update Q lagi berdasarkan ingatan
            # Perlu valid actions dari next_s (ambil dari mask di state)
            _, n_mask = next_s
            n_valid = self.get_valid_actions(n_mask)
            
            max_n_q = 0.0
            if n_valid:
                vals = [self.q_table[next_s].get(act, 0.0) for act in n_valid]
                max_n_q = max(vals) if vals else 0.0
                
            curr_q = self.q_table[s][a]
            self.q_table[s][a] = curr_q + self.alpha * (r + (self.gamma * max_n_q) - curr_q)
