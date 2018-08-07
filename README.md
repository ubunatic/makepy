[![pypi version](https://img.shields.io/pypi/v/makepy.svg)](https://pypi.python.org/pypi/makepy)
[![stage](https://img.shields.io/pypi/status/makepy.svg)](https://pypi.python.org/pypi/makepy)
[![python versions](https://img.shields.io/pypi/pyversions/makepy.svg)](https://pypi.python.org/pypi/makepy)
[![build status](https://storage.googleapis.com/ubunatic-public/makepy/build-status.svg)](https://storage.googleapis.com/ubunatic-public/makepy/build-status.json)
<!--[![license](https://img.shields.io/pypi/l/makepy.svg)](https://pypi.python.org/pypi/makepy)-->

makepy: Handsfree Python Module Programming
===========================================

This project provides:

[`makepy`](#makepy-command): A command line tool to simplify Python project setup,
installation, and testing.<br>
[`makepy.mainlog`](#mainlog-module): A module for making [`logging`][logging]
and [`structlog`][structlog] setup less cumbersome and less error-prone.<br>
[`makepy.argparse`](#argparse-module): A module providing a drop-in `ArgumentParser`
for writing better readable [`argparse`][argparse] code.

Install via `pip3 install --user makepy`.

mainlog module
--------------

As the name suggest, use [`makepy.mainlog`][mp_mainlog] only in your main module.
Do not setup logging outside of main modules!
The module's main function is [`mainlog.setup_logging`][setup_logging]:

```python
import logging
from makepy import mainlog

log = logging.getLogger('app')

def main(argv=None):
    level = logging.INFO
    mainlog.setup_logging(level=level, mode='json')
    log.info('Hello %s!', 'makepy', extra={'v':1})

main()
# {"message": "Hello makepy!", "v": 1}
```

The currently supported logging modes are `json` and `console` (default).
Using `mode='console'` or no mode will produce regular stdlib logs like:

    INFO:app:Hello makepy!

Use `mainlog.setup_logging(level=level, use_structlog=True)` to setup `structlog` logging.
If `struclog` is not installed, stdlib `logging` is used as fallback.
The predefined structlog settings will format stdlib logs as follows.

    [info     ] info msg 1                     [stdlib]
    [debug    ] debug msg 2                    [stdlib]
    [error    ] error msg 3                    [stdlib]

If you use structlog loggers in your modules you also get `extra` key-value pairs.

    [info     ] info msg                       [structlog] a=[1, 2, 3] v=1
    [debug    ] debug msg                      [structlog] b=('a', 'b', 'c') v=2
    [error    ] error msg                      [structlog] c={'x': 1} v=3

If [`colorama`][colorama] is installed, the logs will be nicely colored (structlog feature).

argparse module
---------------

For writing better command line apps, [`makepy.argparse`][mp_argparse] provides a compatible
`ArgumentParser` that uses the 4-letter `opti` and `flag` methods, replacing the original
`add_argument` method.

```python
from makepy import argparse
desc = 'My CLI Tool'
p = argparse.ArgumentParser(description=desc)
p.flag('--json',          help='use json output format')
p.flag('--dry_run',       help='perform dry run')
p.opti('--num',     '-n', help='number of iterations', metavar='N', type=int, default=1)
p.opti('--file',    '-f', help='input file',           required=True)
p.opti('command',         help='command to run',       choices=['upper','lower'])
```

Using shorter names and nice alignment allows `argparse` code to be much more readable.
Yes I know, to allow for such multi-column-based coding, you need to disable some linter rules.
But it's worth it, not just for `argparse` code, but for better readable Python code in general.
makepy's `ArgumentParser` also provides a few shortcuts to setup other commonly used modules
directly via the following flags:

* `with_debug`:   adds `--debug` flag
* `with_logging`: automatically sets up logging using `makepy.mainlog` after parsing args
* `with_input`:   adds `--input` option, defaulting to `-` (aka. `stdin`)
* `with_protected_spaces`: modifies the `argparse` formatter, to protect white space as defined
  in your `help` statements. Otherwise `argparse` will strip any newline and repeated spaces,
  etc., to create condense help paragraphs. Using this option you can now safely align help text
  directly in your code. See `makep/cli.py` as an example.

Here is an example to setup common debug and logging features:

```python
p = argparse.ArgumentParser(description=desc).with_logging(use_structlog=True).with_debug()
```

If you do not like one-liners, you can also break lines.

```python
p = argparse.ArgumentParser(description=desc)
p.with_logging(use_structlog=True)
p.with_debug()
p.with_input()
```

Using the `with_logging` and optionally using `with_debug` allows you to quickly
setup `logging` or `structlog` loggers with human-readable console output.
Therefore, `with_logging` supports the same `mode` and `use_structlog` key-value args
as used by `mainlog.setup_logging` described [above](#mainlog-module).

makepy command
--------------
This project also provides a `makepy` command, used to automate project creation, incremental
building, testing via `tox`, and uploading to PyPi.

![makepy cast](https://storage.googleapis.com/ubunatic-public/makepy/makepy-cli.gif)

Here are some commands supported by `makepy`:

    makepy init --trg ~/workspace/newproject # setup new project/package named "newproject"
    cd ~/workspace/newproject                # enter new project

    makepy backport     # backport project to python2
    tox -e py3          # use `tox` to install and test the package in a Python 3 environment
    tox                 # install and test in all testenvs defined in `tox.ini`
    makepy              # install and test in the default testenv
    makepy clean        # cleanup test environments and build files

    makepy dist         # build python wheel for current project
    makepy dist -P 2    # build python wheel for python2
    makepy dists        # build both wheels for python2 and python3
    makepy version      # read version string from main __init__.py
    makepy bumpversion  # increase patch level in main __init__.py
    makepy install      # pip install the wheel in the system (may require sudo)
    makepy dev-install  # pip install the current editable source code in the system
    makepy uninstall    # uninstall current project/package from all pips

You can also chain commands: `makepy clean bumpversion dists`, and `makepy` will reorder
them and add all required depending commands, e.g., `makepy install -P 2` is equivalent
to `makepy backport dist install -P 2`.

The `makepy` command depends on and can initialize values in the Python config files
[`tox.ini`][tox_ini] and [`setup.cfg`][setup_cfg]. It can also create a generic py2-py3+
compatible [`setup.py`][setup_py], as found in this project.

Run `makepy init --trg PATH_TO_NEW_PROJECT` to setup all required files. Use `-f` to allow
overwriting existing files. See `makepy --help` for more options.

makepy + make
-------------
Some makepy functionality is still only available via [`make`][make], using the
[`make/project.mk`][make_project], [`make/vars.mk`][make_vars], etc. include files. You can
use these in your project. Just copy them to a `make` dir in your project and `include` them
in your `Makefile`, as [done][Makefile] by this project. See each mk-file for details and help.

Goals
-----
In general the project aims to provide a few flexible tools and modules that should help with
daily Python programming tasks for developing Python modules, libaries, and command line tools.
It aims to capture best practices and make them reusable, allowing you to write less and more
readable code, without breaking flexibility or compatibility of the enhanced modules and tools.

Motivation
----------
Most Python programmers know [`argparse`][argparse], [`logging`][logging] or
[`structlog`][structlog], [`tox`][tox] and [`pip`][pip], and many also use [`twine`][twine],
[`setuptools`][setuptools], and others. However, when using these tools you will write the
same or very similar boilerplate code again and again.

Not wanting to repeat myself, I wanted to extract the most common practices from my projects
and make them available for my next projects and for others to use.

History
-------
The utility modules to setup `logging` and `argparse`, were scattered in several private
projects (and reimplemented in corporate projects). Most of the `makepy` commands lived in a
huge `Makefile` that had to be copied and augmented from project to project, before I finally
started porting features to `makepy`. A few `make` features still remain and can be found in
this project's `mk` files, such as the `make tag` and `make publish`.

I will keep `makepy` updated, with future learnings and I am happy to welcome pull requests.

Have fun!

Open Issues/Tasks
-----------------
* Add Python 2 support for namespaces.
* Port doc strings + create readthedocs docs.
* Port version management to use external `bumpversion` command.
* Port integration tests from make.
* Port docker tests from make.
* Port wheel publishing from make.
* Port remainder from make + remove make related code.


[structlog]:     https://github.com/hynek/structlog
[colorama]:      https://github.com/tartley/colorama
[logging]:       https://docs.python.org/3/library/logging.html
[argparse]:      https://docs.python.org/3/library/argparse.html
[setuptools]:    https://pypi.org/project/setuptools
[twine]:         https://github.com/pypa/twine
[tox]:           https://pypi.org/project/tox
[pip]:           https://pypi.org/project/pip
[make]:          https://www.gnu.org/software/make

[makefile]:      Makefile
[project_cfg]:   project.cfg
[setup_cfg]:     setup.cfg
[tox_ini]:       tox.ini
[setup_py]:      setup.py
[make_project]:  make/project.mk
[mp_argparse]:   makepy/argparse.py
[mp_mainlog]:    makepy/mainlog.py
[setup_logging]: https://github.com/ubunatic/makepy/search?q=setup_logging
