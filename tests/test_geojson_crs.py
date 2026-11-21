"""Tests for the CRS member check on GeoJSON dict input."""

import pytest

from geonest import Map


def _collection(crs_name, coords):
    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": crs_name}},
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": coords},
            }
        ],
    }


def test_projected_crs_member_is_rejected():
    # Cairo in Web Mercator metres; plotting as lon/lat would misplace it.
    data = _collection("urn:ogc:def:crs:EPSG::3857", [3480000.0, 3540000.0])
    with pytest.raises(ValueError, match="3857"):
        Map().add_geojson(data)


def _added_geojson(m):
    return m.layers[-1].data["features"][0]["geometry"]["coordinates"]


@pytest.mark.parametrize(
    "name", ["urn:ogc:def:crs:OGC:1.3:CRS84", "urn:ogc:def:crs:EPSG::4326", "EPSG:4326"]
)
def test_wgs84_member_is_accepted_and_coordinates_preserved(name):
    # Cairo as lon, lat.
    data = _collection(name, [31.2357, 30.0444])
    m = Map()
    m.add_geojson(data)
    assert _added_geojson(m) == [31.2357, 30.0444]


def test_fit_bounds_receives_lat_lon(monkeypatch):
    calls = []
    m = Map()
    monkeypatch.setattr(m, "fit_bounds", lambda b: calls.append(b))
    m.add_geojson(_collection("EPSG:4326", [31.2357, 30.0444]))
    assert calls == [[[30.0444, 31.2357], [30.0444, 31.2357]]]


@pytest.mark.parametrize(
    "crs",
    [
        {"type": "link", "properties": {"href": "http://x/crs.wkt", "type": "ogcwkt"}},
        {"type": "name", "properties": {}},
        "EPSG:3857",
    ],
)
def test_uninterpretable_crs_member_is_rejected(crs):
    data = _collection("EPSG:4326", [3480000.0, 3540000.0])
    data["crs"] = crs
    with pytest.raises(ValueError, match="CRS"):
        Map().add_geojson(data)


def test_null_crs_member_is_accepted():
    data = _collection("EPSG:4326", [31.2357, 30.0444])
    data["crs"] = None
    m = Map()
    m.add_geojson(data)
    assert _added_geojson(m) == [31.2357, 30.0444]


def test_dict_without_crs_member_is_accepted():
    data = _collection("EPSG:4326", [31.2357, 30.0444])
    del data["crs"]
    m = Map()
    before = len(m.layers)
    m.add_geojson(data)
    assert len(m.layers) == before + 1
