PimPy: Setup common Python modules with a few lines of code
===========================================================

PimPy provides best practices for a few very common Python modules,
allowing you to set them up with less and more readable code.

Install via `pip install pimpy`.

PimPy improves usage with breaking flexibility or compatibility of the
following modules.

`pimpy.mainlog`
---------------
The name suggest to use it only in your main. Do not setup logging outside of main modules!
The modules main function is `mainlog.setup_logging`:

```python
    import logging
	 from pimpy import mainlog
    level = logging.INFO
    mainlog.setup_logging(level=level)
```
Use `mainlog.setup_logging(level=level, use_structlog=True)` to setup `structlog` logging
if possible and use stdlib `logging` as fallback. The predefined structlog settings produce
logs as follows, if you use a stdlib logger aterwards:

    [info     ] info msg 1                     [stdlib]
    [debug    ] debug msg 2                    [stdlib]
    [error    ] error msg 3                    [stdlib]

And if you use a structlog logger you can also add key-value pairs:

    [info     ] info msg                       [structlog] a=[1, 2, 3] v=1
    [debug    ] debug msg                      [structlog] b=('a', 'b', 'c') v=2
    [error    ] error msg                      [structlog] c={'x': 1} v=3

If `colorama` is installed, the logs will be nicely colored.
If `structlog` is not installed you get the default stdlib logging output.

`pimpy.argparse`
----------------
For readabilty `pimpy.argparse` provides a compatible `ArgumentParser` that uses
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

Using shorter names and nice alignement allows `argparse` code to be much more readable.
Yes I know you need to disable some linter rules, but it's worth it, trust me! ;-)
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
setup `logging` or `structlog` loggers with human-readable console output:

```python
from pimpy import argparse
import logging

log = logging.getLogger(__name__)  # this logger becomes usable after parsing args

desc = 'JustLogIt CLI'
p = argparse.ArgumentParser(description=desc).with_logging().with_debug()
args = p.parse_args()

# just start logging, the logger is now setup
log.debug('running %s with args:%s', desc, args)
```

If you run the above program with `--debug` you will see:

    DEBUG:pimpy.mainlog:setup logging, level=DEBUG
    DEBUG:__main__:running JustLogIt CLI with args:Namespace(debug=True)

If you use `p.with_logging(use_structlog=True)` you get colored stuctlog output.

    [debug    ] setup structlog level=DEBUG    [pimpy.mainlog] use_colors=True
    [debug    ] setup logging, level=DEBUG     [pimpy.mainlog]
    [debug    ] running JustLogIt CLI with args:Namespace(debug=True) [__main__]


Motivation
----------
Most Python developer know `argparse`, `logging`, and `structlog` and have
used them before. However, in my projects I have used the same or very similar
code over and over again when using these modules. And since I do not like to
repeat myself, I wanted to extract the most common practices from my projects
and make them available for my next projects and for others to use.

Have fun!
