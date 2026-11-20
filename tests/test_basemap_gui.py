"""Tests for the basemap selector widget."""

import ipyleaflet
import ipywidgets as widgets

from geonest import Map


def _dropdown(m):
    control = next(c for c in m.controls if isinstance(c, ipyleaflet.WidgetControl))
    dropdown = control.widget.children[1]
    assert isinstance(dropdown, widgets.Dropdown)
    return dropdown


def test_basemap_gui_keeps_data_layers():
    """Switching basemap replaces only the selector's own layer."""
    m = Map()
    m.add_basemap_gui(options=["OpenTopoMap", "Esri.WorldImagery", "CartoDB.DarkMatter"])
    dropdown = _dropdown(m)
    dropdown.value = "Esri.WorldImagery"
    # Cairo, lon/lat order
    m.add_geojson(
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [31.2357, 30.0444]},
            "properties": {},
        },
        zoom_to_layer=False,
    )
    data_layer = m.layers[-1]
    dropdown.value = "CartoDB.DarkMatter"
    names = [getattr(layer, "name", "") for layer in m.layers]
    assert data_layer in m.layers
    assert "CartoDB.DarkMatter" in names
    assert "Esri.WorldImagery" not in names
