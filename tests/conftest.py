"""
Pytest Configuration and Shared Fixtures
This module provides shared test fixtures for the Flask TSP project.
"""

import pytest
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the Flask app from app.py (not the app/ package directory)
# We need to use importlib to avoid conflict with app/ directory
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", os.path.join(project_root, "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
flask_app = app_module.app


@pytest.fixture
def app():
    """Get the Flask application instance for testing."""
    # Configure the app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = False
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def sample_cities():
    """Provide sample city data for testing TSP algorithms."""
    return [
        {"id": 0, "name": "City A", "lat": 0.0, "lng": 0.0},
        {"id": 1, "name": "City B", "lat": 1.0, "lng": 1.0},
        {"id": 2, "name": "City C", "lat": 2.0, "lng": 2.0},
        {"id": 3, "name": "City D", "lat": 3.0, "lng": 3.0},
        {"id": 4, "name": "City E", "lat": 4.0, "lng": 4.0}
    ]


@pytest.fixture
def sample_distance_matrix():
    """Provide a sample distance matrix for testing."""
    # 5x5 symmetric distance matrix
    return [
        [0, 10, 15, 20, 25],
        [10, 0, 35, 25, 30],
        [15, 35, 0, 30, 20],
        [20, 25, 30, 0, 15],
        [25, 30, 20, 15, 0]
    ]
