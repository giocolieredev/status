# status.crii.me — System Status

A professional status page for the crii.me ecosystem.  
**Fully automatic** — a GitHub Action checks every service every 10 minutes
and updates `status.json` for you. No manual editing needed.

## How it works

1. **GitHub Action** (`.github/workflows/monitor.yml`) runs every 10 minutes
   on a free GitHub-hosted runner (free for public repos).
2. **`monitor.py`** checks each service's URL over HTTPS (HEAD request,
   15s timeout) and writes the results to `status.json`:
   - `2xx/3xx` → operational
   - `4xx` → degraded
   - `5xx` / timeout / connection error → outage
   - Uptime history keeps the last 24 samples
3. The action commits and pushes the updated `status.json`.
4. The status page (client-side) loads `status.json` and refreshes every 5 min.

## Manual override

You can still edit `status.json` by hand if you want to add incidents or
override a status — the next automated run will only change what the checks
say, so incidents you add manually stay.

### Report an incident

Add to the `incidents` array:

```json
{
  "id": "inc-2026-08-21-001",
  "title": "Website returning 502 errors",
  "status": "investigating",
  "severity": "major",
  "created": "2026-08-21T10:00:00Z",
  "resolved": null,
  "services": ["website"],
  "updates": [
    {
      "time": "2026-08-21T10:00:00Z",
      "status": "investigating",
      "message": "We are investigating reports of 502 errors."
    }
  ]
}
```

Incident statuses: `investigating`, `identified`, `monitoring`, `resolved`, `postmortem`

## Running checks manually

From the repo's **Actions** tab → *Monitor services* → **Run workflow**.

Or locally:

```bash
python3 monitor.py   # or: py monitor.py on Windows
```

## Auto-refresh

The page auto-refreshes every 5 minutes. No build step needed.

## DNS

```
Type:  CNAME
Name:  status
Value: giocolieredev.github.io
```

## Architecture

```
status/
├── index.html              ← Status page (fetches status.json)
├── status.json             ← Updated automatically by the Action
├── monitor.py              ← Health-check script
├── .github/workflows/
│   └── monitor.yml         ← Runs every 10 min, commits results
├── CNAME                   ← status.crii.me
└── .nojekyll               ← Static serving
```

The page is fully client-side — no server needed. All monitoring runs on
GitHub's free public-repo Actions minutes.
