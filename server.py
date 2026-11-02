#!/usr/bin/env python3
"""Static file server for the God Sky Network sites.

One service, several hosts:
- weather.godsky.net / worldhealth.godsky.net (and the Railway domain):
  the updates blog and its pages (index, /health/, /articles/, ...),
  served exactly as before.
- godsky.net / www.godsky.net: the Orbital Network globe page, stored
  under globe/ and served at the root path, with its /assets/ and
  /llms.txt namespaced to the same folder. Every other path on those
  hosts falls through to the normal files.

Responses are gzipped when the client accepts it, HTML/JSON get a short
cache lifetime so edits propagate quickly, and no Content-Security-Policy
is set: the globe page fetches live data cross-origin by design.
"""
import email.utils
import gzip
import html
import http
import http.server
import io
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from datetime import date

PORT = int(os.environ.get("PORT", "8080"))
ROOT = os.path.dirname(os.path.abspath(__file__))

GLOBE_HOSTS = {"godsky.net", "www.godsky.net"}
GZIP_EXTS = {".html", ".htm", ".css", ".js", ".json", ".txt", ".svg", ".xml", ".md"}
SHORT_CACHE_EXTS = {".html", ".htm", ".json"}
SHORT_CACHE = "public, max-age=300"
STATIC_CACHE = "public, max-age=3600"


# ------------------------------------------------------------- /digest
# "Earth, measured" — the daily digest of the permanent record.
# Data comes from the public archive (github.com/mel-gregory/
# orbital-record): MANIFEST.json for the day index and running totals,
# days/<day>/manifest.json for each day's breakdowns. Fetches are
# cached for ~10 minutes; every number on the page is the archived
# number, so the page can always be checked against the record.
ARCHIVE_RAW = "https://raw.githubusercontent.com/mel-gregory/orbital-record/main"
ARCHIVE_WEB = "https://github.com/mel-gregory/orbital-record"
RECORD_FIRST_DAY = date(2026, 10, 13)
DIGEST_CACHE_TTL = 600
_digest_cache = {}
_digest_lock = threading.Lock()

EVENT_LABELS = {"emsc": "EMSC earthquakes", "usgs": "USGS earthquakes",
                "eonet": "NASA EONET events", "gdacs": "GDACS alerts",
                "who": "WHO outbreak reports"}
READING_LABELS = {"ndbc": "Ocean buoys (NDBC)",
                  "noaa_coops": "Tides (NOAA CO-OPS)",
                  "usgs_nwis": "Rivers (USGS NWIS)"}


def _archive_json(path):
    key = path
    now = time.time()
    with _digest_lock:
        hit = _digest_cache.get(key)
        if hit and now - hit[0] < DIGEST_CACHE_TTL:
            return hit[1]
    req = urllib.request.Request(
        f"{ARCHIVE_RAW}/{path}",
        headers={"User-Agent": "orbital-digest-page"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    with _digest_lock:
        _digest_cache[key] = (now, data)
    return data


def _fmt(n):
    return f"{n:,}"


def _render_digest(day_str):
    """HTML for one archived day, or None if the day is not archived."""
    index = _archive_json("MANIFEST.json")
    days = sorted(d["day"] for d in index.get("days", []))
    if day_str is None:
        if not days:
            return None
        day_str = days[-1]
    if day_str not in days:
        return None
    man = _archive_json(f"days/{day_str}/manifest.json")
    d = date.fromisoformat(day_str)
    n = (d - RECORD_FIRST_DAY).days + 1
    c = man.get("counts", {})
    ebs = man.get("events_by_source", {})
    rbs = man.get("readings_by_source", {})
    sha = man.get("sha256_record_json_gz", "")

    totals = {"events": 0, "readings": 0, "quarantine": 0}
    for entry in index.get("days", []):
        for k in totals:
            totals[k] += entry.get("counts", {}).get(k, 0)

    def rows(source_map, labels):
        out = []
        for k, v in sorted(source_map.items(), key=lambda kv: -kv[1]):
            label = html.escape(labels.get(k, k))
            out.append(f"<tr><td>{label}</td><td>{_fmt(v)}</td></tr>")
        return "\n".join(out)

    pos = days.index(day_str)
    prev_link = (f'<a href="/digest/{days[pos - 1]}">&larr; {days[pos - 1]}</a>'
                 if pos > 0 else "<span></span>")
    next_link = (f'<a href="/digest/{days[pos + 1]}">{days[pos + 1]} &rarr;</a>'
                 if pos < len(days) - 1 else "<span></span>")
    long_date = d.strftime("%A, %B %-d, %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Earth, measured — {long_date} — Orbital Network</title>
<meta name="description" content="The daily digest of Orbital Network's permanent record of the measurements of Planet Earth.">
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #0a0e1a; color: #e8ecf4;
         font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  .wrap {{ max-width: 680px; margin: 0 auto; padding: 28px 18px 40px; }}
  .brand {{ font-size: 11px; letter-spacing: 2px; color: #7a8aa5; }}
  .brand a {{ color: #7a8aa5; text-decoration: none; }}
  h1 {{ font-size: 32px; margin: 8px 0 4px; }}
  .sub {{ color: #9aa8c3; font-size: 14px; margin-bottom: 20px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .card {{ background: #121a2e; border-radius: 10px; padding: 14px; }}
  .card .v {{ font-size: 28px; font-weight: 700; color: #6db3f2; }}
  .card .k {{ font-size: 12px; color: #9aa8c3; margin-top: 2px; }}
  .panel {{ background: #10182b; border-radius: 10px; padding: 14px; margin-top: 10px; }}
  .panel h2 {{ font-size: 11px; letter-spacing: 1.5px; color: #7a8aa5; margin: 0 0 8px; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  td {{ padding: 4px 0; }}
  td:last-child {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .check {{ border: 1px dashed #2a3556; border-radius: 10px; padding: 14px; margin-top: 10px; font-size: 14px; line-height: 1.6; }}
  .check h2 {{ font-size: 11px; letter-spacing: 1.5px; color: #7a8aa5; margin: 0 0 6px; font-weight: 600; }}
  .check a, .nav a {{ color: #6db3f2; }}
  code {{ font-size: 12px; color: #9aa8c3; }}
  .totals {{ border-top: 1px solid #2a3556; margin-top: 16px; padding-top: 12px; font-size: 13px; color: #9aa8c3; }}
  .nav {{ display: flex; justify-content: space-between; margin-top: 14px; font-size: 13px; }}
  footer {{ margin-top: 22px; font-size: 12px; color: #5a6a85; font-style: italic; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand"><a href="/">ORBITAL NETWORK</a> &middot; THE PERMANENT RECORD</div>
  <h1>Earth, measured</h1>
  <div class="sub">{long_date} &middot; Day {n} of the permanent record</div>
  <div class="grid">
    <div class="card"><div class="v">{_fmt(c.get('events', 0))}</div><div class="k">events kept</div></div>
    <div class="card"><div class="v">{_fmt(c.get('readings', 0))}</div><div class="k">measurements recorded</div></div>
    <div class="card"><div class="v">{_fmt(c.get('event_link_groups', 0))}</div><div class="k">events linked across independent sources ({_fmt(c.get('event_link_members', 0))} reports)</div></div>
    <div class="card"><div class="v">{_fmt(c.get('quarantine', 0))}</div><div class="k">items quarantined as implausible — counted, not hidden</div></div>
  </div>
  <div class="panel"><h2>EVENTS BY SOURCE</h2><table>{rows(ebs, EVENT_LABELS)}</table></div>
  <div class="panel"><h2>MEASUREMENTS</h2><table>{rows(rbs, READING_LABELS)}</table></div>
  <div class="check"><h2>CHECK IT YOURSELF</h2>
    This day is archived in the public record with its own fingerprint.<br>
    Day archive SHA-256 begins <code>{html.escape(sha[:16])}&hellip;</code><br>
    <a href="{ARCHIVE_WEB}/tree/main/days/{day_str}">github.com/mel-gregory/orbital-record — day {day_str}</a>
  </div>
  <div class="totals">Since October 13, 2026: <b>{len(days)} days</b> archived &middot; <b>{_fmt(totals['events'])} events</b> &middot; <b>{_fmt(totals['readings'])} measurements</b> &middot; <b>{_fmt(totals['quarantine'])} quarantined</b></div>
  <div class="nav">{prev_link}{next_link}</div>
  <footer>Live broadcast of Planet Earth. Permanent record of its measurements.</footer>
</div>
</body>
</html>"""


# ---------------------------------------------------------- /cameras
# Public traffic cameras for the globe's CCTV layer and the landing
# camera loop. Every source is an official transport authority
# publishing its camera directory openly, with no API key:
# Caltrans (California), Minnesota DOT, Colorado DOT, DriveBC,
# Fintraffic (Finland), TfL (London), the Hong Kong Transport
# Department, DGT (Spain), NZTA (New Zealand), Vegagerðin
# (Iceland), LTA via data.gov.sg (Singapore), Ontario 511,
# Wisconsin 511WI, and Pennsylvania 511PA. Each feed is
# fetched server-side, normalized to one compact list labeled by
# operator, and cached for 5 minutes; the snapshots themselves are
# served by the operators and refresh in place. A feed that fails
# simply drops out of that cycle's list — the rest still serve.
CAMERAS_CACHE_TTL = 300
_cameras_cache = {}
_cameras_lock = threading.Lock()
CALTRANS_DISTRICTS = range(1, 13)


def _http_bytes(url, timeout=30, accept=None):
    headers = {"User-Agent": "orbital-cctv-layer",
               "Accept-Encoding": "gzip"}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    return raw


def _http_json(url, timeout=30, accept=None):
    return json.loads(
        _http_bytes(url, timeout, accept).decode("utf-8", "replace"))


def _cam(n, p, r, la, lo, img, s):
    try:
        la, lo = float(la), float(lo)
    except (TypeError, ValueError):
        return None
    if not img or not (-90 <= la <= 90 and -180 <= lo <= 180):
        return None
    if la == 0 and lo == 0:
        return None
    return {"n": str(n or "Traffic camera")[:120], "p": str(p or "")[:80],
            "r": str(r or "")[:40], "la": round(la, 5), "lo": round(lo, 5),
            "img": img, "s": s}


def _caltrans_url(d):
    return (f"https://cwwp2.dot.ca.gov/data/d{d}/cctv/"
            f"cctvStatusD{d:02d}.json")


def _parse_caltrans(doc):
    out = []
    for row in (doc or {}).get("data", []):
        cam = (row or {}).get("cctv") or {}
        if str(cam.get("inService", "")).lower() != "true":
            continue
        loc = cam.get("location") or {}
        img = ((cam.get("imageData") or {}).get("static") or {}).get(
            "currentImageURL") or ""
        if not img:
            continue
        try:
            lat = float(loc.get("latitude"))
            lon = float(loc.get("longitude"))
        except (TypeError, ValueError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
            continue
        out.append({
            "n": loc.get("locationName") or "Traffic camera",
            "p": loc.get("nearbyPlace") or "",
            "r": loc.get("route") or "",
            "la": round(lat, 5),
            "lo": round(lon, 5),
            "img": img,
            "s": "caltrans",
        })
    return out


def _src_caltrans():
    import concurrent.futures

    def one(d):
        return _parse_caltrans(_http_json(_caltrans_url(d), timeout=25))

    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for batch in pool.map(lambda d: _safe(one, d), CALTRANS_DISTRICTS):
            out.extend(batch or [])
    return out


def _src_finland():
    doc = _http_json("https://tie.digitraffic.fi/api/weathercam/v1/stations",
                     timeout=40)
    out = []
    for f in doc.get("features", []):
        props = f.get("properties") or {}
        coords = (f.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        img = ""
        for preset in props.get("presets", []):
            if preset.get("inCollection") and preset.get("id"):
                img = ("https://weathercam.digitraffic.fi/"
                       f"{preset['id']}.jpg")
                break
        cam = _cam(str(props.get("name") or "Road camera").replace("_", " "),
                   "", "", coords[1], coords[0], img, "finland")
        if cam:
            out.append(cam)
    return out


def _src_tfl():
    doc = _http_json("https://api.tfl.gov.uk/Place/Type/JamCam", timeout=40)
    out = []
    for place in doc if isinstance(doc, list) else []:
        props = {p.get("key"): p.get("value")
                 for p in place.get("additionalProperties", [])}
        if props.get("available") == "false":
            continue
        cam = _cam(place.get("commonName"), "London", "",
                   place.get("lat"), place.get("lon"),
                   props.get("imageUrl") or "", "tfl")
        if cam:
            out.append(cam)
    return out


def _src_drivebc():
    import csv
    text = _http_bytes(
        "https://catalogue.data.gov.bc.ca/dataset/"
        "6b39a910-6c77-476f-ac96-7b4f18849b1c/resource/"
        "a9d52d85-8402-4ce7-b2ac-a2779837c48a/download/webcams.csv",
        timeout=40).decode("utf-8-sig", "replace")
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        img = row.get("links_imageURL") or ""
        if not img and row.get("id"):
            img = f"https://www.drivebc.ca/images/{row['id']}.jpg"
        hwy = (row.get("highway_number") or "").strip()
        cam = _cam(row.get("camName"), row.get("region_name"),
                   f"Highway {hwy}" if hwy else "",
                   row.get("latitude"), row.get("longitude"), img, "drivebc")
        if cam:
            out.append(cam)
    return out


def _src_hongkong():
    import csv
    text = _http_bytes(
        "https://static.data.gov.hk/td/traffic-snapshot-images/code/"
        "Traffic_Camera_Locations_En.csv", timeout=40).decode(
            "utf-16", "replace").lstrip("\ufeff")
    out = []
    for row in csv.DictReader(io.StringIO(text), delimiter="\t"):
        row = {(k or "").strip("\ufeff").strip().lower(): (v or "").strip()
               for k, v in row.items()}
        key = row.get("key")
        if not key:
            continue
        cam = _cam(row.get("description"), row.get("district"),
                   row.get("region"), row.get("latitude"),
                   row.get("longitude"),
                   row.get("url")
                   or f"https://tdcctv.data.one.gov.hk/{key}.JPG", "hongkong")
        if cam:
            out.append(cam)
    return out


def _src_minnesota():
    doc = _http_json("https://mntg.carsprogram.org/cameras_v1/api/cameras",
                     timeout=40)
    out = []
    for entry in doc if isinstance(doc, list) else []:
        loc = entry.get("location") or {}
        img = ""
        for view in entry.get("views", []):
            if view.get("videoPreviewUrl"):
                img = view["videoPreviewUrl"]
                break
        place = (loc.get("cityReference") or "").removeprefix("in ").strip()
        cam = _cam(entry.get("name"), place, loc.get("routeId"),
                   loc.get("latitude"), loc.get("longitude"), img, "minnesota")
        if cam:
            out.append(cam)
    return out


def _src_colorado():
    doc = _http_json(
        "https://api-511x-co.carsprogram.org/cameras/map-features",
        timeout=40)
    out = []
    for f in doc.get("features", []):
        props = f.get("properties") or {}
        coords = (f.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        img = ""
        for view in props.get("views", []):
            if view.get("videoPreviewUrl") and not view.get("broken"):
                img = view["videoPreviewUrl"]
                break
        loc = props.get("location") or {}
        place = (loc.get("cityReference") or "").removeprefix("in ").strip()
        cam = _cam(props.get("name"), place, props.get("route"),
                   coords[1], coords[0], img, "colorado")
        if cam:
            out.append(cam)
    return out


def _src_nz():
    # NZTA serves XML unless JSON is explicitly requested.
    doc = _http_json(
        "https://trafficnz.info/service/traffic/rest/4/cameras/all",
        timeout=40, accept="application/json")
    out = []
    for entry in (doc.get("response") or {}).get("camera", []):
        if entry.get("offline") or entry.get("underMaintenance"):
            continue
        img = entry.get("imageUrl") or ""
        if img and not img.startswith("http"):
            img = "https://trafficnz.info" + img
        region = entry.get("region") or {}
        cam = _cam((entry.get("name") or "").strip()
                   or entry.get("description"),
                   region.get("name") if isinstance(region, dict) else "",
                   entry.get("highway"), entry.get("latitude"),
                   entry.get("longitude"), img, "nz")
        if cam:
            out.append(cam)
    return out


def _src_iceland():
    doc = _http_json(
        "https://gagnaveita.vegagerdin.is/api/vefmyndavelar2014_1",
        timeout=40)
    out, seen = [], set()
    for entry in doc if isinstance(doc, list) else []:
        station = entry.get("Maelist_nr")
        if station in seen:
            continue
        seen.add(station)
        cam = _cam(entry.get("Myndavel"), entry.get("Skyring"),
                   entry.get("Vegheiti"), entry.get("Breidd"),
                   entry.get("Lengd"), entry.get("Slod") or "", "iceland")
        if cam:
            out.append(cam)
    return out


def _src_singapore():
    doc = _http_json("https://api.data.gov.sg/v1/transport/traffic-images",
                     timeout=30)
    items = doc.get("items") or []
    out = []
    if items:
        for entry in items[-1].get("cameras", []):
            loc = entry.get("location") or {}
            cam = _cam(f"Traffic camera {entry.get('camera_id', '')}".strip(),
                       "Singapore", "", loc.get("latitude"),
                       loc.get("longitude"), entry.get("image") or "",
                       "singapore")
            if cam:
                out.append(cam)
    return out


def _src_spain():
    import xml.etree.ElementTree as ET

    def local(tag):
        return tag.rsplit("}", 1)[-1]

    raw = _http_bytes(
        "https://nap.dgt.es/datex2/v3/dgt/DevicePublication/"
        "camaras_datex2_v37.xml", timeout=60)
    root = ET.fromstring(raw)
    out = []
    for dev in root.iter():
        if local(dev.tag) != "device":
            continue
        vals = {}
        for e in dev.iter():
            ln = local(e.tag)
            if ln in ("typeOfDevice", "latitude", "longitude", "roadName",
                      "roadDestination", "province") and ln not in vals:
                vals[ln] = (e.text or "").strip()
        if vals.get("typeOfDevice") != "camera":
            continue
        cid = dev.get("id")
        if not cid or "latitude" not in vals or "longitude" not in vals:
            continue
        name = " · ".join(x for x in (vals.get("roadName"),
                                      vals.get("roadDestination")) if x)
        cam = _cam(name or vals.get("province"), vals.get("province"),
                   vals.get("roadName"), vals["latitude"], vals["longitude"],
                   f"https://etraffic.dgt.es/camarasEtraffic/{cid}.jpg",
                   "spain")
        if cam:
            out.append(cam)
    return out


# IBI 511 platforms (Ontario, Wisconsin, Pennsylvania) publish no
# bulk camera directory: their /Camera/GetUserCameras endpoint only
# returns a small default set (a handful of sites). The full network
# is the map layer's own icon index ({base}/map/mapIcons/Cameras:
# site id + coordinates for every site), and each site's name and
# snapshot path come from its tooltip page
# ({base}/tooltip/Cameras/{id}), the same pages the operators' maps
# load on marker click. Names and image paths change rarely, so
# tooltip details are memoised per site for the life of the process
# and only sites missing from the memo are fetched — steady state is
# one icon-index request per source per cycle, and a site whose
# tooltip fails simply joins the next cycle instead.
_ibi_details = {}
_ibi_lock = threading.Lock()


def _ibi_tooltip(base, site_id):
    page = _http_bytes(f"{base}/tooltip/Cameras/{site_id}?lang=en",
                       timeout=20).decode("utf-8", "replace")
    name = place = img = ""
    m = re.search(r'data-fs-title="([^"]+)"', page)
    if m:
        name = html.unescape(m.group(1)).strip()
    if not name:
        m = re.search(
            r"CameraTooltipDescriptionColumn.*?<strong>(.*?)</strong>",
            page, re.S)
        if m:
            name = html.unescape(
                re.sub(r"<[^>]+>", "", m.group(1))).strip()
    m = re.search(r'data-fs-extra="([^"]+)"', page)
    if m:
        place = html.unescape(m.group(1)).strip()
    for tag in re.findall(r"<img[^>]*>", page):
        if "cctvImage" not in tag:
            continue
        m = re.search(r'(?:data-lazy|src)="(/map/Cctv/\d+)"', tag)
        if m:
            img = base + m.group(1)
            break
    return name, place, img


def _src_ibi(base, code):
    import concurrent.futures

    doc = _http_json(f"{base}/map/mapIcons/Cameras", timeout=40)
    sites = []
    for item in doc.get("item2", []):
        loc = item.get("location") or []
        if len(loc) < 2:
            continue
        sites.append((str(item.get("itemId")), loc[0], loc[1]))

    def detail(site):
        try:
            name, place, img = _ibi_tooltip(base, site[0])
        except Exception:
            return
        if img:
            with _ibi_lock:
                _ibi_details[(base, site[0])] = (name, place, img)

    with _ibi_lock:
        missing = [s for s in sites
                   if (base, s[0]) not in _ibi_details]
    if missing:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            list(pool.map(detail, missing))
    with _ibi_lock:
        details = dict(_ibi_details)
        live = {(base, s[0]) for s in sites}
        for key in [k for k in _ibi_details
                    if k[0] == base and k not in live]:
            del _ibi_details[key]
    out = []
    for sid, la, lo in sites:
        got = details.get((base, sid))
        if not got:
            continue
        name, place, img = got
        cam = _cam(name, place, "", la, lo, img, code)
        if cam:
            out.append(cam)
    return out


def _src_ontario():
    return _src_ibi("https://511on.ca", "ontario")


def _src_wisconsin():
    return _src_ibi("https://511wi.gov", "wisconsin")


def _src_pennsylvania():
    return _src_ibi("https://www.511pa.com", "pennsylvania")


CAMERA_SOURCES = [
    ("caltrans", "Caltrans · California", _src_caltrans),
    ("minnesota", "Minnesota DOT", _src_minnesota),
    ("colorado", "Colorado DOT", _src_colorado),
    ("drivebc", "DriveBC · British Columbia", _src_drivebc),
    ("finland", "Fintraffic · Finland", _src_finland),
    ("tfl", "TfL · London", _src_tfl),
    ("hongkong", "Hong Kong Transport Department", _src_hongkong),
    ("spain", "DGT · Spain", _src_spain),
    ("nz", "NZTA · New Zealand", _src_nz),
    ("iceland", "Vegagerðin · Iceland", _src_iceland),
    ("singapore", "LTA · Singapore", _src_singapore),
    ("ontario", "Ontario 511", _src_ontario),
    ("wisconsin", "511WI · Wisconsin", _src_wisconsin),
    ("pennsylvania", "511PA · Pennsylvania", _src_pennsylvania),
]


def _fetch_cameras(force=False):
    now = time.time()
    with _cameras_lock:
        hit = _cameras_cache.get("all")
        if hit and not force and now - hit[0] < CAMERAS_CACHE_TTL:
            return hit[1]
    import concurrent.futures

    def run(fn):
        try:
            return fn() or []
        except Exception:
            return []

    cams, seen, sources = [], set(), []
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(CAMERA_SOURCES)) as pool:
        results = list(pool.map(lambda s: run(s[2]), CAMERA_SOURCES))
    for (code, label, _fn), batch in zip(CAMERA_SOURCES, results):
        kept = 0
        for cam in batch:
            if cam["img"] in seen:
                continue
            seen.add(cam["img"])
            cams.append(cam)
            kept += 1
        if kept:
            sources.append({"code": code, "label": label, "count": kept})
    if not cams:
        with _cameras_lock:
            hit = _cameras_cache.get("all")
            if hit:
                return hit[1]  # serve the last good list rather than none
        raise RuntimeError("no cameras fetched")
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(cams),
        "sources": sources,
        "cameras": cams,
    }
    with _cameras_lock:
        _cameras_cache["all"] = (time.time(), payload)
    return payload


def _cameras_warmer():
    """Keep the camera aggregate warm. A cold build sweeps every
    source (the 511 tooltip passes alone can take minutes), so a
    background thread rebuilds ahead of the cache TTL and no
    visitor request ever pays for a cold build."""
    while True:
        try:
            _fetch_cameras(force=True)
        except Exception:
            pass
        time.sleep(240)


def _start_cameras_warmer():
    threading.Thread(target=_cameras_warmer, daemon=True).start()


# --------------------------------------------- /camera-playlist.json
# The landing camera loop's playlist. The loop used to pick cameras
# by an even stride across the aggregate — a tour of random places.
# The playlist gives every frame a reason, in the Camera Agent's own
# order of meaning:
#   1. event frames — the nearest public camera to something the
#      world is reporting right now (USGS earthquakes, NHC active
#      storms, GDACS disaster alerts), under the board's fences:
#      at most 250 km, distance always stated, presence only (a
#      camera beside an event is never said to show it), and the
#      rotating-URL network (Singapore) never cited.
#   2. moment frames — cameras standing on the sunrise or sunset
#      line, or in morning peak hour, by local solar time.
#   3. presence frames — the network itself, counted.
# Every frame carries its `reason`; the loop prints it as the
# caption. Built from the same aggregate as /cameras.json plus
# keyless public event feeds, each fail-soft; cached five minutes,
# last good playlist served on failure.
PLAYLIST_TTL = 300
PLAYLIST_MAX_KM = 250.0
PLAYLIST_MAX_FRAMES = 24
PLAYLIST_EXCLUDE_SOURCES = {"singapore"}
_playlist_cache = {}
_playlist_lock = threading.Lock()


def _hav_km(lat1, lon1, lat2, lon2):
    import math
    p = math.pi / 180.0
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p)
         * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 12742 * math.asin(min(1.0, math.sqrt(a)))


def _http_text(url, timeout=12):
    req = urllib.request.Request(
        url, headers={"User-Agent": "orbital-camera-playlist"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _age_str(ts, now):
    mins = max(0, int((now - ts) // 60))
    if mins < 2:
        return "just now"
    if mins < 60:
        return f"{mins} min ago"
    hrs = mins // 60
    return f"{hrs} h ago" if hrs < 48 else f"{hrs // 24} d ago"


def _playlist_events(now):
    """Current public events with coordinates, newest first.
    Each source fails soft: a dead feed simply contributes none."""
    events = []
    try:  # USGS — M4.5+ worldwide, past 24 h; cited only within 6 h
        doc = _http_json("https://earthquake.usgs.gov/earthquakes/"
                         "feed/v1.0/summary/4.5_day.geojson",
                         timeout=12)
        for f in doc.get("features", []):
            props = f.get("properties") or {}
            coords = (f.get("geometry") or {}).get("coordinates") or []
            if len(coords) < 2 or props.get("time") is None:
                continue
            ts = props["time"] / 1000.0
            if now - ts > 6 * 3600:
                continue
            mag = props.get("mag")
            label = (f"M{mag:.1f} earthquake — {props.get('place')}"
                     if isinstance(mag, (int, float))
                     else f"Earthquake — {props.get('place')}")
            events.append({"label": label, "lat": coords[1],
                           "lon": coords[0], "ts": ts, "rank": 0,
                           "tail": _age_str(ts, now)})
    except Exception:
        pass
    try:  # NHC — active tropical cyclones (current by construction)
        doc = _http_json("https://www.nhc.noaa.gov/CurrentStorms.json",
                         timeout=12)
        for s in doc.get("activeStorms", []):
            lat, lon = s.get("latitudeNumeric"), s.get("longitudeNumeric")
            if not isinstance(lat, (int, float)) \
                    or not isinstance(lon, (int, float)):
                continue
            events.append({"label": f"Active storm {s.get('name')} (NHC)",
                           "lat": lat, "lon": lon, "ts": now, "rank": 0,
                           "tail": "active now"})
    except Exception:
        pass
    try:  # GDACS — current disaster alerts (orange/red preferred)
        xml = _http_text("https://www.gdacs.org/xml/rss.xml")
        for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
            lat = re.search(
                r"<geo:lat[^>]*>([\-0-9.]+)</geo:lat>", item)
            lon = re.search(
                r"<geo:long[^>]*>([\-0-9.]+)</geo:long>", item)
            title = re.search(r"<title>(.*?)</title>", item, re.S)
            pub = re.search(r"<pubDate>(.*?)</pubDate>", item)
            if not (lat and lon and title):
                continue
            ts = now
            if pub:
                try:
                    ts = email.utils.parsedate_to_datetime(
                        pub.group(1).strip()).timestamp()
                except Exception:
                    pass
            if now - ts > 48 * 3600:
                continue
            label = html.unescape(title.group(1).strip())
            label = re.sub(r"\s*-\s*\d{1,2}\s+\w{3,9}\s+\d{4}\s*$",
                           "", label)
            level = re.search(r"alertlevel>([A-Za-z]+)<", item)
            lvl = level.group(1) if level else ""
            events.append({"label": f"GDACS alert — {label}",
                           "lat": float(lat.group(1)),
                           "lon": float(lon.group(1)), "ts": ts,
                           "rank": 1 if lvl in ("Orange", "Red") else 2,
                           "tail": (f"{lvl} alert · " if lvl
                                    else "alert · ")
                                   + _age_str(ts, now)})
    except Exception:
        pass
    # quakes and storms first, then orange/red alerts, then the
    # green notification tail — newest first inside each rank, so
    # routine notifications never crowd out a measured event
    events.sort(key=lambda e: (e["rank"], -e["ts"]))
    return events


def _nearest_camera(cams, lat, lon):
    best, best_km = None, PLAYLIST_MAX_KM
    for c in cams:
        km = _hav_km(lat, lon, c["la"], c["lo"])
        if km < best_km:
            best, best_km = c, km
    return best, best_km


def _local_solar_h(lon, now):
    return ((now / 3600.0) + lon / 15.0) % 24.0


def _build_playlist():
    payload = _fetch_cameras()
    now = time.time()
    cams = [c for c in payload.get("cameras", [])
            if c.get("img") and c.get("s") not in PLAYLIST_EXCLUDE_SOURCES
            and isinstance(c.get("la"), (int, float))
            and isinstance(c.get("lo"), (int, float))]
    frames, used = [], set()

    def take(cam, kind, reason):
        if cam is None or cam["img"] in used \
                or len(frames) >= PLAYLIST_MAX_FRAMES:
            return
        used.add(cam["img"])
        frames.append({"n": cam.get("n"), "p": cam.get("p"),
                       "s": cam.get("s"), "img": cam["img"],
                       "la": cam["la"], "lo": cam["lo"],
                       "kind": kind, "reason": reason})

    for ev in _playlist_events(now):
        cam, km = _nearest_camera(cams, ev["lat"], ev["lon"])
        dist = f"{km:.0f}" if km >= 0.5 else "<1"
        take(cam, "event",
             f"Nearest public camera to the {ev['label']} — "
             f"camera {dist} km away · {ev['tail']}")

    def moment(lo_h, hi_h, pick, reason_fn):
        pool = [c for c in cams
                if lo_h <= _local_solar_h(c["lo"], now) < hi_h
                and c["img"] not in used]
        pool.sort(key=lambda c: c["la"])
        for i in range(pick):
            if not pool:
                break
            cam = pool[int((i + 0.5) * len(pool) / pick)]
            lst = _local_solar_h(cam["lo"], now)
            take(cam, "moment", reason_fn(lst))

    moment(5.2, 6.8, 2, lambda h: f"On the sunrise line — about "
                                  f"{int(h):02d}:{int((h % 1) * 60):02d} "
                                  f"local solar time")
    moment(17.2, 18.8, 2, lambda h: f"Evening — about "
                                    f"{int(h):02d}:{int((h % 1) * 60):02d} "
                                    f"local solar time")
    moment(7.4, 8.6, 2, lambda h: f"Morning peak hour — about "
                                  f"{int(h):02d}:{int((h % 1) * 60):02d} "
                                  f"local solar time")

    total = payload.get("count", len(cams))
    nets = len(payload.get("sources") or [])
    stride = max(1, len(cams) // 3)
    for i in range(0, len(cams), stride):
        take(cams[i], "presence",
             f"One of {total:,} public cameras reporting now "
             f"across {nets} networks")
        if len(frames) >= 6:
            break

    return {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(now)),
            "cameras_reporting": total, "networks": nets,
            "frames": frames}


def _get_playlist():
    now = time.time()
    with _playlist_lock:
        hit = _playlist_cache.get("pl")
        if hit and now - hit[0] < PLAYLIST_TTL:
            return hit[1]
    try:
        built = _build_playlist()
    except Exception:
        with _playlist_lock:
            hit = _playlist_cache.get("pl")
        if hit:
            return hit[1]  # last good playlist rather than none
        raise
    with _playlist_lock:
        _playlist_cache["pl"] = (now, built)
    return built

# ---------------------------------------------------- /incidents
# The Incident Register's own page, rendered from the public record
# repo's published companions (register.json, index.json,
# ai-layer.json) so the page can never drift from the register it
# presents. Cached ten minutes; last good render served on failure.
# Record-only, as the register is: attributed reports, the three
# dates kept separate, no warnings, no findings of our own.
REGISTER_RAW = ARCHIVE_RAW + "/incident-register"
_incidents_cache = {}
_incidents_lock = threading.Lock()
INCIDENTS_TTL = 600


def _register_companions():
    now = time.time()
    with _incidents_lock:
        hit = _incidents_cache.get("data")
        if hit and now - hit[0] < INCIDENTS_TTL:
            return hit[1]
    try:
        data = {
            "register": _http_json(REGISTER_RAW + "/register.json",
                                   timeout=15),
            "index": _http_json(REGISTER_RAW + "/index.json",
                                timeout=15),
            "markers": _http_json(REGISTER_RAW + "/ai-layer.json",
                                  timeout=15),
        }
    except Exception:
        with _incidents_lock:
            hit = _incidents_cache.get("data")
        if hit:
            return hit[1]
        raise
    with _incidents_lock:
        _incidents_cache["data"] = (now, data)
    return data


def _esc(x):
    return html.escape(str(x if x is not None else ""))


def _render_incidents():
    data = _register_companions()
    reg, idx = data["register"], data["index"]
    markers = data["markers"]
    lags = idx.get("disclosure_lags_days", {})
    cov = idx.get("registry_coverage", {})

    dev_rows = []
    for name, dev in (idx.get("developers") or {}).items():
        dev_rows.append(
            f"<tr><td>{_esc(name)}</td><td>{len(dev.get('entries', []))}"
            f"</td><td>{_esc(', '.join(str(x) for x in dev.get('lags_days', [])))}"
            f"</td><td>{_esc(dev.get('lag_median_days'))}</td>"
            f"<td>{_esc(dev.get('lag_max_days'))}</td></tr>")

    entry_html = []
    for e in reg.get("entries", []):
        parts = [f'<section class="entry" id="{_esc(e["id"])}">',
                 f"<h3>{_esc(e['id'])} — "
                 f"{_esc(e.get('developer_as_named_by_source') if e.get('kind') == 'incident' else 'Founding context')}</h3>"]
        if e.get("kind") == "incident":
            parts.append(f"<p><strong>System, as named by the source:</strong> "
                         f"{_esc(e.get('system_as_named_by_source'))}<br>"
                         f"<strong>Criteria met:</strong> "
                         f"{_esc(', '.join(e.get('criteria_met') or []))}</p>")
        for d in e.get("incident_dates_as_dated_by_source") or []:
            parts.append(f"<p><strong>Incident, as dated by the source "
                         f"({_esc(d.get('date'))}):</strong> {_esc(d.get('what'))}</p>")
        for d in e.get("report_dates") or []:
            parts.append(f"<p><strong>Reported ({_esc(d.get('date'))}):</strong> "
                         f"{_esc(d.get('what'))}</p>")
        lag = e.get("disclosure_lag_days")
        if isinstance(lag, dict):
            lag = [lag]
        for item in lag or []:
            parts.append(f"<p><strong>Disclosure lag: {_esc(item.get('days'))} "
                         f"days</strong> — {_esc(item.get('case'))}.</p>")
        for rname, r in (e.get("registries") or {}).items():
            label = "AIID" if rname == "aiid" else "OECD AIM"
            parts.append(f"<p><strong>{label}:</strong> {_esc(r.get('status'))} — "
                         f"{_esc(r.get('as_listed'))}</p>")
        for rev in e.get("source_revisions") or []:
            parts.append(f"<p><strong>Source revised ({_esc(rev.get('date'))}):"
                         f"</strong> {_esc(rev.get('what'))}</p>")
        for fw_name, fw in (e.get("frameworks") or {}).items():
            parts.append(f"<p><strong>Framework mapping — "
                         f"{_esc(fw_name.replace('_', ' '))}:</strong> {_esc(fw)}</p>")
        parts.append(f"<p class='src'><strong>Sources:</strong> "
                     f"{_esc(' '.join(e.get('sources') or []))}<br>"
                     f"Recorded {_esc(e.get('recorded_at'))} · SHA-256 "
                     f"<code>{_esc((e.get('sha256') or '')[:16])}…</code></p>")
        parts.append("</section>")
        entry_html.append("\n".join(parts))

    inst_rows = []
    for inst in idx.get("institutions_indexed") or []:
        inst_rows.append(f"<li>{_esc(inst.get('institution'))} — "
                         f"{_esc(inst.get('place'))} ({_esc(inst.get('entry'))})</li>")
    ver_rows = []
    for v in reg.get("version_history") or []:
        ver_rows.append(f"<li><strong>Version {_esc(v.get('version'))} — "
                        f"{_esc(v.get('date'))}:</strong> {_esc(v.get('note'))}</li>")
    crit_rows = []
    for k in sorted(reg.get("criteria") or {}):
        crit_rows.append(f"<li><strong>{_esc(k)}.</strong> "
                         f"{_esc(reg['criteria'][k])}</li>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Incident Register — Orbital Network</title>
<meta name="description" content="A public register of serious AI incidents, kept inside Orbital Network's permanent record — recording what was published, when, and how long it took to reach the public.">
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: Georgia, 'Times New Roman', serif;
         color: #1a2332; background: #f7f5f0; line-height: 1.55; }}
  main {{ max-width: 820px; margin: 0 auto; padding: 2.5rem 1.25rem 3rem; }}
  h1 {{ font-size: 2rem; margin: 0 0 .25rem; }}
  h2 {{ font-size: 1.25rem; margin: 2.25rem 0 .75rem;
        border-bottom: 2px solid #1a2332; padding-bottom: .3rem; }}
  h3 {{ font-size: 1.05rem; margin: 0 0 .5rem; }}
  .tag {{ font-style: italic; color: #44506a; margin: 0 0 1.5rem; }}
  .entry {{ background: #fff; border: 1px solid #ddd6c8; border-radius: 8px;
            padding: 1rem 1.25rem; margin: 0 0 1rem; }}
  .entry p {{ margin: .45rem 0; }}
  .src {{ font-size: .88rem; color: #44506a; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; }}
  th, td {{ border: 1px solid #ddd6c8; padding: .45rem .6rem;
            text-align: left; font-size: .95rem; }}
  th {{ background: #efece4; }}
  a {{ color: #20509e; }}
  footer {{ margin-top: 2.5rem; font-size: .88rem; color: #44506a; }}
  code {{ font-size: .85em; }}
</style>
</head>
<body>
<main>
<h1>The Incident Register</h1>
<p class="tag">Live broadcast of Planet Earth. Permanent record of its measurements.</p>
<p>A public register of serious AI incidents, kept inside Orbital Network's
permanent record. The register <strong>opened on {_esc(reg.get('opened'))}</strong>;
its <strong>coverage begins {_esc(reg.get('coverage_begins'))}</strong>, the first day of
the permanent record. Every entry carries three true dates, never merged: the
date the source dates the incident, the date the report was published, and the
date Orbital recorded it.</p>
<p>Orbital Network operates no satellites or ground stations of its own. It
republishes, links, and permanently records the official reports of the systems
that do. This register likewise senses nothing: it records published reports of
AI incidents exactly as named sources published them, and measures the reporting
system itself — how long each incident took to reach the public, and when the
standing registries listed it. It makes no finding of its own and issues no
warnings or forecasts.</p>

<h2>The measurements</h2>
<table>
<tr><th>Developer</th><th>Entries</th><th>Measured disclosure lags (days)</th><th>Median</th><th>Longest</th></tr>
{chr(10).join(dev_rows)}
</table>
<p>Register-wide: {_esc(len(lags.get('all_measured') or []))} measured lags —
median {_esc(lags.get('median'))} days, longest {_esc(lags.get('max'))} days,
shortest {_esc(lags.get('min'))} days. Registry coverage:
AIID lists {_esc((cov.get('aiid') or {}).get('listed'))} of
{_esc(idx.get('incident_entries'))} incident entries;
OECD AIM lists {_esc((cov.get('oecd_aim') or {}).get('listed'))} of
{_esc(idx.get('incident_entries'))} (all checked against the live registries).</p>

<h2>Entries</h2>
{chr(10).join(entry_html)}

<h2>Institutions named by the sources</h2>
<p>A marker stands only at the published seat of an institution the incident
report itself names as acted upon — never where a system was located. Where a
source names no institution, there is no marker.</p>
<ul>
{chr(10).join(inst_rows)}
</ul>

<h2>What counts as serious</h2>
<ul>
{chr(10).join(crit_rows)}
</ul>

<h2>Versions</h2>
<ul>
{chr(10).join(ver_rows)}
</ul>
<p>Corrections arrive as new versions only. The register's machine-readable
companions — entries, lag index, markers, and source snapshots — are published
in the permanent record.</p>

<footer>
<p>Register: <a href="https://github.com/mel-gregory/orbital-record/tree/main/incident-register">github.com/mel-gregory/orbital-record — incident-register/</a> ·
Paper: <a href="https://doi.org/10.5281/zenodo.23886994">doi.org/10.5281/zenodo.23886994</a> ·
Daily register posts: <a href="https://incidents.godsky.net">incidents.godsky.net</a> ·
<a href="https://godsky.net">Orbital Network</a></p>
<p>Entries are attributed reports as published by the named sources. See the
AI Incident Database (incidentdatabase.ai) and the OECD AI Incidents and Hazards
Monitor for the standing general registries this register measures itself against.</p>
</footer>
</main>
</body>
</html>"""


def _safe(fn, arg):
    try:
        return fn(arg)
    except Exception:
        return None


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

    # -- /digest (dynamic; every other path stays static) ------------
    def _digest_day(self):
        """Archived day for this request path, or False if the path is
        not a digest path. None means the newest archived day."""
        try:
            raw = urllib.parse.urlsplit(self.path).path
        except Exception:
            return False
        if raw in ("/digest", "/digest/"):
            return None
        m = re.fullmatch(r"/digest/(\d{4}-\d{2}-\d{2})", raw)
        if m:
            return m.group(1)
        return False

    def _serve_digest(self, head_only=False):
        day = self._digest_day()
        if day is False:
            return False
        try:
            page = _render_digest(day)
        except Exception:
            self.send_error(http.HTTPStatus.BAD_GATEWAY,
                            "Digest data unavailable")
            return True
        if page is None:
            self.send_error(http.HTTPStatus.NOT_FOUND, "Day not archived")
            return True
        body = page.encode("utf-8")
        encoding = None
        if "gzip" in (self.headers.get("Accept-Encoding") or ""):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
                gz.write(body)
            body = buf.getvalue()
            encoding = "gzip"
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if encoding:
            self.send_header("Content-Encoding", encoding)
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Cache-Control", SHORT_CACHE)
        self.end_headers()
        if not head_only:
            self.wfile.write(body)
        return True

    # -- /cameras.json (dynamic; every other path stays static) ------
    def _serve_cameras(self, head_only=False):
        try:
            raw = urllib.parse.urlsplit(self.path).path
        except Exception:
            return False
        if raw != "/cameras.json":
            return False
        try:
            payload = _fetch_cameras()
        except Exception:
            self.send_error(http.HTTPStatus.BAD_GATEWAY,
                            "Camera data unavailable")
            return True
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        sample = qs.get("sample", [None])[0]
        if sample:
            try:
                n = max(1, min(int(sample), 2000))
            except ValueError:
                n = None
            if n and len(payload["cameras"]) > n:
                cams = payload["cameras"]
                stride = len(cams) / n
                picked = [cams[int(i * stride)] for i in range(n)]
                payload = {**payload, "total": payload["count"],
                           "count": len(picked), "cameras": picked}
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        encoding = None
        if "gzip" in (self.headers.get("Accept-Encoding") or ""):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
                gz.write(body)
            body = buf.getvalue()
            encoding = "gzip"
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if encoding:
            self.send_header("Content-Encoding", encoding)
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Cache-Control", SHORT_CACHE)
        self.end_headers()
        if not head_only:
            self.wfile.write(body)
        return True

    # -- /camera-playlist.json (dynamic) ------------------------------
    def _serve_playlist(self, head_only=False):
        try:
            raw = urllib.parse.urlsplit(self.path).path
        except Exception:
            return False
        if raw != "/camera-playlist.json":
            return False
        try:
            payload = _get_playlist()
        except Exception:
            self.send_error(http.HTTPStatus.BAD_GATEWAY,
                            "Playlist data unavailable")
            return True
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        encoding = None
        if "gzip" in (self.headers.get("Accept-Encoding") or ""):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
                gz.write(body)
            body = buf.getvalue()
            encoding = "gzip"
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if encoding:
            self.send_header("Content-Encoding", encoding)
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Cache-Control", SHORT_CACHE)
        self.end_headers()
        if not head_only:
            self.wfile.write(body)
        return True

    # -- /incidents (dynamic) ------------------------------------------
    def _serve_incidents(self, head_only=False):
        try:
            raw = urllib.parse.urlsplit(self.path).path
        except Exception:
            return False
        if raw not in ("/incidents", "/incidents/"):
            return False
        try:
            page = _render_incidents()
        except Exception:
            self.send_error(http.HTTPStatus.BAD_GATEWAY,
                            "Register data unavailable")
            return True
        body = page.encode("utf-8")
        encoding = None
        if "gzip" in (self.headers.get("Accept-Encoding") or ""):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
                gz.write(body)
            body = buf.getvalue()
            encoding = "gzip"
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if encoding:
            self.send_header("Content-Encoding", encoding)
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Cache-Control", SHORT_CACHE)
        self.end_headers()
        if not head_only:
            self.wfile.write(body)
        return True

    def do_GET(self):
        if self._serve_incidents():
            return
        if self._serve_playlist():
            return
        if self._serve_cameras():
            return
        if self._serve_digest():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._serve_incidents(head_only=True):
            return
        if self._serve_playlist(head_only=True):
            return
        if self._serve_cameras(head_only=True):
            return
        if self._serve_digest(head_only=True):
            return
        super().do_HEAD()

    # -- host routing -------------------------------------------------
    def _host(self):
        return (self.headers.get("Host") or "").split(":")[0].strip().lower()

    def _globe_relpath(self, raw_path):
        """Map a godsky.net request path to a file under globe/, or None."""
        if raw_path in ("", "/", "/index.html"):
            return os.path.join("globe", "index.html")
        if raw_path == "/llms.txt":
            return os.path.join("globe", "llms.txt")
        if raw_path.startswith("/assets/"):
            rel = os.path.normpath(raw_path.lstrip("/"))
            if rel.startswith("assets" + os.sep) and ".." not in rel.split(os.sep):
                return os.path.join("globe", rel)
        return None

    def translate_path(self, path):
        if self._host() in GLOBE_HOSTS:
            try:
                raw = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
            except Exception:
                raw = path
            rel = self._globe_relpath(raw)
            if rel is not None:
                full = os.path.join(ROOT, rel)
                if os.path.isfile(full):
                    return full
        return super().translate_path(path)

    # -- response -----------------------------------------------------
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith("/"):
                # Redirect to the trailing-slash URL, as the stdlib does.
                self.send_response(http.HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + "/", parts[3], parts[4])
                self.send_header("Location", urllib.parse.urlunsplit(new_parts))
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            for index in ("index.html", "index.htm"):
                candidate = os.path.join(path, index)
                if os.path.exists(candidate):
                    path = candidate
                    break
            else:
                return self.list_directory(path)
        if not os.path.isfile(path):
            self.send_error(http.HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            mtime = os.path.getmtime(path)
        except OSError:
            self.send_error(http.HTTPStatus.NOT_FOUND, "File not found")
            return None

        ims = self.headers.get("If-Modified-Since")
        if ims:
            try:
                ims_ts = email.utils.parsedate_to_datetime(ims).timestamp()
            except Exception:
                ims_ts = None
            if ims_ts is not None and ims_ts >= int(mtime):
                self.send_response(http.HTTPStatus.NOT_MODIFIED)
                self.end_headers()
                return None

        try:
            with open(path, "rb") as fh:
                body = fh.read()
        except OSError:
            self.send_error(http.HTTPStatus.NOT_FOUND, "File not found")
            return None

        ext = os.path.splitext(path)[1].lower()
        encoding = None
        if ext in GZIP_EXTS and "gzip" in (self.headers.get("Accept-Encoding") or ""):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
                gz.write(body)
            body = buf.getvalue()
            encoding = "gzip"

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(len(body)))
        if encoding:
            self.send_header("Content-Encoding", encoding)
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Last-Modified", self.date_time_string(mtime))
        self.send_header(
            "Cache-Control",
            SHORT_CACHE if ext in SHORT_CACHE_EXTS else STATIC_CACHE,
        )
        self.end_headers()
        return io.BytesIO(body)


if __name__ == "__main__":
    import functools

    handler = functools.partial(Handler, directory=ROOT)
    _start_cameras_warmer()
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    httpd.serve_forever()
