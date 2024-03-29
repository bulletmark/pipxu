# Author: Mark Blakeney, Feb 2024.
'Common module containing shared functions'
from __future__ import annotations

import json
import os
import shutil
import sys
from argparse import Namespace
from pathlib import Path
from typing import Iterable, Optional

from .run import run

def get_json(vdir: Path, args: Namespace) -> Optional[dict]:
    'Get JSON data for this virtual environment'
    tgt = vdir.resolve() / args._meta
    try:
        with tgt.open() as fp:
            return json.load(fp)
    except Exception:
        return None

def _set_json(vdir: Path, args: Namespace, data: dict) -> Optional[str]:
    'Set JSON data for this virtual environment'
    tgt = vdir.resolve() / args._meta
    try:
        with tgt.open('w') as fp:
            json.dump(data, fp)
    except Exception as e:
        return str(e)

    return None

def piprun(vdir: Path, cmd: str, **args) -> Optional[str]:
    'Run given pip command in the virtual environment'
    os.environ['VIRTUAL_ENV'] = str(vdir.resolve())
    return run(f'uv pip {cmd}', **args)

def get_versions(vdir: Path) -> Optional[dict[str, tuple[str, Optional[str]]]]:
    'Return the versions of the packages in the virtual environment'
    out = piprun(vdir, 'list', capture=True)
    if not out:
        return None

    found = False
    data: dict[str, tuple[str, Optional[str]]] = {}
    for line in out.splitlines():
        if line.startswith('-'):
            found = True
        elif found:
            fields = line.split(maxsplit=2)
            if len(fields) == 2:
                data[fields[0]] = fields[1], None
            else:
                data[fields[0]] = fields[1], fields[2]

    return data

def make_args(*args: tuple[bool, str]) -> str:
    'Build a string of args based on (bool, arg) pairs'
    argstr = ' '.join(v2 for v1, v2 in args if v1)
    return ' ' + argstr if argstr else ''

def _load_record(rfile: Path) -> Iterable[str]:
    'Yield the executable names from a RECORD file'
    with rfile.open() as fp:
        for line in fp:
            line = line.strip()
            if line.startswith('../../../bin/'):
                yield Path(line.split(',', 1)[0]).name

def _link_exists(path: Path) -> bool:
    'Return True if the path is a link (regardless if the target exists)'
    # Equivalent to path.exists(follow_symlinks=False) on Python < 3.12.
    try:
        exists = path.lstat()
    except Exception:
        return False

    return bool(exists)

def _link_app_files(vdir: Path, tgtdir: Path, pkgname: str,
                    args: Namespace, include_deps: bool) -> Iterable[str]:
    'Link app files from entry_points to tgtdir'
    pkgname = pkgname.replace('-', '_')
    for efile in vdir.glob('**/*.dist-info/RECORD'):
        if include_deps or efile.parent.name.startswith(f'{pkgname}-'):
            for app in _load_record(efile):
                srcfile = vdir / 'bin' / app
                if srcfile.is_file() and not srcfile.is_symlink() and \
                      (srcfile.stat().st_mode & 0o111) == 0o111:
                    tgtfile = tgtdir / app
                    if _link_exists(tgtfile):
                        tgtfile.unlink()

                    if args.verbose:
                        print(f'Linking {srcfile} -> {tgtfile}')

                    tgtfile.parent.mkdir(parents=True, exist_ok=True)
                    tgtfile.symlink_to(srcfile)
                    yield srcfile.name

def _link_all_files(srcdir: Path, tgtdir: Path, pat: str,
                    verbose: bool) -> None:
    'Link files from srcdir to tgtdir'
    for srcfile in srcdir.glob(pat):
        tgtfile = tgtdir / srcfile.relative_to(srcdir)
        if _link_exists(tgtfile):
            tgtfile.unlink()

        if verbose:
            print(f'Linking {srcfile} -> {tgtfile}')

        tgtfile.parent.mkdir(parents=True, exist_ok=True)
        tgtfile.symlink_to(srcfile)

def _unlink_all_files(vdir: Path, args: Namespace) -> None:
    'Unlink all link files'
    for srcdir, pat in ((args._bin_dir, '*'), (args._man_dir, '*/*')):
        if srcdir.is_dir():
            for file in srcdir.glob(pat):
                if file.is_symlink() and vdir in file.resolve().parents:
                    if args.verbose:
                        print(f'Removing link {file}')
                    file.unlink()

def make_links(vdir: Path, pkgname: str, args: Namespace,
               data: Optional[dict]) -> Optional[str]:
    '[Re-]create app and man page links for package'

    vdir = vdir.resolve()

    # Unlink any existing links
    _unlink_all_files(vdir, args)

    # Link the package applications
    data = data or get_json(vdir, args)
    if not data:
        return 'Error: No JSON data found.'

    include_deps = bool(args.include_deps if hasattr(args, 'include_deps')
                        else data.get('deps'))

    apps = list(_link_app_files(vdir, args._bin_dir, pkgname, args,
                                include_deps))

    # Link all the man pages
    if not args.no_man_pages:
        _link_all_files(vdir / 'share' / 'man', args._man_dir, '*/*',
                        args.verbose)

    # Save the apps in the JSON data
    if not apps:
        return f'Error: {pkgname} has no executables to install.'

    data['apps'] = sorted(apps)
    return _set_json(vdir, args, data)

def rm_vdir(vdir: Path, args: Namespace) -> None:
    'Remove all links that point into the virtual environment'
    vdir = vdir.resolve()
    _unlink_all_files(vdir, args)

    # Remove the venv
    if args.verbose:
        print(f'Removing {vdir}')

    shutil.rmtree(vdir)

def add_or_remove_pkg(vdir: Path, pkgname: str, pkgs: list[str],
                      args: Namespace, *, add: bool) -> Optional[str]:
    'Record the addition/removal of a package into the virtual environment'
    data = get_json(vdir, args)
    if not data:
        return 'No JSON data found'

    dataset = set(data.get('injected') or [])
    pkgset = set(pkgs)
    newset = (dataset | pkgset) if add else (dataset - pkgset)

    if newset:
        data['injected'] = sorted(list(newset))
    else:
        data.pop('injected', None)

    return make_links(vdir, pkgname, args, data)

def rm_package(pkgname: str, args: Namespace) -> bool:
    'Remove this package'
    pdir = args._packages_dir / pkgname
    if not pdir.exists():
        return False

    vdir = pdir.resolve()
    pdir.unlink()
    rm_vdir(vdir, args)
    return True

def get_all_pkg_venvs(args: Namespace) -> Iterable[tuple[Path, dict]]:
    'Return a list of all virtual environments and their JSON data'
    for pdir in sorted(args._packages_dir.iterdir()):
        data = get_json(pdir, args)
        if data:
            yield pdir, data

def get_package_from_arg(name: str, args: Namespace) \
        -> tuple[str, Optional[Path]]:
    'Return the package name + vdir corresponding to the given arg, if any'
    if name == '.' or os.sep in name:
        pathstr = str(Path(name).resolve())
        for pdir, data in get_all_pkg_venvs(args):
            if data and data.get('editpath') == pathstr:
                name = pdir.name
                break
        else:
            return name, None

    path = (args._packages_dir / name).resolve()
    return name, (path if path.exists() else None)

def purge_old_venvs(args: Namespace) -> None:
    'Clean out any old virtual environments and package names'
    valids = set(f.resolve().name for f in args._packages_dir.iterdir())
    vdirs = set(f.name for f in args._venvs_dir.iterdir())

    # Remove any venvs that are not in the packages directory
    for vdir in (vdirs - valids):
        tgt = args._venvs_dir / vdir
        print(f'Purging stray venv {tgt}', file=sys.stderr)
        if tgt.is_dir():
            rm_vdir(args._venvs_dir / vdir, args)
        else:
            tgt.unlink()

    # Remove any packages that are not in the venvs directory
    for pkg in (valids - vdirs):
        tgt = args._packages_dir / pkg
        print(f'Purging stray package link {tgt}', file=sys.stderr)
        if tgt.is_dir():
            shutil.rmtree(tgt)
        else:
            tgt.unlink()

def get_all_package_names(args: Namespace) -> list[str]:
    'Return a sorted list of all package names'
    return sorted(set(f.name for f in args._packages_dir.iterdir())
                  - set(args.skip or []))

def version() -> str:
    'Return the version of this package'
    if sys.version_info >= (3, 8):
        from importlib.metadata import version
    else:
        from importlib_metadata import version

    try:
        ver = version(Path(sys.argv[0]).stem)
    except Exception:
        ver = 'unknown'

    return ver
