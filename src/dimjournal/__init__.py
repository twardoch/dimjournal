from importlib.metadata import PackageNotFoundError, version

# Keep 'download' import if it's meant to be part of the public API of the package
from .dimjournal import download  # noqa: F401 - Preserving for potential public API use

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "dimjournal"  # Ensure this matches the package name in setup.cfg
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    # This typically happens if pkg is not installed (e.g., editable mode might
    # work for imports, but not for version data).
    __version__ = "unknown"
finally:
    # Clean up to avoid leaking version and PackageNotFoundError into the module's namespace
    # Note: 'version' here refers to the import from importlib.metadata, not __version__
    del version, PackageNotFoundError
