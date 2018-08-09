from makepy import cli
from makepy import commands
from makepy import config
from makepy import tox

def test_cli():
    assert hasattr(cli,'main')

def test_commands():
    commands.uninstall('makepy-uninstall-dummy')
    assert len(commands.github_name()) > 0

    req = commands.add_requirements(['install'])
    assert 'dist' in req

def test_config():
    exp = ['makepy']
    assert exp == config.find_packages()
    assert exp == config.find_packages_ns('.')
    assert exp == config.find_packages_ns('')

    try: config.find_packages_ns(None); ok = False
    except Exception: ok = True
    assert ok, "None namespace must raise an error"

def test_tox():
    assert hasattr(tox, 'tox')
