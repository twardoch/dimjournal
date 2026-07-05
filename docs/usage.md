# Usage

## Command-line interface

```bash
# Use default archive folder (~/Pictures/midjourney/dimjournal)
dimjournal

# Specify a custom archive folder
dimjournal --archive_folder /path/to/archive

# Limit to N pages of job history
dimjournal --limit 10
```

## Python API

```python
from pathlib import Path
from dimjournal import download

download(
    archive_folder=Path("~/Pictures/midjourney/dimjournal").expanduser(),
    limit=None,   # None = fetch all history
)
```

## Archive layout

```
archive_folder/
├── user.json             # Midjourney user metadata
├── jobs_upscale.json     # Upscale job metadata list
├── cookies.pkl           # Saved session cookies
└── 2024/
    └── 03/
        └── 20240315-1423_a-beautiful-landscape_ab12.png
```

## First run

The first run opens a Chrome browser window. Log in to your Midjourney account manually. After login, cookies are saved for future runs.
