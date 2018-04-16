from ezparz import ArgumentParser
import logging

def test_ezparz():
    log = logging.getLogger('test_ezparz')
    p = ArgumentParser(description='test').with_logging()
    p.flag('--test', help='test flag')
    p.opti('--key',  help='key option', metavar='VALUE', type=int)

    args = p.parse_args(['--test','--key','1'])
    assert args.test
    assert args.key == 1
    log.info('If you see this, logging was setup!')

if __name__ == '__main__': test_ezparz()
