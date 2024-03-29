# Author: Mark Blakeney, Feb 2024.
"Reinstall a package's executables."
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def init(parser: ArgumentParser) -> None:
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('-U', '--upgrade', action='store_true',
                        help='also upgrade package[s] to the latest version')
    parser.add_argument('package', nargs='+',
                        help='package name[s] to reinstall')

def main(args: Namespace) -> Optional[str]:
    pip_args = utils.make_args((args.verbose, '-v'), (args.upgrade, '-U'))
    for pkgname in args.package:
        pkgname, vdir = utils.get_package_from_arg(pkgname, args)
        if not vdir:
            return f'package {pkgname} is not installed.'

        if args.upgrade:
            data = utils.get_json(vdir, args) or {}
            editpath = data.get('editpath')
            pkg = f'-e {editpath}' if editpath else pkgname
            extras = ' '.join(data.get('injected', []))
            if not utils.piprun(vdir, f'install --reinstall '
                                f'{pip_args} {pkg} {extras}'):
                return f'Error: failed to {args.name} {pkgname}'
        else:
            data = None

        err = utils.make_links(vdir, pkgname, args, data)
        if err:
            return err

        op = args.name.rsplit('-', 1)[0]
        print(f'{op} {pkgname} completed.')

    return None
