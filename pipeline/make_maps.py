"""Render the static maps (print PNGs) and transparent web layers for index.html."""
from __future__ import annotations

import json

import cartopy.crs as ccrs
import matplotlib
import numpy as np
import pandas as pd
import xarray as xr

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from cartopy.mpl.patch import geos_to_path  # noqa: E402
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from shapely.geometry import box  # noqa: E402

from config import INTERIM, LAYERS, OUT, SIG_ALPHA, SNOW_RATIO  # noqa: E402
from geo import admin_lines, land_geometry  # noqa: E402

PROJ = ccrs.LambertConformal(central_longitude=-98, central_latitude=40, standard_parallels=(33, 52))
PC = ccrs.PlateCarree()
EXTENT = [-126.5, -61, 23.5, 56]  # lon0, lon1, lat0, lat1 (lower 48 + southern Canada)

# brown (less) -> white -> blue (more)
CMAP = LinearSegmentedColormap.from_list("brown_blue", [
    "#543005", "#8c510a", "#bf812d", "#dfc27d", "#f6e8c3", "#f7f7f7",
    "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"], N=256)

MAJOR = [  # label priority only (positions/values come from the data files)
    "Palisades Tahoe", "Mammoth Mountain", "Jackson Hole", "Aspen Snowmass", "Big Sky", "Alta", "Snowbird",
    "Steamboat", "Winter Park", "Copper Mountain", "Arapahoe Basin", "Taos Ski Valley", "Deer Valley",
    "Sun Valley", "Crystal Mountain", "Mt. Bachelor", "Big Bear Mountain Resort", "Killington", "Sugarbush",
    "Stratton", "Sunday River", "Sugarloaf", "Revelstoke Mountain Resort", "Banff Sunshine Village",
    "Lake Louise Ski Resort", "Tremblant", "Mont-Sainte-Anne", "Schweitzer", "Solitude", "Brighton",
    "Eldora", "Snowbasin", "Red Mountain", "Sun Peaks", "Boyne Highlands", "Blue Mountain", "Windham",
    "Loon Mountain", "Snowshoe", "Cypress Mountain", "Panorama", "Mt. Norquay", "Le Massif", "Jay Peak",
    "Alyeska", "Summit at Snoqualmie", "Mission Ridge", "Bridger Bowl",
]


def nice_limit(values, pct=97):
    v = np.nanpercentile(np.abs(values), pct)
    steps = np.array([0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100])
    return float(steps[np.searchsorted(steps, v)] if v <= steps[-1] else np.ceil(v))


def levels_for(unit, values):
    if unit == "pct":
        lim = min(nice_limit(values - 100), 100)
        return np.linspace(100 - lim, 100 + lim, 11)
    lim = nice_limit(values)
    return np.linspace(-lim, lim, 11)


def clip_patch(ax, **kw):
    """Land-minus-lakes, projected and cut to the visible map frame."""
    geom = land_geometry().intersection(box(EXTENT[0] - 25, EXTENT[2] - 8, EXTENT[1] + 25, EXTENT[3] + 12))
    x0, x1, y0, y1 = ax.get_extent()
    projected = PROJ.project_geometry(geom, PC).buffer(0).intersection(box(x0, y0, x1, y1))
    path = MPath.make_compound_path(*geos_to_path(projected))
    style = {"facecolor": "none", "edgecolor": "none", **kw}
    return PathPatch(path, transform=ax.transData, **style)


def load_layer(layer, unit):
    if layer.startswith("elnino"):
        ds = xr.open_dataset(INTERIM / "era5_layers.nc")
        p = ds[f"{layer}_p"]
    else:
        ds = xr.open_dataset(INTERIM / "forecast_layers.nc")
        p = None
    return ds[f"{layer}_{unit}"], p


def base_axes(fig, rect):
    ax = fig.add_axes(rect, projection=PROJ)
    ax.set_extent(EXTENT, crs=PC)
    ax.set_facecolor("none")
    return ax


def draw_lines(ax, color, lw_state, lw_country):
    states, countries, lakes = admin_lines()
    ax.add_geometries(lakes, PC, facecolor="none", edgecolor=color, linewidth=lw_state * 0.9, zorder=4)
    ax.add_geometries(states, PC, facecolor="none", edgecolor=color, linewidth=lw_state, zorder=4)
    ax.add_geometries(countries, PC, facecolor="none", edgecolor=color, linewidth=lw_country, zorder=4)


def draw_field(ax, da, p, levels):
    norm = BoundaryNorm(levels, CMAP.N, extend="both")
    lon, lat = np.meshgrid(da.lon.values, da.lat.values)
    mesh = ax.pcolormesh(lon, lat, da.values, cmap=CMAP, norm=norm, transform=PC, shading="nearest", zorder=2,
                         rasterized=True)
    patch = clip_patch(ax)
    ax.add_patch(patch)
    mesh.set_clip_path(patch)
    if p is not None:
        ns = (p.values >= SIG_ALPHA).astype(float)
        matplotlib.rcParams["hatch.linewidth"] = 0.45
        cs = ax.contourf(lon, lat, ns, levels=[0.5, 1.5], colors="none", hatches=["///"], transform=PC, zorder=3)
        for coll in getattr(cs, "collections", [cs]):
            coll.set_clip_path(patch)
            coll.set_edgecolor((0.3, 0.3, 0.3, 0.45))
            coll.set_linewidth(0)
    outline = clip_patch(ax, edgecolor="#555", linewidth=0.5, zorder=4)
    ax.add_patch(outline)
    return mesh, norm, outline


def project(ax, lon, lat):
    xy = PROJ.transform_points(PC, np.asarray(lon), np.asarray(lat))[:, :2]
    return ax.transData.transform(xy)  # display pixels


def place_labels(fig, ax, res, fontsize):
    renderer = fig.canvas.get_renderer()
    disp = project(ax, res.lon.values, res.lat.values)
    ax_bb = ax.get_window_extent(renderer)
    r = fontsize * 0.55 * fig.dpi / 72
    occupied = [matplotlib.transforms.Bbox.from_extents(x - r, y - r, x + r, y + r) for x, y in disp]
    rank = {n: i for i, n in enumerate(MAJOR)}
    order = sorted(range(len(res)), key=lambda i: rank.get(res.resort.iloc[i], 999))
    offsets = [(6, 4, "left", "bottom"), (6, -4, "left", "top"), (-6, 4, "right", "bottom"),
               (-6, -4, "right", "top"), (0, 9, "center", "bottom"), (0, -9, "center", "top")]
    placed = 0
    for i in order:
        if res.resort.iloc[i] not in rank or not res.visible.iloc[i]:
            continue
        x, y = disp[i]
        for dx, dy, ha, va in offsets:
            t = ax.annotate(res.resort.iloc[i], xy=(x, y), xycoords="figure pixels", xytext=(dx, dy),
                            textcoords="offset points", ha=ha, va=va, fontsize=fontsize, zorder=7,
                            color="#111", fontweight="bold",
                            bbox=dict(boxstyle="round,pad=0.15", fc=(1, 1, 1, 0.78), ec="none"))
            bb = t.get_window_extent(renderer).expanded(1.04, 1.1)
            inside = ax_bb.contains(bb.x0, bb.y0) and ax_bb.contains(bb.x1, bb.y1)
            if inside and not any(bb.overlaps(o) for o in occupied):
                occupied.append(bb)
                placed += 1
                break
            t.remove()
    return placed


def visible_mask(res):
    return (res.lon.between(EXTENT[0], EXTENT[1]) & res.lat.between(EXTENT[2], EXTENT[3])).values


def print_map(layer, unit, meta, res):
    da, p = load_layer(layer, unit)
    land_vals = da.values[np.isfinite(da.values)]
    levels = levels_for(unit, land_vals)
    fig = plt.figure(figsize=(16, 11.6), dpi=200)  # 3200 x 2320 px
    ax = base_axes(fig, [0.02, 0.165, 0.96, 0.725])
    mesh, norm, _ = draw_field(ax, da, p, levels)
    draw_lines(ax, "#6b6b6b", 0.35, 0.8)
    res = res.assign(visible=visible_mask(res))
    v = res[res.visible]
    ax.scatter(v.lon, v.lat, marker="^", s=70, c="#ffd400", edgecolors="#111", linewidths=0.9, transform=PC,
               zorder=6)
    fig.canvas.draw()
    place_labels(fig, ax, res, 7.5)

    unit_lbl = "Water-equivalent anomaly (inches, DJF total)" if unit == "in" else "Percent of 1991–2020 normal (%)"
    cax = fig.add_axes([0.2, 0.09, 0.6, 0.015])
    cb = fig.colorbar(mesh, cax=cax, orientation="horizontal", extend="both", ticks=levels)
    cb.set_label(unit_lbl, fontsize=11)
    if unit == "in":
        sec = cax.secondary_xaxis("top", functions=(lambda x: x * SNOW_RATIO, lambda x: x / SNOW_RATIO))
        sec.set_xlabel(f"≈ snowfall at {int(SNOW_RATIO)}:1 (inches, approximate)", fontsize=9)
        sec.tick_params(labelsize=8)

    yrs = meta["el_nino_years"] if layer == "elnino_all" else meta.get("strong_years")
    title = {"elnino_all": "Winter snowfall in El Niño years vs. normal",
             "elnino_strong": "Winter snowfall in strong El Niño years vs. normal",
             "forecast_ecmwf": "2026/27 winter snowfall forecast: ECMWF",
             "forecast_c3s": "2026/27 winter snowfall forecast: C3S multi-system mean"}[layer]
    if layer.startswith("elnino"):
        thr = meta["oni_thresholds"]["el_nino" if layer == "elnino_all" else "strong"]
        sub = (f"ERA5 monthly means (Copernicus C3S), Dec–Feb, composite of {len(yrs)} winters with DJF ONI ≥ "
               f"+{thr} (NOAA CPC), {meta['era5_seasons'][0]-1}/{str(meta['era5_seasons'][0])[2:]}–"
               f"{meta['era5_seasons'][1]-1}/{str(meta['era5_seasons'][1])[2:]}, vs. 1991–2020 mean. "
               f"Hatched: not significant (Welch t-test vs. other winters, p ≥ {SIG_ALPHA}).")
    else:
        sys_ = ", ".join(meta["forecast_systems"]) if layer == "forecast_c3s" else \
            next(s for s in meta["forecast_systems"] if s.startswith("ecmwf"))
        sub = (f"Copernicus C3S seasonal forecast, ensemble-mean snowfall anomaly for Dec 2026–Feb 2027, "
               f"initialised {meta['forecast_init']} ({sys_}); anomaly vs. 1993–2016 hindcast; "
               f"% of normal uses the ERA5 1991–2020 mean.")
    fig.text(0.02, 0.965, title, fontsize=22, fontweight="bold", va="top")
    fig.text(0.02, 0.925, sub, fontsize=10.5, va="top", wrap=True, color="#333")
    out_dom = meta.get("outside_domain") or []
    foot = ("Triangles: Ikon Pass 2026/27 North American destinations (ikonpass.com). Values are grid-scale: "
            "ERA5 (~0.25°, ~25 km) and seasonal models (~1°, ~100 km) do not resolve individual peaks; resort "
            "values describe the surrounding area. Snow depth equivalents assume 10:1 and are approximate. "
            "Seasonal forecasts of snowfall have limited skill. Boundaries: Natural Earth 1:50m.")
    if out_dom:
        foot += f" Outside map/data domain: {', '.join(out_dom)}."
    fig.text(0.02, 0.032, foot, fontsize=8.5, va="top", color="#444", wrap=True)
    name = f"snow_ikon_map_{layer}.png" if unit == "in" else f"snow_ikon_map_{layer}_pct.png"
    fig.savefig(OUT / name, dpi=200, facecolor="white")
    plt.close(fig)
    return name


def web_layer(layer, unit, res):
    """Transparent-ocean field image + resort pixel positions for the HTML page."""
    da, p = load_layer(layer, unit)
    levels = levels_for(unit, da.values[np.isfinite(da.values)])
    W, H = 1600, 1000
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = base_axes(fig, [0, 0, 1, 1])
    ax.spines["geo"].set_visible(False)
    draw_field(ax, da, p, levels)
    draw_lines(ax, "#7a7a7a", 0.5, 1.0)
    fig.canvas.draw()
    disp = project(ax, res.lon.values, res.lat.values)
    fname = INTERIM / f"web_{layer}_{unit}.png"
    fig.savefig(fname, dpi=100, transparent=True)
    plt.close(fig)
    pos = [{"x": float(x / W), "y": float(1 - y / H)} for x, y in disp]
    norm = BoundaryNorm(levels, CMAP.N, extend="both")
    mids = [levels[0] - 1] + list((levels[:-1] + levels[1:]) / 2) + [levels[-1] + 1]
    colors = [matplotlib.colors.to_hex(CMAP(norm(v))) for v in mids]
    return {"image": fname.name, "levels": levels.round(3).tolist(), "colors": colors, "positions": pos}


def main():
    meta = json.loads((INTERIM / "meta.json").read_text())
    res = pd.read_csv(OUT / "ikon_resorts.csv")
    layers = [k for k in LAYERS if (k != "forecast_c3s") or "forecast_c3s_in" in res.columns]
    web = {}
    for layer in layers:
        for unit in ("in", "pct"):
            print("[maps]", print_map(layer, unit, meta, res))
            web[f"{layer}_{unit}"] = web_layer(layer, unit, res)
    (INTERIM / "web_layers.json").write_text(json.dumps(web))


if __name__ == "__main__":
    main()
