# Author: Mark Blakeney, Feb 2024.
'Reinstall an application.'
from __future__ import annotations

import shutil
import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from .. import utils
from ..run import run

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.9".')
    parser.add_argument('--system-site-packages', action='store_true',
                        help='allow venv access to system packages. '
                        'Overrides the per-application setting.')
    parser.add_argument('--no-system-site-packages', action='store_true',
                        help='remove venv access to system packages. '
                        'Overrides the per-application setting.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('package', nargs='+',
                        help='application[s] to reinstall')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    pyexe = utils.get_python(args)
    venv_args = utils.make_args((args.verbose, '-v'), (not args.verbose, '-q'),
                                (True, f'--python={pyexe}'))
    pip_args = utils.make_args((args.verbose, '-v'))
    for pkgname in args.package:
        pkgname, vdir = utils.get_package_from_arg(pkgname, args)
        if not vdir:
            return f'Application {pkgname} is not installed.'

        print(f'Reinstalling {pkgname} ..')
        data = utils.get_json(vdir, args) or {}

        if args.system_site_packages or (
                not args.no_system_site_packages and data.get('sys')):
            data['sys'] = True
        else:
            data.pop('sys', None)

        sysp = ' --system-site-packages' if data.get('sys') else ''
        with tempfile.TemporaryDirectory() as tdir:
            tfile = Path(tdir, args._freeze_file)
            shutil.copyfile(vdir / args._freeze_file, tfile)

            # Recreate the vdir
            if not run(f'{args._uv} venv{venv_args}{sysp} {vdir}'):
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

    return None
