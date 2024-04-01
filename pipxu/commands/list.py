# Author: Mark Blakeney, Feb 2024.
'List all applications installed by this tool.'
from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def show(value: str) -> str:
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
    pkgs = set(utils.get_package_from_arg(p, args)[0] for p in args.package)
    json_out = {}
    for pdir in sorted(args._packages_dir.iterdir()):
        pkgname = pdir.name
        if pkgs and pkgname not in pkgs:
            continue

        data = utils.get_json(pdir, args)
        if data:
            data.pop('name', None)
            if args.json:
                json_out[pkgname] = data
            else:
                d = ', '.join(f'{k}={show(data[k])}' for k in sorted(data))
                print(f'{pkgname}: {d}')

    if args.json:
        print(json.dumps(json_out, indent=2))

    return None
