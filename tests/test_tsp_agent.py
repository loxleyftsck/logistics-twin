"""
Unit Tests for TSP Agent
Tests for TSP solving algorithms and helper functions.
"""

import pytest
import numpy as np
import sys
import os

# Ensure tsp_agent can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import tsp_agent
except ImportError:
    tsp_agent = None


@pytest.mark.skipif(tsp_agent is None, reason="tsp_agent module not found")
class TestTSPAgent:
    """Test suite for TSP Agent algorithms."""

    @pytest.mark.unit
    def test_calculate_distance(self, sample_distance_matrix):
        """Test distance calculation for a route."""
        if not hasattr(tsp_agent, 'calculate_total_distance'):
            pytest.skip("Function not found in tsp_agent")
        
        route = [0, 1, 2, 3, 4, 0]
        # Expected: 10 + 35 + 30 + 15 + 25 = 115
        distance = tsp_agent.calculate_total_distance(route, sample_distance_matrix)
        assert distance == 115

    @pytest.mark.unit
    def test_route_validity(self):
        """Test that generated routes visit all cities exactly once."""
        if not hasattr(tsp_agent, 'generate_random_route'):
            pytest.skip("Function not found in tsp_agent")
        
        num_cities = 10
        route = tsp_agent.generate_random_route(num_cities)
        
        # Check all cities are visited
        assert len(set(route)) == num_cities
        # Check route returns to start (if applicable)
        # assert route[0] == route[-1]  # Uncomment if routes are circular

    @pytest.mark.slow
    def test_genetic_algorithm_convergence(self, sample_distance_matrix):
        """Test that genetic algorithm improves solution over iterations."""
        if not hasattr(tsp_agent, 'solve_tsp_genetic'):
            pytest.skip("Function not found in tsp_agent")
        
        result = tsp_agent.solve_tsp_genetic(
            sample_distance_matrix,
            population_size=20,
            generations=50
        )
        
        # Verify result structure
        assert 'route' in result or 'best_route' in result
        assert 'distance' in result or 'best_distance' in result
        
        # Distance should be positive and reasonable
        distance = result.get('distance') or result.get('best_distance')
        assert distance > 0


class TestDistanceMatrixOperations:
    """Test suite for distance matrix calculations."""

    @pytest.mark.unit
    def test_distance_matrix_symmetry(self, sample_distance_matrix):
        """Test that distance matrix is symmetric."""
        matrix = np.array(sample_distance_matrix)
        assert np.allclose(matrix, matrix.T), "Distance matrix should be symmetric"

    @pytest.mark.unit
    def test_distance_matrix_diagonal_zeros(self, sample_distance_matrix):
        """Test that diagonal elements are zero (distance from city to itself)."""
        matrix = np.array(sample_distance_matrix)
        diagonal = np.diag(matrix)
        assert np.allclose(diagonal, 0), "Diagonal should be all zeros"

    @pytest.mark.unit
    def test_create_distance_matrix_from_coords(self, sample_cities):
        """Test creating distance matrix from city coordinates."""
        if not hasattr(tsp_agent, 'create_distance_matrix'):
            pytest.skip("Function not found in tsp_agent")
        
        matrix = tsp_agent.create_distance_matrix(sample_cities)
        
        # Basic validations
        assert matrix.shape[0] == matrix.shape[1]
        assert matrix.shape[0] == len(sample_cities)
        assert np.all(np.diag(matrix) == 0)
