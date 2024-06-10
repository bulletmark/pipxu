# Debug Command

[`pipxu`][pipxu] adds a [`debug`](/README.md#command-debug) command
which [`pipx`][pipx] does not have.
```
usage: pipxu debug [-h] [-e EXECUTABLE] [-d DEBUGGER] package [args ...]
```

The `debug` command is useful for developers who want to easily run an
installed Python application using a debugger, usually when they have
installed that application in editable form, e.g.

```sh
$ cd myproject
$ pipxu install -e .
```

The command tries to work out your preferred debugger package from the
standard
[PYTHONBREAKPOINT](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONBREAKPOINT)
environment variable. If that variable is not set it defaults to the
standard `pdb`. Or you can set the debugger package explicitly with the
`-d/--debugger` option.

E.g. my personal preference is to use [`pudb`][pudb] debugger so I have
`PYTHONBREAKPOINT=pudb.set_trace` set in my environment for normal
Python [`breakpoint()`](https://peps.python.org/pep-0553/) debugging. So
to debug `myproject` from that same directory and from start I would use:

```sh
pipxu debug . <myproject-args>
```

And the above would start the `myproject` application (with passed
`<myproject-args>`) in the `pudb` debugger within my terminal. To be
more explicit, this is equivalent to:

```sh
pipxu debug -d pudb . <myproject-args>
```

The command assumes the executable name is the same name as the package
which is usually the case. But if it is not then you can specify the
executable using the `-e/--executable` option.

```sh
pipxu debug -e <myproject-exe-name> . <myproject-args>
```

If you want to specify `-` or `--` options to your command being debugged
then you must delimit them from arguments to `pipxu` with `--`, e.g.

```sh
pipxu debug -d pudb . -- <-m --myarg-long-opt>
```

Of course the python installed in the virtual environment is used to run
the application so that virtual environment must have the debugger
package installed. So it is very common to get an error message, e.g.
`No module named pudb` when you first try to use the `pipxu debug`
command for your project. In that case you simply install the debugger
package, e.g.`pudb`, to that virtual environment, i.e:

```sh
pipxu inject . pudb
```

Then run your `pipxu debug` command again.

[pipxu]: https://github.com/bulletmark/pipxu
[pipx]: https://github.com/pypa/pipx
[pudb]: https://documen.tician.de/pudb/

<!-- vim: se ai syn=markdown: -->
