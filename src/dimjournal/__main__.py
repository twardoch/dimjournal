#!/usr/bin/env python3

import fire

from .ui import main as ui_main


def cli():
    ui_main()


if __name__ == "__main__":
    cli()
