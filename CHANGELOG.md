# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **CI workflow:** `.github/workflows/ci.yml` with ruff lint, ruff format-check, pytest, and build jobs using `uv` and `hatchling`.
- **Release workflow:** `.github/workflows/release.yml` triggered on `v*` tags — builds distributions, creates a GitHub release, and publishes to PyPI via Trusted Publishing (OIDC).
- **MkDocs site:** `mkdocs.yml` with Material theme; `docs/` containing `index.md`, `installation.md`, `usage.md`, `api.md`.
- **Project icon:** `docs/assets/icon.png`, referenced from the README.
- **`MidjourneyDownloader.generate_image_path()`:** Extracted image-path construction from `download_missing()` into a dedicated, testable method.
- **`MidjourneyDownloader.read_jobs()`:** Now handles missing `jobs_upscale.json` gracefully (returns `[]` instead of raising `FileNotFoundError`).

### Changed
- **Build system:** Migrated from `setuptools` + `setuptools_scm` to `hatchling` + `hatch-vcs`; removed the legacy `setup.py`, `setup.cfg`, and `tox.ini`.
- **Type hints & lint:** `dimjournal.py` and `__init__.py` are now `ruff` and `mypy` clean; added return/variable annotations and explanatory comments (e.g. why `undetected_chromedriver` is required).
- **`pyproject.toml`:** Added `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]`, `[tool.mypy]`, and `[tool.hatch.*]` sections; removed `[tool.black]` and `[tool.isort]`; dropped `--cov-fail-under` from default pytest run.
- **`MidjourneyAPI.__init__()`:** `cookies_path` is now initialised in `__init__` so `save_cookies()` works even when `log_in()` is mocked in tests.
- **`MidjourneyJobCrawler.load_archive_data()`:** Now returns `self.archive_data` for easier testing.
- **`download_missing()`:** Refactored to call `generate_image_path()`; fixed an invalid `except dt.datetime.strptime` clause (replaced with `except ValueError`).

### Fixed
- **PNG metadata fallback:** `fetch_and_write_image()` referenced an undefined `img_array` in a broken, unreachable `except` block. Rewritten so a `pymtpng` failure cleanly falls back to writing the raw image bytes.
- **`request_recent_jobs()`:** Guard against a missing `<pre>` payload (no longer raises `AttributeError` on `None`), and repaired the JSON-decode error-log snippet.
- **Test: leap-year date subtraction** — corrected expected result for `2024-03-01 − 90 days` (is `2023-12-02`, not `2023-12-01`).
- **Test: `test_load_archive_data_*`** — aligned JSON file format with actual flat-list storage and updated assertions.
- **Test: `test_update_archive_data`** — set `crawler.archive_data` to a list instead of a `{"jobs": [...]}` dict.
- **Test: `test_crawl_with_limit`** — added required `enqueue_time` field to mock job data.
- **Test: `test_download_missing_images`** — corrected filename (`jobs_upscale.json`) and data format (flat list).
- **Test: `test_download_function_success`** — updated `assert_called_once_with` to use keyword arguments matching the `download()` call site.

## [1.0.9] - 2025-06-25

### Added
- Created `PLAN.md` to outline project tasks and strategy.
- Created `TODO.md` to track pending tasks.
- Created `CHANGELOG.md` (this file) to document project changes.
- **Error Handling & Logging:** Significantly improved error handling across `dimjournal.py` with more specific exceptions, detailed logging messages (including `exc_info=True` for exceptions), and checks for common failure points (e.g., missing elements, network issues, file I/O problems).
- **README Enhancements:**
    - Added a "Features" section.
    - Included a "Disclaimer" regarding Midjourney's ToS.
    - Added prerequisites to the "Installation" section.
    - Updated CLI examples.
    - Provided a more detailed Python usage example including logging.
    - Added a "Contributing" section with guidelines.
- **Build & CI/CD:**
    - Updated GitHub Actions workflow (`.github/workflows/ci.yml`) to use newer versions of `actions/checkout` (v4) and `actions/setup-python` (v5).
    - Added a linting step with `flake8` to the CI workflow.
    - Ensured Python 3.10+ consistency for version-dependent imports (`importlib.metadata`).
- **Testing:**
    - Added a comprehensive test suite in `tests/test_dimjournal.py`.
    - Implemented tests for utility functions (`get_date_ninety_days_prior`).
    - Added mocked tests for `MidjourneyAPI` (login, user info fetching, job requests).
    - Added mocked tests for `MidjourneyJobCrawler` (archive loading, data updates, crawl logic).
    - Added mocked tests for `MidjourneyDownloader` (job reading, folder creation, image fetching/writing, download loop).
    - Used `pytest-mock` and `tmp_path` fixtures for effective testing.

### Changed
- **Code Refinements in `dimjournal.py`:**
    - Improved robustness of login sequence, user info parsing, and API request handling.
    - Enhanced file operations (reading/writing JSON, creating folders) with better error catching.
    - Made image downloading logic more resilient, including fallback for PNG metadata processing.
    - Refined logging messages to be more informative.
- **`src/dimjournal/__init__.py`:** Simplified `importlib.metadata` import for Python 3.10+ and set `dist_name` explicitly to `dimjournal`.
- Default archive path in `download()` function now uses a base `midjourney` folder under user's Pictures, then `dimjournal` (e.g., `~/Pictures/midjourney/dimjournal`).

### Deprecated

### Removed

### Fixed

### Security
