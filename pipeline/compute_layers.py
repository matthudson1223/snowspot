"""Build the anomaly layers, the grid CSV and the per-resort table.

Layers (DJF totals, water-equivalent inches, anomaly vs 1991-2020 ERA5 normal):
  elnino_all      ERA5 composite of all El Niño winters (DJF ONI >= +0.5)
  elnino_strong   ERA5 composite of strong/super winters (DJF ONI >= +1.5)
  forecast_ecmwf  ECMWF seasonal forecast ensemble-mean anomaly
  forecast_c3s    equal-weight mean of the available C3S systems' anomalies
"""
from __future__ import annotations

import calendar
import json

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

from config import (CLIM_FIRST, CLIM_LAST, ERA5_FIRST_YEAR, IKON_DEST_CSV, INTERIM, M_TO_IN, OUT,
                    PCT_MIN_CLIM_IN, RAW, SEAS_TARGET_MONTHS, SIG_ALPHA, SNOW_RATIO, FetchError, norm_lon)
from geo import land_mask


# ---------------------------------------------------------------- helpers
def _standardise(ds: xr.Dataset) -> xr.Dataset:
    ren = {}
    for a, b in (("valid_time", "time"), ("latitude", "lat"), ("longitude", "lon")):
        if a in ds.dims or a in ds.coords:
            ren[a] = b
    ds = ds.rename(ren)
    ds = ds.assign_coords(lon=norm_lon(ds["lon"])).sortby("lon").sortby("lat")
    return ds


def days_in(t) -> int:
    t = pd.Timestamp(t)
    return calendar.monthrange(t.year, t.month)[1]


def load_era5_monthly() -> xr.DataArray:
    files = sorted(RAW.glob("era5_sf_*.nc"))
    if not files:
        raise FetchError("No ERA5 files in data/raw; run fetch_era5.py")
    parts = []
    for f in files:
        ds = _standardise(xr.open_dataset(f))
        da = ds["sf"]
        if "expver" in da.dims:  # legacy CDS: ERA5 + ERA5T split on an expver dimension
            da = da.max("expver") if da.notnull().sum("expver").max() <= 1 else da.isel(expver=0)
        da = da.drop_vars([c for c in da.coords if c not in ("time", "lat", "lon")])
        da = da.squeeze(drop=True)
        parts.append(da)
    da = xr.concat(parts, "time").sortby("time")
    da = da.isel(time=~da.get_index("time").duplicated())
    units = da.attrs.get("units", "")
    if units not in ("m of water equivalent", "m"):
        raise FetchError(f"Unexpected ERA5 snowfall units {units!r}")
    # monthly_averaged_reanalysis for accumulations = mean DAILY accumulation (m w.e. / day)
    ndays = xr.DataArray([days_in(t) for t in da.time.values], dims="time", coords={"time": da.time})
    return (da * ndays).assign_attrs(units="m w.e. per month")


def djf_totals(monthly: xr.DataArray) -> xr.DataArray:
    t = monthly.get_index("time")
    seasons, fields = [], []
    for y in range(ERA5_FIRST_YEAR + 1, t.year.max() + 1):
        want = [pd.Timestamp(y - 1, 12, 1), pd.Timestamp(y, 1, 1), pd.Timestamp(y, 2, 1)]
        sel = [ts for ts in t if pd.Timestamp(ts.year, ts.month, 1) in want]
        if len(sel) == 3:
            seasons.append(y)
            fields.append(monthly.sel(time=sel).sum("time"))
    out = xr.concat(fields, pd.Index(seasons, name="season")) * M_TO_IN
    return out.assign_attrs(units="in w.e. (DJF total)")


def composite(djf: xr.DataArray, clim: xr.DataArray, years: list[int], others: list[int]):
    yrs = [y for y in years if y in djf.season.values]
    oth = [y for y in others if y in djf.season.values]
    sel = djf.sel(season=yrs)
    mean = sel.mean("season")
    anom = mean - clim
    pct = (100.0 * mean / clim).where(clim >= PCT_MIN_CLIM_IN)
    _, p = stats.ttest_ind(sel.values, djf.sel(season=oth).values, axis=0, equal_var=False, nan_policy="omit")
    p = xr.DataArray(np.asarray(p), coords=mean.coords, dims=mean.dims)
    return anom, pct, p, yrs


# ------------------------------------------------------------- forecasts
def _open_grib(path) -> xr.DataArray:
    ds = xr.open_dataset(path, engine="cfgrib", backend_kwargs={"indexpath": ""})
    names = [v for v in ds.data_vars]
    if len(names) != 1:
        raise FetchError(f"{path.name}: expected one variable, got {names}")
    da = _standardise(ds)[names[0]]
    return da


def _monthly_rate_to_djf_in(da: xr.DataArray, init: pd.Timestamp) -> xr.DataArray:
    """da has a forecastMonth dim (1 = init month). Convert rates to DJF total inches."""
    units = da.attrs.get("units", da.attrs.get("GRIB_units", ""))
    if "s**-1" not in units and "s-1" not in units:
        raise FetchError(f"Unexpected seasonal snowfall units {units!r} (expected a rate per second)")
    totals = []
    for fm in da["forecastMonth"].values:
        valid = init + pd.DateOffset(months=int(fm) - 1)
        if (valid.year, valid.month) not in SEAS_TARGET_MONTHS:
            continue
        totals.append(da.sel(forecastMonth=fm) * days_in(valid) * 86400.0)
    if len(totals) != 3:
        raise FetchError(f"Lead-time mapping error: found {len(totals)} of Dec/Jan/Feb for init {init:%Y-%m}")
    return sum(totals) * M_TO_IN


def load_forecasts(clim_era5: xr.DataArray):
    man_f = INTERIM / "seasonal_manifest.json"
    if not man_f.exists():
        raise FetchError("No seasonal manifest; run fetch_seasonal.py")
    man = json.loads(man_f.read_text())
    init = pd.Timestamp(man["init"])
    per_system = {}
    for s in man["systems"]:
        if s["mode"] == "postprocessed":
            da = _open_grib(RAW / s["files"][0])
            anom = _monthly_rate_to_djf_in(da, init)
        else:
            fc = _open_grib(RAW / s["files"][0])
            hc = _open_grib(RAW / s["files"][1])
            fcm = fc.mean("number") if "number" in fc.dims else fc
            hcm = hc.mean([d for d in ("number", "time") if d in hc.dims])
            anom = _monthly_rate_to_djf_in(fcm, init) - _monthly_rate_to_djf_in(hcm, init)
        anom = anom.drop_vars([c for c in anom.coords if c not in ("lat", "lon")]).squeeze(drop=True)
        per_system[f"{s['centre']}:{s['system']}"] = anom
    ecmwf_key = next(k for k in per_system if k.startswith("ecmwf:"))
    ref = per_system[ecmwf_key]
    regridded = [a.interp(lat=ref.lat, lon=ref.lon, method="linear") for a in per_system.values()]
    multi = xr.concat(regridded, "system").mean("system", skipna=False) if len(regridded) > 1 else None
    clim_fc = clim_era5.interp(lat=ref.lat, lon=ref.lon, method="linear")

    def pct(a):
        return (100.0 * (clim_fc + a) / clim_fc).where(clim_fc >= PCT_MIN_CLIM_IN)

    layers = {"forecast_ecmwf": (ref, pct(ref))}
    if multi is not None:
        layers["forecast_c3s"] = (multi, pct(multi))
    return layers, man, list(per_system)


# ------------------------------------------------------------------ main
def sanity(anom: xr.DataArray, label: str) -> dict:
    boxes = {  # (lat0, lat1, lon0, lon1), expected El Niño sign of snowfall anomaly
        "Great Lakes / Ohio Valley": ((38, 46), (-90, -78), "-"),
        "Pacific Northwest": ((44, 49), (-124, -116), "-"),
        "Northern Rockies (MT/WY/ID)": ((43, 49), (-116, -104), "-"),
        "Sierra Nevada": ((36, 40), (-121, -118), "+"),
        "Southern Rockies (CO/NM/AZ)": ((33, 39), (-112, -104), "+"),
        "Southern tier (TX-GA)": ((30, 35), (-100, -82), "+"),
    }
    out = {}
    for name, ((a, b), (c, d), sign) in boxes.items():
        v = float(anom.sel(lat=slice(a, b), lon=slice(c, d)).mean())
        ok = (v < 0) if sign == "-" else (v > 0)
        out[name] = {"mean_anom_in": round(v, 3), "expected": sign, "consistent": bool(ok)}
        print(f"[sanity:{label}] {name:30s} {v:+.2f} in (expected {sign}) {'ok' if ok else 'CHECK'}")
    return out


def bilinear(da: xr.DataArray, lat, lon):
    return da.interp(lat=xr.DataArray(lat, dims="p"), lon=xr.DataArray(lon, dims="p"), method="linear").values


def main():
    oni = json.loads((INTERIM / "oni_classification.json").read_text())
    monthly = load_era5_monthly()
    djf = djf_totals(monthly)
    clim_years = [y for y in range(CLIM_FIRST, CLIM_LAST + 1) if y in djf.season.values]
    if len(clim_years) != CLIM_LAST - CLIM_FIRST + 1:
        raise FetchError(f"Climatology incomplete: {len(clim_years)} seasons")
    clim = djf.sel(season=clim_years).mean("season")

    el = oni["el_nino_years"]
    strong = oni["strong_years"]
    oni_years = {int(k) for k in oni["djf_oni"]}
    others = [y for y in djf.season.values.tolist() if y not in el and y in oni_years]
    a_all, p_all, pv_all, yrs_all = composite(djf, clim, el, others)
    a_str, p_str, pv_str, yrs_str = composite(djf, clim, strong, others)

    fc_layers, man, systems = load_forecasts(clim)

    ds_era = xr.Dataset({
        "clim_djf_in": clim,
        "elnino_all_in": a_all, "elnino_all_pct": p_all, "elnino_all_p": pv_all,
        "elnino_strong_in": a_str, "elnino_strong_pct": p_str, "elnino_strong_p": pv_str,
    })
    lon2d, lat2d = np.meshgrid(ds_era.lon.values, ds_era.lat.values)
    ds_era["is_land"] = (("lat", "lon"), land_mask(lon2d, lat2d))
    ds_era.to_netcdf(INTERIM / "era5_layers.nc")
    ds_fc = xr.Dataset({f"{k}_{u}": v for k, (a, p) in fc_layers.items() for u, v in (("in", a), ("pct", p))})
    ds_fc.to_netcdf(INTERIM / "forecast_layers.nc")

    # grid CSV on the ERA5 0.25° grid (forecasts bilinearly interpolated from ~1°)
    grid = ds_era.copy()
    for v in ds_fc.data_vars:
        grid[v] = ds_fc[v].interp(lat=grid.lat, lon=grid.lon, method="linear")
    for k in ("elnino_all", "elnino_strong"):
        grid[f"{k}_sig"] = grid[f"{k}_p"] < SIG_ALPHA
    df = grid.to_dataframe().reset_index()
    cols = ["lon", "lat", "is_land", "clim_djf_in"] + [c for c in df.columns if c.startswith(("elnino", "forecast"))]
    df[cols].round(4).to_csv(OUT / "snow_anomaly_grid.csv", index=False)

    # resorts
    res = pd.read_csv(IKON_DEST_CSV)
    if res[["lat", "lon"]].isna().any().any():
        raise FetchError(f"Resorts without coordinates: {res[res.lat.isna()].resort.tolist()}")
    lat, lon = res["lat"].values, res["lon"].values
    in_domain = (lat > float(ds_era.lat.min())) & (lat < float(ds_era.lat.max())) & \
                (lon > float(ds_era.lon.min())) & (lon < float(ds_era.lon.max()))
    res["in_data_domain"] = in_domain
    res["on_land"] = land_mask(lon, lat)
    res["clim_djf_in"] = bilinear(clim, lat, lon)
    for k in ("elnino_all", "elnino_strong"):
        res[f"{k}_in"] = bilinear(ds_era[f"{k}_in"], lat, lon)
        res[f"{k}_snow10_in"] = res[f"{k}_in"] * SNOW_RATIO
        res[f"{k}_pct"] = bilinear(ds_era[f"{k}_pct"], lat, lon)
        res[f"{k}_p"] = bilinear(ds_era[f"{k}_p"], lat, lon)
    for k in fc_layers:
        res[f"{k}_in"] = bilinear(ds_fc[f"{k}_in"], lat, lon)
        res[f"{k}_snow10_in"] = res[f"{k}_in"] * SNOW_RATIO
        res[f"{k}_pct"] = bilinear(ds_fc[f"{k}_pct"], lat, lon)
    res = res.rename(columns={"list_source_url": "source_url"})
    res.round(3).to_csv(OUT / "ikon_resorts.csv", index=False)

    meta = {
        "era5_seasons": [int(djf.season.min()), int(djf.season.max())],
        "clim_period": [CLIM_FIRST, CLIM_LAST],
        "el_nino_years": yrs_all, "strong_years": yrs_str, "n_other": len(others),
        "djf_oni": oni["djf_oni"], "oni_thresholds": oni["thresholds"],
        "forecast_init": man["init"], "forecast_leadtime_month": man["leadtime_month"],
        "forecast_systems": systems, "forecast_skipped": man.get("skipped", []),
        "sig_alpha": SIG_ALPHA, "snow_ratio": SNOW_RATIO,
        "n_resorts": int(len(res)), "n_outside_domain": int((~res.in_data_domain).sum()),
        "outside_domain": res.loc[~res.in_data_domain, "resort"].tolist(),
        "not_on_land": res.loc[~res.on_land, "resort"].tolist(),
        "sanity": {"elnino_all": sanity(a_all, "all"), "elnino_strong": sanity(a_str, "strong")},
    }
    (INTERIM / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[layers] {len(yrs_all)} El Niño, {len(yrs_str)} strong; forecast init {man['init']} "
          f"systems={systems}; resorts={len(res)} (outside domain: {meta['outside_domain']}, "
          f"not on land: {meta['not_on_land']})")
    return meta


if __name__ == "__main__":
    main()
