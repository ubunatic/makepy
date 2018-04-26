from __future__ import absolute_import
import logging, os, sys, argparse
from makepy import mainlog

PY2 = sys.version_info.major < 3

log = logging.getLogger(__name__)

class MakepyParser(argparse.ArgumentParser):
    """MakepyParser is an argparse.ArgumentParser with convenience functions
    for setting up common and custom flags and options.
    """ + argparse.ArgumentParser.__doc__

    _callbacks = None
    _use_structlog = False
    _space_repl = None

    # explicitly add most common methods to provide better autocompletion
    parse_args       = argparse.ArgumentParser.parse_args
    parse_known_args = argparse.ArgumentParser.parse_known_args
    add_argument     = argparse.ArgumentParser.add_argument

    def opti(p, *args, **kwargs):             # 4-letter name for key-value arguments
        if 'help' in kwargs and p._space_repl is not None:
            content = kwargs['help']
            kwargs['help'] = content.replace(' ', p._space_repl)
        return p.add_argument(*args, **kwargs)

    def flag(p, flag, *args, **kwargs):       # 4-letter name for boolean arguments
        """flag create command line flag that does not take additional value parameters"""
        if 'action' not in kwargs:
            kwargs['action'] = 'store_true'   # make the option a flag
        return p.opti(flag, *args, **kwargs)  # passthrough any other args

    def with_debug(p, help='enable debug log'):
        """with_debug adds a --debug flag"""
        p.add_argument('--debug', help=help, action='store_true')
        return p

    def with_input(p, default='-', nargs='?', help='input file descriptor', **argparse_args):
        """with_input adds a positional optional 'input' argument"""
        p.add_argument('input', help=help, default=default, nargs=nargs, **argparse_args)
        return p

    def with_protected_spaces(p, space_repl=u'\u00A0'):
        p._space_repl = space_repl
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
        args, rest  = argparse.ArgumentParser._parse_known_args(p, *args, **kwargs)
        p.call_callbacks(args)
        return args, rest

    def _print_message(p, message, file=None, **kwargs):
        """safely print unicode messages"""
        if PY2 and message is not None:
            message = message.encode('utf-8', 'ignore')
        argparse.ArgumentParser._print_message(p, message, file=file, **kwargs)

    def fix_narg(p, value, default=()):
        if   value is None:                return default
        elif type(value) in (list, tuple): return value
        else:                              return (value,)

ArgumentParser = MakepyParser
