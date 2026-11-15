"""One-off download of the showcase input (not needed to rebuild the showcase).

Fetches Natural Earth 1:10m admin-1 boundaries, keeps Egypt's governorates and
writes showcase/data/egypt_governorates.geojson. Natural Earth is public domain.
"""

import json
import urllib.request
from pathlib import Path

URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_10m_admin_1_states_provinces.geojson"
)
KEEP = ["name", "name_en", "iso_3166_2", "type_en", "adm0_a3"]


def main() -> None:
    data = json.loads(urllib.request.urlopen(URL, timeout=300).read())
    feats = [f for f in data["features"] if f["properties"].get("adm0_a3") == "EGY"]
    out = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {k: f["properties"].get(k) for k in KEEP},
                "geometry": f["geometry"],
            }
            for f in feats
        ],
    }
    dest = Path(__file__).parent / "data" / "egypt_governorates.geojson"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(len(feats), "features,", dest.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
