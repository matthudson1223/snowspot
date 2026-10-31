"""Shared configuration for the El Niño snowfall / Ikon Pass pipeline."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("SNOW_RAW_DIR", ROOT / "data" / "raw"))
INTERIM = Path(os.environ.get("SNOW_INTERIM_DIR", ROOT / "data" / "interim"))
OUT = Path(os.environ.get("SNOW_OUT_DIR", ROOT / "output"))
for _d in (RAW, INTERIM, OUT):
    _d.mkdir(parents=True, exist_ok=True)

# CDS "area" ordering is [North, West, South, East]
AREA = [62, -140, 22, -52]

# ERA5 history
ERA5_DATASET = "reanalysis-era5-single-levels-monthly-means"
ERA5_FIRST_YEAR = 1950
ERA5_FILE = RAW / "era5_snowfall_monthly_DJF.nc"

# Climatology base period (DJF seasons labelled by their January year: 1991 = Dec 1990-Feb 1991)
CLIM_FIRST, CLIM_LAST = 1991, 2020

# ONI
ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
ONI_FILE = RAW / "oni.ascii.txt"
ONI_EL_NINO = 0.5      # DJF ONI >= +0.5  -> El Niño winter
ONI_STRONG = 1.5       # DJF ONI >= +1.5  -> strong / "super" El Niño winter

# Seasonal forecasts
SEAS_PP_DATASET = "seasonal-postprocessed-single-levels"
SEAS_MONTHLY_DATASET = "seasonal-monthly-single-levels"
SEAS_PP_VARIABLE = "snowfall_anomalous_rate_of_accumulation"
SEAS_TARGET_MONTHS = [(2026, 12), (2027, 1), (2027, 2)]   # valid months: Dec 2026, Jan 2027, Feb 2027
SEAS_ACCEPTABLE_INITS = [(2026, 11), (2026, 10)]          # newest first
# C3S originating centres for the multi-system mean (CDS request keys)
C3S_CENTRES = ["ecmwf", "ukmo", "meteo_france", "dwd", "cmcc", "ncep", "jma", "eccc"]

# Ikon Pass
IKON_URL = "https://www.ikonpass.com/en/destinations"
IKON_RAW_HTML = RAW / "ikonpass_destinations.html"
# reviewed, geocoded list (input; produced by fetch_ikon.py, then checked by hand)
IKON_DEST_CSV = Path(os.environ.get("SNOW_IKON_CSV", ROOT / "data" / "ikon_destinations_2026_27.csv"))

# Natural Earth 1:50m
NE_PRIMARY = "https://naciscdn.org/naturalearth/50m/{kind}/{name}.zip"
NE_MIRROR = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/50m_{kind}/{name}.{ext}"
NE_LAYERS = {
    "ne_50m_admin_1_states_provinces": "cultural",
    "ne_50m_admin_0_countries": "cultural",
    "ne_50m_lakes": "physical",
    "ne_50m_land": "physical",
}
NE_DIR = RAW / "natural_earth"

# Units
M_TO_IN = 39.3700787
SNOW_RATIO = 10.0  # approx. 10:1 snow-to-liquid ratio, for the "approximate snowfall" display only
# Percent of normal is masked where the DJF climatology is below this many WE inches
PCT_MIN_CLIM_IN = 0.25
SIG_ALPHA = 0.10   # two-sided Welch t-test threshold for hatching/fading

LAYERS = {
    "elnino_all": "All El Niño winters (ERA5 composite)",
    "elnino_strong": "Strong/super El Niño winters (ERA5 composite)",
    "forecast_ecmwf": "2026/27 forecast: ECMWF",
    "forecast_c3s": "2026/27 forecast: C3S multi-system mean",
}


class FetchError(RuntimeError):
    """Raised when a required download fails. Never fall back to synthetic data."""


def norm_lon(lon):
    """Map longitudes from 0..360 to -180..180."""
    return ((lon + 180.0) % 360.0) - 180.0
