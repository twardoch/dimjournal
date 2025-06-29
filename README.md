# Dimjournal: Your Automated Midjourney Backup Tool

Dimjournal is a powerful Python tool designed to create and maintain a local backup of your Midjourney image generations. It automates the process of downloading your job history (metadata) and upscaled images, organizing them neatly on your computer.

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
2.  **Login & Session Management:**
    *   On the first run, the user logs into Midjourney through the automated browser.
    *   Dimjournal then saves the session cookies (specifically `__Secure-next-auth.session-token`) to a local file (`cookies.pkl`) within the archive directory.
    *   Subsequent runs load these cookies, attempting to restore the session and bypass manual login.
3.  **User Information Fetching:**
    *   It navigates to the Midjourney account page (`https://www.midjourney.com/account/`).
    *   It extracts user data, including the crucial `user_id`, from a JSON object embedded in the page's HTML (within a `<script id="__NEXT_DATA__">` tag).
    *   This user information is saved to `user.json` in the archive directory.
4.  **API Interaction & Job Crawling:**
    *   Dimjournal makes GET requests to Midjourney's internal API endpoint (`https://www.midjourney.com/api/app/recent-jobs/`) to fetch job listings.
    *   It constructs query parameters for this API call, including `userId`, `jobType` (e.g., 'upscale'), `page`, `amount`, `orderBy`, `jobStatus`, etc.
    *   The tool performs two main crawling passes:
        *   One for `'upscale'` jobs (to get images).
        *   One for all job types (to get a more complete metadata archive).
    *   Fetched job data is stored and updated in `jobs_upscaled.json` (for upscales) and `jobs.json` (for all jobs) within the archive directory. The crawler only adds new jobs not already present in these files.
5.  **Image Downloading & Processing:**
    *   For each upscale job identified, Dimjournal checks if the image has already been archived.
    *   If an image is missing, it navigates the automated browser to the image URL.
    *   It then executes a JavaScript snippet (`Constants.mj_download_image_js`) in the browser to fetch the image data as a base64 encoded string. This method can be more robust for images that are dynamically loaded or protected.
    *   The base64 string is decoded into binary image data.
6.  **File Organization & Metadata Embedding:**
    *   Images are saved to a structured directory: `ARCHIVE_FOLDER/YYYY/MM/YYYYMMDD-HHMM_prompt-slug_jobIDprefix.png`.
        *   `YYYY`: Year
        *   `MM`: Month (zero-padded)
        *   `YYYYMMDD-HHMM`: Timestamp of the job
        *   `prompt-slug`: A slugified version of the prompt (max 49 chars)
        *   `jobIDprefix`: The first 4 characters of the job ID
    *   For PNG images, Dimjournal uses the `pymtpng` library to embed metadata (prompt, author, creation time, etc.) into the PNG's tEXt chunks. Non-PNG images are saved as-is.
7.  **Logging:** Throughout the process, detailed logs are generated using Python's `logging` module, providing insight into operations and aiding in troubleshooting.

**Key Libraries Used:**

*   `undetected_chromedriver` & `selenium`: For web browser automation and interaction.
*   `BeautifulSoup4`: For parsing HTML content (primarily to extract user info).
*   `Pillow (PIL)`: Used by `pymtpng` for image manipulation before saving PNGs with metadata.
*   `pymtpng`: For embedding metadata into PNG files.
*   `python-slugify`: To create safe filenames from prompts.
*   `fire`: To create the command-line interface.
*   `tqdm`: For displaying progress bars during crawling and downloading.

### Code Structure

The project is organized as follows:

*   `src/dimjournal/`
    *   `dimjournal.py`: Contains the core logic of the application.
        *   `Constants`: Class holding various constants like URLs, cookie names, date formats.
        *   `MidjourneyAPI`: Handles all direct interactions with Midjourney via the browser (login, fetching user info, making API calls for job data).
        *   `MidjourneyJobCrawler`: Responsible for iterating through job history pages, fetching job data using `MidjourneyAPI`, and saving/updating `jobs_*.json` files.
        *   `MidjourneyDownloader`: Manages the download of actual image files, organizes them into folders, and embeds metadata into PNGs.
        *   `download()`: The main public function that orchestrates the instances of the above classes to perform the full backup process.
    *   `__main__.py`: Provides the CLI entry point, using `python-fire` to expose the `download` function.
    *   `__init__.py`: Makes the `download` function available for import and sets up package versioning.
*   `tests/`: Contains unit and integration tests written using `pytest`.
    *   `test_dimjournal.py`: Test suite for the core functionalities.
*   `setup.py`, `pyproject.toml`, `setup.cfg`: Files related to packaging, dependencies, and project configuration (following PyScaffold structure).
*   `.github/workflows/ci.yml`: GitHub Actions workflow for continuous integration (testing, linting).
*   `README.md`: This file.
*   `LICENSE.txt`: Apache 2.0 License.
*   `CHANGELOG.md`: History of changes to the project.
*   `AUTHORS.md`: List of contributors.

### Key Classes and Functions

*   **`MidjourneyAPI(driver, archive_folder)`**
    *   `log_in()`: Manages login, loads/saves cookies.
    *   `get_user_info()`: Fetches and stores user ID and other account details.
    *   `request_recent_jobs(...)`: Queries the Midjourney API for job listings.
*   **`MidjourneyJobCrawler(api, archive_folder, job_type)`**
    *   `load_archive_data()`: Loads existing job data from local JSON files.
    *   `update_archive_data(job_listing)`: Adds new jobs to the local archive and saves.
    *   `crawl(limit, from_date)`: Iteratively calls `api.request_recent_jobs()` and updates the archive.
*   **`MidjourneyDownloader(api, archive_folder)`**
    *   `fetch_image(url)`: Retrieves image data using JavaScript execution in the browser.
    *   `create_folders(dt_obj)`: Creates the year/month directory structure.
    *   `fetch_and_write_image(image_url, image_path, info)`: Downloads an image and saves it, embedding metadata if it's a PNG.
    *   `download_missing()`: Iterates through upscaled jobs, downloads missing images, and updates job metadata with archive status.
*   **`download(archive_folder, user_id, limit)`** (in `src/dimjournal/dimjournal.py`)
    *   The main entry point function called by the CLI or when used as a library.
    *   Initializes the WebDriver, `MidjourneyAPI`, `MidjourneyJobCrawler` (for upscales and all jobs), and `MidjourneyDownloader`.
    *   Orchestrates the entire backup process: login, crawl jobs, download images.
    *   Handles overall error catching and WebDriver cleanup.

### Contributing

Contributions are highly welcome! If you'd like to improve Dimjournal, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally: `git clone https://github.com/YOUR_USERNAME/dimjournal.git`
3.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b fix/your-bug-fix`.
4.  **Set up your development environment.** It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e ".[testing]" # Installs package in editable mode with testing extras
    pip install pre-commit
    pre-commit install # Sets up pre-commit hooks for formatting and linting
    ```
5.  **Make your changes.** Implement your feature or fix the bug.
6.  **Ensure your changes pass all checks:**
    *   Run linters and formatters using pre-commit: `pre-commit run --all-files`
    *   Run the test suite: `pytest`
7.  **Commit your changes** with a descriptive commit message (e.g., `feat: Add support for grid image downloads` or `fix: Correctly handle XYZ error`).
8.  **Push your changes** to your fork: `git push origin feature/your-feature-name`.
9.  **Open a Pull Request (PR)** from your fork to the main `dimjournal` repository. Clearly describe the changes you've made and why.

**Coding Conventions & Rules:**

*   **Python Version:** Code should be compatible with Python 3.10 and newer.
*   **Style:** Adhere to PEP 8. `pre-commit` with `flake8` and `black` (if configured, or a similar formatter) will help enforce this.
*   **Type Hinting:** Use type hints for function signatures and variables where appropriate to improve code clarity and enable static analysis.
*   **Logging:** Utilize the `logging` module for diagnostic messages. Use appropriate log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
*   **Error Handling:** Implement robust error handling. Catch specific exceptions where possible and log errors clearly.
*   **Testing:** Write tests for new features and bug fixes using `pytest`. Ensure existing tests pass.
*   **Semantic Versioning:** Follow semantic versioning (Major.Minor.Patch) for releases, as outlined in `CHANGELOG.md`.

### Changelog

For a detailed history of changes, please refer to the [CHANGELOG.md](./CHANGELOG.md) file.

### License

Dimjournal is licensed under the Apache License, Version 2.0. See the [LICENSE.txt](./LICENSE.txt) file for the full license text.

### Authors

See the [AUTHORS.md](./AUTHORS.md) file for a list of contributors.
---

*Initial development assisted by AI.*
