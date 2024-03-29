# Author: Mark Blakeney, Feb 2024.
"Reinstall all packages executables."
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from . import reinstall

def init(parser: ArgumentParser) -> None:
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-U', '--upgrade', action='store_true',
                        help='also upgrade the package[s] to latest version')
    parser.add_argument('-s', '--skip', nargs='*',
                        help='skip these packages, e.g. package1 package2')

def main(args: Namespace) -> Optional[str]:
    args.package = utils.get_all_package_names(args)
    return reinstall.main(args)
