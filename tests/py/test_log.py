from __future__ import absolute_import, print_function

import logging
try: import structlog; _log = structlog.getLogger('structlog')
except ImportError: structlog = _log = None
try: import pythonjsonlogger
except ImportError: pythonjsonlogger = None


from makepy import mainlog

log = logging.getLogger('stdlib')

def run_logger(mode, use_structlog):
    msg = 'mode:{}, structlog:{}'.format(mode, use_structlog)
    print("TEST:", msg)

    mainlog.setup_logging(level=logging.DEBUG,
                          use_structlog=use_structlog,
                          mode=mode)

    logging.getLogger('other').info('mode:%s, structlog:%s', mode, use_structlog)
    log.info('info msg %d',  1)
    log.debug('debug msg %d', 2)
    log.error('error msg %d', 3)

    if structlog is not None:
        structlog.getLogger('other').info('test', mode=mode, structlog=use_structlog)
        _log.info('info msg',  v=1, a=[1,2,3])
        _log.debug('debug msg', v=2, b=tuple('abc'))
        _log.error('error msg', v=3, c=dict(x=1))
    print('---------------')

def test_log():
    modes = [mainlog.CONSOLE]
    if pythonjsonlogger is not None: modes.append(mainlog.JSON)

    for mode in modes:
        for use_structlog in (True, False):
            run_logger(mode, use_structlog)

if __name__ == '__main__': test_log()
