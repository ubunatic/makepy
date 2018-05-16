from makepy.cli import github_name
from builtins import str

def test_ghname():
    name = github_name()
    assert type(name) is str

def main():
    test_ghname()

if __name__ == '__main__': main()
