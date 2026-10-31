"""Download the NOAA CPC Oceanic Niño Index table and classify each DJF season.

Season labelling: the ONI row "DJF <YR>" covers Dec <YR-1>, Jan <YR>, Feb <YR>.
We label winters by that January year throughout the pipeline.
"""
from __future__ import annotations

import json

import pandas as pd
import requests

from config import INTERIM, ONI_EL_NINO, ONI_FILE, ONI_STRONG, ONI_URL, FetchError


def download() -> str:
    try:
        r = requests.get(ONI_URL, timeout=60, headers={"User-Agent": "snowspot-elnino/1.0"})
        r.raise_for_status()
    except Exception as e:  # noqa: BLE001
        raise FetchError(f"ONI download failed: {ONI_URL}: {e}") from e
    if "SEAS" not in r.text or "ANOM" not in r.text:
        raise FetchError(f"ONI download from {ONI_URL} did not look like the ONI table")
    ONI_FILE.write_text(r.text)
    return r.text


def parse(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) == 4 and p[0].isalpha() and p[1].isdigit():
            rows.append((p[0], int(p[1]), float(p[2]), float(p[3])))
    df = pd.DataFrame(rows, columns=["season", "year", "total", "anom"])
    if df.empty:
        raise FetchError("ONI table parsed to zero rows")
    return df


def classify(df: pd.DataFrame, first_year: int, last_year: int) -> dict:
    djf = df[df.season == "DJF"].set_index("year")["anom"]
    djf = djf[(djf.index >= first_year) & (djf.index <= last_year)]
    el = [int(y) for y, v in djf.items() if v >= ONI_EL_NINO]
    strong = [int(y) for y, v in djf.items() if v >= ONI_STRONG]
    return {
        "source": ONI_URL,
        "thresholds": {"el_nino": ONI_EL_NINO, "strong": ONI_STRONG},
        "label_convention": "winter labelled by January year; DJF 1998 = Dec 1997-Feb 1998",
        "djf_oni": {int(k): float(v) for k, v in djf.items()},
        "el_nino_years": el,
        "strong_years": strong,
        "other_years": [int(y) for y in djf.index if int(y) not in el],
    }


def main(first_year: int = 1951, last_year: int = 2026):
    text = download()
    info = classify(parse(text), first_year, last_year)
    (INTERIM / "oni_classification.json").write_text(json.dumps(info, indent=1))
    fmt = lambda ys: ", ".join(f"{y-1}/{str(y)[2:]}" for y in ys)  # noqa: E731
    print(f"[oni] {len(info['el_nino_years'])} El Niño winters: {fmt(info['el_nino_years'])}")
    print(f"[oni] {len(info['strong_years'])} strong winters: {fmt(info['strong_years'])}")
    return info


if __name__ == "__main__":
    main()
