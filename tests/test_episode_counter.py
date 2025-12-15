
import pytest
import json

def test_episode_counter_increments(client):
    """Test that episode counter increments correctly"""
    # Reset first to start fresh
    client.get('/api/reset')
    
    # Call train endpoint
    response1 = client.get('/api/train')
    assert response1.status_code == 200
    data1 = response1.get_json()
    ep1 = data1['episode']
    
    # Call again
    response2 = client.get('/api/train')
    assert response2.status_code == 200
    data2 = response2.get_json()
    ep2 = data2['episode']
    
    # Episode should increment
    assert ep2 == ep1 + 1, f"Expected episode {ep1 + 1}, got {ep2}"

def test_episode_counter_resets(client):
    """Test that episode counter resets to 0"""
    # Train a few times
    for _ in range(5):
        client.get('/api/train')
    
    # Reset
    reset_response = client.get('/api/reset')
    assert reset_response.status_code == 200
    
    # Next train should be episode 1
    train_response = client.get('/api/train')
    data = train_response.get_json()
    
    assert data['episode'] == 1, f"Expected episode 1 after reset, got {data['episode']}"
