from builtins import open, str
import sys, os, re, logging
from datetime import datetime
from glob import glob
from makepy.__datafiles__ import data_files
from makepy.__templates__  import templates
from makepy import argparse
from makepy.tox import tox, clean
from os.path import join, isfile, dirname, abspath, basename

from makepy.shell import run, cp, call_unsafe, sed, mkdir, rm, block

log = logging.getLogger('makepy')

py       = sys.version_info.major
wheeltag = 'py{}'.format(py)
here     = dirname(__file__)

def python(py=py): return 'python{}'.format(py)

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

def setup_dir(py=py):
    if int(py) < 3: return 'backport'
    else:           return '.'

def pwd(): return abspath(os.curdir)

def find_wheel(pkg,tag):
    return glob(join('dist','{}*{}*.whl'.format(pkg,tag)))[0]

def dist(py=py):
    os.environ['MAKEPYPATH'] = makepypath()
    args = ' setup.py bdist_wheel -q -d {pwd}/dist'.format(pwd=pwd())
    run(python(py) + args, cwd=setup_dir(py))

def dists(py=py):
    pys = range(2, max(3, py) + 1)  # include [2,3] + major versions up to `py`
    for py in pys: dist(py=py)

def install(pkg, py=py, source=False):
    if source:
        os.environ['MAKEPYPATH'] = makepypath()
        run('pip{} install --user -e .'.format(py), cwd=setup_dir(py))
        run('pip{}'.format(py), 'show', pkg)
        if setup_dir(py) == 'backport':
            sys.stderr.write(block(
                """
                ### Attention ###
                Installed {PKG} backport!'
                You must run `makepy backport` to update the installation'
                ### Attention ###
                """, PKG=pkg
            ))
    else:
        run('pip{} install'.format(py), find_wheel(pkg, 'py{}'.format(py)))

def uninstall(pkg, py=py):
    assert pkg is not None
    for p in {'pip', 'pip{}'.format(py), 'pip2', 'pip3'}:
        try: run(p, 'uninstall', '-y', pkg)
        except Exception: pass

def lint(py=py):
    run(python(py) + ' -m flake8', cwd=setup_dir(py))

def test(tests=None, py=py):
    if tests is None: tests = 'tests'
    run(python(py) + ' -m pytest -xv', tests)

def copy_tools(trg, force=False):
    mkdir(trg)
    # create project tools that do not have any custom code
    for f, text in data_files.items(): write_file(f, trg, text)
    log.info('copied tools: %s -> %s', list(data_files) + ['setup.py'], trg)

def write_file(name, trg_dir, text, force=False, strip=True, **fmt):
    trg = join(trg_dir, name)
    if isfile(trg) and not force: return
    if strip: text = text.strip() + '\n'
    if len(fmt) > 0: text = text.format(**fmt)
    with open(trg, 'w') as f: f.write(str(text))

def generate_makefile(trg, main):
    if main is not None:
        log.info('using MAIN=%s as main module.', main)
        text = templates['Makefile'].format(MAIN=main)
    else:
        log.info('using empty MAIN (use -m MAIN to set a custom main module).')
        text = 'include $(shell makepy include)\n'
    write_file('Makefile', trg, text)

def generate_toxini(trg, envlist=None):
    if envlist is None: envlist = 'py36,py27,pypy'
    envline = 'envlist   = ' + envlist
    log.info('using %s', envlist)
    write_file('tox.ini', trg, templates['tox.ini'], envline=envline)

def generate_packagefiles(pkg_dir, main):
    write_file('__init__.py', pkg_dir, templates['__init__.py'].format(MAIN=main))
    write_file('__main__.py', pkg_dir, templates['__main__.py'].format(MAIN=main))

def user_name():
    name = call_unsafe('git config --get user.name').strip()
    if name == '': name = os.environ.get('USER','System Root')
    return name

def safe_name(): return re.sub(r'[^a-z0-9_\.]', str('.'), str(user_name()))

def github_name(): return os.environ.get('GITHUB_NAME', '@' + safe_name())

def user_email():
    email = call_unsafe('git config --get user.email').strip()
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
    prj = re.sub('[^A-Za-z0-9_-]+','-', basename(abspath(trg)))
    mkdir(pkg_dir)
    copy_tools(trg, force=force)
    generate_makefile(trg, main)
    generate_toxini(trg, envlist)
    generate_packagefiles(pkg_dir, main)
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

def bumpversion(pkg):
    init = join(pkg, '__init__.py')
    lines = []
    with open(init) as f:
        for line in f:
            m = re.match(r'(__version__[^0-9]+)([0-9\.]+)([^0-9]+)', line)
            if m is not None:
                pre, version, post = m.groups()
                ma, mi, pa = version.split('.')
                pa = str(int(pa) + 1)
                version = '.'.join([ma, mi, pa])
                log.info('bumpversion to %s', version)
                line = pre + version + post
            lines.append(line)
    with open(init, 'w') as f: f.writelines(lines)

def format(src_files, force=False):
    # TODO: implement modern multi-column-aware unorthodox Python formatter
    print('ATTENTION: Formatting not implemented!')
    for f in src_files:
        if not f.endswith('.py'): print('skipping:', f); continue
        print('Fake formatting:', f, 'OK')

def help(commands):
    # TODO: implement contextual help
    print('ATTENTION: Contextual help is work-in-progress!')
    for cmd in commands: print('no contextual help found for command:', cmd)

def include():
    # TODO: use tmp mk file or located dist installed version
    return 'project.mk'

def makepypath(): return (abspath(join(here,'..')))

def complement_commands(commands, py=py):
    # complete dependencies
    l = commands
    if 'install' in l or 'dev-install' in l:     l = ['dist']     + l  # any install requires dist
    if 'dists'   in l or 'dist' in l and py < 3: l = ['backport'] + l  # py2 dist requires backport
    if 'clean'   in l:                           l = ['clean']    + l  # move clean to front

    # remove dupes, while preserving order of args
    uniq = []
    for cmd in l:
        if cmd not in uniq: uniq.append(cmd)

    return uniq

def main(argv=None):
    # 1. setup defaults for often required options
    common_src = list(data_files) + ['setup.py', 'project.cfg', 'tox.ini', 'README.md']
    src = [basename(abspath('.'))] + common_src
    # 2. create the parser with common options
    p = argparse.MakepyParser().with_logging().with_debug().with_protected_spaces()
    # 3. setup all flags, commands, etc. as aligned one-liners
    p.opti('commands',        help='makepy command', nargs='*', default=[], metavar='CMD')
    p.flag('tox',             help='run tox tests')
    p.flag('backport',        help='backport project to Python 2')
    p.flag('uninstall',       help='uninstall package from all pips')
    p.flag('clean',           help='clean build files')
    p.flag('test',            help='run unit tests directly')
    p.flag('lint',            help='lint source code')
    p.flag('dist',            help='build the wheel')
    p.flag('dists',           help='build all the wheels')
    p.flag('install',         help='build and install the wheel')
    p.flag('dev-install',     help='directly install the source code in the current environment')
    p.flag('init',            help='create makepy files in a new project')
    p.flag('include',         help='print makepy Makefile location (usage: `include $(shell makepy include)`)')
    p.flag('path',            help='print PYHTONPATH to use makepy as module')
    p.flag('format',          help='format python source files using makepy column-aligned formatter')
    p.opti('--py',      '-P', help='set python version  CMD: test, lint, install, uninstall', default=py, type=int)
    p.opti('--pkg',     '-p', help='set package name    CMD: init, install, uninstall')
    p.opti('--src',     '-s', help='set source files    CMD: backport', nargs='*', default=src)
    p.opti('--trg',     '-t', help='set target dir      CMD: init, copy-tools, dist-install', default='.')
    p.opti('--tests',   '-T', help='set tests dir       CMD: test')
    p.opti('--main',    '-m', help='set main module     CMD: init, backport')
    p.opti('--envlist', '-e', help='set tox envlist     CMD: init, tox')
    p.flag('--force',   '-f', help='overwrite files     CMD: init, copy-tools')
    # additional help should be available via the 'help' command that
    # provides help for all or some ot the next given option
    p.flag('help',            help='show contextual help')

    # 4. parse, analyze, and repair args
    args = p.parse_args(argv)

    # repair missing args from related args
    args.trg = abspath(args.trg)  # create a valid named path
    pkg = basename(args.trg)      # override default pkg for new trg
    if args.pkg  is None: args.pkg = args.main
    if args.pkg  is None: args.pkg = pkg
    if args.main is None: args.main = args.pkg

    # decide what to do when run without any command
    commands = args.commands
    if len(commands) == 0: tox(wheeltag);  return
    if 'help' in commands: help(commands); return
    commands = complement_commands(commands, py=args.py)

    # 5. run all passed commands with their shared flags and args
    for cmd in commands:
        if   cmd == 'backport':    backport(args.src, main=args.main)
        elif cmd == 'tox':         tox(args.envlist)
        elif cmd == 'uninstall':   uninstall(args.pkg, py=args.py)
        elif cmd == 'clean':       clean()
        elif cmd == 'include':     print(include())
        elif cmd == 'path':        print(makepypath())
        elif cmd == 'copy':        copy_tools(args.trg, force=args.force)
        elif cmd == 'test':        test(tests=args.tests, py=args.py)
        elif cmd == 'dist':        dist(py=args.py)
        elif cmd == 'dists':       dists(py=args.py)
        elif cmd == 'install':     install(pkg=args.pkg, py=args.py, source=False)
        elif cmd == 'dev-install': install(pkg=args.pkg, py=args.py, source=True)
        elif cmd == 'lint':        lint(py=args.py)
        elif cmd == 'init':        init(args.trg, args.pkg, args.main,
                                        envlist=args.envlist, force=args.force)
        elif cmd == 'format':      format(args.src, force=args.force)
        elif cmd == 'bumpversion': bumpversion(args.pkg)
        else:                      raise ValueError('invalid command: {}'.format(cmd))

if __name__ == '__main__': main()
