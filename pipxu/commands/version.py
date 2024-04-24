# Author: Mark Blakeney, Feb 2024.
'List installed application versions.'
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Optional

from .. import utils

def init(parser: ArgumentParser) -> None:
    'Called to add command arguments to parser at init'
    parser.add_argument('package', nargs='?',
                        help='report specific application and dependent '
                        'package versions')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    def display(pkgname, version):
        ver, loc = version
        if loc:
            ver += f' @ {loc}'
        print(f'{pkgname}=={ver}')

    if args.package:
        pkgname, vdir = utils.get_package_from_arg(args.package, args)
        if not vdir:
            return f'Application {pkgname} not found.'

        if not (versions := utils.get_versions(args._packages_dir / pkgname,
                                               args)):
            return f'Application {pkgname} versions not found.'

        # Reorder version dict to put pkgname first
        if pkgname in versions:
            sversions = {pkgname: versions[pkgname]}
            del versions[pkgname]
            sversions.update(versions)
            versions = sversions

        for pkg, ver in versions.items():
            display(pkg, ver)

        return None

    for pdir, data in utils.get_all_pkg_venvs(args):
        package = pdir.name
        if versions := utils.get_versions(pdir, args):
            display(package, versions.get(package, ("unknown", None)))

    return None
