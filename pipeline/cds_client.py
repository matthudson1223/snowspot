"""Thin wrapper around cdsapi that gives clear errors and records every request."""
from __future__ import annotations

import json
import os
from pathlib import Path

from config import INTERIM, FetchError

CDS_URL = "https://cds.climate.copernicus.eu/api"
REQUEST_LOG = INTERIM / "cds_requests.json"


def client():
    try:
        import cdsapi
    except ImportError as e:
        raise FetchError("cdsapi is not installed (pip install 'cdsapi>=0.7.4')") from e
    rc = Path(os.environ.get("CDSAPI_RC", Path.home() / ".cdsapirc"))
    key = os.environ.get("CDSAPI_KEY")
    if not key and not rc.exists():
        raise FetchError(
            "No CDS credentials: set CDSAPI_KEY (personal access token from "
            "https://cds.climate.copernicus.eu/profile) or create ~/.cdsapirc. "
            "You must also accept each dataset's licence on its CDS page."
        )
    kw = {}
    if key:
        kw = {"url": os.environ.get("CDSAPI_URL", CDS_URL), "key": key}
    return cdsapi.Client(quiet=False, **kw)


def log_request(dataset: str, request: dict, target: Path):
    log = json.loads(REQUEST_LOG.read_text()) if REQUEST_LOG.exists() else []
    log = [e for e in log if e["target"] != str(target.name)]
    log.append({"dataset": dataset, "request": request, "target": target.name})
    REQUEST_LOG.write_text(json.dumps(log, indent=1))


def retrieve(dataset: str, request: dict, target: Path, force: bool = False) -> Path:
    log_request(dataset, request, target)
    if target.exists() and target.stat().st_size > 0 and not force:
        print(f"[cds] cached {target.name}")
        return target
    c = client()
    try:
        c.retrieve(dataset, request, str(target))
    except Exception as e:  # noqa: BLE001
        if target.exists():
            target.unlink()
        raise FetchError(f"CDS request to {dataset} failed: {type(e).__name__}: {e}\nrequest={json.dumps(request)}") from e
    return target


def constraints(dataset: str) -> list[dict]:
    """Fetch the dataset's constraints.json (valid request combinations)."""
    import requests

    url = f"{CDS_URL}/catalogue/v1/collections/{dataset}/constraints.json"
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:  # noqa: BLE001
        raise FetchError(f"Could not read CDS constraints {url}: {e}") from e
