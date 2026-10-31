"""Run the whole pipeline. Stops at the first failed download and reports why.

    python pipeline/run_all.py            # everything
    python pipeline/run_all.py --ecmwf-only   # skip the C3S multi-system layer
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback

import pandas as pd

from config import INTERIM, LAYERS, OUT, FetchError


def summary():
    meta = json.loads((INTERIM / "meta.json").read_text())
    res = pd.read_csv(OUT / "ikon_resorts.csv")
    fmt = lambda ys: ", ".join(f"{y-1}/{str(y)[2:]}" for y in ys)  # noqa: E731
    lines = [f"El Niño winters ({len(meta['el_nino_years'])}): {fmt(meta['el_nino_years'])}",
             f"Strong winters ({len(meta['strong_years'])}): {fmt(meta['strong_years'])}",
             f"Forecast init: {meta['forecast_init']} (leadtime_month {meta['forecast_leadtime_month']}); "
             f"systems: {', '.join(meta['forecast_systems'])}",
             f"Resorts: {meta['n_resorts']} (outside data domain: {meta['outside_domain'] or 'none'}; "
             f"not on land: {meta['not_on_land'] or 'none'})"]
    for k in LAYERS:
        col = f"{k}_in"
        if col not in res:
            continue
        s = res.dropna(subset=[col]).sort_values(col)
        top = ", ".join(f"{r.resort} {r[col]:+.2f}" for _, r in s.tail(5)[::-1].iterrows())
        bot = ", ".join(f"{r.resort} {r[col]:+.2f}" for _, r in s.head(5).iterrows())
        lines += [f"[{k}] biggest surplus (in w.e.): {top}", f"[{k}] biggest deficit (in w.e.): {bot}"]
    text = "\n".join(lines)
    (OUT / "summary.txt").write_text(text + "\n")
    print(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ecmwf-only", action="store_true")
    args = ap.parse_args()
    import build_html
    import compute_layers
    import fetch_boundaries
    import fetch_era5
    import fetch_ikon
    import fetch_oni
    import fetch_seasonal
    import make_maps

    steps = [("Natural Earth boundaries", fetch_boundaries.main),
             ("NOAA CPC ONI table", fetch_oni.main),
             ("Ikon Pass destinations", fetch_ikon.main),
             ("ERA5 monthly snowfall (CDS)", fetch_era5.main),
             ("C3S seasonal forecasts (CDS)", lambda: fetch_seasonal.main(multi_system=not args.ecmwf_only)),
             ("Compute layers", compute_layers.main),
             ("Render maps", make_maps.main),
             ("Build index.html", build_html.main),
             ("Summary", summary)]
    for name, fn in steps:
        print(f"\n=== {name} ===")
        try:
            fn()
        except FetchError as e:
            msg = f"STOPPED at step '{name}': {e}"
            (OUT / "FAILED.txt").write_text(msg + "\n")
            print(msg, file=sys.stderr)
            sys.exit(2)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            sys.exit(1)
    (OUT / "FAILED.txt").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
