# GitHub Actions Workflow Templates

This file contains the workflow templates that need to be manually created due to GitHub App permissions limitations.

## Basic Build and Test Workflow

Create `.github/workflows/build.yml`:

```yaml
name: Build and Test

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[testing]
      
      - name: Run tests
        run: |
          pytest --verbose

  build:
    name: Build Package
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
          pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

## Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags: ['v*']

permissions:
  contents: write

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Advanced CI/CD Pipeline

For the complete CI/CD pipeline with multi-platform testing, binary builds, and PyPI publishing, see the `CICD_SETUP.md` file for the full workflow configuration.

## Manual Setup Instructions

1. Create the `.github/workflows/` directory in your repository
2. Add the workflow files above
3. Add required secrets (PYPI_TOKEN for publishing)
4. Push a git tag to trigger releases: `git tag v1.0.0 && git push origin v1.0.0`

The development tools and scripts are all ready to use locally!