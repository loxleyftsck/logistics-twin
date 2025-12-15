
import pytest
import json
import time

def test_exploit_empty_route(client):
    """RED TEAM: Attempt to crash server with empty route"""
    payload = {
        "agent": "QL-Bot",
        "route": [] 
    }
    response = client.post('/api/teach', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # Ideally should be 400, but we expect 500 due to unhandled IndexError
    print(f"\n[Empty Route] Status Code: {response.status_code}")
    if response.status_code == 500:
        print("[VULN CONFIRMED] Server crashed with 500 on empty route (IndexError likely)")
    elif response.status_code == 400:
        print("[SAFE] Server handled empty route correctly")
    else:
        print(f"[UNKNOWN] Server returned {response.status_code}")

def test_exploit_massive_route(client):
    """RED TEAM: Attempt memory exhaustion/CPU spike with massive route"""
    # Create a route with 10,000 cities (repeated) to valid cities
    # Just repeating "Jakarta City 🏢" 10000 times
    # Note: Logic allows cycles, so this is valid from API perspective, even if nonsense for TSP
    massive_route = ["Jakarta City 🏢"] * 5000 
    
    payload = {
        "agent": "QL-Bot",
        "route": massive_route
    }
    
    start_time = time.time()
    response = client.post('/api/teach', 
                          data=json.dumps(payload),
                          content_type='application/json')
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n[Massive Payload] Duration: {duration:.4f}s")
    if duration > 1.0:
        print(f"[WARN] Processing took {duration:.4f}s - Potential DoS vector")
    else:
         print(f"[INFO] Server handled massive payload in {duration:.4f}s")

# We can't easily test Rate Limit with test_client as it mocks the server, 
# but we can visually inspect the code directly.
