# Author: Mark Blakeney, Feb 2024.
'Uninstall one, or more, or all applications.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def _uninstall(args: Namespace, pkgname: str) -> Optional[str]:
    'Uninstall given package'
    pkgname, vdir = utils.get_package_from_arg(pkgname, args)
    if not vdir:
        return f'Application {pkgname} is not installed.'

    if not utils.rm_package(pkgname, args):
        return f'Failed to uninstall {pkgname}.'

    print(f'{pkgname} uninstalled.')
    return None

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('--all', action='store_true',
                        help='uninstall ALL applications')
    parser.add_argument('--skip', action='store_true',
                        help='skip the specified applications when '
                        'uninstalling all (only can be specified with --all)')
    parser.add_argument('package', nargs='*',
                        help='application[s] to uninstall (or to skip for '
                        '--all --skip)')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    for pkgname in utils.get_package_names(args):
        if error := _uninstall(args, pkgname):
            return error

    return None
