from makepy import python
from makepy import shell

def test_python():
    v    = python.pyv()
    assert v > 0
    py   = python.python()
    assert len(py) > 0
    pip  = python.pip()
    assert len(pip) > 0
    whl  = python.wheeltag()
    assert len(whl) > 0

    for py in (1,2,3,4):
        assert len(python.python(py)) > 0
        assert len(python.pip(py)) > 0
        assert len(python.wheeltag(py)) > 0

def test_python_versions():
    py2 = python.python(2)
    shell.run(py2 + ' --version')
    v = shell.call(py2, '-c', 'print 1').strip()
    assert v == '1'

    py3 = python.python(3)
    shell.run(py3 + ' --version')
    v = shell.call(py3, '-c', 'print(1)').strip()
    assert v == '1'

