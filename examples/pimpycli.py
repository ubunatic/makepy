# Complete CLI Tool Example
# =========================
from __future__ import print_function
from pimpy import argparse
import logging, json

log  = logging.getLogger(__name__)  # this logger becomes usable after parsing args
desc = 'PimPy CLI Example'

def main(argv=None):
    # The parser is a regular argparse ArgumentParser.
    # PimPy just allows you to write less and more readable and aligned code.
    p = argparse.ArgumentParser(description=desc).with_logging(use_structlog=True).with_debug()
    p.flag('--json',          help='use json output format')
    p.flag('--dry_run',       help='perform dry run')
    p.opti('--num',     '-n', help='number of iterations', metavar='N', type=int, default=1)
    p.opti('--file',    '-f', help='input file',           required=True)
    p.opti('command',         help='command to run',       choices=['upper','lower'])

    args = p.parse_args(argv)
    log.info('running %s on %s for %d iterations, outputting as %s',
             args.command, args.file, args.num, args.json and 'json' or 'text')

    with open(args.file) as f: text = f.read().strip()

    cmd = fmt = lambda t: t
    if args.command == 'lower': cmd = lambda t: t.lower()
    if args.command == 'upper': cmd = lambda t: t.upper()
    if args.json:               fmt = lambda t: json.dumps(t)

    for i in range(args.num): text = fmt(cmd(text))

    if args.dry_run: log.info('dry run successfull')
    else:            print(text)
    log.info('processed %d characters in %d lines of text',
             len(text), len(text.split('\n')))

if __name__ == '__main__': main()
