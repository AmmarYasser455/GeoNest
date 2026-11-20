# Changelog

## 0.1.1

### Fixed
- `pip install geonest` now installs a working package. The 0.1.0 wheel on PyPI shipped a `GeoNest/` folder whose `__init__` imported a missing module, so `from geonest import Map` failed with `ModuleNotFoundError`.
- `add_basemap_gui` no longer removes your data layers when you switch basemap (#8).
- `zoom_to_layer` now works for dict and GeoDataFrame input (#2, #3), and layers with non-finite bounds no longer break fitting (#2).

### Changed
- `add_geojson` / `add_vector` accept path-like input and give a clear error for files without a CRS (#6).
- `add_gdf` raises a clear `ValueError` for GeoDataFrames without a CRS (#7).
- `add_basemap` raises `ValueError` for provider-group names (#4).
- Packaging: `pyproject.toml` is the only build config (the old `setup.py` is gone), and the version comes from `geonest.__version__`. CI now builds the wheel, installs it in a clean venv and runs the README quick start.

## 0.1.0

First release.
