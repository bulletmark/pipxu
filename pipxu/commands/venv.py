# Author: Mark Blakeney, Feb 2024.
"List application virtual environment paths."

from __future__ import annotations

import platform
from argparse import ArgumentParser, Namespace
from pathlib import Path

from .. import utils


def init(parser: ArgumentParser) -> None:
    "Called to add command arguments to parser at init"
    parser.add_argument(
        '-p', '--path-full', action='store_true', help="don't abbreviate the path"
    )
    parser.add_argument(
        '-P',
        '--path-python',
        action='store_true',
        help='show resolved path to python executable',
    )
    parser.add_argument(
        '-s',
        '--sort-venv',
        action='store_true',
        help='sort by venv path rather than package name',
    )
    parser.add_argument(
        'package',
        nargs='*',
        help='list the path for the given application[s] rather than all applications.',
    )


def main(args: Namespace) -> str | None:
    "Called to action this command"
    if args.path_python:
        args.path_full = True

    if args.package:
        pkgs = dict(utils.get_package_from_arg(p, args) for p in args.package)
    else:
        all_pkgs = {p.name: p.resolve() for p in args._packages_dir.iterdir()}

        def keycmp(k: str) -> int:
            val = all_pkgs.get(k, '/0')
            return int(val.name)

        key = keycmp if args.sort_venv else None
        pkgs = {k: all_pkgs[k] for k in sorted(all_pkgs, key=key)}

    for pkgname, vdir in pkgs.items():
        if not vdir:
            return f'Application {pkgname} is not installed.'

        path = vdir if args.path_full else Path(utils.unexpanduser(vdir))

        if args.path_python:
            if platform.system() == 'Windows':
                path = path / 'Scripts' / 'python.exe'
            else:
                path = path / 'bin' / 'python'

            if path.is_file():
                path = path.resolve()

        if len(pkgs) > 1:
            print(f'{pkgname} -> {path}')
        else:
            print(path)

    return None
