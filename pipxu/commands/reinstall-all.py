# Author: Mark Blakeney, Feb 2024.
'Reinstall all applications.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from . import reinstall

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.12"')
    xgroup.add_argument('--reset-python', action='store_true',
                        help='reset any explicit python path or pyenv '
                        'version to default python')
    parser.add_argument('--system-site-packages', action='store_true',
                        help='allow venv access to system packages, '
                        'overrides the per-application setting')
    parser.add_argument('--no-system-site-packages', action='store_true',
                        help='remove venv access to system packages, '
                        'overrides the per-application setting')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-s', '--skip', nargs='*',
                        help='skip these applications, '
                        'e.g. "-s package1 package2"')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    args.package = utils.get_all_package_names(args)
    return reinstall.main(args)
