# Athena PMO Data Layer

## Purpose

Athena HTML files should be treated as views, not project data sources. Shared project data lives in:

```text
docs/data/athena_project_data.json
```

The first shared fields are module-level PMO fields:

- `priority`
- `owner`
- `status`
- `isMvp`
- `commercialization`
- `targetDate`
- `risk`
- `next`
- `decision`
- `requirements`

## Local Server

Recommended daily use: double-click this file in the Athena project folder:

```text
Start_Athena_PMO.bat
```

It starts the local PMO server and opens `Athena.html` automatically.

Manual start, if needed:

Run the local PMO server from the project root:

```powershell
python tools/athena_pmo_server.py --root docs --port 8787
```

Then open:

```text
http://127.0.0.1:8787/Athena.html
http://127.0.0.1:8787/Athena_Project_Progress.html
```

## API

```text
GET /api/athena-project-data
PUT /api/athena-project-data
GET /api/health
```

When `Athena_Project_Progress.html` is opened through this server, Save writes to `docs/data/athena_project_data.json` and creates timestamped backups under:

```text
docs/data/backups/
```

When the HTML file is opened directly from the filesystem, it falls back to browser local cache.

## Current Linked Views

- `Athena_Project_Progress.html` reads and saves shared project data when served through Athena PMO Server.
- `Athena.html` reads module priorities from shared project data when served through Athena PMO Server.

Next step: convert additional repeated fields in `Athena.html` and department/topic HTML files to shared-data bindings.
