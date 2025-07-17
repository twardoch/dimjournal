import sys

from .dimjournal import download

try:
    from ._version import __version__
except ImportError:
    # Fallback to importlib.metadata if _version.py doesn't exist
    try:
        from importlib.metadata import version, PackageNotFoundError
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
        try:
            del version, PackageNotFoundError
        except NameError:
            pass
