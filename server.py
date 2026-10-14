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
import http
import http.server
import io
import os
import urllib.parse

PORT = int(os.environ.get("PORT", "8080"))
ROOT = os.path.dirname(os.path.abspath(__file__))

GLOBE_HOSTS = {"godsky.net", "www.godsky.net"}
GZIP_EXTS = {".html", ".htm", ".css", ".js", ".json", ".txt", ".svg", ".xml", ".md"}
SHORT_CACHE_EXTS = {".html", ".htm", ".json"}
SHORT_CACHE = "public, max-age=300"
STATIC_CACHE = "public, max-age=3600"


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

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
