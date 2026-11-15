"""Build the GeoNest showcase offline from showcase/data/.

Question: which Egyptian governorates cover the most land, and what share of
the country do the five largest hold?

Run from the repository root:  python showcase/make_showcase.py
Writes map.geojson, map.png and index.html into showcase/ (or --out DIR).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "egypt_governorates.geojson"
AREA_CRS = "EPSG:6933"  # WGS 84 / NSIDC EASE-Grid 2.0 Global, equal-area, metres
CREDIT = "Data: Natural Earth (public domain). Built with GeoNest."
REPO = "https://github.com/AmmarYasser455/GeoNest"


def _orient(geom):
    """RFC 7946 ring order: exterior counter-clockwise, holes clockwise."""
    if geom.geom_type == "Polygon":
        return orient(geom, 1.0)
    if geom.geom_type == "MultiPolygon":
        return type(geom)([orient(p, 1.0) for p in geom.geoms])
    return geom


def load(path: Path = DATA) -> gpd.GeoDataFrame:
    """Read the governorate polygons (lon/lat, EPSG:4326)."""
    gdf = gpd.read_file(path)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        raise ValueError("expected EPSG:4326 input")
    return gdf


def analyse(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add area (km2, equal-area CRS), share of the total and rank."""
    out = gdf.copy()
    area_km2 = out.to_crs(AREA_CRS).area / 1e6
    out["area_km2"] = area_km2.round(1)
    out["share_pct"] = (100 * area_km2 / area_km2.sum()).round(2)
    out["rank"] = area_km2.rank(ascending=False, method="first").astype(int)
    out["geometry"] = out.geometry.apply(_orient)
    return out.sort_values("rank").reset_index(drop=True)


def geonest_layer(gdf: gpd.GeoDataFrame) -> dict:
    """Run the data through GeoNest's Map.add_gdf and return the layer's GeoJSON.

    add_gdf reprojects to EPSG:4326 and hands GeoJSON to the web map layer.
    """
    from geonest import Map

    m = Map(center=(26.8, 30.8), zoom=5)
    m.add_gdf(gdf)
    layer = m.layers[-1]
    return json.loads(json.dumps(layer.data))


def write_geojson(fc: dict, path: Path) -> None:
    path.write_text(json.dumps(fc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def write_png(gdf: gpd.GeoDataFrame, path: Path) -> None:
    import math

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.5, 8.6), dpi=150)
    gdf.plot(
        column="area_km2", cmap="YlGnBu", edgecolor="white", linewidth=0.6, ax=ax,
        legend=True, legend_kwds={"label": "Area (km², equal-area EPSG:6933)", "shrink": 0.7},
    )
    for _, r in gdf[(gdf["rank"] <= 5) | (gdf["name"] == "Al Qahirah")].iterrows():
        p = r.geometry.representative_point()
        ax.annotate(
            f"{r['name']}\n{r['area_km2']:,.0f} km²", (p.x, p.y), ha="center", fontsize=7.5,
            bbox={"boxstyle": "round,pad=0.2", "fc": "white", "alpha": 0.8, "lw": 0},
        )
    minx, miny, maxx, maxy = gdf.total_bounds
    ax.set_aspect(1 / math.cos(math.radians((miny + maxy) / 2)))
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Egypt's governorates by area\nFive largest hold "
                 f"{gdf.nsmallest(5, 'rank')['share_pct'].sum():.1f}% of the land")
    ax.text(0.01, 0.01, "North up; lon/lat axes (EPSG:4326)", transform=ax.transAxes, fontsize=7)
    ax.text(0.99, 0.01, CREDIT, transform=ax.transAxes, fontsize=7, ha="right")
    fig.savefig(path, dpi=150)
    plt.close(fig)


INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GeoNest showcase: Egypt's governorates by area</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
 body{margin:0;font-family:sans-serif}
 header{padding:8px 14px}
 h1{font-size:1.2em;margin:0 0 4px}
 p{margin:2px 0;font-size:.9em}
 #map{height:calc(100vh - 110px)}
</style>
</head>
<body>
<header>
<h1>Egypt's governorates by area</h1>
<p>Polygons are Natural Earth admin-1 boundaries; areas are computed in an equal-area projection (EPSG:6933) and the layer is prepared with GeoNest.</p>
<p>Darker means larger. Click a governorate for its area, share and rank. Source code: <a href="__REPO__">GeoNest on GitHub</a>.</p>
</header>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('map');
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Data: Natural Earth'
}).addTo(map);
function color(a){return a>200000?'#08306b':a>80000?'#2171b5':a>20000?'#6baed6':a>5000?'#bdd7e7':'#eff3ff';}
fetch('map.geojson').then(function(r){return r.json();}).then(function(fc){
  var layer = L.geoJSON(fc, {
    style: function(f){return {color:'#fff',weight:1,fillColor:color(f.properties.area_km2),fillOpacity:0.75};},
    onEachFeature: function(f, l){
      var p = f.properties;
      l.bindPopup('<b>'+p.name+'</b><br>Area: '+p.area_km2.toLocaleString()+' km²<br>Share of Egypt: '+p.share_pct+'%<br>Rank: '+p.rank+' of 27<br>ISO 3166-2: '+p.iso_3166_2);
    }
  }).addTo(map);
  map.fitBounds(layer.getBounds());
});
</script>
</body>
</html>
"""


def build(out_dir: Path, data: Path = DATA, png: bool = True) -> gpd.GeoDataFrame:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    gdf = analyse(load(data))
    write_geojson(geonest_layer(gdf), out_dir / "map.geojson")
    (out_dir / "index.html").write_text(INDEX.replace("__REPO__", REPO), encoding="utf-8")
    if png:
        write_png(gdf, out_dir / "map.png")
    return gdf


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(HERE), help="output directory (default: showcase/)")
    args = ap.parse_args(argv)
    gdf = build(Path(args.out))
    print(gdf[["rank", "name", "area_km2", "share_pct"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
