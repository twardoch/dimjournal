# CI/CD Setup Guide

## Overview

This guide explains how to set up the complete CI/CD pipeline for the dimjournal project, including the advanced workflow that couldn't be automatically committed due to GitHub App permissions.

## Current Status

✅ **Already Set Up:**
- Git-tag-based semversioning with setuptools_scm
- Comprehensive test suite
- Build and release scripts
- Basic GitHub Actions workflows

⚠️ **Requires Manual Setup:**
- Advanced CI/CD pipeline (due to GitHub App workflow permissions)
- PyPI publishing secrets
- Multi-platform binary builds

## Manual CI/CD Pipeline Setup

### 1. Complete CI/CD Workflow

Create `.github/workflows/ci.yml` with the following content:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  packages: write

concurrency:
  group: >-
    ${{ github.workflow }}-${{ github.ref_type }}-${{ github.event.pull_request.number || github.sha }}
  cancel-in-progress: true

jobs:
  test:
    name: Test on ${{ matrix.os }} with Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Chrome (Ubuntu)
        if: matrix.os == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable
      
      - name: Install Chrome (macOS)
        if: matrix.os == 'macos-latest'
        run: |
          brew install --cask google-chrome
      
      - name: Install Chrome (Windows)
        if: matrix.os == 'windows-latest'
        run: |
          choco install googlechrome
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[testing]
          pip install flake8 black isort pytest-cov
      
      - name: Lint with flake8
        run: flake8 src tests scripts
      
      - name: Check code formatting with black
        run: black --check src tests scripts
      
      - name: Check import sorting with isort
        run: isort --check-only src tests scripts
      
      - name: Run tests with pytest
        run: |
          pytest --verbose --cov=dimjournal --cov-report=xml --cov-report=html --cov-report=term-missing
      
      - name: Upload coverage to Codecov
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.10'
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false

  build-package:
    name: Build Python Package
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build setuptools setuptools_scm wheel
      
      - name: Build package
        run: python -m build
      
      - name: Upload package artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-package
          path: dist/
          retention-days: 30

  build-binaries:
    name: Build Binary on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    needs: test
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            artifact_name: dimjournal-linux-x64
            binary_name: dimjournal
          - os: windows-latest
            artifact_name: dimjournal-windows-x64
            binary_name: dimjournal.exe
          - os: macos-latest
            artifact_name: dimjournal-macos-x64
            binary_name: dimjournal

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install Chrome (Ubuntu)
        if: matrix.os == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable
      
      - name: Install Chrome (macOS)
        if: matrix.os == 'macos-latest'
        run: |
          brew install --cask google-chrome
      
      - name: Install Chrome (Windows)
        if: matrix.os == 'windows-latest'
        run: |
          choco install googlechrome
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install PyInstaller
      
      - name: Build binary
        run: |
          pyinstaller --onefile --name ${{ matrix.binary_name }} --hidden-import dimjournal --hidden-import undetected_chromedriver --hidden-import selenium --hidden-import PIL --hidden-import pymtpng src/dimjournal/__main__.py
      
      - name: Test binary (Unix)
        if: matrix.os != 'windows-latest'
        run: |
          ./dist/${{ matrix.binary_name }} --help
      
      - name: Test binary (Windows)
        if: matrix.os == 'windows-latest'
        run: |
          ./dist/${{ matrix.binary_name }} --help
      
      - name: Upload binary artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: dist/${{ matrix.binary_name }}
          retention-days: 30

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install bandit safety
      
      - name: Run bandit security scan
        run: bandit -r src/
      
      - name: Check for known security vulnerabilities
        run: safety check

  publish-package:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    needs: [test, build-package, build-binaries]
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Download package artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package
          path: dist/
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_TOKEN }}
          verbose: true

  create-release:
    name: Create GitHub Release
    runs-on: ubuntu-latest
    needs: [test, build-package, build-binaries]
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts/
      
      - name: Prepare release assets
        run: |
          mkdir -p release-assets
          
          # Copy Python package
          cp artifacts/python-package/* release-assets/
          
          # Copy and rename binaries
          cp artifacts/dimjournal-linux-x64/dimjournal release-assets/dimjournal-linux-x64
          cp artifacts/dimjournal-windows-x64/dimjournal.exe release-assets/dimjournal-windows-x64.exe
          cp artifacts/dimjournal-macos-x64/dimjournal release-assets/dimjournal-macos-x64
          
          # Make binaries executable
          chmod +x release-assets/dimjournal-*
      
      - name: Generate release notes
        id: release_notes
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
          
          # Extract release notes from CHANGELOG.md
          sed -n "/## \[${VERSION#v}\]/,/## \[/p" CHANGELOG.md | sed '$d' > release_notes.md
          
          # If no changelog entry, create default notes
          if [ ! -s release_notes.md ]; then
            echo "## Changes in $VERSION" > release_notes.md
            echo "- Bug fixes and improvements" >> release_notes.md
          fi
          
          echo "RELEASE_NOTES<<EOF" >> $GITHUB_OUTPUT
          cat release_notes.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          name: Release ${{ steps.release_notes.outputs.VERSION }}
          body: ${{ steps.release_notes.outputs.RELEASE_NOTES }}
          files: release-assets/*
          draft: false
          prerelease: false
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  update-docs:
    name: Update Documentation
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pydoc-markdown
      
      - name: Generate API documentation
        run: |
          pydoc-markdown > API.md
      
      - name: Commit and push documentation
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'docs: Update API documentation [skip ci]'
          file_pattern: 'API.md'
          commit_author: 'github-actions[bot] <github-actions[bot]@users.noreply.github.com>'
```

### 2. Required Secrets

To enable PyPI publishing, add these secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:

**PYPI_TOKEN**
- Go to [PyPI](https://pypi.org/manage/account/token/)
- Create a new API token
- Copy the token and add it as a secret

### 3. Optional: Codecov Integration

For code coverage reporting:

1. Go to [Codecov](https://codecov.io/)
2. Connect your GitHub repository
3. Add the `CODECOV_TOKEN` secret (if required)

## Current Working Features

Even without the advanced CI/CD pipeline, you have:

### ✅ Local Development Tools
```bash
# All these work locally
make test                    # Run tests
make build                   # Build package
make binary                  # Build binary
make release VERSION=v1.0.0  # Create release
```

### ✅ Basic CI/CD
- `build.yml`: Tests and builds on push/PR
- `release.yml`: Creates GitHub releases on git tags

### ✅ Git-Tag Versioning
```bash
# Create a release
git tag v1.0.0
git push origin v1.0.0
# This will trigger the release workflow
```

## Manual Release Process

Until the full CI/CD is set up, you can create releases manually:

```bash
# 1. Run tests locally
make test

# 2. Build package
make build

# 3. Create git tag
git tag v1.0.0
git push origin v1.0.0

# 4. Upload to PyPI manually (if desired)
pip install twine
twine upload dist/*

# 5. Create GitHub release manually
# Go to GitHub → Releases → Create new release
# Upload the files from dist/ folder
```

## Next Steps

1. **Set up the complete CI/CD pipeline** by creating the workflow file manually
2. **Add PyPI token** to enable automated publishing
3. **Test the pipeline** by creating a test release
4. **Monitor the builds** and adjust as needed

The foundation is solid - you have all the tools and scripts needed for a robust development and release process!