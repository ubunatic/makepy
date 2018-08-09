from makepy import argparse
from makepy import mainlog
import logging

def test_argparse():
    p = argparse.ArgumentParser()
    p.flag('--test', help='test')
    p.opti('opt',    help='opt', type=int, default=1, metavar='OPT')
    p.with_debug()
    p.with_logging(use_structlog=True, mode=mainlog.CONSOLE)
    p.with_protected_spaces()
    p.with_input()


def test_argparse_parsing():
    log = logging.getLogger('test_argparse')
    p = argparse.ArgumentParser(description='test').with_logging().with_debug()
    p.flag('--test', help='test flag')
    p.opti('--key',  help='key option', metavar='VALUE', type=int)

    args = p.parse_args(['--test','--key','2','--debug'])
    assert args.test is True
    assert args.key == 2
    assert args.debug is True
    log.debug('If you see this, DEBUG logging was setup!')
    logging.getLogger().setLevel(logging.INFO)
    log.info('logging should be back to INFO level')
    log.debug('YOU SHOULD NOT SEE THIS!')

if __name__ == '__main__': test_argparse()
