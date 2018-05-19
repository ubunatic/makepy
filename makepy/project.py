from __future__ import absolute_import
from builtins import open
from configparser import ConfigParser
import sys, os

def warn(text, *values):
    w = 'WARNING: ' + (text % tuple(values)) + '\n'
    sys.stderr.write(w)

def read(filename):
    with open(filename) as f: return f.read()

def read_lines(filename):
    with open(filename) as f:
        for l in f: yield l.strip()

def read_config(cfg_file='setup.cfg'):
    p = ConfigParser()
    p.read(cfg_file)
    return {sec:dict(p.items(sec)) for sec in p.sections()}

def unquote(s): return s.replace('"','').replace("'",'').strip()

def cleanup_classifiers(classifiers):
    return [c for c in classifiers if c.strip() != ""]

def read_version(main_dir, init='__init__.py'):
    version = tag = None
    init = os.path.join(main_dir, init)
    for l in read_lines(init):
        if   l.startswith('__version__'): version = unquote(l.split('=')[1])
        elif l.startswith('__tag__'):     tag     = unquote(l.split('=')[1])

    if version is None: raise ValueError('__version__ missing in {}'.format(init))
    if tag     is None: raise ValueError('__tag__ missing in {}'.format(init))
    return version, tag

def parse_wheeltag(args=None):
    if args is None: args = sys.argv[1:]
    wheeltag = 'py{}'.format(sys.version_info.major)
    for i, arg in enumerate(args):
        if arg == '--python-tag': wheeltag = args[i+1]
    return wheeltag

def read_makepy_section(*files):
    files = set(tuple(files) + ('makepy.cfg', 'setup.cfg'))
    d = None
    for f in files:
        if os.path.isfile(f): d = read_config(f).get('makepy')
        if d is not None: break
    if d is None:
        raise Exception('[makepy] section not found in config files', files,
                        os.listdir('.'))
    return d

def read_setup_args(cfg_file='setup.cfg'):
    d = read_makepy_section(cfg_file)

    author_name  = d.get('author')
    author_email = d.get('email')
    github_name  = d.get('github_name')

    name     = d['name']
    license  = d['license']
    main     = d['main']
    binary   = d.get('binary')
    requires = d.get('requires','').split(' ')
    keywords = d.get('keywords','').split(' ')

    description   = d['description']
    readme_format = d.get('readme_format', 'text/markdown')
    readme = read('README.md')  # TODO: detect readme format

    classifiers  = d.get('classifiers', '').split('\n')
    classifiers += [d['status']]

    project_dir = os.path.dirname(cfg_file)
    project_name = name

    scripts = [s.split('=') for s in d.get('scripts','').strip().split('\n')]

    code_version, tag = read_version(os.path.join(project_dir, main))
    wheeltag          = parse_wheeltag()
    version           = d.get('version', code_version)
    if version != code_version:
        raise ValueError('project version != code_version, '
                         'please update or remove "makepy:version" from setup.cfg')

    if wheeltag != tag:
        warn('Wheel tag != code tag. You are building for python-tag "%s", '
             'but your code is tagged with "%s"', wheeltag, tag)

    if wheeltag == 'py2': py = 2
    else:                 py = sys.version_info.major

    versions      = [unquote(v) for v in d.get('python_versions', str(py)).split()]
    deps_default  = d.get('default_deps','').split(' ')
    deps_backport = d.get('backport_deps','').split(' ')

    console_scripts = ['{}={}'.format(cmd, spec) for cmd, spec in scripts]
    entry_points    = {'console_scripts': console_scripts}

    if binary is not None and main is not None:
        script = '{b}={m}:main'.format(b=binary, m=main)
        console_scripts.append(script)

    if wheeltag == 'py2':
        for script in console_scripts[:]:
            b,m = script.split('=')
            b = '{}'.format(b)  # TODO: check if exists and propose resolutions
            console_scripts.remove(script)
            console_scripts.append('{}={}'.format(b,m))

        orig_version = version
        version = version  # + '.pre'

        requires += deps_backport
        readme = """
        **<span style="color:red">
        This is the backport version {version} of '{name}' for Python 2.
        Please upgrade to Python 3+ and use the current '{name}' version {orig_version}.
        </span>**\n\n{rest}
        """.format(name=name, rest=readme, version=version, orig_version=orig_version)
    else:
        requires += deps_default

    # NOTE: We must not distinguish between py2/py3 in python_requires and classifiers,
    #       since this will prevent pip2 to find the py2 wheel for versions, which have
    #       the py3 wheel tagged with, e.g., '>=3'.
    classifiers += ['Programming Language :: Python :: {}'.format(v) for v in versions]
    classifiers = list(set(classifiers))
    python_requires = d.get('python_requires', '>=2.6')

    if github_name is None:
        project_urls = None
        url = None
    else:
        gh = github_name
        url = 'https://github.com/{}/{}'.format(gh, name)
        project_urls = {
            'Documentation': 'https://github.com/{}/{}'.format(gh, name),
            'Bug Reports':   'https://github.com/{}/{}/issues'.format(gh, name),
            'Funding':       'https://github.com/{}/{}'.format(gh, name),
            'Say Thanks!':   'https://saythanks.io/to/{}'.format(gh),
            'Source':        'https://github.com/{}/{}'.format(gh, name),
        }

    classifiers = cleanup_classifiers(classifiers)

    return dict(
        name             = project_name,
        version          = version,
        description      = description,
        long_description = readme,
        long_description_content_type = readme_format,
        url              = url,
        author           = author_name,
        author_email     = author_email,
        python_requires  = python_requires,
        license          = license,
        classifiers      = classifiers,
        keywords         = keywords,
        install_requires = requires,
        # example: pip install widdy[dev]
        extras_require = {
            'dev': ['pytest','flake8','twine','pasteurize'],
            # check-mainfest coverage
        },
        # data files
        # package_data={ 'sample': ['package_data.dat'] },
        # extern data files installed into '<sys.prefix>/my_data'
        # data_files=[('my_data', ['data/data_file'])],
        entry_points = entry_points,
        # The key is used to render the link text on PyPI.
        project_urls = project_urls,
    )

