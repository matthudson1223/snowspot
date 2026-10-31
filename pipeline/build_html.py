"""Assemble output/index.html: a single self-contained page (images + data inlined)."""
from __future__ import annotations

import base64
import html
import json

import numpy as np
import pandas as pd

from config import INTERIM, LAYERS, OUT, SIG_ALPHA, SNOW_RATIO


def _clean(v):
    if isinstance(v, (float, np.floating)):
        return None if not np.isfinite(v) else round(float(v), 3)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return None if pd.isna(v) else v


def main():
    meta = json.loads((INTERIM / "meta.json").read_text())
    web = json.loads((INTERIM / "web_layers.json").read_text())
    res = pd.read_csv(OUT / "ikon_resorts.csv")
    for k, w in web.items():
        w["image"] = "data:image/png;base64," + base64.b64encode((INTERIM / w["image"]).read_bytes()).decode()
    layers = [k for k in LAYERS if f"{k}_in" in web]
    rows = [{c: _clean(v) for c, v in r.items()} for r in res.to_dict("records")]
    data = {"meta": meta, "web": web, "resorts": rows,
            "layers": {k: LAYERS[k] for k in layers}, "snowRatio": SNOW_RATIO, "sigAlpha": SIG_ALPHA}
    page = TEMPLATE.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")).replace("</", "<\\/"))
    page = page.replace("__METHODS__", methods_html(meta))
    (OUT / "index.html").write_text(page)
    print(f"[html] {OUT / 'index.html'} ({len(page) / 1e6:.1f} MB)")


def methods_html(m):
    fmt = lambda ys: ", ".join(f"{y-1}/{str(y)[2:]}" for y in ys)  # noqa: E731
    e = html.escape
    skipped = "; ".join(f"{s['centre']} ({s['reason'][:80]})" for s in m.get("forecast_skipped", [])) or "none"
    return f"""
<p><b>Historical layers.</b> ERA5 monthly-averaged reanalysis snowfall (Copernicus Climate Change Service,
dataset <code>reanalysis-era5-single-levels-monthly-means</code>), converted from metres water-equivalent per day
to monthly totals using the number of days in each month and summed over December–February. Winters run
{m['era5_seasons'][0]-1}/{str(m['era5_seasons'][0])[2:]} to {m['era5_seasons'][1]-1}/{str(m['era5_seasons'][1])[2:]};
the normal is the 1991–2020 DJF mean. A winter counts as El Niño when its DJF Oceanic Niño Index
(NOAA CPC, <code>oni.ascii.txt</code>) is ≥ +{m['oni_thresholds']['el_nino']}, and as strong when it is ≥
+{m['oni_thresholds']['strong']}.</p>
<p><b>El Niño winters ({len(m['el_nino_years'])}):</b> {e(fmt(m['el_nino_years']))}.<br>
<b>Strong winters ({len(m['strong_years'])}):</b> {e(fmt(m['strong_years']))}.</p>
<p>Significance: two-sided Welch t-test of the composite winters against all other winters
({m['n_other']}); areas with p ≥ {SIG_ALPHA} are hatched.</p>
<p><b>Forecast layers.</b> Copernicus C3S seasonal forecasts initialised {e(m['forecast_init'])}
(lead-time months {', '.join(m['forecast_leadtime_month'])} = Dec, Jan, Feb), ensemble-mean snowfall anomaly
relative to each system's 1993–2016 hindcast climatology. Systems: {e(', '.join(m['forecast_systems']))}.
Not included: {e(skipped)}. The multi-system mean weights each system equally after bilinear regridding to the
ECMWF grid. Percent of normal adds the anomaly to the ERA5 1991–2020 normal, so treat it as approximate.</p>
<p><b>Resorts.</b> Ikon Pass 2026/27 destinations in North America from ikonpass.com; coordinates as listed per
resort (source column). Layer values are bilinearly interpolated to each resort. ERA5 (~0.25°) and the seasonal
models (~1°) do not resolve individual peaks, so values describe the surrounding area, not the summit.
Snow amounts assume a 10:1 snow-to-liquid ratio and are approximate. Boundaries: Natural Earth 1:50m.</p>"""


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>El Niño Snow &amp; Ikon</title>
<style>
:root{--bg:#f7f6f2;--fg:#1d1d1b;--muted:#5d5d58;--card:#fff;--line:#d9d7cf;--accent:#1f5fa8;--onaccent:#fff;--hi:#ffd400}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15171a;--fg:#ecebe6;--muted:#a3a29c;--card:#1f2226;--line:#34383e;--accent:#7fb2ff;--onaccent:#0b1a2e}}
:root[data-theme="dark"]{--bg:#15171a;--fg:#ecebe6;--muted:#a3a29c;--card:#1f2226;--line:#34383e;--accent:#7fb2ff;--onaccent:#0b1a2e}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:16px}
h1{font-size:clamp(1.3rem,3.5vw,2rem);margin:.2em 0}.sub{color:var(--muted);margin:0 0 12px}
.controls{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;flex-wrap:wrap}
.seg button{border:0;background:var(--card);color:var(--fg);padding:7px 12px;font:inherit;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--accent);color:var(--onaccent)}
.map{position:relative;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.map img{display:block;width:100%;height:auto}
.map svg{position:absolute;inset:0;width:100%;height:100%}
.tri{fill:var(--hi);stroke:#111;stroke-width:1.2;vector-effect:non-scaling-stroke;cursor:pointer}.tri:hover,.tri.sel{fill:#ff6a00}
#tip{position:absolute;pointer-events:none;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px;box-shadow:0 4px 16px #0003;max-width:260px;display:none;z-index:5}
.legend{display:flex;align-items:center;gap:8px;margin:10px 0;flex-wrap:wrap;font-size:13px;color:var(--muted)}
.bar{display:flex;flex:1 1 320px;min-width:240px}.bar div{flex:1;height:14px}.ticks{display:flex;justify-content:space-between;font-size:11px}
table{width:100%;border-collapse:collapse;background:var(--card);font-size:14px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
th{cursor:pointer;position:sticky;top:0;background:var(--card);z-index:1}td:first-child,th:first-child{position:sticky;left:0;background:var(--card)}th:first-child{z-index:2}td.n{text-align:right;font-variant-numeric:tabular-nums}
.tw{overflow:auto;max-height:70vh;border:1px solid var(--line);border-radius:10px}
input[type=search]{padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit;width:min(100%,320px)}
.pos{color:#2b7bd6}.neg{color:#a5651c}section{margin:24px 0}.note{color:var(--muted);font-size:13px}
</style></head><body><main>
<h1>Winter snowfall in El Niño years and the 2026/27 forecast, with Ikon Pass resorts</h1>
<p class="sub" id="subtitle"></p>
<div class="controls">
 <div class="seg" id="layerSeg" role="group" aria-label="Layer"></div>
 <div class="seg" id="unitSeg" role="group" aria-label="Units">
  <button data-u="in" aria-pressed="true">Inches (water equiv.)</button><button data-u="pct" aria-pressed="false">% of normal</button></div>
</div>
<div class="map" id="map"><img id="mapimg" alt="Snowfall anomaly map"><svg id="ov" viewBox="0 0 1600 1000" preserveAspectRatio="none"></svg><div id="tip"></div></div>
<div class="legend"><span id="legLabel"></span><div style="flex:1 1 320px"><div class="bar" id="bar"></div><div class="ticks" id="ticks"></div></div></div>
<p class="note" id="hatchNote"></p>
<section><h2>Resorts</h2>
<input type="search" id="q" placeholder="Search resort, state, region…" aria-label="Search resorts">
<div class="tw" style="margin-top:8px"><table id="tbl"><thead></thead><tbody></tbody></table></div>
<p class="note">Values are for the surrounding ~25 km (ERA5) or ~100 km (forecast) grid area, not the summit. Snow ≈ 10 × water equivalent (approximate).</p></section>
<section><h2>Methods &amp; sources</h2>__METHODS__</section>
</main>
<script>
const D=/*__DATA__*/null;
let layer=Object.keys(D.layers)[0],unit="in",sortKey=null,sortDir=-1;
const $=s=>document.querySelector(s),R=D.resorts,svgNS="http://www.w3.org/2000/svg";
const fmt=(v,u)=>v==null?"–":u==="pct"?Math.round(v)+"%":(v>0?"+":"")+v.toFixed(2)+"″";
const cls=(v,u)=>v==null?"":(u==="pct"?v-100:v)>0?"pos":"neg";
function buildLayerButtons(){const s=$("#layerSeg");for(const[k,l]of Object.entries(D.layers)){const b=document.createElement("button");b.textContent=l.replace(" (ERA5 composite)","").replace("2026/27 forecast: ","Forecast: ");b.dataset.l=k;b.setAttribute("aria-pressed",k===layer);b.onclick=()=>{layer=k;render()};s.appendChild(b)}
 document.querySelectorAll("#unitSeg button").forEach(b=>b.onclick=()=>{unit=b.dataset.u;render()})}
function render(){const w=D.web[layer+"_"+unit];$("#mapimg").src=w.image;
 document.querySelectorAll("#layerSeg button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.l===layer));
 document.querySelectorAll("#unitSeg button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.u===unit));
 $("#subtitle").textContent=D.layers[layer]+(layer.startsWith("elnino")?` · ${(layer==="elnino_all"?D.meta.el_nino_years:D.meta.strong_years).length} winters vs 1991–2020 normal`:` · initialised ${D.meta.forecast_init}`);
 $("#hatchNote").textContent=layer.startsWith("elnino")?`Hatching: not statistically significant (Welch t-test, p ≥ ${D.sigAlpha}).`:"Forecast layer: ensemble mean; no significance hatching. Seasonal snowfall forecasts have limited skill.";
 const bar=$("#bar");bar.innerHTML="";w.colors.slice(1,-1).forEach(c=>{const d=document.createElement("div");d.style.background=c;bar.appendChild(d)});
 const t=$("#ticks");t.innerHTML="";w.levels.forEach(v=>{const s=document.createElement("span");s.textContent=unit==="pct"?Math.round(v)+"%":v;t.appendChild(s)});
 $("#legLabel").textContent=unit==="pct"?"% of normal":"Inches water equiv. (×10 ≈ snow)";
 const ov=$("#ov");ov.innerHTML="";const k=1600/Math.max(1,$("#map").clientWidth),s=Math.max(11,8*k);w.positions.forEach((p,i)=>{if(p.x<0||p.x>1||p.y<0||p.y>1)return;const x=p.x*1600,y=p.y*1000;
  const tri=document.createElementNS(svgNS,"polygon");tri.setAttribute("points",`${x},${y-s} ${x-s*.9},${y+s*.6} ${x+s*.9},${y+s*.6}`);tri.setAttribute("class","tri");tri.dataset.i=i;
  tri.setAttribute("tabindex","0");tri.addEventListener("mouseenter",e=>tip(i,e));tri.addEventListener("click",e=>{tip(i,e);e.stopPropagation()});tri.addEventListener("mouseleave",()=>$("#tip").style.display="none");ov.appendChild(tri)});
 table()}
function tip(i,e){const r=R[i],t=$("#tip"),v=r[layer+"_"+unit],m=$("#map").getBoundingClientRect();
 const snow=unit==="in"&&v!=null?`<br>≈ ${(v>0?"+":"")+(v*D.snowRatio).toFixed(1)}″ snow at 10:1 (approx.)`:"";
 t.innerHTML=`<b>${r.resort}</b><br>${r.state_province||""}${r.region?" · "+r.region:""}<br>${r.pass_access?"Access: "+r.pass_access+"<br>":""}<span class="${cls(v,unit)}"><b>${fmt(v,unit)}</b></span> ${unit==="pct"?"of normal":"water equiv."}${snow}<br><span class="note">Normal DJF: ${r.clim_djf_in!=null?r.clim_djf_in.toFixed(1)+"″ w.e.":"–"}</span>`;
 t.style.display="block";let x=e.clientX-m.left+12,y=e.clientY-m.top+12;if(x+260>m.width)x=Math.max(4,x-280);t.style.left=x+"px";t.style.top=y+"px"}
document.addEventListener("click",()=>$("#tip").style.display="none");
function table(){const cols=[["resort","Resort"],["state_province","State/Prov."],["region","Region"],["pass_access","Access"],...Object.keys(D.layers).map(k=>[k+"_"+unit,D.layers[k].replace(" (ERA5 composite)","").replace("2026/27 forecast: ","Fcst: ")])];
 $("#tbl thead").innerHTML="<tr>"+cols.map(([k,l])=>`<th data-k="${k}">${l}${sortKey===k?(sortDir>0?" ▲":" ▼"):""}</th>`).join("")+"</tr>";
 document.querySelectorAll("#tbl th").forEach(th=>th.onclick=()=>{const k=th.dataset.k;sortDir=sortKey===k?-sortDir:(k.includes("_in")||k.includes("_pct")?-1:1);sortKey=k;table()});
 const q=$("#q").value.toLowerCase();let rows=R.map((r,i)=>[r,i]).filter(([r])=>!q||[r.resort,r.state_province,r.region,r.pass_access].join(" ").toLowerCase().includes(q));
 if(sortKey)rows.sort((a,b)=>{const x=a[0][sortKey],y=b[0][sortKey];if(x==null)return 1;if(y==null)return -1;return (x>y?1:x<y?-1:0)*sortDir});
 $("#tbl tbody").innerHTML=rows.map(([r,i])=>"<tr>"+cols.map(([k],j)=>j<4?`<td>${r[k]??""}</td>`:`<td class="n ${cls(r[k],unit)}">${fmt(r[k],unit)}</td>`).join("")+"</tr>").join("")}
$("#q").addEventListener("input",table);let rt;addEventListener("resize",()=>{clearTimeout(rt);rt=setTimeout(render,150)});buildLayerButtons();render();
</script></body></html>"""


if __name__ == "__main__":
    main()
