# El Niño snowfall × Ikon Pass map (North America)

This pipeline maps winter (Dec–Feb) snowfall anomalies across the US and Canada with every North American Ikon Pass destination overlaid. It produces:

- **(a)** an ERA5 composite of all El Niño winters
- **(b)** an ERA5 composite of strong/super El Niño winters
- **(c)** the 2026/27 seasonal forecast (ECMWF, plus a C3S multi-system mean)

Everything is built from downloaded data. If any download fails, the pipeline stops and writes the reason to `output/FAILED.txt`. Nothing is estimated, interpolated from memory or hand-built.

## Status

**The outputs have not been generated yet.** The build environment's network policy denied every primary source the pipeline needs, and no CDS API key was configured. The last run stopped with:

| Source | Host | Result |
|---|---|---|
| ERA5 monthly means, C3S seasonal forecasts | `cds.climate.copernicus.eu` | proxy `403 Forbidden` on CONNECT; no `CDSAPI_KEY` / `~/.cdsapirc` |
| ONI table | `www.cpc.ncep.noaa.gov` | proxy `403 Forbidden` |
| Ikon destinations | `www.ikonpass.com` | proxy `403 Forbidden` |
| Geocoding | `nominatim.openstreetmap.org` | proxy `403 Forbidden` |
| Natural Earth (primary) | `naciscdn.org` | proxy `403 Forbidden`; the official GitHub mirror (`raw.githubusercontent.com/nvkelso/natural-earth-vector`) worked |

To run it, allow those hosts (or use an unrestricted network), set `CDSAPI_KEY`, and accept the licences on each CDS dataset page: ERA5 monthly means, seasonal post-processed single levels, and seasonal monthly single levels. Then run:

```bash
pip install -r requirements.txt
export CDSAPI_KEY=<personal access token from https://cds.climate.copernicus.eu/profile>
python pipeline/run_all.py            # add --ecmwf-only to skip the multi-system layer
```

`fetch_ikon.py` writes `data/ikon_destinations_2026_27.csv`. **Review it against ikonpass.com** for pass tier, access days and base-area coordinates, then re-run. Edited rows are preserved.

## Outputs (`output/`)

| File | Contents |
|---|---|
| `snow_anomaly_grid.csv` | ERA5 0.25° grid. Columns: `lon, lat, is_land, clim_djf_in`; `<layer>_in` (anomaly, water-equivalent inches); `<layer>_pct` (% of normal); and for the composites `<layer>_p` (t-test p-value) and `<layer>_sig` (p < 0.10). Forecast columns are bilinearly interpolated from the ~1° native grid. |
| `ikon_resorts.csv` | One row per resort. Columns: resort, state/province, country, region, lat, lon, pass access, `source_url` (Ikon list), `coord_source` (OSM object); `in_data_domain` and `on_land` flags; normal DJF w.e.; and for each layer `_in`, `_snow10_in` (approximate snowfall at 10:1) and `_pct`, bilinearly sampled. |
| `snow_ikon_map_<layer>.png` / `_pct.png` | 3200 × 2320 px, Lambert conformal conic, brown→blue diverging scale centred on 0 (or 100 %), shading clipped to land minus lakes. Hatching marks p ≥ 0.10. |
| `index.html` | Single self-contained page with images and data inlined. It has layer and unit toggles, resort tooltips (hover or tap), a sortable, searchable table, a methods section, and light/dark support. |
| `summary.txt` | El Niño year lists, forecast init date, and the top 5 surplus/deficit resorts per layer. |

Layers: `elnino_all`, `elnino_strong`, `forecast_ecmwf`, `forecast_c3s`.

## Exact CDS requests

All requests use the new CDS API (`cdsapi>=0.7.4`, `https://cds.climate.copernicus.eu/api`). Every request actually sent is also logged to `data/interim/cds_requests.json`.

**ERA5**: `reanalysis-era5-single-levels-monthly-means`

```python
{"product_type": ["monthly_averaged_reanalysis"], "variable": ["snowfall"], "time": ["00:00"],
 "year": ["1950", ..., "2025"], "month": ["01", "02", "12"],
 "data_format": "netcdf", "download_format": "unarchived", "area": [62, -140, 22, -52]}
# plus the same with "year": ["2026"], "month": ["01", "02"] for the most recent winter
```

**Seasonal (preferred)**: `seasonal-postprocessed-single-levels`

```python
{"originating_centre": "ecmwf", "system": "<latest, read from constraints.json>",
 "variable": ["snowfall_anomalous_rate_of_accumulation"], "product_type": ["ensemble_mean"],
 "year": ["2026"], "month": ["11"],          # or "10" if November is not yet published
 "leadtime_month": ["2", "3", "4"],          # Nov init -> Dec, Jan, Feb ("3","4","5" for an Oct init)
 "data_format": "grib", "area": [62, -140, 22, -52]}
```

The same request is repeated for `ukmo`, `meteo_france`, `dwd`, `cmcc`, `ncep`, `jma` and `eccc`, all at the same init month. The script reads each dataset's `constraints.json` to choose the newest system per centre and the newest init (Nov 2026, otherwise Oct 2026) that ECMWF has published. Lead time on CDS counts the init month as `leadtime_month = 1`.

**Seasonal (fallback, per system, only if the post-processed product is missing)**: `seasonal-monthly-single-levels`, `"variable": ["snowfall"]`, `"product_type": ["monthly_mean"]`, the same months and leads. It is fetched once for 2026 and once for the 1993–2016 hindcast years. The anomaly is the forecast ensemble mean minus the hindcast mean.

**Before running, verify these on the CDS pages:** variable and product names, system numbers and release dates can change between seasons. The scripts fail loudly if constraints don't match.

## ONI classification

- Source: <https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt>, raw copy saved to `data/raw/oni.ascii.txt`.
- Only the `DJF` row is used. A winter is labelled by its January year (`DJF 1998` = Dec 1997 – Feb 1998).
- **El Niño:** DJF ONI ≥ +0.5. **Strong/super:** DJF ONI ≥ +1.5. These are single-season thresholds, not the 5-overlapping-season ENSO-event rule.
- Year lists are derived from the table at run time and written to `data/interim/oni_classification.json`, `output/summary.txt` and the HTML methods section. Nothing is hardcoded.
- The comparison set for the t-test is all other winters 1950/51–2025/26 that are not El Niño. That set includes neutral and La Niña winters.

## Processing steps

1. **Units.** ERA5 `monthly_averaged_reanalysis` snowfall `sf` is the mean daily accumulation in m water equivalent. Each month is multiplied by its number of days, then Dec(Y−1) + Jan(Y) + Feb(Y) are summed and the total is converted to inches (× 39.3701). Winters missing any month are dropped. Approximate snowfall is water equivalent × 10 (10:1). It is labelled approximate everywhere.
2. **Climatology.** Mean of DJF 1990/91–2019/20 (label years 1991–2020).
3. **Composites.** Anomaly = mean over composite winters − climatology. Percent of normal = 100 × composite mean / climatology, masked where the normal is below 0.25 in w.e. Significance uses a two-sided Welch t-test (`scipy.stats.ttest_ind`, `equal_var=False`) of composite winters against all other winters. The p-value is stored and p ≥ 0.10 is hatched.
4. **Forecast.** The post-processed anomaly is a rate in m s⁻¹. Each valid month is multiplied by its seconds, using the init date and lead to find the month. A check confirms that exactly Dec, Jan and Feb were found, then the three are summed. The units attribute is checked, and the script stops if it isn't a per-second rate. The C3S mean is the equal-weight mean of the available systems after bilinear regridding to the ECMWF grid. Forecast percent of normal = 100 × (ERA5 normal + anomaly) / ERA5 normal on the forecast grid. This is approximate, because the model anomalies use a 1993–2016 hindcast base, not 1991–2020.
5. **Longitudes.** All grids are mapped from 0–360 to −180–180 and sorted. Latitudes are sorted ascending. NetCDF dimensions `valid_time`/`latitude`/`longitude` (new CDS) and legacy `time`/`expver` are both handled. GRIB is read with cfgrib.
6. **Resorts.** Layers are bilinearly interpolated (`xarray.interp`, `method="linear"`) at each resort. ERA5 (~0.25°, ~25 km) and the seasonal models (~1°, ~100 km) do not resolve individual peaks, so values describe the surrounding area. Each resort is checked for falling on land (Natural Earth land minus lakes) and inside the data domain.
7. **Quality checks** (`data/interim/meta.json`, printed during the run):
   - Regional mean anomalies are compared with the canonical El Niño pattern: drier Great Lakes/Ohio Valley, Pacific Northwest and northern Rockies; wetter southern tier, Sierra and southern Rockies. Inconsistent boxes print `CHECK`. If the pattern looks inverted, inspect units, sign and lead mapping first.
   - The resort count is reported and compared with the Ikon list, along with lists of resorts outside the domain or off land.

**Known domain issue:** the requested area's western edge (−140°) excludes Alaska. Alyeska (about −149°) gets flagged `in_data_domain = False`, with no sampled values. It is named in the map footer. To include it, widen `AREA` in `pipeline/config.py` to about −152° W.

## Code layout

| File | Role |
|---|---|
| `pipeline/config.py` | Area, periods, thresholds, paths |
| `pipeline/fetch_*.py` | One downloader per source; each raises `FetchError` on failure |
| `pipeline/compute_layers.py` | DJF totals, climatology, composites, t-test, forecasts, grid CSV, resort CSV, sanity checks |
| `pipeline/make_maps.py` | Print PNGs and transparent web layers (cartopy) |
| `pipeline/build_html.py` | Self-contained `index.html` |
| `pipeline/run_all.py` | Runs everything in order; stops at the first failure and writes `output/FAILED.txt` |

## Sources

- Hersbach et al. (2023): ERA5 monthly averaged data on single levels from 1940 to present. Copernicus C3S CDS, DOI 10.24381/cds.f17050d7.
- Copernicus C3S seasonal forecast datasets (CDS): `seasonal-postprocessed-single-levels` and `seasonal-monthly-single-levels`. Systems: ECMWF, UK Met Office, Météo-France, DWD, CMCC, NCEP, JMA, ECCC.
- NOAA Climate Prediction Center: Oceanic Niño Index (ERSSTv5).
- Ikon Pass destinations: <https://www.ikonpass.com/en/destinations>. Coordinates from OpenStreetMap via Nominatim, with the per-resort OSM URL recorded.
- Natural Earth 1:50m admin-1 states/provinces, admin-0 countries, lakes and land (public domain).
