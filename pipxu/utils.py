# Author: Mark Blakeney, Feb 2024.
"Common module containing shared functions"

from __future__ import annotations

import json
import os
import shutil
import sys
from argparse import Namespace
from pathlib import Path
from typing import Iterable, Sequence

from .run import run

HOME = Path.home()


def subenvars(path: str, *, resolve: bool = False) -> Path:
    "Substitute environment variables in a path string"
    spath = Path(os.path.expandvars(path)).expanduser()
    return spath.resolve() if resolve else spath


def unexpanduser(path: str | Path) -> str:
    "Return path name, with $HOME replaced by ~ (opposite of Path.expanduser())"
    ppath = Path(path)

    if ppath.parts[: len(HOME.parts)] != HOME.parts:
        return str(path)

    return str(Path('~', *ppath.parts[len(HOME.parts) :]))


def get_json(vdir: Path, args: Namespace) -> dict | None:
    "Get JSON data for this virtual environment"
    tgt = vdir.resolve() / args._meta_file
    try:
        with tgt.open() as fp:
            return json.load(fp)
    except Exception:
        return None


def _set_json(vdir: Path, args: Namespace, data: dict) -> str | None:
    "Set JSON data for this virtual environment"
    tgt = vdir.resolve() / args._meta_file
    try:
        with tgt.open('w') as fp:
            json.dump(data, fp)
    except Exception as e:
        return str(e)

    return None


def piprun(vdir: Path, args: Namespace, cmd: list[str], **kargs) -> str | None:
    "Run given pip command in the virtual environment"
    # First element in cmd is the command, the rest are arguments. So
    # insert path to virtual environment after the command.
    cmd[1:1] = ['-p', str(vdir.resolve())]
    return run([args._uv, 'pip'] + cmd, **kargs)


def get_versions(
    vdir: Path, args: Namespace
) -> dict[str, tuple[str, str | None]] | None:
    "Return the versions of the packages in the virtual environment"
    if not (out := piprun(vdir, args, ['list', '-q'], capture=True)):
        return None

    found = False
    data: dict[str, tuple[str, str | None]] = {}
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
    "Build a list of args based on (bool, arg1, [arg2]) sequences"
    retlist: list[str] = []
    for alist in args:
        if alist[0]:
            retlist.extend(alist[1:])

    return retlist


def vdir_bin(vdir: Path) -> Path:
    "Return the bin directory for the virtual environment"
    return vdir / 'bin'


def _load_record(rfile: Path) -> Iterable[str]:
    "Yield the executable names from a RECORD file"
    with rfile.open() as fp:
        for line in fp:
            line = line.strip()
            if line.startswith('../../../bin/'):
                yield Path(line.split(',', 1)[0]).name


def _link_app_files(
    vdir: Path, tgtdir: Path, pkgname: str, args: Namespace, include_deps: bool
) -> Iterable[str]:
    "Link app files from entry_points to tgtdir"
    vpath = vdir_bin(vdir)

    key = pkgname.replace('-', '_').lower() + '-'
    for efile in vdir.glob('**/*.dist-info/RECORD'):
        if include_deps or efile.parent.name.lower().startswith(key):
            for app in _load_record(efile):
                srcfile = vpath / app
                if (
                    srcfile.is_file()
                    and not srcfile.is_symlink()
                    and (srcfile.stat().st_mode & 0o111) == 0o111
                ):
                    tgtfile = tgtdir / app
                    if tgtfile.is_symlink():
                        tgtfile.unlink()

                    if args.verbose:
                        print(f'Linking "{srcfile}" -> "{tgtfile}"')

                    tgtfile.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        tgtfile.symlink_to(srcfile)
                    except Exception as e:
                        print(f'Error: {e}', file=sys.stderr)
                        return

                    yield srcfile.name


def _link_all_files(srcdir: Path, tgtdir: Path, pat: str, verbose: bool) -> None:
    "Link files from srcdir to tgtdir"
    for srcfile in srcdir.glob(pat):
        tgtfile = tgtdir / srcfile.relative_to(srcdir)
        if tgtfile.is_symlink():
            tgtfile.unlink()

        if verbose:
            print(f'Linking "{srcfile}" -> "{tgtfile}"')

        tgtfile.parent.mkdir(parents=True, exist_ok=True)
        try:
            tgtfile.symlink_to(srcfile)
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)


def _unlink_all_files(vdir: Path, args: Namespace) -> None:
    "Unlink all link files"
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


def make_links(
    vdir: Path, pkgname: str, args: Namespace, data: dict | None
) -> str | None:
    "[Re-]create app and man page links for package"

    vdir = vdir.resolve()

    # Unlink any existing links
    _unlink_all_files(vdir, args)

    # Link the package applications
    if not data and not (data := get_json(vdir, args)):
        return 'Error: No JSON data found.'

    include_deps = bool(
        args.include_deps if hasattr(args, 'include_deps') else data.get('deps')
    )

    apps = list(_link_app_files(vdir, args._bin_dir, pkgname, args, include_deps))

    # Link all the man pages
    if not args.no_man_pages:
        _link_all_files(vdir / 'share' / 'man', args._man_dir, '*/*', args.verbose)

    # Save the apps in the JSON data
    if not apps:
        return f'Error: {pkgname} has no executables to install.'

    if not (freeze := piprun(vdir, args, ['freeze'], capture=True)):
        return 'Error: Failed to fetch freeze list.'

    (vdir / args._freeze_file).write_text(freeze)
    data['apps'] = sorted(apps)
    return _set_json(vdir, args, data)


def rm_vdir(vdir: Path, args: Namespace) -> None:
    "Remove all links that point into the virtual environment"
    vdir = vdir.resolve()
    _unlink_all_files(vdir, args)

    # Remove the venv
    if vdir.exists():
        if args.verbose:
            print(f'Removing "{vdir}"')

        shutil.rmtree(vdir)


def _pkg_merge(inset: list[str], changeset: list[str], add: bool) -> Iterable[str]:
    "Merge a new list of package names/requirements"
    from packaging.requirements import Requirement

    inset_names = {Requirement(p).name: p for p in inset}
    changeset_names = {Requirement(p).name: p for p in changeset}

    if add:
        inset_names.update(changeset_names)
    else:
        for k in changeset_names:
            inset_names.pop(k, None)

    return inset_names.values()


def add_or_remove_pkg(
    vdir: Path,
    args: Namespace,
    pkgname: str,
    pkgs: list[str],
    *,
    add: bool,
    data: dict | None = None,
) -> str | None:
    "Record the addition/removal of a package into the virtual environment"
    if not data:
        data = get_json(vdir, args)
        if not data:
            return 'No JSON data found'

    newpkgs = _pkg_merge(data.get('injected', []), pkgs, add)

    if newpkgs:
        data['injected'] = sorted(newpkgs)
    else:
        data.pop('injected', None)

    return make_links(vdir, pkgname, args, data)


def rm_package(pkgname: str, args: Namespace) -> bool:
    "Remove this package"
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
    "Return a list of all virtual environments and their JSON data"
    for pdir in sorted(args._packages_dir.iterdir()):
        if data := get_json(pdir, args):
            yield pdir, data


def _get_package_if_dir(name: str, args: Namespace) -> str | None:
    "Convert the given name if it corresponds to a package directory"
    if name not in {'.', '..'} and os.sep not in name:
        return name

    if not (namepath := Path(name).resolve()).is_dir():
        return None

    # Work out the package name from the current path. We look for
    # the closest parent (i.e. longest path) across all matching
    # application editpaths, unless we find an exact match then just
    # use that.
    candidates = {}
    for pdir, data in get_all_pkg_venvs(args):
        if data and (path := data.get('editpath')):
            # If we have an exact match then use it and ignore any
            # previous candidates.
            if (path := Path(path).expanduser()) == namepath:
                return pdir.name

            if path in namepath.parents:
                # This path has a candidate parent, so record it.
                candidates[len(path.parts)] = pdir.name

    return candidates[max(candidates)] if candidates else None


def get_package_from_arg(name: str, args: Namespace) -> tuple[str, Path | None]:
    "Return the package name + vdir corresponding to the given arg, if any"
    if not (pkg := _get_package_if_dir(name, args)):
        return name, None

    vdir = (args._packages_dir / pkg).resolve()
    return pkg, (vdir if vdir.exists() else None)


def _rm_path(path: Path) -> None:
    "Remove the given path"
    print(f'Purging stray "{path}"', file=sys.stderr)
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def purge_old_files(args: Namespace) -> None:
    "Clean out any old virtual environments, packages, and executables"
    # Remove any packages that do not point to a dir in the venvs directory
    valids_venvs = set()
    for pkg in args._packages_dir.iterdir():
        vdir = pkg.resolve()
        if (
            vdir.parent != args._venvs_dir
            or not vdir.is_dir()
            or not vdir.name.isdigit()
        ):
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
    "Return a list of validated package names based on command line args"
    if args.all:
        if not args.skip and args.package:
            args.parser.error(
                'Can not specify package[s] with --all unless also specifying --skip.'
            )
    else:
        if args.skip:
            args.parser.error('--skip can only be specified with --all.')

        if not args.package:
            args.parser.error('Must specify at least one package, or --all.')

    given_names = set((_get_package_if_dir(p, args) or p) for p in args.package)
    all_names = set(f.name for f in args._packages_dir.iterdir() if f.is_dir())

    if unknown := given_names - all_names:
        s = 's' if len(unknown) > 1 else ''
        sys.exit(f'Error: Unknown package{s}: {", ".join(unknown)}')

    return sorted(all_names - given_names) if args.all else args.package


def get_python(args: Namespace) -> Path:
    "Return the python executable based on command line args"
    return subenvars(args.python) if args.python else args._pyexe


def version() -> str:
    "Return the version of this package"
    from importlib.metadata import version

    try:
        ver = version(Path(sys.argv[0]).stem)
    except Exception:
        ver = 'unknown'

    return ver
