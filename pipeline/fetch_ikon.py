"""Fetch the 2026/27 Ikon Pass destination list and geocode North American resorts.

Step 1 scrapes https://www.ikonpass.com/en/destinations (raw HTML is archived in
data/raw). Step 2 geocodes each resort with OpenStreetMap Nominatim and records the
OSM object URL as the coordinate source. The result is written to
data/ikon_destinations_2026_27.csv, which is meant to be REVIEWED by a human
(compare against ikonpass.com, fix tiers/access days, nudge coordinates to the
base area). Existing rows/edits in that file are preserved on re-runs.
"""
from __future__ import annotations

import json
import re
import time

import pandas as pd
import requests

from config import IKON_DEST_CSV, IKON_RAW_HTML, IKON_URL, RAW, FetchError

UA = {"User-Agent": "snowspot-elnino/1.0 (research; contact via github.com/matthudson1223/snowspot)"}
COLUMNS = ["resort", "state_province", "country", "region", "pass_access", "lat", "lon",
           "coord_type", "coord_source", "list_source_url"]


def scrape() -> pd.DataFrame:
    try:
        r = requests.get(IKON_URL, timeout=60, headers={**UA, "Accept-Language": "en-US"})
        r.raise_for_status()
    except Exception as e:  # noqa: BLE001
        raise FetchError(f"Ikon destination list download failed: {IKON_URL}: {e}") from e
    IKON_RAW_HTML.write_text(r.text)
    rows = []
    # Strategy A: embedded Next.js / JSON payloads containing destination objects
    for m in re.finditer(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S):
        _walk(json.loads(m.group(1)), rows)
    # Strategy B: destination links
    if not rows:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select('a[href*="/destinations/"]'):
            name = " ".join(a.get_text(" ").split())
            href = a["href"]
            if name and href.rstrip("/").count("/") >= 3:
                rows.append({"resort": name, "list_source_url": requests.compat.urljoin(IKON_URL, href)})
    df = pd.DataFrame(rows).drop_duplicates("resort") if rows else pd.DataFrame(columns=["resort"])
    if df.empty:
        raise FetchError(f"Parsed zero destinations from {IKON_URL}; the page layout changed - "
                         f"inspect {IKON_RAW_HTML} and update fetch_ikon.scrape()")
    df.to_csv(RAW / "ikon_destinations_scraped.csv", index=False)
    return df


def _walk(obj, rows):
    if isinstance(obj, dict):
        keys = {k.lower() for k in obj}
        if {"name", "slug"} <= keys and ({"region", "state", "location", "country"} & keys):
            rows.append({
                "resort": obj.get("name"),
                "region": _s(obj.get("region")),
                "state_province": _s(obj.get("state") or obj.get("location")),
                "country": _s(obj.get("country")),
                "pass_access": _s(obj.get("access") or obj.get("passAccess") or obj.get("passes")),
                "list_source_url": requests.compat.urljoin(IKON_URL, "/en/destinations/" + str(obj.get("slug"))),
            })
        for v in obj.values():
            _walk(v, rows)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, rows)


def _s(v):
    if isinstance(v, dict):
        return v.get("name") or v.get("title") or json.dumps(v)
    if isinstance(v, list):
        return "; ".join(_s(x) for x in v)
    return v


def geocode(name: str, hint: str | None) -> dict | None:
    q = f"{name} {hint or ''}".strip()
    for query in (q, f"{name} ski area"):
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": query, "format": "jsonv2", "countrycodes": "us,ca", "limit": 5,
                                 "addressdetails": 1},
                         headers=UA, timeout=60)
        r.raise_for_status()
        time.sleep(1.1)  # Nominatim usage policy: max 1 request/second
        hits = r.json()
        # prefer winter-sports features
        hits.sort(key=lambda h: (h.get("type") != "winter_sports", -float(h.get("importance") or 0)))
        if hits:
            h = hits[0]
            a = h.get("address", {})
            return {"lat": float(h["lat"]), "lon": float(h["lon"]),
                    "state_province": a.get("state"), "country": a.get("country_code", "").upper(),
                    "coord_type": f"osm:{h.get('category')}/{h.get('type')}",
                    "coord_source": f"https://www.openstreetmap.org/{h['osm_type']}/{h['osm_id']}"}
    return None


def main():
    scraped = scrape()
    existing = pd.read_csv(IKON_DEST_CSV) if IKON_DEST_CSV.exists() else pd.DataFrame(columns=COLUMNS)
    out = existing.set_index("resort", drop=False) if not existing.empty else pd.DataFrame(columns=COLUMNS)
    for _, row in scraped.iterrows():
        name = row["resort"]
        if name in out.index and pd.notna(out.at[name, "lat"]):
            continue
        g = geocode(name, row.get("state_province"))
        rec = {c: row.get(c) for c in COLUMNS if c in row}
        if g:
            rec = {**rec, **{k: v for k, v in g.items() if v and (k not in rec or pd.isna(rec.get(k)))}}
        else:
            print(f"[ikon] could not geocode {name!r}")
        out.loc[name] = {c: rec.get(c) for c in COLUMNS}
    # North America only (lower 48, Canada, Alaska)
    na = out[out["country"].isin(["US", "CA"]) & out["state_province"].ne("Hawaii")]
    dropped = sorted(set(out.index) - set(na.index))
    na[COLUMNS].sort_values(["country", "state_province", "resort"]).to_csv(IKON_DEST_CSV, index=False)
    print(f"[ikon] {len(na)} North American destinations -> {IKON_DEST_CSV} (dropped non-NA: {len(dropped)})")
    print("[ikon] REVIEW this file against ikonpass.com before publishing.")


if __name__ == "__main__":
    main()
