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
    # Return dict format expected by create_distance_matrix
    return {
        0: {"lat": 0.0, "lon": 0.0},
        1: {"lat": 1.0, "lon": 1.0},
        2: {"lat": 2.0, "lon": 2.0},
        3: {"lat": 3.0, "lon": 3.0},
        4: {"lat": 4.0, "lon": 4.0}
    }



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

@pytest.fixture
def agent_registry():
    """Access the agents dictionary from the running app instance."""
    return app_module.agents
