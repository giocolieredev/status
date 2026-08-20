#!/usr/bin/env python3
"""
Automatic health checker for crii.me services.
Runs as a GitHub Action (see .github/workflows/monitor.yml).
Checks every service's URL over HTTPS and updates status.json:
  - per-service status (operational / degraded / outage)
  - uptime history (last 24 hours, one sample per run)
  - overall status + lastUpdated
"""
import json
import ssl
import sys
import time
import urllib.request
import urllib.error

STATUS_FILE = "status.json"
TIMEOUT = 15  # seconds

STATUS_BY_VALUE = {1: "operational", 0.5: "degraded", 0: "outage"}


def check_url(url):
    """Return 1 (up), 0.5 (degraded/4xx), 0 (down/error)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        code = resp.getcode()
    except urllib.error.HTTPError as e:
        code = e.code
    except (urllib.error.URLError, ssl.SSLError, ConnectionError, TimeoutError, OSError):
        return 0

    if code is None:
        return 0
    if 200 <= code < 400:
        return 1
    if 400 <= code < 500:
        return 0.5  # reachable but broken (e.g. 404 on a service page)
    return 0  # 5xx = outage


def main():
    with open(STATUS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    uptime = data.setdefault("uptime", {})
    services = data.setdefault("services", [])

    checked = 0
    for service in services:
        slug = service.get("slug")
        url = service.get("url")
        if not slug or not url:
            continue  # skip services without a URL (e.g. "API — coming soon")

        value = check_url(url)
        status = STATUS_BY_VALUE[value]

        # Update uptime history (keep last 24 samples)
        hours = uptime.setdefault(slug, [])
        hours.append(value)
        if len(hours) > 24:
            del hours[:-24]

        service["status"] = status
        service["lastChecked"] = now
        checked += 1

    # Overall status: worst of the monitored services
    statuses = [s.get("status") for s in services if s.get("url")]
    if "outage" in statuses:
        overall = "outage"
    elif "degraded" in statuses:
        overall = "degraded"
    elif statuses:
        overall = "operational"
    else:
        overall = data.get("status", "operational")

    data["status"] = overall
    data["lastUpdated"] = now

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[{now}] {checked} services checked — overall: {overall}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
