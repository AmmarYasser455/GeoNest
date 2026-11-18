"""Tests for path-like input and CRS-less files in Map.add_geojson."""

import pytest

from geonest import Map

gpd = pytest.importorskip("geopandas")


def _write(tmp_path):
    from shapely.geometry import Point

    # Cairo, lon/lat order
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(31.2357, 30.0444)], crs="EPSG:4326")
    path = tmp_path / "d.geojson"
    gdf.to_file(path, driver="GeoJSON")
    return path


def test_add_geojson_accepts_pathlib(tmp_path):
    m = Map()
    calls = []
    m.fit_bounds = lambda b: calls.append(b)  # type: ignore
    m.add_geojson(_write(tmp_path))
    assert calls == [[[30.0444, 31.2357], [30.0444, 31.2357]]]


def test_add_vector_accepts_pathlib(tmp_path):
    m = Map()
    n = len(m.layers)
    m.add_vector(_write(tmp_path))
    assert len(m.layers) == n + 1


def test_add_geojson_rejects_file_without_crs(tmp_path, monkeypatch):
    from shapely.geometry import Point

    nocrs = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(1, 2)])
    monkeypatch.setattr(gpd, "read_file", lambda *_a, **_k: nocrs)
    with pytest.raises(ValueError, match="no CRS"):
        Map().add_geojson("whatever.shp")
