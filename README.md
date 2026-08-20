# status.crii.me — System Status

A professional status page for the crii.me ecosystem.  
Shows live status, uptime bars, and incident history.

## How it works

The page loads `status.json` from this repo via GitHub's raw content URL.
Edit `status.json`, commit, push — the status page updates automatically.

## Updating status

### Change a service status

Edit `status.json` → `services` array:

```json
{
  "name": "Website",
  "slug": "website",
  "status": "degraded",
  "description": "Main website and portfolio"
}
```

Valid statuses: `operational`, `degraded`, `outage`, `maintenance`

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

### Update uptime bars

The `uptime` object contains 24-element arrays (one per hour, 24h ago → now):
- `1` = operational
- `0` = down
- `0.5` = degraded
- `2` = maintenance

Example: `[1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]` = 2h downtime

### Quick commands

```bash
# Edit and push
vim status.json
git add status.json
git commit -m "Update: website degraded"
git push
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
├── index.html    ← Status page (fetches status.json)
├── status.json   ← Edit this to update status
├── CNAME         ← status.crii.me
└── .nojekyll     ← Static serving
```

The page is fully client-side — it fetches `status.json` from GitHub's raw
content API on load. No server needed.
