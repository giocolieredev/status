#!/usr/bin/env python3
"""
Reconcile GitHub issues with service statuses from status.json.

Rules:
  - A service with status "outage" or "degraded" must have an open
    issue labelled `status-<slug>` (created if missing).
  - A service back to "operational" closes any open issue for it,
    with a comment noting it recovered.

Uses the `gh` CLI with GITHUB_TOKEN (set on GitHub Actions runners).
"""
import json
import subprocess
import sys

REPO = "giocolieredev/status"
LABEL_PREFIX = "status-"
COLOR = "B60205"

DOWN_STATUSES = ("outage", "degraded")


def gh(*args):
    """Run a gh command; return CompletedProcess."""
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def gh_json(*args):
    """Run gh returning JSON (list)."""
    r = gh(*args)
    if r.returncode != 0:
        print(f"gh {' '.join(args)} failed: {r.stderr.strip()}", file=sys.stderr)
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return []


def ensure_label(label, description):
    """Create the label if it doesn't exist (ignore if it does)."""
    gh("label", "create", label, "--repo", REPO,
       "--color", COLOR, "--description", description)


def main():
    with open("status.json", encoding="utf-8") as f:
        data = json.load(f)

    services = [s for s in data.get("services", []) if s.get("url")]

    for service in services:
        slug = service["slug"]
        status = service.get("status", "operational")
        label = LABEL_PREFIX + slug
        checked = service.get("lastChecked", "unknown")

        ensure_label(label, f"{service['name']} status (auto-managed)")

        open_issues = gh_json(
            "issue", "list", "--repo", REPO,
            "--label", label, "--state", "open",
            "--json", "number,title",
        )

        if status in DOWN_STATUSES:
            # Service is down → make sure an open issue exists
            if not open_issues:
                title = f"[{status.upper()}] {service['name']} is {status}"
                body = (
                    f"**Service:** {service['name']}\n"
                    f"**URL:** {service['url']}\n"
                    f"**Status:** `{status}`\n"
                    f"**Checked at:** {checked}\n\n"
                    f"_Automatically opened by the status monitor._\n"
                    f"_Will be closed automatically when the service recovers._"
                )
                r = gh("issue", "create", "--repo", REPO,
                       "--title", title, "--body", body, "--label", label)
                if r.returncode == 0:
                    print(f"Opened issue for {slug} ({status})")
                else:
                    print(f"Failed to open issue for {slug}: {r.stderr.strip()}", file=sys.stderr)
            else:
                print(f"Issue already open for {slug} ({status})")
        else:
            # Service is back → close any open issues
            for issue in open_issues:
                number = issue["number"]
                gh("issue", "close", str(number), "--repo", REPO,
                   "--comment",
                   f"✅ **{service['name']} is back online.**\n"
                   f"Last checked: {checked}. Closing automatically.")
                print(f"Closed issue #{number} for {slug}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
