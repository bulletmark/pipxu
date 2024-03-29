# Author: Mark Blakeney, Feb 2024.
"Upgrade all packages and their executables."
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from . import upgrade

def init(parser: ArgumentParser) -> None:
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-s', '--skip', nargs='*',
                        help='skip these packages, e.g. package1 package2')

def main(args: Namespace) -> Optional[str]:
    args.package = utils.get_all_package_names(args)
    return upgrade.main(args)
