# Author: Mark Blakeney, Feb 2024.
'List applications installed by this tool.'
from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def _show(value: str) -> str:
    'Show a string with quotes'
    return f'"{value}"' if isinstance(value, str) else value

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('--json', action='store_true',
                        help='output json instead')
    parser.add_argument('package', nargs='*',
                        help='list the given application[s] only')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    if args.package:
        pkgs = [utils.get_package_from_arg(p, args) for p in args.package]
    else:
        pkgs = sorted((p.name, p) for p in args._packages_dir.iterdir())

    json_out = {}
    for pkgname, vdir in pkgs:
        if not vdir:
            return f'Application {pkgname} is not installed.'

        if data := utils.get_json(vdir, args):
            data.pop('name', None)
            if args.json:
                json_out[pkgname] = data
            else:
                d = ', '.join(f'{k}={_show(data[k])}' for k in sorted(data))
                print(f'{pkgname}: {d}')

    if args.json:
        print(json.dumps(json_out, indent=2))

    return None
