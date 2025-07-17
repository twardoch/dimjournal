# this_file: Makefile
# Makefile for dimjournal project

.PHONY: help install test lint format build binary release clean dev-install

help:  ## Show this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install package in development mode
	pip install -e .

dev-install:  ## Install package with development dependencies
	pip install -e .[dev]

test:  ## Run tests
	python scripts/test.py

test-format:  ## Format code and run tests
	python scripts/test.py --format

lint:  ## Run linting only
	python scripts/test.py --lint-only

format:  ## Format code
	python scripts/test.py --format

build:  ## Build package
	python scripts/build.py

binary:  ## Build package and binary
	python scripts/build.py --binary

release:  ## Create a release (requires VERSION=vX.X.X)
ifndef VERSION
	@echo "Error: VERSION variable is required. Use: make release VERSION=v1.0.0"
	@exit 1
endif
	python scripts/release.py $(VERSION)

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf src/dimjournal.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

all: clean test build  ## Clean, test, and build

ci: clean test lint build  ## Run CI pipeline locally

# Convenience targets
t: test  ## Alias for test
b: build  ## Alias for build
f: format  ## Alias for format
l: lint  ## Alias for lint
c: clean  ## Alias for clean