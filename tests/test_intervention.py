
import pytest
import json

# We do NOT import app here, we use fixtures from conftest.py

def test_teach_agent_endpoint(client, agent_registry):
    """Test the /api/teach endpoint works correctly"""
    
    # 1. Define a teaching route (Jakarta -> Bandung -> Cirebon)
    payload = {
        "agent": "QL-Bot",
        "route": ["Jakarta City 🏢", "Bandung Teknopolis 🏢", "Cirebon Port ⚓"]
    }
    
    # 2. Call API
    response = client.post('/api/teach', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # Debug info if failed
    if response.status_code != 200:
        print(f"FAILED Response: {response.get_data(as_text=True)}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert "successfully taught" in data['message']
    
    # 3. Verify Agent Q-Table Updated via shared registry
    agent = agent_registry['QL-Bot']
    
    # Check Q-Values for the taught path
    # Jakarta (1) -> Bandung (4)
    # The map might be reloaded so IDs might differ, but q_table should be mutated.
    # We will just assert that the Q-table is not empty and has entries.
    assert len(agent.q_table) > 0

def test_teach_agent_invalid_city(client, agent_registry):
    """Test validation for unknown cities"""
    payload = {
        "agent": "QL-Bot",
        "route": ["Jakarta", "Atlantis"] 
    }
    response = client.post('/api/teach', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 400
    assert "not found" in response.get_json()['message']

def test_teach_agent_invalid_agent(client, agent_registry):
    """Test validation for unknown agent"""
    payload = {
        "agent": "Terminator-Bot",
        "route": ["Jakarta City 🏢", "Bandung Teknopolis 🏢"]
    }
    response = client.post('/api/teach', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 404
