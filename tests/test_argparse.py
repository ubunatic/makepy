from makepy.argparse import ArgumentParser
import logging

def test_argparse():
    log = logging.getLogger('test_argparse')
    p = ArgumentParser(description='test').with_logging().with_debug()
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
