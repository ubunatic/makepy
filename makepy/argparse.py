from __future__ import absolute_import
import logging, os
from makepy import mainlog
from argparse import ArgumentParser as _AP

class MakepyParser(_AP):
    """MakepyParser is an argparse.ArgumentParser with convenience functions
    for setting custom common and custom flags and options.
    """ + _AP.__doc__

    _callbacks = None
    _use_structlog = False

    # explicitly add most common methods to provide better autocompletion
    parse_args       = _AP.parse_args
    parse_known_args = _AP.parse_known_args
    add_argument     = _AP.add_argument

    opti = _AP.add_argument       # 4-letter short name for add_argument

    def flag(p, flag, *args, **kwargs):               # 4-letter name for boolean arguments
        """flag create command line flag that does not take additional value parameters"""
        if 'action' not in kwargs:
            kwargs['action'] = 'store_true'           # make the option a flag
        return p.add_argument(flag, *args, **kwargs)  # passthrough any other args

    def with_debug(p, help='enable debug log'):
        """with_debug adds a --debug flag"""
        p.add_argument('--debug', help=help, action='store_true')
        return p

    def with_input(p, default='-', nargs='?', help='input file descriptor', **argparse_args):
        """with_input adds a positional optional 'input' argument"""
        p.add_argument('input', help=help, default=default, nargs=nargs, **argparse_args)
        return p

    def with_logging(p, use_structlog=False, mode=mainlog.CONSOLE):
        """with_logging makes the parser setup logging after parsing input args.
        If it finds a --debug flag or a truthy DEBUG value in os.environ,
        logging is setup with DEBUG level. Otherwise logging is setup with INFO level.
        """
        p._use_structlog = use_structlog
        p._mainlog_mode = mode
        p.add_parse_callback(p.setup_logging)
        return p

    def setup_logging(p, args):
        """setup_logging reads the current args and sets up logging"""
        try:                   DEBUG = args.debug
        except AttributeError: DEBUG = False
        DEBUG = DEBUG or os.environ.get('DEBUG','false').lower() in ('1','true','yes')
        if DEBUG: level = logging.DEBUG
        else:     level = logging.INFO
        mainlog.setup_logging(level=level, use_structlog=p._use_structlog, mode=p._mainlog_mode)

    def add_parse_callback(p, fn):
        """add_parse_callback adds the given callback function to be excuted once
        after parsing the parser's arguments"""
        if p._callbacks is None: p._callbacks = []
        p._callbacks.append(fn)

    def call_callbacks(p, args):
        fns = p._callbacks or []  # get current callbacks
        p._callbacks = None       # delete all callbacks to avoid recursion
        for fn in fns: fn(args)   # call callbacks

    def _parse_known_args(p, *args, **kwargs):
        """_parse_known_args wraps argparse.ArgumentParser._parse_known_args
        to trigger defered functions once after parsing."""
        args, rest  = _AP._parse_known_args(p, *args, **kwargs)
        p.call_callbacks(args)
        return args, rest

    def fix_narg(p, value, default=()):
        if   value is None:                return default
        elif type(value) in (list, tuple): return value
        else:                              return (value,)

ArgumentParser = MakepyParser
