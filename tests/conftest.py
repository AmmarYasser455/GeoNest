"""Pytest configuration and fixtures for GeoNest tests."""

import pytest

from geonest import Map


@pytest.fixture
def map_instance():
    """Create a fresh Map instance for testing."""
    return Map()


@pytest.fixture
def cairo_map():
    """Create a Map centered on Cairo, Egypt."""
    return Map(center=[30.0, 31.0], zoom=10)


@pytest.fixture
def sample_geojson():
    """Return a sample GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [31.2357, 30.0444]
                },
                "properties": {"name": "Cairo"}
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [29.9187, 31.2001]
                },
                "properties": {"name": "Alexandria"}
            }
        ]
    }
