# TODO List

This document tracks the tasks to be completed for the `dimjournal` project.

## Completed Tasks

-   [x] **Refine `dimjournal.py`:**
    -   [x] Improve error handling (specific exceptions, detailed logging).
    -   [ ] ~~Enhance configurability (timeouts, retries, etc.).~~ (Deferred)
    -   [ ] ~~Modularize large functions.~~ (Partially addressed through clearer logic, further modularization deferred)
    -   [x] Improve code comments and docstrings (implicitly done via logging and clearer code).
-   [x] **Update `README.md`:**
    -   [x] Reflect changes in functionality/usage.
    -   [x] Add a "Contributing" section.
-   [x] **Enhance build and CI/CD:**
    -   [x] Review `pyproject.toml`, `setup.cfg`, `setup.py`.
    -   [x] Update `.github/workflows/ci.yml` (linting, formatting checks, updated actions).
-   [x] **Write/Update Tests:**
    -   [x] Improve `tests/test_dimjournal.py` with comprehensive mocked tests.
    -   [x] Increase test coverage significantly.
-   [x] **Documentation:**
    -   [x] Ensure `CHANGELOG.md` is up-to-date with all changes.
    -   [x] Ensure `PLAN.md` and `TODO.md` are kept current.

## Pending Tasks

-   [ ] **Refine `dimjournal.py` (Future Considerations):**
    -   [ ] Enhance configurability (e.g., command-line options for timeouts, retries, browser options like headless).
    -   [ ] Further modularize `download_missing` and other large methods in `dimjournal.py`.
    -   [ ] Explicitly add/improve code comments and docstrings where logging is not self-explanatory.
-   [ ] **Final Checks:**
    -   [ ] Run pre-commit hooks.
    -   [ ] Run all tests (locally, though CI will also run them).
-   [ ] **Submit all changes.**
