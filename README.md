# geonest 🗺️

genest is a lightweight, Pythonic mapping library built on top of `ipyleaflet` to simplify interactive geospatial visualization in Jupyter environments.

It is designed for GIS developers, analysts, and researchers who want clean, extensible map objects without heavy abstractions.

[Documentation](docs/) · [Examples](https://github.com/AmmarYasser455/GeoNest/tree/main/examples) · [Contributing](CONTRIBUTING.md) · [License](./LICENSE)

---

Badges
- PyPI: ![PyPI](https://img.shields.io/pypi/v/geonest.svg) ([PyPI page](https://pypi.org/project/geonest/))
- Python: ![Python](https://img.shields.io/pypi/pyversions/geonest.svg)
- License: ![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## Features

- Simple `Map` class extending `ipyleaflet.Map` with a small, predictable API
- Built-in basemap support (OSM, Esri, CartoDB, Google)
- GeoJSON, Shapefile, GeoDataFrame support
- Raster, image, and WMS layers
- Basemap GUI selector widget for interactive switching
- Designed for customization and extension — small surface area, easy to override

---

## Quick install

pip (recommended)
```bash
pip install geonest
