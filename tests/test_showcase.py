"""The committed showcase output must match a fresh build from showcase/data/."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "showcase"


def _load_module():
    spec = importlib.util.spec_from_file_location("make_showcase", SHOWCASE / "make_showcase.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_map_geojson_is_up_to_date(tmp_path):
    mod = _load_module()
    try:
        import matplotlib  # noqa: F401
        have_mpl = True
    except ImportError:
        have_mpl = False
    mod.build(tmp_path, png=have_mpl)

    fresh = json.loads((tmp_path / "map.geojson").read_text(encoding="utf-8"))
    committed = json.loads((SHOWCASE / "map.geojson").read_text(encoding="utf-8"))
    assert fresh == committed
    assert (tmp_path / "index.html").read_text(encoding="utf-8") == (
        SHOWCASE / "index.html"
    ).read_text(encoding="utf-8")
    if have_mpl:
        assert (tmp_path / "map.png").stat().st_size > 0


def test_notebook_executes_offline():
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    pytest.importorskip("ipykernel")
    pytest.importorskip("matplotlib")
    path = SHOWCASE / "showcase.ipynb"
    before = path.read_bytes()
    nb = nbformat.read(str(path), as_version=4)
    nbclient.NotebookClient(
        nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}
    ).execute()  # raises CellExecutionError on any failing cell
    assert path.read_bytes() == before  # the committed notebook is not modified
    images = [
        o
        for c in nb.cells
        if c.cell_type == "code"
        for o in c.outputs
        if o.output_type in ("display_data", "execute_result") and "image/png" in o.get("data", {})
    ]
    assert images, "notebook produced no inline map image"


def test_real_values_lon_lat_and_area():
    fc = json.loads((SHOWCASE / "map.geojson").read_text(encoding="utf-8"))
    by_name = {f["properties"]["name_en"]: f for f in fc["features"]}
    assert len(fc["features"]) == 27
    # Egypt spans roughly 25-37 E, 22-32 N (lon, lat order).
    xs, ys = [], []
    for f in fc["features"]:
        polys = f["geometry"]["coordinates"]
        if f["geometry"]["type"] == "Polygon":
            polys = [polys]
        for poly in polys:
            for x, y in poly[0]:
                xs.append(x)
                ys.append(y)
    assert 24 < min(xs) < max(xs) < 37.5
    assert 21.5 < min(ys) < max(ys) < 32
    # New Valley is the largest governorate (~453,000 km2 in an equal-area CRS).
    assert by_name["New Valley"]["properties"]["rank"] == 1
    assert by_name["New Valley"]["properties"]["area_km2"] == pytest.approx(452983, rel=0.01)
    total = sum(f["properties"]["area_km2"] for f in fc["features"])
    assert total == pytest.approx(1.0e6, rel=0.02)  # Egypt is about 1.0 million km2
