# Author: Mark Blakeney, Feb 2024.
'''
Install Python applications into isolated virtual environments and
create links to the executables in a bin directory for your PATH. Like
pipx but uses uv instead of venv + pip.
'''
from __future__ import annotations

import argparse
import importlib
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Optional

import platformdirs

from .run import run
from . import utils

DEFUV = 'uv'

# Some constants
MOD = Path(__file__)
PROG = MOD.stem
CNFFILE = platformdirs.user_config_path(f'{PROG}-flags.conf')

def path_check(bin_name: str, bin_dir: Path) -> str:
    'Check and report that users PATH is set up correctly'
    path = os.getenv('PATH')
    if not path:
        return 'WARNING: Your PATH is not set.'

    if str(bin_dir) not in path.split(':'):
        return f'WARNING: Your PATH does not contain {bin_name} ({bin_dir}).'

    return f'Your PATH contains {bin_name} ({bin_dir}).'

def main() -> Optional[str]:
    'Main code'
    mainparser = argparse.ArgumentParser(description=__doc__,
        epilog='Note you can set default starting global options '
        f'in {CNFFILE}.')
    mainparser.add_argument('--uv', metavar='uv_path',
                            help=f'path to uv executable, default="{DEFUV}"')
    mainparser.add_argument('-m', '--no-man-pages', action='store_true',
                            help='do not install package man pages')
    mainparser.add_argument('-V', '--version', action='store_true',
                            help=f'just print {PROG} version and exit')
    subparser = mainparser.add_subparsers(title='Commands',
            dest='func')

    # Iterate over the commands to set up their parsers
    progs = {}
    for modfile in sorted((MOD.parent / 'commands').glob('[!_]*.py')):
        name = modfile.stem
        mod = importlib.import_module(f'{PROG}.commands.{name}')
        docstr = mod.__doc__.strip().split('\n\n')[0] if mod.__doc__ else None
        parser = subparser.add_parser(name, description=mod.__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                help=docstr)

        progs[name] = parser.prog

        if hasattr(mod, 'init'):
            mod.init(parser)

        if not hasattr(mod, 'main'):
            mainparser.error(f'"{name}" command must define a main()')

        parser.set_defaults(func=mod.main, parser=parser, name=name)

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

    progu = PROG.upper()

    homedir = os.getenv(f'{progu}_HOME')
    bindir = os.getenv(f'{progu}_BIN_DIR')
    mandir = os.getenv(f'{progu}_MAN_DIR')
    pyexe = os.getenv(f'{progu}_DEFAULT_PYTHON', 'python3')

    if os.geteuid() == 0:
        home_dir = Path(homedir if homedir else f'/opt/{PROG}')
        bin_dir = Path(bindir if bindir else '/usr/local/bin')
        man_dir = Path(mandir if mandir else '/usr/local/share/man')
    else:
        home_dir = Path(homedir) if homedir else \
                        (platformdirs.user_data_path() / PROG)
        bin_dir = Path(bindir) if bindir else \
                Path('~/.local/bin').expanduser()
        man_dir = Path(mandir) if mandir else \
                Path('~/.local/share/man').expanduser()

    if not args.func:
        mainparser.print_help()
        print('\nEnvironment:')
        print(f'{progu}_HOME = {home_dir}')
        print(f'{progu}_BIN_DIR = {bin_dir}')
        print(f'{progu}_MAN_DIR = {man_dir}')
        print(f'{progu}_DEFAULT_PYTHON = {pyexe}')
        print()
        print(path_check(f'{progu}_BIN_DIR', bin_dir))
        return None

    # Ensure uv is installed/available
    uv = args.uv or DEFUV
    version = run(f'{uv} --version', capture=True)
    if not version:
        if args.uv:
            return f'Error: uv program not found at "{uv}"'

        return f'Error: {uv} program must be installed, and in your PATH '\
                'or specified with --uv option.'

    # Keep some useful info in the namespace passed to the command
    args._uv = uv
    args._packages_dir = home_dir / 'packages'
    args._packages_dir.mkdir(parents=True, exist_ok=True)
    args._venvs_dir = home_dir / 'venvs'
    args._venvs_dir.mkdir(parents=True, exist_ok=True)
    args._bin_dir = bin_dir
    args._man_dir = man_dir
    args._pyexe = pyexe
    args._prog = PROG
    args._meta = f'{PROG}_metadata.json'
    if not hasattr(args, 'verbose'):
        args.verbose = False

    # Purge any old venvs left lying around
    utils.purge_old_venvs(args)

    # Run the command that the user specified
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())
