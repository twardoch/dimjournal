# Installation and Development Guide

## Overview

This guide provides comprehensive instructions for setting up the dimjournal project for development and creating releases.

## Prerequisites

- Python 3.10 or higher
- Git
- Google Chrome browser (required for the application)

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/twardoch/dimjournal.git
cd dimjournal
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e .[dev]
```

This installs the package in development mode with all dependencies including:
- Testing tools (pytest, pytest-cov, pytest-mock)
- Code formatting (black, isort)
- Linting (flake8)
- Security scanning (bandit, safety)
- Build tools (build, setuptools_scm, wheel)
- Binary building (PyInstaller)
- Documentation (pydoc-markdown)

## Available Scripts and Commands

### Using Python Scripts

The project includes several Python scripts in the `scripts/` directory:

#### Test Script (`scripts/test.py`)
```bash
python scripts/test.py                 # Run full test suite
python scripts/test.py --format        # Format code and run tests
python scripts/test.py --lint-only     # Run linting only
```

#### Build Script (`scripts/build.py`)
```bash
python scripts/build.py                # Build Python package
python scripts/build.py --binary       # Build package and binary
```

#### Release Script (`scripts/release.py`)
```bash
python scripts/release.py v1.0.0       # Create and tag release
```

#### Validation Script (`scripts/validate.py`)
```bash
python scripts/validate.py             # Validate project structure
```

### Using the Shell Script

The `build-and-test.sh` script provides a convenient wrapper:

```bash
./build-and-test.sh                    # Run all tests and build
./build-and-test.sh --test             # Run tests only
./build-and-test.sh --build            # Build package only
./build-and-test.sh --build --binary   # Build package and binary
./build-and-test.sh --release v1.0.0   # Create release
./build-and-test.sh --format --test    # Format code and run tests
```

### Using Makefile

The project includes a Makefile for convenience:

```bash
make help                              # Show available targets
make install                           # Install in development mode
make dev-install                       # Install with dev dependencies
make test                              # Run tests
make test-format                       # Format code and run tests
make lint                              # Run linting
make format                            # Format code
make build                             # Build package
make binary                            # Build package and binary
make release VERSION=v1.0.0            # Create release
make clean                             # Clean build artifacts
make all                               # Clean, test, and build
make ci                                # Run CI pipeline locally
```

## Development Workflow

### 1. Basic Development Cycle

```bash
# Start development
make dev-install

# Make changes to code
# ...

# Format and test
make test-format

# Build package
make build

# Clean up
make clean
```

### 2. Creating a Release

```bash
# Ensure working directory is clean
git status

# Run full test suite
make test

# Create release (this will create git tag and push)
make release VERSION=v1.0.0

# Or use the script directly
python scripts/release.py v1.0.0
```

### 3. Building Binaries

```bash
# Build standalone binary
make binary

# Or using the script
python scripts/build.py --binary
```

## Git Tag-Based Versioning

The project uses `setuptools_scm` for automatic versioning based on git tags:

- Version is automatically derived from git tags
- Tags should follow semantic versioning (e.g., `v1.0.0`)
- Development versions are automatically generated between tags
- Version information is written to `src/dimjournal/_version.py`

## GitHub Actions CI/CD

The project includes comprehensive GitHub Actions workflows:

### Automated Testing
- Tests on Python 3.10, 3.11, 3.12
- Tests on Ubuntu, Windows, and macOS
- Code formatting checks (black, isort)
- Linting (flake8)
- Security scanning (bandit, safety)
- Coverage reporting

### Automated Building
- Python package building
- Multi-platform binary building (Linux, Windows, macOS)
- Binary testing

### Automated Releases
- Triggered on git tag push (e.g., `v1.0.0`)
- Publishes to PyPI automatically
- Creates GitHub releases with binaries
- Generates release notes from CHANGELOG.md

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dimjournal

# Run specific test file
pytest tests/test_dimjournal.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Configuration

Test configuration is in `pyproject.toml`:
- Coverage threshold: 80%
- Test discovery patterns
- Test markers for categorization

## Code Quality

### Formatting
- **Black**: Code formatting with 88-character line length
- **isort**: Import sorting and organization

### Linting
- **flake8**: Python linting with configured rules
- **bandit**: Security vulnerability scanning
- **safety**: Known vulnerability checking

### Configuration Files
- `pyproject.toml`: Main configuration for tools
- `setup.cfg`: Package metadata and legacy tool configuration

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you've installed with `pip install -e .[dev]`
2. **Test failures**: Check that Chrome is installed and accessible
3. **Build errors**: Ensure all dependencies are installed
4. **Version issues**: Check that git tags are properly formatted

### Getting Help

1. Check the validation script: `python scripts/validate.py`
2. Review the GitHub Actions logs for CI failures
3. Ensure all prerequisites are installed
4. Check that the virtual environment is activated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [setuptools_scm Documentation](https://setuptools-scm.readthedocs.io/)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)