# TODO List

## Critical Issues (Immediate)

- [ ] Fix syntax error in `src/dimjournal/dimjournal.py` line 149 (missing try block)
- [ ] Run tests to verify current functionality
- [ ] Fix any failing tests after syntax error correction

## High Priority (Next 1-2 weeks)

### Code Quality
- [ ] Refactor dimjournal.py into multiple modules:
  - [ ] Create `api.py` for MidjourneyAPI class
  - [ ] Create `crawler.py` for MidjourneyJobCrawler class
  - [ ] Create `downloader.py` for MidjourneyDownloader class
  - [ ] Create `constants.py` for Constants class
  - [ ] Create `utils.py` for utility functions
  - [ ] Create `exceptions.py` for custom exceptions

### Error Handling
- [ ] Implement custom exception hierarchy
- [ ] Add retry logic with exponential backoff for network operations
- [ ] Improve error messages for better user experience

### Testing
- [ ] Restore comprehensive test coverage (target >80%)
- [ ] Add integration tests for main workflows
- [ ] Set up coverage reporting

## Medium Priority (Next month)

### Type Safety
- [ ] Add type hints to all functions and methods
- [ ] Add py.typed marker file
- [ ] Configure mypy and add to pre-commit hooks

### Configuration
- [ ] Implement configuration file support (YAML/TOML)
- [ ] Add environment variable support
- [ ] Make timeouts and retries configurable

### CLI Improvements
- [ ] Replace fire with click for better CLI
- [ ] Add subcommands (download, config, test-auth, clean-cache)
- [ ] Improve progress indicators and user feedback

### Deployment
- [ ] Create Dockerfile with Chrome pre-installed
- [ ] Add docker-compose.yml
- [ ] Document Docker deployment process
- [ ] Add installation script for common platforms

## Low Priority (Future enhancements)

### Performance
- [ ] Implement parallel image downloads
- [ ] Add download resume capability
- [ ] Optimize image processing pipeline
- [ ] Add caching layer

### Features
- [ ] Export metadata to CSV/SQLite formats
- [ ] Add web interface for browsing archives
- [ ] Implement search functionality
- [ ] Add batch operations support

### Documentation
- [ ] Generate API documentation with Sphinx
- [ ] Create architecture diagrams
- [ ] Write troubleshooting guide
- [ ] Record setup video tutorials

### Quality Assurance
- [ ] Set up continuous deployment
- [ ] Add performance benchmarks
- [ ] Implement automated browser testing
- [ ] Add security scanning

## Completed Tasks

- [x] Update CHANGELOG.md with recent changes
- [x] Analyze codebase for improvement areas
- [x] Create comprehensive improvement plan (PLAN.md)
- [x] Create simplified TODO list (this file)