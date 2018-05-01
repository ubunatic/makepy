![build status](https://storage.googleapis.com/ubunatic-public/makepy/build-status.svg)

makepy: do more with with less code
===================================

makepy provides best practices for a few very common Python modules,
allowing you to set them up with less and more readable code.

Install via `pip install --user makepy`.

makepy improves usage without breaking flexibility or compatibility
of the enhanced modules.

makepy.mainlog
--------------

As the name suggest, use it only in your main module. Do not setup logging
outside of main modules! The module's main function is `mainlog.setup_logging`:

```python
import logging
from makepy import mainlog

log = logging.getLogger('pimp-test')

def main(argv=None):
    level = logging.INFO
    mainlog.setup_logging(level=level, mode='json')
    log.info('Hello %s!', 'makepy', extra={'v':1})

main()
# {"message": "Hello makepy!", "v": 1}
```

The currently supported logging modes are `json` and `console` (default).
Using `mode='console'` or no mode will produce regular stdlib logs like:

    INFO:pimp-test:Hello makepy!

Use `mainlog.setup_logging(level=level, use_structlog=True)` to setup `structlog` logging.
If `struclog` is not installed, stdlib `logging` is used as fallback.
The predefined structlog settings will format stdlib logs as follows.

    [info     ] info msg 1                     [stdlib]
    [debug    ] debug msg 2                    [stdlib]
    [error    ] error msg 3                    [stdlib]

If you use structlog loggers in your modules you also get key-value pairs.

    [info     ] info msg                       [structlog] a=[1, 2, 3] v=1
    [debug    ] debug msg                      [structlog] b=('a', 'b', 'c') v=2
    [error    ] error msg                      [structlog] c={'x': 1} v=3

If `colorama` is installed, the logs will be nicely colored.

makepy.argparse
---------------

For readability `makepy.argparse` provides a compatible `ArgumentParser` that uses
the 4-letter `opti` and `flag` methods instead the clumsy `add_argument`.

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
But it's worth it, not just for argparse code, but for better readable Python code in general.
makepy's `ArgumentParser` also provides a few shortcuts to setup commonly found flags directly:

* `with_debug`:   adds `--debug` flag
* `with_logging`: automatically sets up logging using `makepy.mainlog` after parsing args
* `with_input`:   adds `--input` option, defaulting to `-` (aka. `stdin`)
* `with_protected_spaces`: will replace spaces in all `help` texts with protected spaces to
  prevent `argparse` from stripping them. This way, you do not need to setup a special
  help formatter to achive aligned table-like help texts on the command line.
  You can just align them in the code! See `makep/cli.py` as an example.

To setup debug and logging I usually use this one-liner in my parsers:

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
as used by `mainlog.setup_logging` described above.

makepy command
--------------
There is also a `makepy` command that I use to automate project creation, incremental
building, testing via `tox`, and uploading to PyPi.

Here are some commands supported by `makepy`:

    makepy init --trg ~/workspace/newproject # setup new python project
    cd ~/workspace/newproject                # enter new project

    makepy backport   # backport project to python2
    tox -e py3        # install the current version in testenv and run tests
    tox               # install and test in all testenvs
    makepy            # install and test the default testenv
    makepy clean      # cleanup test environments

    makepy dist       # build python wheel for project
    makepy install    # install the wheel in the system (may require sudo)
    makepy uninstall  # uninstall current project from all pips

The `makepy` command uses a custom `project.cfg`, `tox.ini`, `setup.cfg`, and a generic
py2-py3+ compatible `setup.py`, as found in this project. It can also be combined with `make`.

Run `makepy init --trg PATH_TO_NEW_PROJECT` to setup all required files; use `-f` to allow
overwriting existing files. See `makepy --help` for more options.

makepy + make
-------------
Some makepy functionality is still only available via `make`, using the `make/project.mk`,
`make/vars.mk`, etc. include files. You can still use these in your project. Just copy them
to a `make` dir in your project and `include` them in your `Makefile`, as done by this project.
See each mk-file for details and help.

Motivation
----------
Most Python developer know `argparse`, `logging` or `structlog`, `tox` and `pip`, and
many also use `twine`, `setuptools`, and others. However, in my projects I have used the
same or very similar code and build chains over and over again when using these tools and
modules. And since I do not like to repeat myself, I wanted to extract the most common
practices from my projects and make them available for my next projects and for others to use.

I will keep makepy updated, with future learning and are happy to welcome pull requests.

Have fun!
