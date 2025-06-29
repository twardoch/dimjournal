# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Simplified test suite:** Removed excessive mocking in favor of cleaner test structure (2025-06-25)
- **Code cleanup:** Removed redundant error handling and simplified control flow in dimjournal.py
- **Dependency management:** Streamlined imports and removed unnecessary complexity

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
