"""Download ERA5 monthly-mean snowfall for Dec/Jan/Feb, 1950-present, over North America."""
from __future__ import annotations

import datetime as dt

from cds_client import retrieve
from config import AREA, ERA5_DATASET, ERA5_FIRST_YEAR, RAW


def requests_for(today: dt.date | None = None) -> list[tuple[dict, str]]:
    today = today or dt.date.today()
    # ERA5 (ERA5T) monthly means appear ~5-6 days after the month ends.
    last_full_dec = today.year - 2 if (today.month, today.day) < (1, 7) else today.year - 1
    years = [str(y) for y in range(ERA5_FIRST_YEAR, last_full_dec + 1)]
    base = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["snowfall"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }
    reqs = [({**base, "year": years, "month": ["01", "02", "12"]}, f"era5_sf_{years[0]}_{years[-1]}.nc")]
    # Jan/Feb of the current calendar year (the most recent complete winter)
    jf = ["01"] + (["02"] if (today.month, today.day) >= (3, 7) else [])
    if (today.month, today.day) >= (2, 7):
        reqs.append(({**base, "year": [str(today.year)], "month": jf}, f"era5_sf_{today.year}_JF.nc"))
    return reqs


def main():
    paths = []
    for req, name in requests_for():
        paths.append(retrieve(ERA5_DATASET, req, RAW / name))
        print(f"[era5] {name}")
    return paths


if __name__ == "__main__":
    main()
