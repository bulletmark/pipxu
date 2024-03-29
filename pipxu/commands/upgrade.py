# Author: Mark Blakeney, Feb 2024.
"Upgrade a package and their executables."
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from . import reinstall

def init(parser: ArgumentParser) -> None:
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('package', nargs='+',
                        help='package name[s] to upgrade')

def main(args: Namespace) -> Optional[str]:
    args.upgrade = True
    return reinstall.main(args)
