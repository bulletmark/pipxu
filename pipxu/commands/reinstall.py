# Author: Mark Blakeney, Feb 2024.
"Reinstall a package and it's executables."
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional
import shutil
import tempfile
from pathlib import Path

from .. import utils
from ..run import run

def init(parser: ArgumentParser) -> None:
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.9".')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('package', nargs='+',
                        help='package name[s] to upgrade')

def main(args: Namespace) -> Optional[str]:
    pyexe = utils.get_python(args)
    venv_args = utils.make_args((args.verbose, '-v'), (not args.verbose, '-q'),
                                (bool(pyexe), f'--python={pyexe}'))
    pip_args = utils.make_args((args.verbose, '-v'))
    for pkgname in args.package:
        pkgname, vdir = utils.get_package_from_arg(pkgname, args)
        if not vdir:
            return f'package {pkgname} is not installed.'

        data = utils.get_json(vdir, args) or {}

        with tempfile.TemporaryDirectory() as tdir:
            tfile = Path(tdir, args._freeze_file)
            shutil.copyfile(vdir / args._freeze_file, tfile)

            # Recreate the vdir
            if not run(f'uv venv{venv_args} {vdir}'):
                utils.rm_vdir(vdir, args)
                return f'Error: failed to recreate {vdir} for {pkgname}.'

            if not utils.piprun(vdir, f'sync{pip_args} {tfile}'):
                utils.rm_vdir(vdir, args)
                return f'Error: failed to resync {pkgname}'

        err = utils.make_links(vdir, pkgname, args, data)
        if err:
            return err

        print(f'Reinstall of {pkgname} completed.')

    return None
