# Dimjournal: Your Automated Midjourney Backup Tool

Dimjournal is a powerful Python tool designed to create and maintain a local backup of your Midjourney image generations. It automates the process of downloading your job history (metadata) and upscaled images, organizing them neatly on your computer.

<p align="center"><img src="docs/assets/icon.png" alt="Dimjournal: your Midjourney, on your hard drive" width="240"></p>

## Part 1: User-Facing Documentation

### What is Dimjournal?

Dimjournal is a command-line and programmatic tool that interacts with the Midjourney web interface to back up your creative work. It downloads:

*   **Job Metadata:** Information about your prompts, enqueue times, job IDs, etc.
*   **Upscaled Images:** The actual PNG image files of your upscaled generations.

### Who is it For?

This tool is for any Midjourney user who wants:

*   A reliable local backup of their image archive.
*   To prevent data loss in case of issues with the Midjourney service.
*   Offline access to their generated images and associated prompts.
*   An organized way to browse their Midjourney history locally.

### Why is it Useful?

*   **Automated Backups:** Set it up once, and run it periodically to keep your local archive up-to-date.
*   **Local & Private:** Your data is stored on your own machine.
*   **Organized Archive:** Images are saved in a clear `Year/Month/ImageFileName.png` structure.
*   **Metadata Embedding:** Key information like the prompt, author, and creation time is embedded directly into the PNG files for easy reference with compatible image viewers.
*   **Resumable Downloads:** Dimjournal intelligently skips already downloaded images and metadata, only fetching new or missing items.
*   **Session Management:** Saves and reuses login session cookies to minimize the need for manual logins.
*   **Detailed Logging:** Provides comprehensive logs for monitoring and troubleshooting.

### Disclaimer

**Important:** The terms of use of Midjourney may disallow or restrict automation or web scraping. Using this tool may be against Midjourney's Terms of Service. You use Dimjournal at your own risk. The developers of Dimjournal are not responsible for any consequences that may arise from using this software, including but not limited to account suspension or termination.

### Features

*   Automated download of Midjourney job history (metadata) and upscaled images.
*   Creation of an organized local archive (folder structure: `Year/Month/ImageFileName.png`).
*   Embedding of prompt, author, and other metadata directly into PNG image files.
*   Resumable operation: only downloads new or missing data on subsequent runs.
*   Secure local cookie management to persist login sessions.
*   Detailed logging for transparency and troubleshooting.
*   Command-line interface (CLI) and programmatic (Python library) usage.

### Prerequisites

*   **Python:** Version 3.10 or higher.
*   **Google Chrome:** Must be installed on your system, as `undetected_chromedriver` (a dependency) relies on it.

### Installation

You can install Dimjournal using pip.

**Stable Version (Recommended):**

```bash
pip install dimjournal
```

**Development Version (for the latest features and fixes):**

```bash
pip install git+https://github.com/twardoch/dimjournal.git
```
After installation, you should be able to run `dimjournal` from your terminal. If not, ensure your Python scripts directory is in your system's PATH, or use `python3 -m dimjournal`.

### Usage

#### Command Line Interface (CLI)

The first time you run Dimjournal, it will open a Chrome browser window. You will need to manually log in to your Midjourney account. After successful login, Dimjournal will save session cookies to expedite future logins.

**Basic Usage (defaults to `~/Pictures/midjourney/dimjournal` or `~/My Pictures/midjourney/dimjournal`):**

```bash
dimjournal
```

**Specify a Custom Archive Folder:**

```bash
dimjournal --archive_folder /path/to/your/custom_archive
```
or on Windows:
```bash
dimjournal --archive_folder C:\path\to\your\custom_archive
```

**Limit Number of Job Pages to Crawl:**
Useful for initial testing or if you only want to fetch the most recent items. Each page typically contains about 50 jobs.

```bash
dimjournal --limit 5
```
This will crawl the 5 most recent pages of your job history for both upscaled jobs and all jobs.

#### Programmatic Usage (Python)

You can integrate Dimjournal's download functionality into your own Python scripts.

```python
import logging
from pathlib import Path
from dimjournal import download

# It's good practice to configure logging to see Dimjournal's output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Specify the directory where you want to store the data.
# If None, it defaults to Pictures/midjourney/dimjournal or My Pictures/midjourney/dimjournal.
archive_folder_path = Path("./my_midjourney_backup")
# archive_folder_path = None # To use the default location

# Specify a limit for the number of job history pages to crawl (optional).
# Set to None or omit to crawl all available history.
crawl_limit = 10  # Example: Crawl 10 pages of recent jobs

try:
    print(f"Starting Dimjournal backup to: {archive_folder_path.resolve() if archive_folder_path else 'default location'}")
    download(archive_folder=archive_folder_path, limit=crawl_limit)
    print("Dimjournal process complete.")
except Exception as e:
    logging.error(f"An error occurred during the Dimjournal process: {e}", exc_info=True)
    print(f"An error occurred. Check logs for details.")

```

## Part 2: Technical Documentation

### How it Works (Technical Overview)

Dimjournal employs a series of steps to back up your Midjourney data:

1.  **Browser Automation:** It uses `undetected_chromedriver`, a specialized version of Selenium's ChromeDriver, to launch and control a Google Chrome browser. This allows it to mimic human interaction with the Midjourney website.
2.  **Login & Session Management:** Saves session cookies to `cookies.pkl`; reused on subsequent runs.
3.  **User Information:** Extracted from `<script id="__NEXT_DATA__">` on the account page; saved as `user.json`.
4.  **Job Crawling:** GETs `https://www.midjourney.com/api/app/recent-jobs/` (two passes: `upscale` + all); stored in `jobs_upscale.json` / `jobs.json`.
5.  **Image Download:** Browser navigates to each URL; JavaScript fetches as base64; decoded and written to disk.
6.  **File Layout:** `ARCHIVE/YYYY/MM/YYYYMMDD-HHMM_prompt-slug_jobIDprefix.ext`; PNG metadata embedded via `pymtpng`.


### Code Structure

```
src/dimjournal/
├── dimjournal.py   # Core logic: Constants, MidjourneyAPI, MidjourneyJobCrawler, MidjourneyDownloader, download()
├── __main__.py     # CLI entry point (python-fire)
└── __init__.py     # Package init; re-exports download()
tests/
└── test_dimjournal.py
```

### Contributing

1. Fork the repo and create a branch.
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Lint: `ruff check src tests` · Format: `ruff format src tests`
4. Test: `pytest`
5. Open a pull request with a clear description.

Code style: Python 3.10+, ruff-enforced, type hints required, `logging` for diagnostics.

### Changelog

See [CHANGELOG.md](./CHANGELOG.md).

### License

Apache 2.0 — see [LICENSE.txt](./LICENSE.txt).

### Authors

See [AUTHORS.md](./AUTHORS.md).
