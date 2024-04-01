# Author: Mark Blakeney, Feb 2024.
'Upgrade all applications.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from . import upgrade

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-s', '--skip', nargs='*',
                        help='skip these applications, e.g. '
                        '"-s package1 package2"')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    args.package = utils.get_all_package_names(args)
    return upgrade.main(args)
