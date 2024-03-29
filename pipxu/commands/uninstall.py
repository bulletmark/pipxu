# Author: Mark Blakeney, Feb 2024.
"Uninstall a Python application and it's virtual environment"
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('package', nargs='+',
                        help='package name[s] to uninstall')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    for pkgname in args.package:
        pkgname, vdir = utils.get_package_from_arg(pkgname, args)
        if not vdir or not utils.rm_package(pkgname, args):
            return f'{pkgname} is not installed.'

        print(f'{pkgname} uninstalled.')

    return None
