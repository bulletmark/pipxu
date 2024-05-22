# Author: Mark Blakeney, Feb 2024.
'Install one or more Python applications using isolated virtual environments.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from filelock import FileLock

from .. import utils
from ..run import run

MAX_VDIRS = 1_000_000

def _get_next_vdir(vdirbase: Path) -> Optional[Path]:
    'Return the first available venv directory'
    vdirs = set(int(f.name) for f in vdirbase.iterdir())
    for n in range(1, MAX_VDIRS + 1):
        if n not in vdirs:
            return vdirbase / str(n)

    return None

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-p', '--python',
                        help='specify explicit python executable path')
    parser.add_argument('-f', '--force', action='store_true',
                        help='recreate any already installed venv')
    parser.add_argument('-e', '--editable', action='store_true',
                        help='install application[s] in editable mode')
    parser.add_argument('-d', '--include-deps', action='store_true',
                        help='include executables from dependencies')
    parser.add_argument('--system-site-packages', action='store_true',
                        help='allow venv access to system packages')
    parser.add_argument('-i', '--index-url',
                        help='base URL of Python Package Index')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='give more output')
    parser.add_argument('package', nargs='+',
                        help='application[s] to install')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    pyexe = str(utils.get_python(args))
    venv_args = [args._uv, 'venv', '-p', pyexe] + utils.make_args(
            (args.verbose, '-v'), (not args.verbose, '-q'),
            (args.system_site_packages, '--system-site-packages'))

    pip_args = 'install --compile'.split() + utils.make_args(
            (args.verbose, '-v'), (args.index_url, '-i', args.index_url))
    pip_earg = utils.make_args((args.editable, '-e'))

    vdirbase = args._venvs_dir
    for pkg in args.package:
        # Use a lock file in case we are running multiple installs in parallel
        with FileLock(args._lockfile):
            vdir = _get_next_vdir(vdirbase)
            if not vdir:
                return f'Error: Too many vdirs (>{MAX_VDIRS}) in {vdirbase}'

            # Create the vdir
            if not run(venv_args + [str(vdir)]):
                utils.rm_vdir(vdir, args)
                return f'Error: failed to create {vdir} for {pkg}.'

        python_exe = str((utils.vdir_bin(vdir) / 'python').resolve())
        python_ver = run((python_exe, '-V'), capture=True, ignore_error=True)
        python_ver = python_ver.strip().split()[1] if python_ver else '?ver?'
        print(f'Created "{vdir}" using "{python_exe}" ({python_ver})')

        # Install the package
        if not utils.piprun(vdir, args,
                            pip_args + ['--no-deps'] + pip_earg + [pkg]):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to preinstall "{pkg}".'

        if not (versions := utils.get_versions(vdir, args)):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to get versions for {pkg}.'

        if len(versions) != 1:
            return f'Error: multiple packages qualified: {list(versions)}'

        pkgname, (vers, editpath) = versions.popitem()
        pdir = Path(args._packages_dir, pkgname)

        if pdir.exists():
            if not args.force:
                utils.rm_vdir(vdir, args)
                return f'Error: venv for {pkgname} exists. Use -f to force.'
            print(f'Removing pre-existing {pkgname} venv dir.')
            utils.rm_vdir(pdir, args)
            pdir.unlink()

        if not utils.piprun(vdir, args, pip_args + pip_earg + [pkg]):
            utils.rm_vdir(vdir, args)
            return f'Error: failed to install "{pkg}".'

        pdir.symlink_to(vdir)

        data: dict = {'name': pkgname}
        if editpath:
            data['editpath'] = editpath

        if args.include_deps:
            data['deps'] = True

        if args.system_site_packages:
            data['sys'] = True

        if args.index_url:
            data['url'] = args.index_url

        if args.python:
            data['python'] = args.python

        if err := utils.make_links(vdir, pkgname, args, data):
            pdir.unlink()
            utils.rm_vdir(vdir, args)
            return err

    return None
