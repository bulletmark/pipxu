# Author: Mark Blakeney, Feb 2024.
'Common module containing shared functions'
from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from argparse import Namespace
from pathlib import Path
from typing import Iterable, Optional, Sequence

from .run import run

is_windows = platform.system() == 'Windows'

def subenvars(path: str) -> Path:
    'Substitute environment variables in a path string'
    return Path(os.path.expandvars(path)).expanduser()

def get_json(vdir: Path, args: Namespace) -> Optional[dict]:
    'Get JSON data for this virtual environment'
    tgt = vdir.resolve() / args._meta_file
    try:
        with tgt.open() as fp:
            return json.load(fp)
    except Exception:
        return None

def _set_json(vdir: Path, args: Namespace, data: dict) -> Optional[str]:
    'Set JSON data for this virtual environment'
    tgt = vdir.resolve() / args._meta_file
    try:
        with tgt.open('w') as fp:
            json.dump(data, fp)
    except Exception as e:
        return str(e)

    return None

def piprun(vdir: Path, args: Namespace, cmd: list[str],
           **kargs) -> Optional[str]:
    'Run given pip command in the virtual environment'
    # First element in cmd is the command, the rest are arguments. So
    # insert path to virtual environment after the command.
    cmd[1:1] = ['-p', str(vdir.resolve())]
    return run([args._uv, 'pip'] + cmd, **kargs)

def get_versions(vdir: Path, args: Namespace) -> \
        Optional[dict[str, tuple[str, Optional[str]]]]:
    'Return the versions of the packages in the virtual environment'
    if not (out := piprun(vdir, args, ['list'], capture=True)):
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

def make_args(*args: Sequence) -> list[str]:
    'Build a list of args based on (bool, arg1, [arg2]) sequences'
    retlist: list[str] = []
    for alist in args:
        if alist[0]:
            retlist.extend(alist[1:])

    return retlist

def vdir_bin(vdir: Path) -> Path:
    'Return the bin directory for the virtual environment'
    return vdir / ('Scripts' if is_windows else 'bin')

def _load_record(rfile: Path, embedpath: str) -> Iterable[str]:
    'Yield the executable names from a RECORD file'
    with rfile.open() as fp:
        for line in fp:
            line = line.strip()
            if line.startswith(embedpath):
                yield Path(line.split(',', 1)[0]).name

def _link_app_files(vdir: Path, tgtdir: Path, pkgname: str,
                    args: Namespace, include_deps: bool) -> Iterable[str]:
    'Link app files from entry_points to tgtdir'
    vpath = vdir_bin(vdir)
    embedpath = '../../../bin/' if vpath.name == 'bin' \
            else f'..\\..\\{vpath.name}\\'

    pkgname = pkgname.replace('-', '_')
    for efile in vdir.glob('**/*.dist-info/RECORD'):
        if include_deps or efile.parent.name.startswith(f'{pkgname}-'):
            for app in _load_record(efile, embedpath):
                srcfile = vpath / app
                if srcfile.is_file() and not srcfile.is_symlink() and \
                      (srcfile.stat().st_mode & 0o111) == 0o111:
                    tgtfile = tgtdir / app
                    if tgtfile.is_symlink():
                        tgtfile.unlink()

                    if args.verbose:
                        print(f'Linking "{srcfile}" -> "{tgtfile}"')

                    tgtfile.parent.mkdir(parents=True, exist_ok=True)
                    tgtfile.symlink_to(srcfile)
                    yield srcfile.name

def _link_all_files(srcdir: Path, tgtdir: Path, pat: str,
                    verbose: bool) -> None:
    'Link files from srcdir to tgtdir'
    for srcfile in srcdir.glob(pat):
        tgtfile = tgtdir / srcfile.relative_to(srcdir)
        if tgtfile.is_symlink():
            tgtfile.unlink()

        if verbose:
            print(f'Linking "{srcfile}" -> "{tgtfile}"')

        tgtfile.parent.mkdir(parents=True, exist_ok=True)
        tgtfile.symlink_to(srcfile)

def _unlink_all_files(vdir: Path, args: Namespace) -> None:
    'Unlink all link files'
    dirlist: list[tuple[Path, str]] = [(args._bin_dir, '*')]
    if args._man_dir.is_dir():
        dirlist.append((args._man_dir, '*/*'))

    for srcdir, pat in dirlist:
        if srcdir.is_dir():
            for file in srcdir.glob(pat):
                if file.is_symlink() and vdir in file.resolve().parents:
                    if args.verbose:
                        print(f'Removing link "{file}"')
                    file.unlink()

def make_links(vdir: Path, pkgname: str, args: Namespace,
               data: Optional[dict]) -> Optional[str]:
    '[Re-]create app and man page links for package'

    vdir = vdir.resolve()

    # Unlink any existing links
    _unlink_all_files(vdir, args)

    # Link the package applications
    if not data and not (data := get_json(vdir, args)):
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

    if not (freeze := piprun(vdir, args, ['freeze'], capture=True)):
        return 'Error: Failed to fetch freeze list.'

    (vdir / args._freeze_file).write_text(freeze)
    data['apps'] = sorted(apps)
    return _set_json(vdir, args, data)

def rm_vdir(vdir: Path, args: Namespace) -> None:
    'Remove all links that point into the virtual environment'
    vdir = vdir.resolve()
    _unlink_all_files(vdir, args)

    # Remove the venv
    if vdir.exists():
        if args.verbose:
            print(f'Removing "{vdir}"')

        shutil.rmtree(vdir)

def add_or_remove_pkg(vdir: Path, args: Namespace, pkgname: str,
                      pkgs: list[str], *,
                      add: bool, data: Optional[dict] = None) -> Optional[str]:
    'Record the addition/removal of a package into the virtual environment'
    if not data:
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

    if args.verbose:
        print(f'Removing link "{pdir}"')
    pdir.unlink()

    rm_vdir(vdir, args)
    return True

def get_all_pkg_venvs(args: Namespace) -> Iterable[tuple[Path, dict]]:
    'Return a list of all virtual environments and their JSON data'
    for pdir in sorted(args._packages_dir.iterdir()):
        if data := get_json(pdir, args):
            yield pdir, data

def get_package_from_arg(name: str, args: Namespace) \
        -> tuple[str, Optional[Path]]:
    'Return the package name + vdir corresponding to the given arg, if any'
    if name in {'.', '..'} or os.sep in name:
        if not (namepath := Path(name).resolve()).is_dir():
            return name, None

        # Work out the package name from the current path. We look for
        # the closest parent (i.e. longest path) across all matching
        # application editpaths, unless we find an exact match then just
        # use that.
        candidates = {}
        for pdir, data in get_all_pkg_venvs(args):
            if data and (path := data.get('editpath')):
                if (path := Path(path)) == namepath:
                    # We have an exact match so use it and ignore any
                    # previous candidates.
                    name = pdir.name
                    break
                if path in namepath.parents:
                    # This path has a candidate parent, so record it.
                    candidates[len(path.parts)] = pdir.name
        else:
            if not candidates:
                return name, None

            name = candidates[max(candidates)]

    path = (args._packages_dir / name).resolve()
    return name, (path if path.exists() else None)

def _rm_path(path: Path) -> None:
    'Remove the given path'
    print(f'Purging stray "{path}"', file=sys.stderr)
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()

def purge_old_files(args: Namespace) -> None:
    'Clean out any old virtual environments, packages, and executables'
    # Remove any packages that do not point to a dir in the venvs directory
    valids_venvs = set()
    for pkg in args._packages_dir.iterdir():
        vdir = pkg.resolve()
        if vdir.parent != args._venvs_dir or not vdir.is_dir() \
                or not vdir.name.isdigit():
            _rm_path(pkg)
        else:
            valids_venvs.add(vdir.name)

    # Remove any venvs that are not in the packages directory
    for vdir in args._venvs_dir.iterdir():
        if vdir.name not in valids_venvs:
            _rm_path(vdir)

    # Remove any executables that point to a non-existent path
    for exe in args._bin_dir.iterdir():
        rexe = exe.resolve()
        if args._venvs_dir in rexe.parents and not rexe.exists():
            _rm_path(exe)

def get_package_names(args: Namespace) -> list[str]:
    'Return a list of validated package names based on command line args'
    if args.all:
        if not args.skip and args.package:
            args.parser.error('Can not specify package[s] with '
                            '--all unless also specifying --skip.')
    else:
        if args.skip:
            args.parser.error('--skip can only be specified with --all.')

        if not args.package:
            args.parser.error('Must specify at least one package, or --all.')

    given_names = set(args.package)
    all_names = set(f.name for f in args._packages_dir.iterdir() if f.is_dir())

    if (unknown := given_names - all_names):
        s = 's' if len(unknown) > 1 else ''
        sys.exit(f'Error: Unknown package{s}: {", ".join(unknown)}')

    return sorted(all_names - given_names) if args.all else args.package

def get_python(args: Namespace) -> Path:
    'Return the python executable based on command line args'
    return subenvars(args.python) if args.python else args._pyexe

def version() -> str:
    'Return the version of this package'
    from importlib.metadata import version
    try:
        ver = version(Path(sys.argv[0]).stem)
    except Exception:
        ver = 'unknown'

    return ver
