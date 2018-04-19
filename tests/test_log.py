import logging, structlog
from pimpy import mainlog

log = logging.getLogger('stdlib')
_log = structlog.getLogger('structlog')

def test_log():
    for i in range(3):
        mainlog.setup_logging(level=logging.DEBUG, use_structlog=True, allow_reattach=True)
        logging.getLogger('other').info('test %d', i)
        structlog.getLogger('other').info('test', i=i, log=log)

        log.info('info msg %d',  1)
        log.debug('debug msg %d', 2)
        log.error('error msg %d', 3)

        _log.info('info msg',  v=1, a=[1,2,3])
        _log.debug('debug msg', v=2, b=tuple('abc'))
        _log.error('error msg', v=3, c=dict(x=1))

if __name__ == '__main__': test_log()
