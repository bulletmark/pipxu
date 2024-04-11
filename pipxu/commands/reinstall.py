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

def reinstall(args: Namespace, pkgname: str, venv_args: str) -> Optional[str]:
    'Reinstall given application'
    pkgname, vdir = utils.get_package_from_arg(pkgname, args)
    if not vdir:
        return f'Application {pkgname} is not installed.'

    print(f'Reinstalling {pkgname} ..')
    data = utils.get_json(vdir, args) or {}
    url = data.get('url')
    pip_args = utils.make_args((args.verbose, '-v'), (url, f'-i "{url}"'))

    if args.system_site_packages:
        data['sys'] = True
    elif args.no_system_site_packages:
        data.pop('sys', None)

    sysp = ' --system-site-packages' if data.get('sys') else ''

    # Use explicit python (or reset) if given, else use what was
    # explicitly specified in original install, else use default
    # python
    nargs = copy(args)
    if args.reset_python:
        data.pop('pyenv', None)
        data.pop('python', None)
    elif args.pyenv:
        data['pyenv'] = args.pyenv
        data.pop('python', None)
    elif args.python:
        data['python'] = args.python
        data.pop('pyenv', None)
    else:
        nargs.pyenv = data.get('pyenv')
        nargs.python = data.get('python')

    pyexe = utils.get_python(nargs)

    with tempfile.TemporaryDirectory() as tdir:
        tfile = Path(tdir, args._freeze_file)
        shutil.copyfile(vdir / args._freeze_file, tfile)

        # Recreate the vdir
        if not run(f'{args._uv} venv{venv_args}{sysp} --python={pyexe} '
                    f'{vdir}'):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to recreate {vdir} for {pkgname}.'

        if not utils.piprun(vdir, f'sync{pip_args} --compile --reinstall '
                            f'{tfile}', args):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to resync {pkgname}'

    err = utils.make_links(vdir, pkgname, args, data)
    if err:
        return err

    print(f'{pkgname} reinstalled.')

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.12"')
    xgroup.add_argument('--reset-python', action='store_true',
                        help='reset any explicit python path or pyenv '
                        'version to default python')
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
    venv_args = utils.make_args((args.verbose, '-v'), (not args.verbose, '-q'))
    for pkgname in utils.get_package_names(args):
        error = reinstall(args, pkgname, venv_args)
        if error:
            return error

    return None
