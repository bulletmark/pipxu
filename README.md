## PIPXU - Install and Run Python Applications in Isolated Environments using UV
[![PyPi](https://img.shields.io/pypi/v/pipxu)](https://pypi.org/project/pipxu/)
[![AUR](https://img.shields.io/aur/version/pipxu)](https://aur.archlinux.org/packages/pipxu/)

[`pipxu`][pipxu] installs a Python application, i.e. a Python package
which has one or more executable programs, into an independent isolated
virtual environment on your system. The package and it's dependencies
are thus insulated from other applications, and from the system Python.
[`pipxu`][pipxu] creates links to the application's executables in a
common directory, which you have in your [PATH][path]. Packages are
typically sourced from [PyPI][pypi], the Python Package Index.

[`pipxu`][pipxu] is a re-implementation of most of the functionality of
the popular [`pipx`][pipx] tool but is **much faster** because it uses
[`uv`][uv] to create and install application virtual environments
instead of [`venv`][venv] and [`pip`][pip] that [`pipx`][pipx] uses.
[`pipxu`][pipxu] code has been developed completely independently of
[`pipx`][pipx] and is not a fork. For compatibility and ease of
migration, the provided commands have the same names as [`pipx`][pipx].
Most commands are implemented, at least for common use cases, although
some command functionality, options, and output are different.

The latest documentation and code is available at
https://github.com/bulletmark/pipxu.

## Usage

Type `pipxu` or `pipxu -h` to view the usage summary:

```
usage: pipxu [-h] [--uv uv_path] [-m] [-V]
                   {inject,install,list,reinstall-all,reinstall,runpip,uninject,uninstall-all,uninstall,upgrade-all,upgrade,version}
                   ...

Install Python applications into isolated virtual environments and create
links to the executables in a bin directory for your PATH. Like pipx but uses
uv instead of venv + pip.

options:
  -h, --help            show this help message and exit
  --uv uv_path          path to uv executable, default="uv"
  -m, --no-man-pages    do not install package man pages
  -V, --version         just print pipxu version and exit

Commands:
  {inject,install,list,reinstall-all,reinstall,runpip,uninject,uninstall-all,uninstall,upgrade-all,upgrade,version}
    inject              Install extra packages into an application's virtual
                        environment.
    install             Install a Python application using an isolated virtual
                        environment.
    list                List Python applications installed by this tool.
    reinstall-all       Reinstall all packages executables.
    reinstall           Reinstall a package's executables.
    runpip              Run pip with given arguments on virtual environment
                        for the given package.
    uninject            Uninstall extra packages from an application's virtual
                        environment.
    uninstall-all       Uninstall all Python applications and their virtual
                        environments.
    uninstall           Uninstall a Python application and it's virtual
                        environment
    upgrade-all         Upgrade all packages and their executables.
    upgrade             Upgrade a package and their executables.
    version             List installed package versions.

Note you can set default starting global options in $HOME/.config/pipxu-
flags.conf.
```

Type `pipxu <command> -h` to see specific help/usage for any
individual command:

### Command `inject`

```
usage: pipxu inject [-h] [-v] package extras [extras ...]

Install extra packages into an application's virtual environment.

positional arguments:
  package        existing package name
  extras         extra package name[s] to inject/install

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
```

### Command `install`

```
usage: pipxu install [-h] [-p PYTHON | -P PYENV] [-f] [-e] [-d] [-v]
                           package [package ...]

Install a Python application using an isolated virtual environment.

positional arguments:
  package               package[s] to install

options:
  -h, --help            show this help message and exit
  -p PYTHON, --python PYTHON
                        specify explicit python executable path
  -P PYENV, --pyenv PYENV
                        pyenv python version to use, i.e. from `pyenv
                        versions`, e.g. "3.9".
  -f, --force           recreate any existing venv
  -e, --editable        install package[s] in editable mode
  -d, --include-deps    include executables from dependencies
  -v, --verbose         give more output
```

### Command `list`

```
usage: pipxu list [-h] [--json] [package ...]

List Python applications installed by this tool.

positional arguments:
  package     list the given package[s] only

options:
  -h, --help  show this help message and exit
  --json      output json instead
```

### Command `reinstall-all`

```
usage: pipxu reinstall-all [-h] [-v] [-U] [-s [SKIP ...]]

Reinstall all packages executables.

options:
  -h, --help            show this help message and exit
  -v, --verbose         give more output
  -U, --upgrade         also upgrade the package[s] to latest version
  -s [SKIP ...], --skip [SKIP ...]
                        skip these packages, e.g. package1 package2
```

### Command `reinstall`

```
usage: pipxu reinstall [-h] [-v] [-U] package [package ...]

Reinstall a package's executables.

positional arguments:
  package        package name[s] to reinstall

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
  -U, --upgrade  also upgrade package[s] to the latest version
```

### Command `runpip`

```
usage: pipxu runpip [-h] package [args ...]

Run pip with given arguments on virtual environment for the given package.

positional arguments:
  package     existing package name
  args        arguments to pass to uv pip. should start with "--".

options:
  -h, --help  show this help message and exit
```

### Command `uninject`

```
usage: pipxu uninject [-h] [-v] package extras [extras ...]

Uninstall extra packages from an application's virtual environment.

positional arguments:
  package        existing package name
  extras         extra package name[s] to uninstall

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
```

### Command `uninstall-all`

```
usage: pipxu uninstall-all [-h] [-v] [-s [SKIP ...]]

Uninstall all Python applications and their virtual environments.

options:
  -h, --help            show this help message and exit
  -v, --verbose         give more output
  -s [SKIP ...], --skip [SKIP ...]
                        skip these packages, e.g. package1 package2
```

### Command `uninstall`

```
usage: pipxu uninstall [-h] [-v] package [package ...]

Uninstall a Python application and it's virtual environment

positional arguments:
  package        package name[s] to uninstall

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
```

### Command `upgrade-all`

```
usage: pipxu upgrade-all [-h] [-v] [-s [SKIP ...]]

Upgrade all packages and their executables.

options:
  -h, --help            show this help message and exit
  -v, --verbose         give more output
  -s [SKIP ...], --skip [SKIP ...]
                        skip these packages, e.g. package1 package2
```

### Command `upgrade`

```
usage: pipxu upgrade [-h] [-v] package [package ...]

Upgrade a package and their executables.

positional arguments:
  package        package name[s] to upgrade

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
```

### Command `version`

```
usage: pipxu version [-h] [package]

List installed package versions.

positional arguments:
  package     report specific package and dependent package versions

options:
  -h, --help  show this help message and exit
```

## Installation and Upgrade

Python 3.7 or later is required. Arch Linux users can install [`pipxu`
from the AUR](https://aur.archlinux.org/packages/pipxu) and skip this
section.

The [`uv`][uv] program is also required.
The following is an easy way to install it, see
[here](https://github.com/astral-sh/uv#getting-started).

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Note [`pipxu` is on PyPI](https://pypi.org/project/pipxu/). Run the tiny
[bootstrap shell
script](https://github.com/bulletmark/pipxu/blob/main/bootstrap.sh)
which installs `pipxu` to a temporary directory then runs `pipxu` from
there to install itself normally.

```
$ curl -LsSf https://raw.githubusercontent.com/bulletmark/pipxu/main/bootstrap.sh | sh
```

To upgrade:

```
$ pipxu upgrade pipxu
```

To uninstall all `pipxu` installed applications, and then uninstall
`pipxu` itself:

```
$ pipxu uninstall-all --skip pipxu
$ pipxu uninstall pipxu
```

## Comparison to pipx

Why would you use [`pipxu`][pipxu] instead of [`pipx`][pipx]? The main
reason is to gain a massive speed improvement. `pipx` uses [`python -m
venv`][venv] to create and install virtual environments and `pip` to
install packages whereas `pipxu` uses `uv` for these operations.
[`uv`][uv] is [a new project](https://astral.sh/blog/uv) written in
[rust](https://www.rust-lang.org/) which has a better design than
[`venv`][venv] + [`pip`][pip], caches aggressively, and is **much
faster**. Also, `pipx` installs `pip` into each virtual environment
using a shared overlay which it has to update periodically so you
sometimes experience `pipx` seeming to hang for a while while this
update occurs. `pipxu` just creates a minimal lean virtual environment
and uses `uv` for all operations so does not need to do this periodic
update.

Note that `pipx` offers some esoteric options and features which `pipxu`
does not have. `pipxu` caters for the common use cases. `pipxu` never
modifies your PATH.

`pipxu` adds some small but handy features not present in `pipx`:

1. `pipxu` faciliates specifying
   [`pyenv`](https://github.com/pyenv/pyenv) python versions with an
   added `-P/--pyenv` command option to `install`.

2. You can do `pipxu` commands on an editable projects (as often used by
   developers) in the current directory by simply typing "`.`" as the
   package name and this works for all commands. E.g. `pipxu uninstall
   .` or `pipxu inject . pudb`. I.e. `pipxu` automatically determines
   the package name associated with the current directory. Note that
   `pipx` accepts "`.`" for the install command, but not for any others.

3. If run as root or with `sudo`, `pipxu` installs applications to a
   global location.

At the time of initial release, the `pipxu` application comprises 701
lines of Python code whereas the `pipx` application is 4300 lines of
Python code.

## Environment Variables

Type `pipxu` without any arguments to see usage and the current
environment. The environment is printed at the bottom of the screen
output as follows:

E.g. run as my user "mark":

```
Environment:
PIPXU_HOME = /home/mark/.local/share/pipxu
PIPXU_BIN_DIR = /home/mark/.local/bin
PIPXU_MAN_DIR = /home/mark/.local/share/man
PIPXU_DEFAULT_PYTHON = python3

Your PATH contains PIPXU_BIN_DIR (/home/mark/.local/bin).
```

Or run as root, or with [`sudo`](https://www.sudo.ws/):

```
Environment:
PIPXU_HOME = /opt/pipxu
PIPXU_BIN_DIR = /usr/local/bin
PIPXU_MAN_DIR = /usr/local/share/man
PIPXU_DEFAULT_PYTHON = python3

WARNING: Your PATH does not contain PIPXU_BIN_DIR (/usr/local/bin).
```

You can set those environment variables to override the defaults if you
want. Note, as seen in the output above, `pipxu` reports if
`PIPXU_BIN_DIR` is included or not in your PATH. To ensure you can run
the applications installed by `pipxu`, that directory **must be in your
PATH**. E.g. for most users on Linux using the default locations, ensure
that `~/.local/bin` is [added to your PATH environment
variable][path].

## Command Default Options

You can add default global options to a personal configuration file
`~/.config/pipxu-flags.conf`. If that file exists then each line of
options will be concatenated and automatically prepended to your `pipxu`
command line arguments. Comments in the file (i.e. `#` and anything
after on a line) are ignored. Type `pipxu` to see all supported options.

At least currently, the global options `--uv` and `--no-man-pages`, are
the only sensible candidates to consider setting as a default.

## License

Copyright (C) 2024 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License. This program is free software:
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation,
either version 3 of the License, or any later version. This program is
distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License at
<http://www.gnu.org/licenses/> for more details.

[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://github.com/pypa/pipx
[pipxu]: https://github.com/bulletmark/pipxu
[uv]: https://github.com/astral-sh/uv
[venv]: https://docs.python.org/3/library/venv.html
[pypi]: https://pypi.org/
[path]: https://www.baeldung.com/linux/path-variable

<!-- vim: se ai syn=markdown: -->
