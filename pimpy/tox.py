from pimpy.shell import run, rm

def tox(envlist=None):
    if envlist is None: run(['tox'])
    else:               run(['tox', '-e', 'envlist'])

def clean(): rm('.tox')
