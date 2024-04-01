# Author: Mark Blakeney, Feb 2024.
'Uninstall all Python applications and their virtual environments.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from . import uninstall

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-s', '--skip', nargs='*',
                        help='skip these packages, e.g. package1 package2')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    args.package = utils.get_all_package_names(args)
    return uninstall.main(args)
