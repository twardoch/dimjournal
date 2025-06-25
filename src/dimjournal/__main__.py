#!/usr/bin/env python3

# from pathlib import Path # Path was unused
import fire

from .dimjournal import download


def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(download)


if __name__ == "__main__":
    cli()
