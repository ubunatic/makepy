from subprocess import check_output
import sys, os, logging

_py = None

log = logging.getLogger(__name__)

def pyv():
    """Calls `python` determine and return default major python version."""
    global _py
    if _py is None:
        try:
            res = check_output([
                'python', '-c',
                'import sys; sys.stdout.write(str(sys.version_info.major))'
            ]).strip()
            val = str(bytes(res).decode('utf-8'))
        except:
            val = ''
        if val == '': _py = sys.version_info.major
        else:         _py = int(val)
        if _py <= 0: raise SystemError('invalid python version', _py)
    return _py

def wheeltag(py=None):
    return 'py{}'.format(py or pyv())

def pip(py=None):
    py = py or pyv()
    if py == pyv():
        exe = 'pip'
        log.info('using default pip: %s', exe)
    elif sys.version_info.major == py:
        base = os.path.basename(sys.executable)
        if 'python' in base:
            exe = base.replace('python', 'pip')
            log.info('using sys.executable as pip base: %s', exe)
        else:
            log.warn('unknown sys.executable, using pip string: %s', exe)
    else:
        # TODO: test existence and find alternatives
        exe = 'pip{}'.format(py)
        log.info('using pip string: %s', exe)
    # TODO: allow spaces!
    if ' ' in exe: raise ValueError('pip executable with spaces is not supported')
    return exe

def python(py=None):
    py = py or pyv()
    if py == pyv():
        exe = 'python'
        log.info('using default python: %s', exe)
    elif sys.version_info.major == py:
        exe = os.path.basename(sys.executable)
        log.info('using sys.executable basename: %s', exe)
    else:
        # TODO: test existence and find alternatives
        exe = 'python{}'.format(py)
        log.info('using python string: %s', exe)
    # TODO: allow spaces!
    if ' ' in exe: raise ValueError('python executable with spaces is not supported')
    return exe
