from pimpy import argparse
import logging

log  = logging.getLogger(__name__)  # this logger becomes usable after parsing args

desc = 'JustLogIt CLI'
p = argparse.ArgumentParser(description=desc).with_logging(use_structlog=True).with_debug()
args = p.parse_args()

# just start logging, the logger is now setup
log.debug('running %s with args:%s', desc, args)
