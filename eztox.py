#!/usr/bin/env python

import shutil as sh
import os
from pimpy import argparse
from subprocess import call

def L(string): return string.split(' ')

PRJ_TOOLS  = L('setup.py setup.cfg project.mk eztox')
PRJ_EXTRAS = L('.gitignore LICENSE.txt project.cfg')

def backport(*src_files, **kwargs):
    main = kwargs['main']
    # copy all code to backport and to convert it to Py2
    sh.rmtree('backport'); os.mkdir('backport')
    for f in src_files: sh.copytree(f, 'backport')
    call(L('pasteurize -j 8 -w --no-diff backport/'))
    # change tag in main modle
    call(['sed', '-i', '"s#^__tag__[ ]*=.*#__tag__ = \'py2\'#"',
          'backport/{}/__init__.py'.format(main)])
    # ignore linter errors caused by transpiler
    call(['sed', '-i', "'s#\(ignore[ ]*=[ ]*.*\)#\\1,F401#g'", 'backport/setup.cfg'])

def main(argv=None):
    p = argparse.ArgumentParser()
    p.opti('command', default='tox', choices=('tox', 'backport'))
    p.opti('--pkg',  required=True)
    p.opti('--src',  required=True)
    p.opti('--main', required=True)
    args, _ = p.parse_known_args(argv)
    cmd = args.command
    if   cmd == 'backport': backport(*L(args.src_files))
    elif cmd == 'tox':      print('tox')
    else:                   raise ValueError('invalid command: {}'.format(cmd))

if __name__ == '__main__': main()
