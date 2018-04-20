#!/usr/bin/env python

from builtins import open, str

import shutil as sh
import os, re, logging
from glob import glob
from pimpy import argparse
from subprocess import call

log = logging.getLogger(__name__)

def L(string): return string.split(' ')

PRJ_TOOLS  = L('setup.py setup.cfg project.mk eztox')
PRJ_EXTRAS = L('.gitignore LICENSE.txt project.cfg')

def rm(*args):
    for f in args: sh.rmtree(f, ignore_errors=True)

def touch(fname):
    with open(fname, 'a'): pass

def cp(*args):
    args = list(args)
    dest = args.pop()
    for f in args:
        trg = os.path.join(dest, f)
        log.info('cp %s %s', f, trg)
        if os.path.isdir(f): sh.copytree(f, trg)
        else:                sh.copyfile(f, trg)

def mkdir(path):
    try: os.makedirs(path)
    except OSError: pass

def transpile(target):
    call(L('pasteurize -j 8 -w --no-diff') + [target])

def sed(pattern, repl, *files):
    for p in files:
        with open(p, 'r') as f: orig = f.read()
        log.debug('sub(%s,%s)', pattern, repl)
        text = re.sub(pattern, repl, orig, flags=re.DOTALL)
        msg = 'replacing pattern in {}'.format(p)
        if text == orig: log.info(msg + ':skipped'); continue
        with open(p, 'w') as f: f.write(text)
        log.info(msg + ':replaced')

def backport(*src_files, **kwargs):
    main = kwargs['main']
    rm('backport')
    mkdir('backport')
    cp(*(src_files + ('backport',)))
    transpile('backport')
    # change tag in main modle
    sed(r'__tag__[ ]*=.*', "__tag__ = 'py2'", os.path.join('backport', main, '__init__.py'))
    # ignore linter errors caused by transpiler
    sed(r'(ignore[ ]*=[ ]*.*)', '\\1,F401', 'backport/setup.cfg')

def tox(envlist=None):
    if envlist is None: call(['tox'])
    else:               call(['tox', '-e', 'envlist'])

def uninstall(pkg, pip='pip'):
    for p in (pip, 'pip2', 'pip3'):
        try: call([p, 'uninstall', '-y', pkg])
        except OSError: pass

def clean(): rm('.tox')

def find_wheel(pkg,tag):
    return glob(os.path.join('dist','{}*{}*.whl'.format(pkg,tag)))[0]

def generate_main(pkg_dir):
    touch(os.path.join(pkg_dir, '__main__.py'))    # make package runnable

def generate_makefile(trg, main):
    Mf = os.path.join(trg, 'Makefile')
    if os.path.isfile(Mf): return
    if main is not None:
        log.info('using MAIN=%s as main module.', main)
        with open(Mf, 'w') as f: f.write(str("""
MAIN         := {MAIN}
TEST_SCRIPTS := {MAIN} -h
include project.mk\n""".format(MAIN=main)))
    else:
        log.info('using empty MAIN (use -m MAIN to set a custom main module).')
        with open(Mf, 'w') as f: f.write(str("include project.mk\n"))

def generate_toxini(trg, envlist=None):
    ini = os.path.join(trg, 'tox.ini')
    if os.path.isfile(ini): return
    if envlist is None: envlist = 'py36,py27,pypy'
    envline = 'envlist   = ' + envlist
    log.info('using %s', envlist)
    with open(ini, 'w') as f: f.write(str("""
[tox]
{envline}
skipsdist = True

[testenv]
deps =
    pytest
    flake8
    future

commands = make dist-install {{posargs:lint dist-test}}
whitelist_externals = make
\n""".format(envline=envline)))

def generate_initpy(pkg_dir):
    ipy = os.path.join(pkg_dir, '__init__.py')
    if os.path.isfile(ipy): return
    with open(ipy, 'w') as f: f.write(str("""
# flake8: noqa: F401
__version__ = '0.0.1'
__tag__     = 'py3'\n"""))
    log.info('created %s', ipy)

def init(trg, pkg, main, envlist=None):
    assert None not in (trg, pkg)
    pkg_dir = os.path.join(trg, pkg)
    mkdir(pkg_dir)
    generate_main(pkg_dir)
    generate_makefile(trg, main)
    generate_toxini(trg, envlist)
    generate_initpy(pkg_dir)

def main(argv=None):
    p = argparse.ArgumentParser().with_logging()
    p.opti('command', default='tox')
    p.opti('--pkg')
    p.opti('--trg')
    p.opti('--src')
    p.opti('--main')
    p.opti('--envlist')
    args, _ = p.parse_known_args(argv)
    cmd = args.command
    if   cmd == 'backport':  backport(*L(args.src), main=args.main)
    elif cmd == 'tox':       tox(args.envlist)
    elif cmd == 'uninstall': uninstall(args.pkg)
    elif cmd == 'clean':     clean()
    elif cmd == 'init':      init(args.trg, args.pkg, args.main)
    else:                    raise ValueError('invalid command: {}'.format(cmd))

if __name__ == '__main__': main()
