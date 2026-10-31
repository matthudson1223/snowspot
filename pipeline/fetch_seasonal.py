"""Download C3S seasonal-forecast snowfall anomalies for DJF 2026/27.

Preferred: seasonal-postprocessed-single-levels, variable
"snowfall_anomalous_rate_of_accumulation", product_type "ensemble_mean"
(anomaly w.r.t. each system's 1993-2016 hindcast climatology).

Fallback (only if the post-processed product is not offered for a system):
seasonal-monthly-single-levels "snowfall", product_type "monthly_mean" for the
forecast year AND the 1993-2016 hindcast, anomaly computed in compute_layers.py.

Lead-time convention on CDS: leadtime_month 1 = the initialisation month itself.
For a 1 Nov init, Dec/Jan/Feb = leadtime_month 2/3/4; for a 1 Oct init, 3/4/5.
"""
from __future__ import annotations

import json

from cds_client import constraints, retrieve
from config import (AREA, C3S_CENTRES, INTERIM, RAW, SEAS_ACCEPTABLE_INITS, SEAS_MONTHLY_DATASET,
                    SEAS_PP_DATASET, SEAS_PP_VARIABLE, SEAS_TARGET_MONTHS, FetchError)

HINDCAST_YEARS = [str(y) for y in range(1993, 2017)]
MANIFEST = INTERIM / "seasonal_manifest.json"


def lead_months(init: tuple[int, int]) -> list[str]:
    iy, im = init
    leads = [(ty * 12 + tm) - (iy * 12 + im) + 1 for ty, tm in SEAS_TARGET_MONTHS]
    if min(leads) < 1 or max(leads) > 6:
        raise ValueError(f"init {init} cannot reach all target months (leads={leads})")
    return [str(x) for x in leads]


def _has(entry: dict, key: str, value: str) -> bool:
    return key not in entry or value in entry[key]


def available_systems(cons: list[dict], centre: str, variable: str, init: tuple[int, int],
                      product_type: str) -> list[str]:
    y, m = str(init[0]), f"{init[1]:02d}"
    systems = set()
    for e in cons:
        if centre not in e.get("originating_centre", []):
            continue
        if not (_has(e, "variable", variable) and _has(e, "product_type", product_type)):
            continue
        if y in e.get("year", []) and (m in e.get("month", []) or str(init[1]) in e.get("month", [])):
            systems.update(e.get("system", []))
    return sorted(systems, key=lambda s: (len(s), s))


def pp_request(centre: str, system: str, init: tuple[int, int]) -> dict:
    return {
        "originating_centre": centre,
        "system": system,
        "variable": [SEAS_PP_VARIABLE],
        "product_type": ["ensemble_mean"],
        "year": [str(init[0])],
        "month": [f"{init[1]:02d}"],
        "leadtime_month": lead_months(init),
        "data_format": "grib",
        "area": AREA,
    }


def monthly_request(centre: str, system: str, init: tuple[int, int], years: list[str]) -> dict:
    return {
        "originating_centre": centre,
        "system": system,
        "variable": ["snowfall"],
        "product_type": ["monthly_mean"],
        "year": years,
        "month": [f"{init[1]:02d}"],
        "leadtime_month": lead_months(init),
        "data_format": "grib",
        "area": AREA,
    }


def main(multi_system: bool = True):
    pp_cons = constraints(SEAS_PP_DATASET)
    mo_cons = constraints(SEAS_MONTHLY_DATASET)

    # 1) choose the latest init that ECMWF has published
    init, ecmwf_sys, ecmwf_mode = None, None, None
    for cand in SEAS_ACCEPTABLE_INITS:
        s = available_systems(pp_cons, "ecmwf", SEAS_PP_VARIABLE, cand, "ensemble_mean")
        if s:
            init, ecmwf_sys, ecmwf_mode = cand, s[-1], "postprocessed"
            break
        s = available_systems(mo_cons, "ecmwf", "snowfall", cand, "monthly_mean")
        if s:
            init, ecmwf_sys, ecmwf_mode = cand, s[-1], "monthly+hindcast"
            break
    if init is None:
        raise FetchError(f"No ECMWF seasonal forecast found on CDS for inits {SEAS_ACCEPTABLE_INITS}")
    print(f"[seasonal] init {init[0]}-{init[1]:02d}, ECMWF system {ecmwf_sys} ({ecmwf_mode}), "
          f"leadtime_month={lead_months(init)}")

    manifest = {"init": f"{init[0]}-{init[1]:02d}-01", "leadtime_month": lead_months(init), "systems": []}
    centres = C3S_CENTRES if multi_system else ["ecmwf"]
    for centre in centres:
        try:
            pp = available_systems(pp_cons, centre, SEAS_PP_VARIABLE, init, "ensemble_mean")
            if pp:
                system = pp[-1]
                req = pp_request(centre, system, init)
                f = retrieve(SEAS_PP_DATASET, req, RAW / f"seas_pp_{centre}_s{system}_{init[0]}{init[1]:02d}.grib")
                manifest["systems"].append({"centre": centre, "system": system, "mode": "postprocessed",
                                            "dataset": SEAS_PP_DATASET, "files": [f.name]})
                continue
            mo = available_systems(mo_cons, centre, "snowfall", init, "monthly_mean")
            if not mo:
                print(f"[seasonal] {centre}: no {init} snowfall forecast on CDS; skipped")
                manifest.setdefault("skipped", []).append({"centre": centre, "reason": "not available"})
                continue
            system = mo[-1]
            fc = retrieve(SEAS_MONTHLY_DATASET, monthly_request(centre, system, init, [str(init[0])]),
                          RAW / f"seas_mo_{centre}_s{system}_{init[0]}{init[1]:02d}_fc.grib")
            hc = retrieve(SEAS_MONTHLY_DATASET, monthly_request(centre, system, init, HINDCAST_YEARS),
                          RAW / f"seas_mo_{centre}_s{system}_{init[1]:02d}_hc1993-2016.grib")
            manifest["systems"].append({"centre": centre, "system": system, "mode": "monthly+hindcast",
                                        "dataset": SEAS_MONTHLY_DATASET, "files": [fc.name, hc.name]})
        except FetchError as e:
            if centre == "ecmwf":
                raise
            print(f"[seasonal] {centre} FAILED: {e}")
            manifest.setdefault("skipped", []).append({"centre": centre, "reason": str(e)[:500]})
        print(f"[seasonal] {centre}: done")
    MANIFEST.write_text(json.dumps(manifest, indent=1))
    return manifest


if __name__ == "__main__":
    main()
