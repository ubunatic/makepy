# Complete CLI Tool Example
# =========================
from __future__ import print_function
from ezparz import ArgumentParser
import logging, json

log  = logging.getLogger(__name__)  # this logger becomes usable after parsing args
desc = 'My EehZee CLI Tool'

def main(argv=None):
    # use the ezparzer just like a regular argparser, with more readable and aligned code
    p = ArgumentParser(description=desc).with_logging().with_debug()
    p.flag('--json',          help='use json output format')
    p.flag('--dry_run',       help='perform dry run')
    p.opti('--file',    '-f', help='input file')
    p.opti('--num',     '-n', help='number of iterations', metavar='N', type=int)
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

if __name__ == '__main__': main()
