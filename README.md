# geonest 🗺️

geonest is a lightweight, Pythonic mapping library built on top of `ipyleaflet` to simplify interactive geospatial visualization in Jupyter environments.

It is designed for GIS developers, analysts, and researchers who want clean, extensible map objects without heavy abstractions.

[Documentation](#) · [Examples](#examples) · [Contributing](#contributing) · [License](./LICENSE)

---

Badges
- PyPI: ![PyPI](https://img.shields.io/[pypi/v/geonest](https://pypi.org/project/geonest/))
- Python: ![Python](https://img.shields.io/pypi/pyversions/geonest)
- License: ![License](https://img.shields.io/badge/license-MIT-blue)

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
```

Optional (for Geopandas/shapefile/raster support):
```bash
pip install "geonest[geopandas,raster]"
```

For JupyterLab, ensure ipyleaflet is installed and enabled:
```bash
pip install ipyleaflet
jupyter labextension install @jupyter-widgets/jupyterlab-manager
# (depending on JupyterLab version you may also need the ipyleaflet labextension)
```

---

## Quickstart

Open a Jupyter notebook or JupyterLab and run:

```python
from geonest import Map

m = Map(center=(51.505, -0.09), zoom=13, basemap="Esri.WorldImagery")
# Add a GeoJSON feature (dict or file path)
m.add_geojson({
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"name": "Point A"},
         "geometry": {"type":"Point","coordinates":[-0.09,51.505]}}
    ]
})
m  # display the map inline
```

Other conveniences:
- `Map.from_geodataframe(gdf)` — create a map centered on a GeoDataFrame
- `Map.add_raster(path_or_url, name="Raster")` — add image/raster layers
- `Map.add_wms(url, layers="layername")` — add WMS services
- `m.basemap = "CartoDB.Positron"` — switch basemap programmatically

See the `examples/` directory for more complete usage samples.

---

## API overview

- geonest.Map
  - Constructor accepts `center`, `zoom`, `basemap` and other `ipyleaflet.Map` kwargs
  - Methods: `add_geojson`, `add_shapefile`, `add_geodataframe`, `add_raster`, `add_wms`, `clear_layers`, `fit_bounds`, etc.

(For full API reference see the docs — TODO: add link when docs are available.)

---

## Development & Contributing

Contributions are welcome!

- Open an issue for feature requests or bugs
- Fork the repo and submit a pull request
- Run tests with:
```bash
pip install -e .[dev]
pytest
```
- Keep changes small and focused. Add examples or notebook demos for new features.

---

## Roadmap / Ideas

- Better raster reprojection/tiling support
- Additional basemaps and an offline basemap option
- Improved examples and a documentation site

---

## License

See the LICENSE file in this repository.

---
