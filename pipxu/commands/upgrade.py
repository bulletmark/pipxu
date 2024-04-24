# Author: Mark Blakeney, Feb 2024.
'Upgrade one, or more, or all applications.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def _upgrade(args: Namespace, pkgname: str) -> Optional[str]:
    'Upgrade given package'
    pkgname, vdir = utils.get_package_from_arg(pkgname, args)
    if not vdir:
        return f'Application {pkgname} is not installed.'

    print(f'Upgrading {pkgname} ..')
    data = utils.get_json(vdir, args) or {}
    url = data.get('url')
    pip_args = 'install --compile --reinstall -U'.split() + \
            utils.make_args((args.verbose, '-v'), (url, '-i', url))
    editpath = data.get('editpath')
    if editpath:
        pip_args += ['-e', editpath]
    else:
        pip_args.append(pkgname)

    pip_args += data.get('injected', [])

    if not utils.piprun(vdir, args, pip_args):
        return f'Error: failed to {args.name} {pkgname}'

    err = utils.make_links(vdir, pkgname, args, data)
    if err:
        return err

    print(f'{pkgname} upgraded.')
    return None

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('--all', action='store_true',
                        help='upgrade ALL applications')
    parser.add_argument('--skip', action='store_true',
                        help='skip the specified applications when '
                        'upgrading all (only can be specified with --all)')
    parser.add_argument('package', nargs='*',
                        help='application[s] to upgrade (or to skip for '
                        '--all --skip)')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    for pkgname in utils.get_package_names(args):
        error = _upgrade(args, pkgname)
        if error:
            return error

    return None
