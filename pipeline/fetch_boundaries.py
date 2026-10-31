"""Download Natural Earth 1:50m admin-1, countries, lakes and land shapefiles."""
from __future__ import annotations

import io
import zipfile

import requests

from config import NE_DIR, NE_LAYERS, NE_MIRROR, NE_PRIMARY, FetchError

EXTS = ["shp", "shx", "dbf", "prj", "cpg"]


def fetch_layer(name: str, kind: str) -> str:
    if (NE_DIR / f"{name}.shp").exists():
        return "cached"
    NE_DIR.mkdir(parents=True, exist_ok=True)
    errors = []
    url = NE_PRIMARY.format(kind=kind, name=name)
    try:
        r = requests.get(url, timeout=120, headers={"User-Agent": "snowspot-elnino/1.0"})
        r.raise_for_status()
        zipfile.ZipFile(io.BytesIO(r.content)).extractall(NE_DIR)
        return url
    except Exception as e:  # noqa: BLE001
        errors.append(f"{url}: {e}")
    # Official Natural Earth GitHub repository (same files, unzipped)
    try:
        for ext in EXTS:
            u = NE_MIRROR.format(kind=kind, name=name, ext=ext)
            r = requests.get(u, timeout=120)
            if r.status_code == 404 and ext == "cpg":
                continue
            r.raise_for_status()
            (NE_DIR / f"{name}.{ext}").write_bytes(r.content)
        return NE_MIRROR.format(kind=kind, name=name, ext="shp")
    except Exception as e:  # noqa: BLE001
        errors.append(f"github mirror: {e}")
    raise FetchError(f"Natural Earth {name} could not be downloaded:\n  " + "\n  ".join(errors))


def main():
    for name, kind in NE_LAYERS.items():
        src = fetch_layer(name, kind)
        print(f"[natural earth] {name}: {src}")


if __name__ == "__main__":
    main()
