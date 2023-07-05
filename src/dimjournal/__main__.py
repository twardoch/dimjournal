#!/usr/bin/env python3
from pathlib import Path
from typing import Union

import fire

from .dimjournal import download
from .ui import main as ui_main


def cli(archive_folder: Union[Path, str] = None):
    if archive_folder is None:
        ui_main(archive_folder)
    else:
        fire.core.Display = lambda lines, out: print(*lines, file=out)
        fire.Fire(download)


if __name__ == "__main__":
    cli()
