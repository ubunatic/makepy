ezparz: Eeh-Zee-Par-Zee: The easy-peasy argparse-compatible ArgumentParser
==========================================================================

Using `argparse` it already very concise, but having only one generic `add_argument`
function to add args is very unfortunate. This package provides `ezparz.ArgumentParser`
for writing more readable, yet fully `argparse`-felxible code.

Main Purpose
------------
The main goal of `ezparz` was to allow aligning the `argparse` code
for better in-file readability.

* `flag`: use `p.flag('--flag')` instead of `p.add_argument('--flag', action='store_true')`
* `opti`: use `p.opti(...)`      instead of `p.add_argument(...)`

Extra Features
--------------
Since many flags and options are common in many projects, I added my most common flags
explicitly. Moreover, I often use the `--debug` flag to control `logging`. `ezparz` can
now do this automatically.

* `with_debug`:   adds `--debug` flag
* `with_logging`: automatically setup logging after parsing args
* `with_input`:   adds  `--input` option, defaulting to `-` (aka. `stdin`)

Usage Example
-------------
Install via `pip install ezparz`. Then use as follows:

```python
from ezparz import ArgumentParser
import logging

log  = logging.getLogger(__name__)  # this logger becomes usable after parsing args
desc = 'My EehZee CLI Tool'

# use the ezparzer just like a regular argparser, just with more readable and aligned code
p = ArgumentParser(description=desc).with_logging().with_debug()
p.flag('--json',          help='use json output format')
p.flag('--dry_run',       help='perform dry run')
p.opti('--file',    '-f', help='input file')
p.opti('--num',     '-n', help='number of iterations', metavar='N', type=int)
p.opti('command',         help='command to run',       choices=['upper','lower'])

args = p.parse_args()
# just start logging, the logger is now setup
log.debug('running %s on %s for %d iterations, outputting as %s',
          args.command, args.file, args.num, args.json and 'json' or 'text')

# see `examples/myezcli.py` for the remaining code
```

If you run this script with `--help` you will see the regular `argparse` output:

    usage: myezcli.py [-h] [--debug] [--json] [--dry_run] [--file FILE] [--num N]
                      {upper,lower}
    
    My EehZee CLI Tool
    
    positional arguments:
      {upper,lower}         command to run
    
    optional arguments:
      -h, --help            show this help message and exit
      --debug               enable debug log
      --json                use json output format
      --dry_run             perform dry run
      --file FILE, -f FILE  input file
      --num N, -n N         number of iterations

Using `ArgumentParser().with_debug().with_logging()` is a nice and concise way
of setting up logging and choosing between `DEBUG` and `INFO` level.

If you use `--debug` with the above script you get:

    python examples/myezcli.py -f <(echo ABC) --debug lower -n1 --json
    DEBUG:__main__:running lower on /proc/self/fd/11 for 1 iterations, outputting as text
	 "abc"
