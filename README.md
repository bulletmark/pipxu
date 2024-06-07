## PIPXU - Install and Run Python Applications in Isolated Environments using UV
[![PyPi](https://img.shields.io/pypi/v/pipxu)](https://pypi.org/project/pipxu/)
[![AUR](https://img.shields.io/aur/version/pipxu)](https://aur.archlinux.org/packages/pipxu/)

[`pipxu`][pipxu] installs Python applications, i.e. Python packages
which have one or more executable programs, into independent isolated
virtual environments on your system. Each package and it's dependencies
are thus insulated from all other applications, and from the system
Python. [`pipxu`][pipxu] creates links to application executables in a
common directory, which you have in your [PATH][path]. Packages are
typically sourced from [PyPI][pypi], the Python Package Index.

[`pipxu`][pipxu] is a re-implementation of most of the functionality of
the popular [`pipx`][pipx] tool but is **much faster** because it uses
[`uv`][uv] to create and install application virtual environments
instead of [`venv`][venv] and [`pip`][pip] as used by [`pipx`][pipx].
The [`pipxu`][pipxu] code has been developed completely independently of
[`pipx`][pipx] and is not a fork. For compatibility and ease of
migration, the provided commands have the same names as [`pipx`][pipx].
Most commands are implemented, at least for common use cases, although
some command functionality, options, and output are slightly different.

This utility has been developed and tested on Linux but will likely also
work on macOS. It has been briefly tested and seems to run ok on
Windows. The latest documentation and code is available at
https://github.com/bulletmark/pipxu.

## Usage

Type `pipxu` or `pipxu -h` to view the usage summary:

```
usage: pipxu [-h] [--uv uv_path] [-m] [--home HOME] [--bin-dir BIN_DIR]
                   [--man-dir MAN_DIR] [--default-python DEFAULT_PYTHON] [-V]
                   {debug,inject,install,list,reinstall,runpip,uninject,uninstall,upgrade,version}
                   ...

Install Python applications into isolated virtual environments and create
links to the executables in a bin directory for your PATH. Like pipx but uses
uv instead of venv + pip.

options:
  -h, --help            show this help message and exit
  --uv uv_path          path to uv executable, default="uv"
  -m, --no-man-pages    do not install package man pages
  --home HOME           specify PIPXU_HOME
  --bin-dir BIN_DIR     specify PIPXU_BIN_DIR
  --man-dir MAN_DIR     specify PIPXU_MAN_DIR
  --default-python DEFAULT_PYTHON
                        path to default python executable, default="python3"
  -V, --version         just print pipxu version and exit

Commands:
  {debug,inject,install,list,reinstall,runpip,uninject,uninstall,upgrade,version}
    debug               Run an installed application using a debugger.
    inject              Install extra packages into an application.
    install             Install one or more Python applications using isolated
                        virtual environments.
    list                List applications installed by this tool.
    reinstall           Reinstall one, or more, or all applications.
    runpip              Run pip with given arguments on virtual environment
                        for the given application.
    uninject            Uninstall extra packages from an application.
    uninstall           Uninstall one, or more, or all applications.
    upgrade             Upgrade one, or more, or all applications.
    version             List installed application versions.

Note you can set default starting global options in $HOME/.config/pipxu-
flags.conf.
```

Type `pipxu <command> -h` to see specific help/usage for any
individual command:

### Command `debug`

```
usage: pipxu debug [-h] [-e EXECUTABLE] [-d DEBUGGER] package [args ...]

Run an installed application using a debugger. Tries to work out your
preferred debugger from the standard PYTHONBREAKPOINT environment variable. If
not set it defaults to pdb. Or you can set it explicitly with the
-d/--debugger option.

positional arguments:
  package               installed application name
  args                  options and arguments to pass to application, should
                        start with "--"

options:
  -h, --help            show this help message and exit
  -e EXECUTABLE, --executable EXECUTABLE
                        executable to run, default is same as "package" name
  -d DEBUGGER, --debugger DEBUGGER
                        explicit debugger package to use
```

### Command `inject`

```
usage: pipxu inject [-h] [-v] package extras [extras ...]

Install extra packages into an application. Note the same --index-url is used
as/if specified in the original install.

positional arguments:
  package        installed application name
  extras         extra package name[s] to inject/install

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
```

### Command `install`

```
usage: pipxu install [-h] [-p PYTHON] [-f] [-e] [-d]
                           [--system-site-packages] [-i INDEX_URL] [-v]
                           package [package ...]

Install one or more Python applications using isolated virtual environments.

positional arguments:
  package               application[s] to install

options:
  -h, --help            show this help message and exit
  -p PYTHON, --python PYTHON
                        specify explicit python executable path
  -f, --force           recreate any already installed venv
  -e, --editable        install application[s] in editable mode
  -d, --include-deps    include executables from dependencies
  --system-site-packages
                        allow venv access to system packages
  -i INDEX_URL, --index-url INDEX_URL
                        base URL of Python Package Index
  -v, --verbose         give more output
```

### Command `list`

```
usage: pipxu list [-h] [--json] [package ...]

List applications installed by this tool.

positional arguments:
  package     list the given application[s] only

options:
  -h, --help  show this help message and exit
  --json      output json instead
```

### Command `reinstall`

```
usage: pipxu reinstall [-h] [-p PYTHON | --reset-python]
                             [--system-site-packages | --no-system-site-packages]
                             [-v] [--all] [--skip]
                             [package ...]

Reinstall one, or more, or all applications.

positional arguments:
  package               application[s] to reinstall (or to skip for --all
                        --skip)

options:
  -h, --help            show this help message and exit
  -p PYTHON, --python PYTHON
                        specify explicit python executable path
  --reset-python        reset any explicit python path to default python
  --system-site-packages
                        allow venv access to system packages, overrides the
                        per-application setting
  --no-system-site-packages
                        remove venv access to system packages, overrides the
                        per-application setting
  -v, --verbose         give more output
  --all                 reinstall ALL applications
  --skip                skip the specified applications when reinstalling all
                        (only can be specified with --all)
```

### Command `runpip`

```
usage: pipxu runpip [-h] package [args ...]

Run pip with given arguments on virtual environment for the given application.

positional arguments:
  package     installed application name
  args        arguments to pass to uv pip, should start with "--".

options:
  -h, --help  show this help message and exit
```

### Command `uninject`

```
usage: pipxu uninject [-h] [-v] package extras [extras ...]

Uninstall extra packages from an application.

positional arguments:
  package        installed application name
  extras         extra package name[s] to uninstall

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
```

### Command `uninstall`

```
usage: pipxu uninstall [-h] [-v] [--all] [--skip] [package ...]

Uninstall one, or more, or all applications.

positional arguments:
  package        application[s] to uninstall (or to skip for --all --skip)

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
  --all          uninstall ALL applications
  --skip         skip the specified applications when uninstalling all (only
                 can be specified with --all)
```

### Command `upgrade`

```
usage: pipxu upgrade [-h] [-v] [--all] [--skip] [package ...]

Upgrade one, or more, or all applications.

positional arguments:
  package        application[s] to upgrade (or to skip for --all --skip)

options:
  -h, --help     show this help message and exit
  -v, --verbose  give more output
  --all          upgrade ALL applications
  --skip         skip the specified applications when upgrading all (only can
                 be specified with --all)
```

### Command `version`

```
usage: pipxu version [-h] [package]

List installed application versions.

positional arguments:
  package     report specific application and dependent package versions

options:
  -h, --help  show this help message and exit
```

## Installation and Upgrade

Python 3.8 or later is required. Arch Linux users can install [`pipxu`
from the AUR](https://aur.archlinux.org/packages/pipxu) and skip this
section.

The [`uv`][uv] program must be installed (and it's version must be
0.1.33 or later). If [`uv`][uv] is not available via your system
packages, you can install it by following the [uv installation
instructions](https://github.com/astral-sh/uv#getting-started) for your
platform.

E.g. For Linux and macOS:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

E.g. For Windows:
```sh
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Note [`pipxu` is on PyPI](https://pypi.org/project/pipxu/). With `uv`
installed and on your PATH, run the tiny [bootstrap shell
script](https://github.com/bulletmark/pipxu/blob/main/pipxu-bootstrap)
which installs `pipxu` to a temporary directory then runs `pipxu` from
there to install itself normally:

```sh
$ curl -LsSf https://raw.githubusercontent.com/bulletmark/pipxu/main/pipxu-bootstrap | sh
```

Or install `pipxu` using `pipx` if you prefer (or you are using Windows
where `pipxu-bootstrap` may not work):

```sh
$ pipx install pipxu
$ pipxu install pipxu
$ pipx uninstall pipxu
```

To upgrade:

```sh
$ pipxu upgrade pipxu
```

To uninstall all `pipxu` installed applications, and then uninstall
`pipxu` itself:

```sh
$ pipxu uninstall --all --skip pipxu
$ pipxu uninstall pipxu
```

## Recovery

The `pipxu` package also installs the aforementioned
[`pipxu-bootstrap`](https://github.com/bulletmark/pipxu/blob/main/pipxu-bootstrap)
shell script on your system so you can always recover easily from a
broken `pipxu` installation by manually running that script. E.g. The
following may be needed after a major or incompatible Python version
upgrade where `pipxu` may have stopped working:

```sh
$ pipxu-bootstrap
$ pipxu reinstall --all --skip pipxu
```

If you are on Windows, reinstall `pipxu` using `pipx` as described
in the previous section then `pipxu reinstall --all --skip pipxu`.

## Comparison to pipx

Why would you use [`pipxu`][pipxu] instead of [`pipx`][pipx]? The main
reason is to gain a massive speed improvement. `pipx` uses [`python -m
venv`][venv] to create and install virtual environments and [`pip`][pip]
to install packages whereas `pipxu` uses [`uv`][uv] for these
operations. [`uv`][uv] is [a new project](https://astral.sh/blog/uv)
written in [rust](https://www.rust-lang.org/) which has a better design
than [`venv`][venv] + [`pip`][pip], caches aggressively, and is **much
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

1. For the commands `uninstall`, `reinstall`, and `upgrade`, `pipx` only
   allows you to specify one application whereas `pipxu` allows you to
   specify one or more applications. To do an operation on **all**
   applications, `pipx`, requires you use a corresponding `*-all`
   command, e.g. to `upgrade` all applications you use `upgrade-all`.
   `pipxu` simply offers a `--all` option on each of those base commands
   to do the same thing, thus avoiding the need for the extra `*-all`
   commands. Also, `pipx` also does not offer `--skip` for all those
   `*-all` commands consistently, whereas `pipxu` does.

2. You can do `pipxu` commands on an editable projects (as often used by
   developers) in the current directory by simply typing "`.`" as the
   package name and this works for all commands. E.g. `pipxu uninstall
   .` or `pipxu inject . pudb`. I.e. `pipxu` automatically determines
   the package name associated with the current directory. Note that
   `pipx` accepts "`.`" for the install command, but not for any others.

3. For Python developers,`pipxu` adds a [`debug`](#command-debug)
   command to conveniently run an installed application using a
   debugger. `pipx` does not have this command. Read more about the
   `debug` command [here](doc/debug.md).

4. If run as root or with `sudo`, `pipxu` installs applications to a
   global location.

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

You can set those environment variables, or provide them as command line
options, to override the defaults if you want. Note, as seen in the
output above, `pipxu` reports if `PIPXU_BIN_DIR` is included or not in
your PATH. To ensure you can run the applications installed by `pipxu`,
that directory **must be in your PATH**. E.g. for most users on Linux
using the default locations, ensure that `~/.local/bin` is [added to
your PATH environment variable][path].

## Command Default Options

You can add default global options to a personal configuration file
`~/.config/pipxu-flags.conf`. If that file exists then each line of
options will be concatenated and automatically prepended to your `pipxu`
command line arguments. Comments in the file (i.e. `#` and anything
after on a line) are ignored. Type `pipxu` to see all supported options.

The global options: `--uv`, `--no-man-pages`, `--home`, `--bin-dir`,
`--man-dir`, `--default-python`, are the only sensible candidates to
consider setting as defaults.

## Command Line Tab Completion

Command line shell [tab
completion](https://en.wikipedia.org/wiki/Command-line_completion) is
automatically enabled on `pipxu` commands and options using
[`argcomplete`](https://github.com/kislyuk/argcomplete). You may need to
first (once-only) [activate argcomplete global
completion](https://github.com/kislyuk/argcomplete#global-completion).

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

[pipxu]: https://github.com/bulletmark/pipxu
[pipx]: https://github.com/pypa/pipx
[uv]: https://github.com/astral-sh/uv
[venv]: https://docs.python.org/3/library/venv.html
[pip]: https://pip.pypa.io/en/stable/
[pypi]: https://pypi.org/
[path]: https://www.baeldung.com/linux/path-variable

<!-- vim: se ai syn=markdown: -->
