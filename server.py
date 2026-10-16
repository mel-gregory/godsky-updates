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


def _fetch_cameras():
    now = time.time()
    with _cameras_lock:
        hit = _cameras_cache.get("all")
        if hit and now - hit[0] < CAMERAS_CACHE_TTL:
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
        _cameras_cache["all"] = (now, payload)
    return payload


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

    def do_GET(self):
        if self._serve_cameras():
            return
        if self._serve_digest():
            return
        super().do_GET()

    def do_HEAD(self):
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
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    httpd.serve_forever()
