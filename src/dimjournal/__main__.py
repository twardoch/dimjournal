#!/usr/bin/env python3

import fire
from pathlib import Path
from .dimjournal import download


def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(download)


if __name__ == "__main__":
    cli()
