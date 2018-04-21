from builtins import open, str
import os, re, logging
from datetime import datetime
from glob import glob
from pimpy.__datafiles__ import data_files
from pimpy.__templates__  import templates
from pimpy import argparse
from pimpy.tox import tox, clean
from os.path import join, isfile

from pimpy.shell import run, cp, call, sed, mkdir, rm, touch, block

log = logging.getLogger('pimpy')

def transpile(target):
    run('pasteurize -j 8 -w --no-diff ', target)

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

def uninstall(pkg, pip='pip'):
    for p in (pip, 'pip2', 'pip3'):
        try: run([p, 'uninstall', '-y', pkg])
        except OSError: pass

def find_wheel(pkg,tag):
    return glob(join('dist','{}*{}*.whl'.format(pkg,tag)))[0]

def copy_tools(trg, force=False):
    mkdir(trg)
    # create project tools that do not have any custom code
    for f, text in data_files.items(): write_file(f, trg, text)
    log.info('copied tools: %s -> %s', list(data_files), trg)

def write_file(name, trg_dir, text, force=False, **fmt):
    trg = join(trg_dir, name)
    if isfile(trg) and not force: return
    if len(fmt) > 0: text = text.format(**fmt)
    with open(trg, 'w') as f: f.write(str(text))

def generate_main(pkg_dir):
    touch(join(pkg_dir, '__main__.py'))    # make package runnable

def generate_makefile(trg, main):
    if main is not None:
        log.info('using MAIN=%s as main module.', main)
        text = templates['Makefile'].format(MAIN=main)
    else:
        log.info('using empty MAIN (use -m MAIN to set a custom main module).')
        text = 'include project.mk\n'
    write_file('Makefile', trg, text)

def generate_toxini(trg, envlist=None):
    if envlist is None: envlist = 'py36,py27,pypy'
    envline = 'envlist   = ' + envlist
    log.info('using %s', envlist)
    write_file('tox.ini', trg, templates['tox.ini'], envline=envline)

def generate_initpy(pkg_dir):
    write_file('__init__.py', pkg_dir, templates['__init__.py'])

def user_name():
    name = call('git config --get user.name').strip()
    if name == '': name = os.environ.get('USER')
    return name

def safe_name(): return re.sub(r'[^a-z0-9_\.]', '.', user_name())

def github_name(): return os.environ.get('GITHUB_NAME', '@' + safe_name())

def user_email():
    email = call('git config --get user.email').strip()
    if email == '': email = safe_name() + '@gmail.com'
    return email

def date(fmt='%Y-%m-%d', dt=None):
    if dt is None: dt = datetime.utcnow()
    return dt.strftime(fmt)

def generate_readme(trg, prj):
    COPY_INFO = 'Copyright (c) {} {} {}'.format(date('%Y'), user_name(), user_email())
    log.debug('using COPY_INFO = %s', COPY_INFO)
    write_file('README.md', trg, templates['README.md'], NEW_PRJ=prj, COPY_INFO=COPY_INFO)

def generate_project_cfg(trg, prj):
    write_file('project.cfg', trg, templates['project.cfg'],
               NAME = user_name(),
               EMAIL = user_email(),
               GITHUB_NAME = github_name(),
               PROJECT = prj)

def generate_tests(trg,prj):
    test_dir  = join(trg, 'tests')
    test_file = 'test_{}.py'.format(prj)
    test_func = re.sub('[^A-Za-z0-9_]+','_', prj)
    test_code = 'def test_{}(): pass\n'.format(test_func)
    mkdir(test_dir)
    write_file(test_file, test_dir, test_code)

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
    generate_project_cfg(trg, prj)
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
    src = [curdir] + list(data_files)
    p = argparse.PimpyParser().with_logging().with_debug()
    p.opti('commands',        help='command to run', nargs='*', default=['tox'], metavar='CMD')
    p.opti('--pip',           help='set pip executable')
    p.opti('--pkg',     '-p', help='set package name')
    p.opti('--src',     '-s', help='set source files for building backport', nargs='*', default=src)
    p.opti('--trg',     '-t', help='set target dir for init or copy_tools')
    p.opti('--main',    '-m', help='set main module')
    p.opti('--envlist', '-e', help='set tox envlist')
    p.flag('--force',   '-f', help='force overwriting files')
    args = p.parse_args(argv)
    # args.src = p.fix_narg(args.src, default_src)
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
