
import pytest
import json

def test_security_empty_route(client):
    """Ensure empty route returns 400, not 500"""
    payload = {"agent": "QL-Bot", "route": []}
    response = client.post('/api/teach', json=payload)
    assert response.status_code == 400
    assert "at least 2 cities" in response.get_json()['message']

def test_security_massive_route(client):
    """Ensure massive route returns 400, preventing DOS"""
    # 60 cities (limit is 50)
    payload = {"agent": "QL-Bot", "route": ["Jakarta City 🏢"] * 60}
    response = client.post('/api/teach', json=payload)
    assert response.status_code == 400
    assert "Route too long" in response.get_json()['message']

def test_security_single_city(client):
    """Ensure single city route returns 400"""
    payload = {"agent": "QL-Bot", "route": ["Jakarta City 🏢"]}
    response = client.post('/api/teach', json=payload)
    assert response.status_code == 400
    assert "at least 2 cities" in response.get_json()['message']
