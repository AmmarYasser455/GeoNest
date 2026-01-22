import geonest
from geonest.map import Map


def test_map_creation():
    m = Map()
    assert m is not None
    assert isinstance(m, Map)


def test_map_center_and_zoom():
    m = Map(center=[30, 31], zoom=10)
    assert m.center == [30, 31]
    assert m.zoom == 10


def test_add_basemap():
    m = Map()
    m.add_basemap("OpenStreetMap.Mapnik")

