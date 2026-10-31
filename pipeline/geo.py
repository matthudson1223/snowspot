"""Natural Earth helpers: read shapefiles, land(-minus-lakes) geometry and masks."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import shapefile  # pyshp
from shapely import contains_xy
from shapely.geometry import box, shape
from shapely.ops import unary_union

from config import NE_DIR, FetchError


def read_shapes(name: str):
    p = NE_DIR / f"{name}.shp"
    if not p.exists():
        raise FetchError(f"Missing {p}; run fetch_boundaries.py first")
    r = shapefile.Reader(str(p), encoding="utf-8")
    fields = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.iterShapeRecords():
        out.append((shape(sr.shape.__geo_interface__), dict(zip(fields, sr.record))))
    return out


@lru_cache(maxsize=4)
def land_geometry(bbox=(-170, 10, -40, 75)):
    """Land minus lakes, clipped to a lon/lat bbox (shading is clipped to this)."""
    clip = box(*bbox)
    land = unary_union([g.intersection(clip) for g, _ in read_shapes("ne_50m_land") if g.intersects(clip)])
    lakes = unary_union([g.intersection(clip) for g, _ in read_shapes("ne_50m_lakes") if g.intersects(clip)])
    return land.difference(lakes).buffer(0)


def land_mask(lon2d: np.ndarray, lat2d: np.ndarray) -> np.ndarray:
    return contains_xy(land_geometry(), lon2d, lat2d)


def admin_lines(bbox=(-170, 10, -40, 75)):
    clip = box(*bbox)
    states = [g.intersection(clip).boundary for g, a in read_shapes("ne_50m_admin_1_states_provinces")
              if a.get("adm0_a3") in ("USA", "CAN", "MEX") and g.intersects(clip)]
    countries = [g.intersection(clip).boundary for g, _ in read_shapes("ne_50m_admin_0_countries")
                 if g.intersects(clip)]
    lakes = [g.intersection(clip) for g, _ in read_shapes("ne_50m_lakes") if g.intersects(clip)]
    return states, countries, lakes
