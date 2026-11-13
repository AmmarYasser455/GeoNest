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
