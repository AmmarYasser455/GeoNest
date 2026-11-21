"""Tests for Map.add_gdf zoom behaviour."""

import pytest

from geonest import Map


def _map_with_fit_recorder():
    m = Map()
    calls = []
    m.fit_bounds = lambda bounds: calls.append(bounds)  # type: ignore
    return m, calls


def _gdf(geoms):
    gpd = pytest.importorskip("geopandas")
    return gpd.GeoDataFrame({"id": range(len(geoms))}, geometry=geoms, crs="EPSG:4326")


def test_add_gdf_zooms_to_layer():
    from shapely.geometry import Point

    m, calls = _map_with_fit_recorder()
    m.add_gdf(_gdf([Point(1, 2), Point(3, 4)]))
    assert calls == [[[2.0, 1.0], [4.0, 3.0]]]


def test_add_gdf_zoom_disabled():
    from shapely.geometry import Point

    m, calls = _map_with_fit_recorder()
    m.add_gdf(_gdf([Point(1, 2)]), zoom_to_layer=False)
    assert calls == []


def test_add_gdf_null_geometries_do_not_fit():
    m, calls = _map_with_fit_recorder()
    m.add_gdf(_gdf([None, None]))
    assert calls == []


def test_add_gdf_empty_geometries_do_not_fit():
    from shapely.geometry import Point

    m, calls = _map_with_fit_recorder()
    m.add_gdf(_gdf([Point(), Point()]))
    assert calls == []


def test_add_gdf_datetime_and_nan_columns_are_json_safe():
    import json

    import numpy as np
    import pandas as pd
    from shapely.geometry import Point

    gpd = pytest.importorskip("geopandas")
    gdf = gpd.GeoDataFrame(
        {"seen": pd.to_datetime(["2024-01-01"]), "v": [np.nan]},
        geometry=[Point(31.2357, 30.0444)],  # Cairo, (lon, lat)
        crs="EPSG:4326",
    )
    m, calls = _map_with_fit_recorder()
    m.add_gdf(gdf)
    data = json.loads(json.dumps(m.layers[-1].data))
    props = data["features"][0]["properties"]
    assert data["features"][0]["geometry"]["coordinates"] == [31.2357, 30.0444]
    assert props["seen"].startswith("2024-01-01")
    assert props["v"] is None
    assert calls == [[[30.0444, 31.2357], [30.0444, 31.2357]]]
