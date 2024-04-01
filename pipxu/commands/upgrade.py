# Author: Mark Blakeney, Feb 2024.
'Upgrade an application.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('package', nargs='+',
                        help='application[s] to upgrade')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    pip_args = utils.make_args((args.verbose, '-v'), (True, '-U'))
    for pkgname in args.package:
        pkgname, vdir = utils.get_package_from_arg(pkgname, args)
        if not vdir:
            return f'Application {pkgname} is not installed.'

        data = utils.get_json(vdir, args) or {}
        editpath = data.get('editpath')
        pkg = f'-e {editpath}' if editpath else pkgname
        extras = ' '.join(data.get('injected', []))
        if not utils.piprun(vdir, f'install --reinstall'
                            f'{pip_args} {pkg} {extras}'):
            return f'Error: failed to {args.name} {pkgname}'

        err = utils.make_links(vdir, pkgname, args, data)
        if err:
            return err

        print(f'{pkgname} upgraded.')

    return None
