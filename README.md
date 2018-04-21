PimPy: Do more with with less code
==================================

PimPy provides best practices for a few very common Python modules,
allowing you to set them up with less and more readable code.

Install via `pip install --user pimpy`.

PimPy improves usage without breaking flexibility or compatibility
of the enhanced modules.

pimpy.mainlog
-------------

As the name suggest to use it only in your main. Do not setup logging outside of main modules!
The module's main function is `mainlog.setup_logging`:

```python
import logging
from pimpy import mainlog

log = logging.getLogger('pimp-test')

def main(argv=None):
    level = logging.INFO
    mainlog.setup_logging(level=level, mode='json')
    log.info('Hello %s!', 'PimPy', extra={'v':1})

main()
# {"message": "Hello PimPy!", "v": 1}
```

The currently supported logging modes are `json` and `console` (default).
Using `mode='console'` or no mode will produce regular stdlib logs like:

    INFO:pimp-test:Hello PimPy!

Use `mainlog.setup_logging(level=level, use_structlog=True)` to setup `structlog` logging.
If `struclog` is not installed, stdlib `logging` is used as fallback.
The predefined structlog settings will format stdlib logs as follows.

    [info     ] info msg 1                     [stdlib]
    [debug    ] debug msg 2                    [stdlib]
    [error    ] error msg 3                    [stdlib]

If you use a structlog logger you also get key-value pairs.

    [info     ] info msg                       [structlog] a=[1, 2, 3] v=1
    [debug    ] debug msg                      [structlog] b=('a', 'b', 'c') v=2
    [error    ] error msg                      [structlog] c={'x': 1} v=3

If `colorama` is installed, the logs will be nicely colored.

pimpy.argparse
--------------

For readability `pimpy.argparse` provides a compatible `ArgumentParser` that uses
the 4-letter `opti` and `flag` methods instead the clumsy `add_argument`.

```python
    from pimpy import argparse
    desc = 'My CLI Tool'
    p = argparse.ArgumentParser(description=desc)
    p.flag('--json',          help='use json output format')
    p.flag('--dry_run',       help='perform dry run')
    p.opti('--num',     '-n', help='number of iterations', metavar='N', type=int, default=1)
    p.opti('--file',    '-f', help='input file',           required=True)
    p.opti('command',         help='command to run',       choices=['upper','lower'])
```

Using shorter names and nice alignment allows `argparse` code to be much more readable.
Yes I know, to allow for such multi-column-based coding, you need to disable some linter rules,
but it's worth it -- not just with setting up parsers -- trust me! ;-)
PimPy also provides a few shortcuts to setup commonly found flags directly:

* `with_debug`:   adds `--debug` flag
* `with_logging`: automatically sets up logging using `pimpy.mainlog` after parsing args
* `with_input`:   adds `--input` option, defaulting to `-` (aka. `stdin`)

I often use this one-liner.

```python
    p = argparse.ArgumentParser(description=desc).with_logging(use_structlog=True).with_debug()
```

But you can also break lines.

```python
    p = argparse.ArgumentParser(description=desc)
    p.with_logging(use_structlog=True)
    p.with_debug()
    p.with_input()
```

Using the `with_logging` and optionally using `with_debug` allows you to quickly
setup `logging` or `structlog` loggers with human-readable console output, as already
shown above; `with_logging` supports the same `mode` and `use_structlog` key-value args
as used by `mainlog.setup_logging`, described above.

pimpy
-----
There is also a `pimpy` command that I use to automate project creation, incremental
building, testing via `tox`, and uploading to PyPi.

Here are some commands supported by `pimpy`:

    pimpy init --trg ../newproject  # setup new python project
	 cd ../newproject                # enter new project
    pimpy backport                  # backport project to python2
    pimpy uninstall                 # uninstall currently developed package from all pips
    pimpy clean                     # clean test environments    
    tox -e py3                      # dist-install the current version and run some tests
    tox                             # dist-install and test in all testenvs

The `pimpy` command is used in combination with `make`, a custom `Makefile` + a generic
`project.mk` include, a custom `project.cfg` + a generic py2-py3+ compatible `setup.py`,
as found in this project. Run `pimpy init --trg PATH_TO_NEW_PROJECT` to setup these files
in your project and see `pimpy --help` for more options.

Motivation
----------
Most Python developer know `argparse`, `logging`, and `structlog` and have
used them before. However, in my projects I have used the same or very similar
code over and over again when using these modules. And since I do not like to
repeat myself, I wanted to extract the most common practices from my projects
and make them available for my next projects and for others to use.

Have fun!
