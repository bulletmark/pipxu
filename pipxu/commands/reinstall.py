# Author: Mark Blakeney, Feb 2024.
'Reinstall one, or more, or all applications.'
from __future__ import annotations

import shutil
import tempfile
from argparse import ArgumentParser, Namespace
from copy import copy
from pathlib import Path
from typing import Optional

from .. import utils
from ..run import run

def _reinstall(args: Namespace, pkgname: str,
              venv_args: list[str]) -> Optional[str]:
    'Reinstall given application'
    pkgname, vdir = utils.get_package_from_arg(pkgname, args)
    if not vdir:
        return f'Application {pkgname} is not installed.'

    print(f'Reinstalling {pkgname} ..')
    pip_args = 'sync --compile --reinstall'.split() + \
            utils.make_args((args.verbose, '-v'))

    data = utils.get_json(vdir, args) or {}
    if url := data.get('url'):
        pip_args.extend(['-i', url])

    # Use explicit python (or reset) if given, else use what was
    # explicitly specified in original install, else use default
    # python
    nargs = copy(args)
    if args.reset_python:
        data.pop('python', None)
    elif args.python:
        data['python'] = args.python
    else:
        nargs.python = data.get('python')

    venv_args.extend(['-p', str(utils.get_python(nargs))])

    if args.system_site_packages:
        data['sys'] = True
    elif args.no_system_site_packages:
        data.pop('sys', None)

    if data.get('sys'):
        venv_args.append('--system-site-packages')

    with tempfile.TemporaryDirectory() as tdir:
        tfile = Path(tdir, args._freeze_file)
        shutil.copyfile(vdir / args._freeze_file, tfile)

        # Recreate the vdir
        if not run(venv_args + [str(vdir)]):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to recreate {vdir} for {pkgname}.'

        if not utils.piprun(vdir, args, pip_args + [str(tfile)]):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to resync {pkgname}'

    if err := utils.make_links(vdir, pkgname, args, data):
        return err

    print(f'{pkgname} reinstalled.')
    return None

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    xgroup.add_argument('--reset-python', action='store_true',
                        help='reset any explicit python path to default python')
    ygroup = parser.add_mutually_exclusive_group()
    ygroup.add_argument('--system-site-packages', action='store_true',
                        help='allow venv access to system packages, '
                        'overrides the per-application setting')
    ygroup.add_argument('--no-system-site-packages', action='store_true',
                        help='remove venv access to system packages, '
                        'overrides the per-application setting')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('--all', action='store_true',
                        help='reinstall ALL applications')
    parser.add_argument('--skip', action='store_true',
                        help='skip the specified applications when '
                        'reinstalling all (only can be specified with --all)')
    parser.add_argument('package', nargs='*',
                        help='application[s] to reinstall (or to skip for '
                        '--all --skip)')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    venv_args = [args._uv, 'venv'] + utils.make_args((args.verbose, '-v'),
                                                     (not args.verbose, '-q'))
    for pkgname in utils.get_package_names(args):
        if error := _reinstall(args, pkgname, venv_args.copy()):
            return error

    return None
