import argparse, logging, os

log = logging.getLogger(__name__)

def setup_logging(args):
    """setup_logging checks the given arpparse args for the "default" flag,
    the os.environ for a truthy DEBUG var, and then sets up logging accordingly.
    """
    DEBUG = os.environ.get('DEBUG','false').lower() in ('1','true','yes')
    if getattr(args,'debug', False) or DEBUG: level = logging.DEBUG
    else:                                     level = logging.INFO
    log.debug('setup logging')
    logging.basicConfig(level=level)

class ArgumentParser(argparse.ArgumentParser):
    """ezparz.ArgumentParser is an argparse.ArgumentParser with convenience functions
    for setting custom common and custom flags and options.
    """
    ez_callbacks = None

    opti = argparse.ArgumentParser.add_argument       # 4-letter short name for add_argument

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
        """with_input adds a positional optional "input" argument"""
        p.add_argument('input', help=help, default=default, nargs=nargs, **argparse_args)
        return p

    def with_logging(p):
        """with_logging makes the parser setup logging after parsing input args.
        If it finds a --debug flag or a truthy DEBUG value in os.environ,
        logging is setup with DEBUG level. Otherwise logging is setup with INFO level.
        """
        p.add_parse_callback(p.setup_logging)
        return p

    def setup_logging(p):
        """setup_logging reads the current args and sets up logging"""
        args, _ = p.parse_known_args()
        setup_logging(args)

    def add_parse_callback(p, fn):
        """add_parse_callback adds the given callbacks which are excuted once
        after parsing the parser's arguments"""
        if p.ez_callbacks is None: p.ez_callbacks = []
        p.ez_callbacks.append(fn)

    def _parse_known_args(p, *args, **kwargs):
        """_parse_known_args wraps argparse.ArgumentParser._parse_known_args
        to trigger defered functions once after parsing."""
        res = argparse.ArgumentParser._parse_known_args(p, *args, **kwargs)
        fns = p.ez_callbacks or []  # get current callbacks
        p.ez_callbacks = None       # delete all callbacks to avoid recursion
        for fn in fns: fn()
        return res
