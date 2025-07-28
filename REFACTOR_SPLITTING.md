# Refactoring Plan: Splitting Large Code Files in Dimjournal

This document outlines a meticulous plan for refactoring the `dimjournal` project by splitting large, monolithic code files into smaller, more focused modules. This will enhance maintainability, improve testability, and clarify the separation of concerns within the codebase.

## I. Core Principles for Refactoring

1.  **Functionality Intact**: The primary goal is to split files without altering the existing functionality or introducing regressions.
2.  **Clear Separation of Concerns**: Each new module will encapsulate a specific set of related responsibilities.
3.  **Maintainability**: Smaller files are easier to understand, debug, and modify.
4.  **Testability**: Unit tests can be more granular and focused on individual components.
5.  **Idiomatic Python**: Adhere to Python best practices, including clear imports and module-level documentation.
6.  **Incremental Changes**: Changes will be applied step-by-step, with verification at each stage.

## II. Refactoring `src/dimjournal/dimjournal.py`

This file currently contains the `Constants` class, utility functions, and the core `MidjourneyAPI`, `MidjourneyJobCrawler`, `MidjourneyDownloader` classes, along with the main `download` orchestration function.

**Proposed New Module Structure within `src/dimjournal/`:**

```
src/dimjournal/
├── __init__.py
├── __main__.py
├── api.py          # MidjourneyAPI class and related functions (e.g., cookie handling)
├── crawler.py      # MidjourneyJobCrawler class
├── downloader.py   # MidjourneyDownloader class and image processing functions
├── constants.py    # Constants class
├── utils.py        # General utility functions (e.g., get_date_ninety_days_prior)
└── exceptions.py   # Custom exception classes (to be created)
```

### Step-by-Step Plan for `src/dimjournal/dimjournal.py`

**Phase 1: Extracting Constants and Utilities**

1.  **Create `src/dimjournal/constants.py`**:
    *   Move the entire `Constants` class definition from `src/dimjournal/dimjournal.py` to this new file.
    *   Add necessary imports to `constants.py` (e.g., `from pathlib import Path`).
    *   In `src/dimjournal/dimjournal.py` and any other files that use `Constants`, replace `class Constants:` with `from .constants import Constants`.

2.  **Create `src/dimjournal/utils.py`**:
    *   Move the `get_date_ninety_days_prior` function from `src/dimjournal/dimjournal.py` to this new file.
    *   Add necessary imports to `utils.py` (e.g., `import datetime as dt`).
    *   In `src/dimjournal/dimjournal.py` and `tests/test_dimjournal.py`, replace direct usage with `from .utils import get_date_ninety_days_prior`.

3.  **Create `src/dimjournal/exceptions.py`**:
    *   Create a new file `src/dimjournal/exceptions.py`.
    *   Define a base custom exception, e.g., `class DimjournalError(Exception): pass`.
    *   Define specific custom exceptions that will be used for more granular error handling (e.g., `AuthenticationError`, `NetworkError`, `ParseError`, `StorageError`). These will be integrated in a later phase.
    *   For now, no changes are needed in `src/dimjournal/dimjournal.py` related to this file, but it's good to create it early.

**Phase 2: Extracting Core Classes**

1.  **Create `src/dimjournal/api.py`**:
    *   Move the entire `MidjourneyAPI` class definition from `src/dimjournal/dimjournal.py` to this new file.
    *   Add all necessary imports to `api.py` (e.g., `import json`, `import logging`, `import pickle`, `from pathlib import Path`, `from bs4 import BeautifulSoup`, `from selenium.common.exceptions import InvalidCookieDomainException, TimeoutException`, `from selenium.webdriver.common.by import By`, `from selenium.webdriver.support import expected_conditions as EC`, `from selenium.webdriver.support.ui import WebDriverWait`, `import undetected_chromedriver as webdriver`).
    *   Crucially, update the import for `Constants` within `api.py` to `from .constants import Constants`.
    *   In `src/dimjournal/dimjournal.py`, replace `class MidjourneyAPI:` with `from .api import MidjourneyAPI`.

2.  **Create `src/dimjournal/crawler.py`**:
    *   Move the entire `MidjourneyJobCrawler` class definition from `src/dimjournal/dimjournal.py` to this new file.
    *   Add all necessary imports to `crawler.py` (e.g., `import json`, `import logging`, `import itertools`, `from pathlib import Path`, `from tqdm import tqdm`).
    *   Update imports within `crawler.py`: `from .api import MidjourneyAPI` and `from .constants import Constants`.
    *   In `src/dimjournal/dimjournal.py`, replace `class MidjourneyJobCrawler:` with `from .crawler import MidjourneyJobCrawler`.

3.  **Create `src/dimjournal/downloader.py`**:
    *   Move the entire `MidjourneyDownloader` class definition from `src/dimjournal/dimjournal.py` to this new file.
    *   Add all necessary imports to `downloader.py` (e.g., `import base64`, `import datetime as dt`, `import io`, `import json`, `import logging`, `from pathlib import Path`, `from urllib.parse import urlparse`, `import numpy as np`, `import pymtpng`, `from PIL import Image`, `from slugify import slugify`, `from tqdm import tqdm`).
    *   Update imports within `downloader.py`: `from .api import MidjourneyAPI` (if `MidjourneyAPI` is passed to its constructor, which it is) and `from .constants import Constants`.
    *   In `src/dimjournal/dimjournal.py`, replace `class MidjourneyDownloader:` with `from .downloader import MidjourneyDownloader`.

**Phase 3: Updating `src/dimjournal/dimjournal.py` (Main Orchestration File)**

1.  **Update Imports**: At the top of `src/dimjournal/dimjournal.py`, remove all the moved class and function definitions. Replace them with imports from the newly created modules:
    ```python
    import logging
    import os
    from pathlib import Path
    import undetected_chromedriver as webdriver

    from .api import MidjourneyAPI
    from .crawler import MidjourneyJobCrawler
    from .downloader import MidjourneyDownloader
    from .constants import Constants # Ensure Constants is imported if still used directly
    from .utils import get_date_ninety_days_prior # Ensure utils is imported if still used directly
    # from .exceptions import DimjournalError, AuthenticationError, etc. (for future use)
    ```
2.  **Review `download` function**: Ensure all calls within the `download` function correctly reference the imported classes (e.g., `MidjourneyAPI(...)` instead of assuming it's in the same file). No functional changes should be needed here, only import adjustments.
3.  **Logging**: Ensure the `_log = logging.getLogger("dimjournal")` line remains, and `logging.basicConfig` is handled appropriately (it's currently inside `download`, which is fine for a CLI entry point).

**Phase 4: Updating `src/dimjournal/__init__.py` and `src/dimjournal/__main__.py`**

1.  **`src/dimjournal/__init__.py`**:
    *   The `download` function is currently imported directly from `dimjournal.py`. This import should remain as `from .dimjournal import download` to maintain the public API.
    *   Ensure `importlib.metadata` handling is correct.

2.  **`src/dimjournal/__main__.py`**:
    *   The `cli` function uses `fire.Fire(download)`. This import `from .dimjournal import download` should remain unchanged.

## III. Refactoring `tests/test_dimjournal.py`

This file contains tests for various components. To align with the new module structure, these tests should be split into corresponding test files.

**Proposed New Test File Structure within `tests/`:**

```
tests/
├── conftest.py     # Shared fixtures (mock_driver, mock_api)
├── test_api.py     # Tests for MidjourneyAPI
├── test_crawler.py # Tests for MidjourneyJobCrawler
├── test_downloader.py # Tests for MidjourneyDownloader
└── test_utils.py   # Tests for utility functions (e.g., get_date_ninety_days_prior)
```

### Step-by-Step Plan for `tests/test_dimjournal.py`

**Phase 1: Move Shared Fixtures to `tests/conftest.py`**

1.  **Update `tests/conftest.py`**:
    *   Move the `mock_driver` and `mock_api` fixtures from `tests/test_dimjournal.py` to `tests/conftest.py`.
    *   Ensure all necessary imports are present in `conftest.py` (e.g., `import pytest`, `import json`, `import undetected_chromedriver as webdriver`, `from dimjournal.dimjournal import Constants, MidjourneyAPI`). Note: `MidjourneyAPI` will eventually be imported from `dimjournal.api`. For now, keep the existing import path, and update it once `dimjournal.api` is created.
    *   The `tmp_path` fixture is provided by `pytest` and doesn't need to be moved.

**Phase 2: Create New Test Files and Move Tests**

1.  **Create `tests/test_utils.py`**:
    *   Move `test_get_date_ninety_days_prior` and `test_get_date_ninety_days_prior_leap_year` functions to this file.
    *   Update imports: `from dimjournal.utils import get_date_ninety_days_prior` and `from dimjournal.constants import Constants`.

2.  **Create `tests/test_api.py`**:
    *   Move the `TestMidjourneyAPI` class and all its methods to this file.
    *   Update imports: `from dimjournal.api import MidjourneyAPI` and `from dimjournal.constants import Constants`.
    *   Ensure `mock_api` and `mock_driver` fixtures are correctly referenced (they will be auto-discovered from `conftest.py`).

3.  **Create `tests/test_crawler.py`**:
    *   Move the `TestMidjourneyJobCrawler` class and all its methods to this file.
    *   Update imports: `from dimjournal.crawler import MidjourneyJobCrawler`, `from dimjournal.api import MidjourneyAPI` (for the `mock_api` fixture), and `from dimjournal.constants import Constants`.

4.  **Create `tests/test_downloader.py`**:
    *   Move the `TestMidjourneyDownloader` class and all its methods to this file.
    *   Update imports: `from dimjournal.downloader import MidjourneyDownloader`, `from dimjournal.api import MidjourneyAPI` (for the `mock_api` fixture), `from dimjournal.constants import Constants`, `import datetime as dt`, `import json`, `import numpy as np`, `from PIL import Image`, `import io`, `import pymtpng`, `from urllib.parse import urlparse`, `from slugify import slugify`.

**Phase 3: Clean Up `tests/test_dimjournal.py`**

1.  After moving all tests and fixtures, the original `tests/test_dimjournal.py` file should be almost empty. Remove any remaining test functions and the `test()` placeholder. It can be deleted or kept as a minimal file if desired, but it should no longer contain actual tests.

## IV. Verification Steps After Each Phase

After completing each phase (or even each major step within a phase), it is crucial to verify that the changes have not introduced any regressions.

1.  **Run Linters/Formatters**:
    ```bash
    pre-commit run --all-files
    ```
    This ensures code style and basic syntax are correct.

2.  **Run Tests**:
    ```bash
    pytest
    ```
    Ensure all existing tests pass. If tests fail, debug and fix immediately before proceeding. This is critical for maintaining functionality.

3.  **Manual Smoke Test (if applicable)**:
    *   Run the main `dimjournal` command line tool to ensure it still functions as expected (e.g., `python -m dimjournal --help` or a small download run).

## V. Future Enhancements (Post-Refactoring)

Once the refactoring is complete and verified, the following improvements can be considered:

*   **Integrate Custom Exceptions**: Replace generic `Exception` catches with the specific custom exceptions defined in `exceptions.py` for more precise error handling.
*   **Type Hinting Enforcement**: Configure `mypy` and add it to pre-commit hooks to enforce type checking across the newly typed codebase.
*   **Comprehensive Test Coverage**: Review and expand test coverage, especially for edge cases and error conditions, leveraging the improved modularity.
*   **Documentation**: Update module-level docstrings and potentially generate API documentation using tools like Sphinx.

This detailed plan provides a clear roadmap for a junior developer to systematically refactor the `dimjournal` codebase, ensuring a smooth transition to a more organized and maintainable architecture.
