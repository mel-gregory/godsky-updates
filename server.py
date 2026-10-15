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

    def do_GET(self):
        if self._serve_digest():
            return
        super().do_GET()

    def do_HEAD(self):
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
