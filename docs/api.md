# API Reference

## `dimjournal.download`

```python
def download(
    archive_folder: Path | str | None = None,
    user_id: str | None = None,
    limit: int | None = None,
) -> None
```

Main entry point. Launches a Chrome browser, logs in to Midjourney, crawls job history, and downloads upscaled images.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `archive_folder` | `Path \| str \| None` | `None` | Destination folder. Defaults to `~/Pictures/midjourney/dimjournal` (macOS/Linux) or `~/My Pictures/midjourney/dimjournal` (Windows). |
| `user_id` | `str \| None` | `None` | Optional Midjourney user ID to filter results. |
| `limit` | `int \| None` | `None` | Maximum number of API pages to crawl. `None` fetches all history. |

---

## `dimjournal.dimjournal.MidjourneyAPI`

Manages browser session, authentication, and API requests.

### Key methods

- `log_in()` — Navigates to Midjourney home and waits for login
- `load_cookies()` / `save_cookies()` — Persist session to `cookies.pkl`
- `get_user_info()` — Fetches and saves `user.json`
- `request_recent_jobs(from_date, page, job_type)` — Returns a list of job dicts

---

## `dimjournal.dimjournal.MidjourneyJobCrawler`

Paginates through the API and maintains a local JSON archive of job metadata.

### Key methods

- `load_archive_data()` — Reads the JSON archive; returns the list
- `update_archive_data(job_listing)` — Appends new jobs, persists to disk
- `crawl(limit, from_date)` — Runs the full crawl loop

---

## `dimjournal.dimjournal.MidjourneyDownloader`

Downloads images for jobs in `jobs_upscale.json`.

### Key methods

- `read_jobs()` — Loads job list from disk; returns `[]` if file absent
- `generate_image_path(job_data)` — Returns the `Path` for an image file
- `create_folders(dt_obj)` — Creates `Year/Month/` directory structure
- `fetch_and_write_image(url, path, info)` — Downloads and writes one image
- `download_missing()` — Iterates all jobs and downloads any not yet archived
