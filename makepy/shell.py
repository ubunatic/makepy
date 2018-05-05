from builtins import open, str
import subprocess, re, logging, os
import shutil as sh
from os.path import join, isdir, isfile, islink

log = logging.getLogger(__name__)

def arglist(args, more_args=()):
    log.debug('arglist: (%s:%s, %s)', args, type(args), more_args)
    if type(args) not in (list,tuple): args = args.split(' ')
    return list(args) + list(more_args)

def argstr(args): return ' '.join(str(a) for a in args)

def unpad(text):
    pads = re.findall(r'^[ ]+', text, flags=re.MULTILINE)
    if text.strip() == '' or len(pads) == 0: return text
    pat = r'^{}'.format(len(pads[0]) * ' ')
    return re.sub(pat,'', text, flags=re.MULTILINE)

def block(string, *args, **kwargs):
    string = string.format(*args, **kwargs)
    return str(unpad(string).strip() + '\n')

def run(args, *more_args, **PopenArgs):
    args = arglist(args, more_args)
    log.debug("run: %s, %s", argstr(args), PopenArgs)
    return subprocess.check_call(args, **PopenArgs)

def call(args, *more_args, **PopenArgs):
    args = arglist(args, more_args)
    log.debug("call: %s, %s", argstr(args), PopenArgs)
    return subprocess.check_output(args, **PopenArgs)

def call_unsafe(args, *more_args, **PopenArgs):
    try: return call(args, *more_args, **PopenArgs)
    except subprocess.CalledProcessError as err:
        log.warn('ignoring failed call_unsafe for cmd %s: %s', args, err)
        return ''

def rm(*args):
    for f in args: sh.rmtree(f, ignore_errors=True)

def touch(*args):
    log.debug("touch %s", argstr(args))
    for f in args:
        with open(f, 'a'): pass

def ls(dirname=None):
    log.debug("ls %s", dirname)
    return os.listdir(dirname)

def cp(args, *more_args, **kwargs):
    force = kwargs.get('force', False)
    args = arglist(args, more_args)
    log.debug("cp %s, %s", argstr(args), kwargs)
    dest = args.pop()
    for f in args:
        trg = join(dest, f)
        if   isdir(f):  fn = sh.copytree
        elif isfile(f): fn = sh.copyfile
        elif islink(f): fn = sh.copyfile
        else: raise ValueError("invalid file: {}".format(f))
        exists = os.path.exists(trg)
        if not exists or force: fn(f, trg)
        if exists and force: log.debug('copied %s -> %s: target overwritten', f, trg)
        elif exists:         log.debug('skipped %s -> %s: target exists', f, trg)
        else:                log.debug('copied %s -> %s', f, trg)

def mkdir(*paths):
    log.debug("mkdir %s", argstr(paths))
    try: os.makedirs(join(*paths))
    except OSError: pass

def sed(pattern, repl, *files):
    for p in files:
        with open(p, 'r') as f: orig = f.read()
        log.debug('replacing %s with %s in %s', pattern, repl, p)
        text = re.sub(pattern, repl, orig, flags=re.MULTILINE)
        if text == orig:
            log.info('skipping to modify %s')
        else:
            with open(p, 'w') as f: f.write(text)
            log.info('modified %s', p)
