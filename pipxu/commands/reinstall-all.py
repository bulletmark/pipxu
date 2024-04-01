# Author: Mark Blakeney, Feb 2024.
"Reinstall all packages and their executables."
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from . import reinstall

def init(parser: ArgumentParser) -> None:
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.9".')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-s', '--skip', nargs='*',
                        help='skip these packages, e.g. package1 package2')

def main(args: Namespace) -> Optional[str]:
    args.package = utils.get_all_package_names(args)
    return reinstall.main(args)
