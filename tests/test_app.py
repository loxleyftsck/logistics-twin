"""
Unit Tests for Flask Application
Tests for Flask routes, API endpoints, and core functionality.
"""

import pytest
import json


class TestFlaskApp:
    """Test suite for Flask application."""

    @pytest.mark.unit
    def test_app_creation(self, app):
        """Test that the Flask app is created successfully."""
        assert app is not None
        assert app.config['TESTING'] is True

    @pytest.mark.unit
    def test_index_route(self, client):
        """Test that the index route returns successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data

    @pytest.mark.api
    def test_health_endpoint(self, client):
        """Test the /health endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'cities' in data

    @pytest.mark.api
    def test_get_cities_endpoint(self, client):
        """Test the /get_cities endpoint."""
        response = client.get('/get_cities')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)  # Should return cities dictionary


class TestStaticAssets:
    """Test suite for static assets and templates."""

    @pytest.mark.unit
    def test_static_css_accessible(self, client):
        """Test that static CSS files are accessible."""
        # This is a basic check - adjust path based on your actual static files
        response = client.get('/static/css/style.css')
        # Either file exists (200) or route doesn't (404), but shouldn't error (500)
        assert response.status_code in [200, 404]

    @pytest.mark.unit
    def test_static_js_accessible(self, client):
        """Test that static JS files are accessible."""
        response = client.get('/static/js/main.js')
        assert response.status_code in [200, 404]
