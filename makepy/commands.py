from __future__ import print_function, absolute_import

from builtins import str
import sys, os, re, json, logging
from datetime import datetime
from glob import glob
from os.path import join, isfile, dirname, abspath, basename
from makepy import argparse
from makepy.config import read_setup_args, package_dir, read_config
from makepy.shell import run, cp, call_unsafe, sed, mkdir, rm, block, open

# load files and templates
from makepy._templates import templates
try:    from makepy._datafiles import dirs as datadirs, files as datafiles
except: datafiles = {}; datadirs = set()
try:    from makepy._makefiles import dirs as makedirs, files as makefiles
except: makefiles = {}; makedirs = set()

log = logging.getLogger('makepy')

py       = sys.version_info.major
wheeltag = 'py{}'.format(py)
here     = dirname(__file__)

def python(py=py): return 'python{}'.format(py)

def transpile(target):
    run('pasteurize -j 8 -w --no-diff ', target)

def backport(src_files, module):
    log.info('backporting module: %s, files: %s', module, src_files)
    pkg_dir = package_dir(module)
    rm('backport')
    mkdir('backport')
    cp(src_files, 'backport', skip=True)
    transpile('backport')
    if module is not None:
        # change tag in main modle
        sed(r'__tag__[ ]*=.*', "__tag__ = 'py2'", join('backport', pkg_dir, '__init__.py'))
    # ignore linter errors caused by transpiler
    sed(r'(ignore[ ]*=[ ]*.*)', '\\1,F401', 'backport/setup.cfg')

def setup_dir(py=py):
    if int(py) < 3: return 'backport'
    else:           return '.'

def pwd(): return abspath(os.curdir)

def find_wheel(pkg, tag):
    pat = join('dist','{}*{}*.whl'.format(pkg, tag))
    wheels = glob(pat)
    if len(wheels) == 0:
        log.error('failed to find wheels for %s in dist/%s*%s*.whl', pkg, pkg, tag)
        raise IOError(errno.ENOENT, 'no wheels in', pat)
    return wheels[0]

def dist(py=py):
    # os.environ['MAKEPYPATH'] = makepypath()
    args = ' setup.py bdist_wheel -q -d {pwd}/dist'.format(pwd=pwd())
    run(python(py) + args, cwd=setup_dir(py))

def dists(py=py):
    pys = range(2, max(3, py) + 1)  # include [2,3] + major versions up to `py`
    for py in pys: dist(py=py)

def install(pkg, py=py, source=False):
    log.info('installing pkg=%s, tag=py%s (editable=%s)', pkg, py, source)
    if source:
        # os.environ['MAKEPYPATH'] = makepypath()
        run('pip{} install -I --user -e .'.format(py), cwd=setup_dir(py))
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
        if os.environ.get('USER', '') != '': opts='-I --user'
        else:                                opts='-I'
        run('pip{} install {}'.format(py, opts), find_wheel(pkg, 'py{}'.format(py)))

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

def copy_tools(trg, force=False, mkfiles=False):
    mkdir(trg)
    files = datafiles.copy(); dirs = list(datadirs)
    if mkfiles: files.update(makefiles); dirs += list(makedirs)
    # create project tools that do not have any custom code
    for d in dirs: mkdir(join(trg,d))
    for f, text in files.items(): write_file(f, trg, text, force=force)
    log.info('copied tools: %s -> %s', list(files) + ['setup.py'], trg)

def write_file(name, trg_dir, text, force=False, strip=True, mode='w', **fmt):
    trg = join(trg_dir, name)
    if isfile(trg) and not (force or 'a' in mode):
        log.debug('skipping to write: %s', trg)
        return
    if strip: text = '{}\n'.format(text.strip())
    if len(fmt) > 0: text = text.format(**fmt)
    # log.debug('write %s, mode=%s, text="%s"', trg, mode, text)
    with open(trg, mode) as f: f.write(str(text))

def generate_makefile(trg, main):
    if main is not None:
        log.info('using MAIN=%s as main module.', main)
        text = templates['Makefile'].format(MAIN=main)
    else:
        log.info('using empty MAIN (use -m MAIN to set a custom main module).')
        text = 'include $(shell makepy include)\n'
    write_file('Makefile', trg, text)

def generate_toxini(trg, envlist=None):
    if envlist is None: envlist = 'py36,py27'
    envline = 'envlist   = ' + envlist
    log.info('using %s', envlist)
    write_file('tox.ini', trg, templates['tox.ini'], envline=envline)

def generate_packagefiles(pkg_dir, main):
    write_file('__init__.py', pkg_dir, templates['__init__.py'].format(MAIN=main))
    write_file('__main__.py', pkg_dir, templates['__main__.py'].format(MAIN=main))
    write_file('cli.py',      pkg_dir, templates['cli.py'].format(MAIN=main))

def user_name():
    name = call_unsafe('git config --get user.name').strip()
    log.debug('git user.name: %s', name)
    if name == '': name = str(os.environ.get('USER', 'System Root'))
    return name

def safe_name(): return str(re.sub(r'[^a-z0-9_\.-]', '.', user_name().lower()))

def github_name(): return str(os.environ.get('GITHUB_NAME', safe_name()))

def user_email():
    email = call_unsafe('git config --get user.email').strip()
    if email == '': email = safe_name() + '@gmail.com'
    return str(email)

def date(fmt='%Y-%m-%d', dt=None):
    if dt is None: dt = datetime.utcnow()
    return dt.strftime(fmt)

def year(): return datetime.utcnow().year

def generate_readme(trg, prj):
    COPY_INFO = 'Copyright (c) {} {} {}'.format(date('%Y'), user_name(), user_email())
    log.debug('using COPY_INFO = %s', COPY_INFO)
    write_file('README.md', trg, templates['README.md'], NEW_PRJ=prj, COPY_INFO=COPY_INFO)

def generate_setup_cfg(trg):
    write_file('setup.cfg', trg, templates['setup.cfg'])

def generate_makepy_section(trg, prj, main, module):
    t = join(trg, 'setup.cfg')
    if isfile(t):
        if 'makepy' in read_config(t):
            log.info('skipping to update existing makepy section in %s', t)
            return
        log.info('adding makepy section to %s', t)
        mode = 'a'; strip = False
    else:
        mode = 'w'; strip = True

    write_file('setup.cfg', trg, templates['makepy.cfg'], mode=mode, strip=strip,
               NAME        = user_name(),
               EMAIL       = user_email(),
               GITHUB_NAME = github_name(),
               PROJECT     = prj,
               MAIN        = main,
               MODULE      = module)

def generate_license_txt(trg):
    write_file('LICENSE.txt', trg, templates['LICENSE_txt'],
               NAME = user_name(),
               YEAR = year(),
               GITHUB_NAME = '@{}'.format(github_name()))

def generate_tests(trg, module):
    test_dir  = join(trg, 'tests')
    test_name = re.sub('[^A-Za-z0-9_]+','_', module)
    test_file = 'test_{}.py'.format(test_name)
    test_code = 'def test_{}(): pass\n'.format(test_name)
    mkdir(test_dir)
    write_file(test_file, test_dir, test_code)

def init(trg, pkg_name, module, main, envlist=None, force=False, mkfiles=False):
    assert None not in (trg, module)
    pkg_dir = join(trg, package_dir(module))
    mkdir(pkg_dir)
    copy_tools(trg, force=force, mkfiles=mkfiles)
    generate_setup_cfg(trg)
    generate_makefile(trg, main)
    generate_toxini(trg, envlist)
    generate_packagefiles(pkg_dir, main)
    generate_readme(trg, pkg_name)
    generate_tests(trg, module)
    generate_makepy_section(trg, pkg_name, main, module)
    generate_license_txt(trg)
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
        NEW_PRJ=pkg_name, TARGET=trg
    ))

r_version = r'(__version__[^0-9]+)([0-9\.]+)([^0-9]+)'
def version(pkg_dir):
    init = join(pkg_dir, '__init__.py')
    with open(init) as f:
        for line in f:
            m = re.match(r_version, line)
            if m is not None:
                v = m.groups()[1]
                log.debug('found version: %s==%s', pkg_dir, v)
                print(v)

def bumpversion(pkg_dir):
    init = join(pkg_dir, '__init__.py')
    lines = []
    with open(init) as f:
        for line in f:
            m = re.match(r_version, line)
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

def embed(src_files, target, force=False):
    if isfile(target) and not force:
        log.debug('skippig to overwrite embedding target %s', target)
        return
    log.info('embedding %s in %s', src_files, target)
    with open(target, 'w') as f:
        pre = ('# flake8:noqa=W191\n'
               'from __future__ import unicode_literals\n'
               'files = {}\n'
               'dirs  = set()\n')
        f.write(str(pre))
        for p in src_files:
            if p.startswith('./'): p = p[2:]
            d = dirname(p); code = '\n'
            if d in ('.',''): p = basename(p)
            else:             code += "dirs.add('{d}')\n".format(d=d)
            with open(p) as src: text = src.read()
            t = text.replace('\\', '\\\\').replace('"""','\\"\\"\\"').replace('\t', '\\t')
            v = re.sub(r'[^a-zA-Z0-9_]+', '_', p)
            code += "files['{p}'] = {v} = {q}\n{t}{q}\n".format(p=p, v=v, t=t, q='"""')
            log.debug('embed %s -> %s (%dchr)', p, target, len(text))
            f.write(str(code))

def help(commands):
    # TODO: implement contextual help
    print('ATTENTION: Contextual help is work-in-progress!')
    for cmd in commands: print('no contextual help found for command:', cmd)

def include():
    # TODO: use tmp mk file or located dist installed version
    return 'project.mk'

def makepypath(): return (abspath(join(here,'..')))

def uniqlist(data):
    uniq = []
    for v in data:
        if v not in uniq: uniq.append(v)
    return uniq

def add_requirements(commands, py=py):
    # complete dependencies
    cmds = commands[:]
    req3 = [('install',     'dist'),         # system install requires dist
            ('dists',       'backport')]     # py2 dist requires backport
    req2 = [('dev-install', 'backport'),     # py2 source install requires backport
            ('dist',        'backport')]     # py2 dist requires backport
    req0 = [('clean',       'clean'),        # move clean to front
            ('bumpversion', 'bumpversion')]  # move bumpversion even before clean

    if py >= 3: req2 = []                    # skip py2 requirements for py3

    for reqs in [req3, req2, req0]:
        for target, r in reqs:
            if target in cmds: cmds.insert(0, r)

    return uniqlist(cmds)


