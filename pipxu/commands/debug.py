# Author: Mark Blakeney, Feb 2024.
'''
Run an installed application using a debugger.

Tries to work out your preferred debugger from the standard
PYTHONBREAKPOINT environment variable. If not set it defaults to pdb. Or
you can set it explicitly with the -d/--debugger option.
'''

from __future__ import annotations

import os
import re
from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils
from ..run import run

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('-e', '--executable',
                        help='executable to run, '
                        'default is same as "package" name')
    parser.add_argument('-d', '--debugger',
                        help='explicit debugger package to use')
    parser.add_argument('package',
                        help='installed application name')
    parser.add_argument('args', nargs='*',
                        help='options and arguments to pass to application, '
                        'should start with "--"')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    pkgname, vdir = utils.get_package_from_arg(args.package, args)
    if not vdir:
        return f'Application {pkgname} is not installed.'

    if args.debugger:
        debugger = args.debugger
    else:
        debugger = re.sub(r'\..*', '', os.getenv('PYTHONBREAKPOINT', ''))
        if not debugger or debugger == '0':
            debugger = 'pdb'

    python = str(utils.vdir_bin(vdir) / 'python')
    exe = str(args._bin_dir / (args.executable or pkgname))
    run([python, '-m', debugger, exe] + args.args, quiet=True)
    return None
