# Author: Mark Blakeney, Feb 2024.
# PYTHON_ARGCOMPLETE_OK
'''
Install Python applications into isolated virtual environments and
create links to the executables in a bin directory for your PATH. Like
pipx but uses uv instead of venv + pip.
'''
from __future__ import annotations

import importlib
import os
import re
import shlex
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

import argcomplete
import platformdirs

from . import utils
from .run import run

DEFUV = 'uv'
MIN_UV_VERSION = '0.1.33'
DEFPY = 'python' if utils.is_windows else 'python3'

# Some constants
MOD = Path(__file__)
PROG = MOD.stem
PROGU = PROG.upper()
CNFFILE = platformdirs.user_config_path(f'{PROG}-flags.conf')

def calc_version(verstr: str) -> tuple[int, ...]:
    'Calculate a version tuple from a version string'
    return tuple(int(x) for x in verstr.split('.'))

def is_admin() -> bool:
    'Check if we are running as root'
    if utils.is_windows:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore

    return os.geteuid() == 0

def path_check(bin_name: str, bin_dir: str) -> str:
    'Check and report that users PATH is set up correctly'
    if not (path := os.getenv('PATH')):
        return 'WARNING: Your PATH is not set.'

    in_path = bin_dir.lower() in path.split(';') if utils.is_windows \
            else bin_dir in path.split(':')

    if not in_path:
        return f'WARNING: Your PATH does not contain {bin_name} ({bin_dir}).'

    return f'Your PATH contains {bin_name} ({bin_dir}).'

def main() -> Optional[str]:
    'Main code'
    mainparser = ArgumentParser(description=__doc__,
        epilog='Note you can set default starting global options '
        f'in {CNFFILE}.')
    mainparser.add_argument('--uv', metavar='uv_path',
                            help=f'path to uv executable, default="{DEFUV}"')
    mainparser.add_argument('-m', '--no-man-pages', action='store_true',
                            help='do not install package man pages')
    mainparser.add_argument('--home',
                            help=f'specify {PROGU}_HOME')
    mainparser.add_argument('--bin-dir',
                            help=f'specify {PROGU}_BIN_DIR')
    mainparser.add_argument('--man-dir',
                            help=f'specify {PROGU}_MAN_DIR')
    mainparser.add_argument('--default-python',
                            help='path to default python executable, '
                            f'default="{DEFPY}"')
    mainparser.add_argument('-V', '--version', action='store_true',
                            help=f'just print {PROG} version and exit')
    subparser = mainparser.add_subparsers(title='Commands',
            dest='func')

    # Iterate over the commands to set up their parsers
    for modfile in sorted((MOD.parent / 'commands').glob('[!_]*.py')):
        name = modfile.stem
        mod = importlib.import_module(f'{PROG}.commands.{name}')
        docstr = mod.__doc__.strip().split('\n\n')[0] if mod.__doc__ else None
        parser = subparser.add_parser(name, description=mod.__doc__,
                                      help=docstr)

        if hasattr(mod, 'init'):
            mod.init(parser)

        if not hasattr(mod, 'main'):
            mainparser.error(f'"{name}" command must define a main()')

        parser.set_defaults(func=mod.main, parser=parser, name=name)

    # Command arguments are now defined, so we can set up argcomplete
    argcomplete.autocomplete(mainparser)

    # Merge in default args from user config file. Then parse the
    # command line.
    if CNFFILE.exists():
        with CNFFILE.open() as fp:
            lines = [re.sub(r'#.*$', '', line).strip() for line in fp]
        cnflines = ' '.join(lines).strip()
    else:
        cnflines = ''

    args = mainparser.parse_args(shlex.split(cnflines) + sys.argv[1:])

    if args.version:
        print(f'{PROG}=={utils.version()}')
        return None

    is_root = is_admin()
    home_dir = args.home or os.getenv(f'{PROGU}_HOME')
    bin_dir = args.bin_dir or os.getenv(f'{PROGU}_BIN_DIR')
    man_dir = args.man_dir or os.getenv(f'{PROGU}_MAN_DIR')

    pyexe = utils.subenvars(args.default_python if args.default_python
                else (os.getenv(f'{PROGU}_DEFAULT_PYTHON') or DEFPY))

    if not home_dir:
        home_dir = f'/opt/{PROG}' if is_root else \
                f'{platformdirs.user_data_dir()}/{PROG}'
    if not bin_dir:
        bin_dir = '/usr/local/bin' if is_root else '~/.local/bin'
    if not man_dir:
        man_dir = '/usr/local/share/man' if is_root else '~/.local/share/man'

    home_dir = utils.subenvars(home_dir)
    bin_dir = utils.subenvars(bin_dir)
    man_dir = utils.subenvars(man_dir)

    if not args.func:
        mainparser.print_help()
        print('\nEnvironment:')
        print(f'{PROGU}_HOME = {home_dir}')
        print(f'{PROGU}_BIN_DIR = {bin_dir}')
        print(f'{PROGU}_MAN_DIR = {man_dir}')
        print(f'{PROGU}_DEFAULT_PYTHON = {pyexe}')
        print()
        print(path_check(f'{PROGU}_BIN_DIR', str(bin_dir)))
        return None

    # Ensure uv is installed/available
    uv = args.uv or DEFUV
    if not (verstr := run((uv, '--version'), capture=True, ignore_error=True)):
        if args.uv:
            return f'Error: specified uv "{uv}" program not found.'

        return f'Error: {uv} program must be installed, and in your PATH '\
                'or specified with --uv option.'

    uv_vers = verstr.split()[1]
    if calc_version(uv_vers) < calc_version(MIN_UV_VERSION):
        return f'Error: {uv} version is {uv_vers} '\
                f'but must be at least {MIN_UV_VERSION}.'

    # Keep some useful info in the namespace passed to the command
    args._uv = uv
    args._lockfile = home_dir / f'.{PROG}.lock'
    args._packages_dir = home_dir / 'packages'
    args._packages_dir.mkdir(parents=True, exist_ok=True)
    args._venvs_dir = home_dir / 'venvs'
    args._venvs_dir.mkdir(parents=True, exist_ok=True)
    args._bin_dir = bin_dir
    args._bin_dir.mkdir(parents=True, exist_ok=True)
    args._man_dir = man_dir
    if not args.no_man_pages:
        args._man_dir.mkdir(parents=True, exist_ok=True)
    args._pyexe = pyexe
    args._prog = PROG
    args._meta_file = f'{PROG}_metadata.json'
    args._freeze_file = f'{PROG}_freeze.txt'
    if not hasattr(args, 'verbose'):
        args.verbose = False

    # Purge any old files left lying around
    utils.purge_old_files(args)

    # Run the command that the user specified
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())
