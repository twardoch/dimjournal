# this_file: src/dimjournal/__init__.py
"""dimjournal: archive utility for Midjourney generations."""

import contextlib

from .dimjournal import download

try:
    from ._version import __version__
except ImportError:
    # Fallback to importlib.metadata when the hatch-vcs _version.py is absent.
    try:
        from importlib.metadata import PackageNotFoundError, version

        __version__ = version("dimjournal")
    except PackageNotFoundError:  # pragma: no cover
        # Raised when the package is not installed (e.g. a bare source checkout).
        __version__ = "unknown"
    finally:
        # Avoid leaking the importlib helpers into the package namespace.
        with contextlib.suppress(NameError):
            del version, PackageNotFoundError

__all__ = ["__version__", "download"]
