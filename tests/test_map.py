"""Tests for the GeoNest Map class."""

import pytest

from geonest import Map


class TestMapCreation:
    """Tests for Map initialization."""

    def test_map_creation(self):
        """Test that a Map can be created with defaults."""
        m = Map()
        assert m is not None
        assert isinstance(m, Map)

    def test_map_default_center(self):
        """Test default center is set correctly."""
        m = Map()
        # ipyleaflet converts tuples to lists internally
        assert list(m.center) == [20, 0]

    def test_map_default_zoom(self):
        """Test default zoom is set correctly."""
        m = Map()
        assert m.zoom == 2

    def test_map_custom_center_and_zoom(self):
        """Test custom center and zoom values."""
        m = Map(center=[30, 31], zoom=10)
        assert m.center == [30, 31]
        assert m.zoom == 10

    def test_map_custom_height(self):
        """Test custom height is applied."""
        m = Map(height="800px")
        assert m.layout.height == "800px"

    def test_scroll_wheel_zoom_enabled(self):
        """Test that scroll wheel zoom is enabled by default."""
        m = Map()
        assert m.scroll_wheel_zoom is True


class TestBasemaps:
    """Tests for basemap functionality."""

    def test_add_basemap_valid(self):
        """Test adding a valid basemap."""
        m = Map()
        m.add_basemap("OpenTopoMap")
        # Should have base layer + added basemap
        assert len(m.layers) >= 1

    def test_add_basemap_invalid(self):
        """Test that invalid basemap raises ValueError."""
        m = Map()
        with pytest.raises(ValueError, match="not found"):
            m.add_basemap("NonExistentBasemap")


class TestGoogleMaps:
    """Tests for Google Maps functionality."""

    def test_add_google_map_roadmap(self):
        """Test adding Google roadmap."""
        m = Map()
        m.add_google_map("ROADMAP")
        assert len(m.layers) >= 1

    def test_add_google_map_satellite(self):
        """Test adding Google satellite."""
        m = Map()
        m.add_google_map("SATELLITE")
        assert len(m.layers) >= 1

    def test_add_google_map_invalid(self):
        """Test that invalid Google map type raises ValueError."""
        m = Map()
        with pytest.raises(ValueError, match="Invalid"):
            m.add_google_map("INVALID")


class TestLayerControl:
    """Tests for layer control functionality."""

    def test_add_layer_control(self):
        """Test adding layer control."""
        m = Map()
        m.add_layer_control()
        # Should have controls added
        assert len(m.controls) >= 1


class TestVectorData:
    """Tests for vector data functionality."""

    def test_add_geojson_dict(self):
        """Test adding GeoJSON from a dict."""
        m = Map()
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [31.0, 30.0]
                    },
                    "properties": {"name": "Cairo"}
                }
            ]
        }
        m.add_geojson(geojson, zoom_to_layer=False)
        assert len(m.layers) >= 1

    def test_add_geojson_invalid_type(self):
        """Test that invalid data type raises ValueError."""
        m = Map()
        with pytest.raises(ValueError, match="must be a file path or dict"):
            m.add_geojson(12345)  # type: ignore

    def test_add_vector_dict(self):
        """Test add_vector with a dict."""
        m = Map()
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        m.add_vector(geojson, zoom_to_layer=False)
        assert len(m.layers) >= 1

    def test_add_vector_invalid_type(self):
        """Test that invalid data type raises ValueError."""
        m = Map()
        with pytest.raises(ValueError, match="Unsupported"):
            m.add_vector([1, 2, 3])  # type: ignore
