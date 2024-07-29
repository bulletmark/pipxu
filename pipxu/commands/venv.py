# Author: Mark Blakeney, Feb 2024.
'List application virtual environment paths.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace

from .. import utils

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-p', '--path-full', action='store_true',
                        help='don\'t abbreviate the path')
    parser.add_argument('package', nargs='*',
                        help='list the path for the given application[s] '
                        'rather than all applications.')

def main(args: Namespace) -> str | None:
    'Called to action this command'
    if args.package:
        pkgs = [utils.get_package_from_arg(p, args) for p in args.package]
    else:
        pkgs = sorted((p.name, p) for p in args._packages_dir.iterdir())

    for pkgname, vdir in pkgs:
        if not vdir:
            return f'Application {pkgname} is not installed.'

        path = str(vdir.resolve())
        if not args.path_full:
            path = utils.unexpanduser(path)

        if len(pkgs) > 1:
            print(f'{pkgname} -> {path}')
        else:
            print(path)

    return None
