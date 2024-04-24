# Author: Mark Blakeney, Feb 2024.
'Run pip with given arguments on virtual environment for the given application.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('package',
                        help='installed application name')
    parser.add_argument('args', nargs='*',
                        help='arguments to pass to uv pip, '
                        'should start with "--".')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    pkgname, vdir = utils.get_package_from_arg(args.package, args)
    if not vdir:
        return f'Application {pkgname} is not installed.'

    if not utils.piprun(vdir, args, args.args, quiet=True):
        return f'Error: failed to run pip for {pkgname}'
    return None
