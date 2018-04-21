#!/usr/bin/env python

from builtins import open, str

import shutil as sh
import os, re, subprocess, logging
from datetime import datetime
from glob import glob
from pimpy import argparse
from os.path import join, isdir, isfile

log = logging.getLogger('eztox')

def L(string): return string.split(' ')

PRJ_TOOLS  = L('setup.py setup.cfg project.mk eztox')
PRJ_EXTRAS = L('.gitignore LICENSE.txt project.cfg')

def arglist(args, more_args=()):
    if type(args) in (str,bytes): args = args.split(' ')
    return list(args) + list(more_args)

def unpad(text):
    lines = text.split('\n')
    pads = re.findall(r'^[ ]+', text, flags=re.MULTILINE)
    if text.strip() == '' or len(pads) == 0: return text
    pat = r'^{}'.format(len(pads[0]) * ' ')
    return re.sub(pat,'', text, flags=re.MULTILINE)

def block(string, *args, **kwargs):
    string = string.format(*args, **kwargs)
    return str(unpad(string).strip() + '\n')

def run(args, *more_args): return subprocess.check_call(arglist(args, more_args))

def call(args, *more_args):
    args =  arglist(args, more_args)
    log.debug('call: subprocess.check_output(%s)', args)
    return subprocess.check_output(args)

def rm(*args):
    for f in args: sh.rmtree(f, ignore_errors=True)

def touch(*args):
    for f in args:
        with open(f, 'a'): pass

def cp(args, *more_args, **kwargs):
    force = kwargs.get('force', False)
    args = arglist(args, more_args)
    dest = args.pop()
    for f in args:
        trg = join(dest, f)
        if   isdir(f):  exists = isdir(trg);  fn = sh.copytree
        elif isfile(f): exists = isfile(trg); fn = sh.copyfile
        if not exists or force: fn(f, trg)
        if exists and force: log.debug('copied %s -> %s: overwritten', f, trg)
        elif exists:         log.debug('skipped %s -> %s: exists', f, trg)
        else:                log.debug('copied %s -> %s: copied', f, trg)

def mkdir(*paths):
    try: os.makedirs(join(*paths))
    except OSError: pass

def transpile(target):
    run('pasteurize -j 8 -w --no-diff ', target)

def sed(pattern, repl, *files):
    for p in files:
        with open(p, 'r') as f: orig = f.read()
        log.debug('replacing %s with %s in %s', pattern, repl, p)
        text = re.sub(pattern, repl, orig, flags=re.DOTALL)
        if text == orig:
            log.info('skipping to modify %s')
        else:
            with open(p, 'w') as f: f.write(text)
            log.info('modified %s', p)

def backport(src_files, **kwargs):
    log.info('backporting: %s', src_files)
    main = kwargs['main']
    rm('backport')
    mkdir('backport')
    cp(src_files, 'backport')
    transpile('backport')
    if main is not None:
        # change tag in main modle
        sed(r'__tag__[ ]*=.*', "__tag__ = 'py2'", join('backport', main, '__init__.py'))
    # ignore linter errors caused by transpiler
    sed(r'(ignore[ ]*=[ ]*.*)', '\\1,F401', 'backport/setup.cfg')

def tox(envlist=None):
    if envlist is None: run(['tox'])
    else:               run(['tox', '-e', 'envlist'])

def uninstall(pkg, pip='pip'):
    for p in (pip, 'pip2', 'pip3'):
        try: run([p, 'uninstall', '-y', pkg])
        except OSError: pass

def clean(): rm('.tox')

def find_wheel(pkg,tag):
    return glob(join('dist','{}*{}*.whl'.format(pkg,tag)))[0]

def copy_tools(trg, force=False):
    mkdir(trg)
    cp(PRJ_TOOLS, trg, force=True)  # copy project tools that do not have any custom code/names
    log.info('copied tools: %s -> %s', PRJ_TOOLS, trg)
    cp(PRJ_EXTRAS, trg, force=force)
    if force: log.info('updated extras: %s -> %s', PRJ_EXTRAS, trg)
    else:     log.info('safely copied extras: %s -> %s', PRJ_EXTRAS, trg)

def generate_main(pkg_dir):
    touch(join(pkg_dir, '__main__.py'))    # make package runnable

def generate_makefile(trg, main):
    Mf = join(trg, 'Makefile')
    if isfile(Mf): return
    if main is not None:
        log.info('using MAIN=%s as main module.', main)
        with open(Mf, 'w') as f: f.write(block(
            """
            MAIN         := {MAIN}
            TEST_SCRIPTS := {MAIN} -h
            include project.mk
            """,
            MAIN=main
        ))
    else:
        log.info('using empty MAIN (use -m MAIN to set a custom main module).')
        with open(Mf, 'w') as f: f.write(block(
            """
            include project.mk
            """
        ))

def generate_toxini(trg, envlist=None):
    ini = join(trg, 'tox.ini')
    if isfile(ini): return
    if envlist is None: envlist = 'py36,py27,pypy'
    envline = 'envlist   = ' + envlist
    log.info('using %s', envlist)
    with open(ini, 'w') as f: f.write(block(
        """
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
        """,
        envline=envline
    ))

def generate_initpy(pkg_dir):
    ipy = join(pkg_dir, '__init__.py')
    if isfile(ipy): return
    with open(ipy, 'w') as f: f.write(block(
        """# flake8: noqa: F401
        __version__ = '0.0.1'
        __tag__     = 'py3'
        """
    ))
    log.info('created %s', ipy)
    
def user_name():
    name = call('git config --get user.name').strip()
    if name == '': name = os.environ.get('USER')
    return name

def safe_name():  return sed('[^a-z0-9_\.]','.', user_name())

def user_email():
    email = call('git config --get user.email').strip()
    if email == '': email = safe_name() + '@gmail.com'
    return email

def date(fmt='%Y-%m-%d', dt=None):
    if dt is None: dt = datetime.utcnow()
    return dt.strftime(fmt)

def generate_readme(trg, prj):
    rdm = join(trg, 'README.md')
    if isfile(rdm): return
    COPY_INFO = '(c) Copyright {}, {}, {}'.format(date('%Y'), user_name(), user_email())
    log.debug('using COPY_INFO = %s', COPY_INFO)
    with open(rdm, 'w') as f: f.write(block(
        """
        {NEW_PRJ}
        =========

        Install via `pip install {NEW_PRJ}`. Then run the program:

            {NEW_PRJ} --help       # show help
            {NEW_PRJ}              # run with defaults

        {COPY_INFO}
        """,
        NEW_PRJ=prj, COPY_INFO=COPY_INFO
    ))

def generate_tests(trg,prj):
    test_dir  = join(trg, 'tests')
    test_file = join(test_dir, 'test_{}.py'.format(prj))
    if isfile(test_file): return
    test_func = re.sub('[^A-Za-z0-9_]+','_', prj)
    test_code = 'def test_{}(): pass'.format(test_func)
    mkdir(test_dir)
    with open(test_file, 'w') as f: f.write(str(test_code) + '\n')
    log.debug('created test: %s.', test_file)

def init(trg, pkg, main, envlist=None, force=False):
    assert None not in (trg, pkg)
    pkg_dir = join(trg, pkg)
    prj = re.sub('[^A-Za-z0-9_-]+','-', os.path.basename(trg))
    mkdir(pkg_dir)
    copy_tools(trg, force=force)
    generate_main(pkg_dir)
    generate_makefile(trg, main)
    generate_toxini(trg, envlist)
    generate_initpy(pkg_dir)
    generate_readme(trg, prj)
    generate_tests(trg, prj)
    log.info('done:\n%s', block(
        """
        -------------------------------------------
        Created new project: {NEW_PRJ} in {TARGET}!
        You can now build it using make:
        -------------------------------------------
        cd {TARGET}
        make
        make dist
        -------------------------------------------
        """,
        NEW_PRJ=prj, TARGET=trg
    ))

def main(argv=None):
    curdir = os.path.basename(os.path.abspath(os.path.curdir))
    src = [curdir] + PRJ_TOOLS
    p = argparse.ArgumentParser().with_logging().with_debug()
    p.opti('commands',        help='command to run', nargs='*', default=['tox'], metavar='CMD')
    p.opti('--pip',           help='set pip executable')
    p.opti('--pkg',     '-p', help='set package name')
    p.opti('--src',     '-s', help='set source files for building backport', nargs='*', default=src)
    p.opti('--trg',     '-t', help='set target dir for init or copy_tools')
    p.opti('--main',    '-m', help='set main module')
    p.opti('--envlist', '-e', help='set tox envlist')
    p.flag('--force',   '-f', help='force overwriting files')
    args = p.parse_args(argv)
    if args.main is not None and args.pkg is None: args.pkg = args.main
    for cmd in args.commands:
        if   cmd == 'backport':  backport(args.src, main=args.main)
        elif cmd == 'tox':       tox(args.envlist)
        elif cmd == 'uninstall': uninstall(args.pkg)
        elif cmd == 'clean':     clean()
        elif cmd == 'copy':      copy_tools(args.trg, force=args.force)
        elif cmd == 'init':      init(args.trg, args.pkg, args.main,
                                      envlist=args.envlist, force=args.force)
        else:                    raise ValueError('invalid command: {}'.format(cmd))

if __name__ == '__main__': main()
