
import os
import sys


def testingPath():
    return os.path.join(
        os.path.abspath(sys.modules['imapfw'].__path__[0]),
        'testing')
