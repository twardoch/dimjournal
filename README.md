# Dimjournal

Dimjournal is a Midjourney backup tool. It automatically downloads the metadata archive and the upscaled images from Midjourney into a local archive (folder tree). It also embeds some basic metadata (like the prompt) into the PNG files.

**Disclaimer:** The terms of use of Midjourney may disallow automation. Use this tool at your own risk. The developers of Dimjournal are not responsible for any consequences of using this software.

Dimjournal is a Python tool that uses the Selenium WebDriver to log into the Midjourney website, fetch user data, and download job information and images. It aims to be robust by incorporating error handling and clear logging.

## Features

*   **Automated Backup:** Downloads your Midjourney job history (metadata) and upscaled images.
*   **Organized Archive:** Saves images in a structured folder hierarchy (Year/Month/Image).
*   **Metadata Embedding:** Embeds prompt information and other details directly into PNG files.
*   **Resumable Downloads:** Only downloads new or missing images and metadata on subsequent runs.
*   **Cookie Management:** Saves and reuses login session cookies to reduce manual logins.
*   **Logging:** Provides detailed logs for troubleshooting.

## Changelog

Refer to [CHANGELOG.md](./CHANGELOG.md) for a detailed history of changes.

-   v1.0.8: Fixes (prior version)
-   v1.0.3: Tested on macOS in July 2023 (prior version)

## Installation

**Prerequisites:**
*   Python 3.10 or higher
*   Google Chrome browser installed (as `undetected_chromedriver` relies on it)

Stable version:

```
pip install dimjournal
```

Development version:

```
python3 -m pip install git+https://github.com/twardoch/dimjournal
```

## Usage

### Command Line Interface (CLI)

In Terminal, run:

```bash
dimjournal
```

Dimjournal will open a browser where you need to log into MidJourney. The tool will create the backup folder, which by default is the `midjourney/dimjournal` subfolder inside your `Pictures`/`My Pictures` folder. It will operate the browser, download all metadata (up to 2,500 last upscale jobs, and up to 2,500 jobs), and save it in JSON files in the backup folder. Then it will use the browser to download all upscales that are not in the backup folder. If you run the tool again, it will only download new metadata, and new images.

To specify a different backup folder, use:

```bash
dimjournal --archive_folder /path/to/your/archive/folder
```
(Note: If `dimjournal` is not directly in your PATH, you might need to use `python3 -m dimjournal --archive_folder ...`)

You can also specify a limit on the number of pages of job history to crawl (useful for initial runs or if you only want recent items):
```bash
dimjournal --limit 5
```

### Python

You can also use Dimjournal in your Python scripts. Here is an example of how to import and use the `download` function:

```python
import logging
from dimjournal import download
from pathlib import Path

# Optional: Configure logging to see output from dimjournal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Specify the directory where you want to store the data
# If None, it defaults to Pictures/midjourney/dimjournal or My Pictures/midjourney/dimjournal
archive_folder_path = Path("./my_midjourney_backup")
# archive_folder_path = None # To use default location

# Specify a limit for the number of pages to crawl (optional)
crawl_limit = 10  # Crawl 10 pages of recent jobs
# crawl_limit = None # To crawl all available history

# Download the data
download(archive_folder=archive_folder_path, limit=crawl_limit)

print(f"Download process complete. Check the folder: {archive_folder_path.resolve() if archive_folder_path else 'default location'}")
```

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally: `git clone https://github.com/YOUR_USERNAME/dimjournal.git`
3.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b fix/your-bug-fix`.
4.  **Install dependencies** for development (it's recommended to use a virtual environment):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e .[testing]
    pip install pre-commit
    pre-commit install
    ```
5.  **Make your changes.**
6.  **Ensure your changes pass tests and pre-commit hooks:**
    ```bash
    pytest
    pre-commit run --all-files
    ```
7.  **Commit your changes:** `git commit -m "feat: Describe your feature"` or `git commit -m "fix: Describe your bug fix"`.
8.  **Push to your fork:** `git push origin feature/your-feature-name`.
9.  **Open a Pull Request** from your fork to the main `dimjournal` repository.

Please ensure your code adheres to the existing style and that all tests pass.

## License

- Licensed under the [Apache-2.0 License](./LICENSE.txt)
- Initial development assisted by AI.
