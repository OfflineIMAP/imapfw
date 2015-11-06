# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""

Test the rascal.

This intend to check all the content of the rascal. The API of accounts,
repositories, controllers and drivers are tested using mocks.

"""

import unittest

from imapfw import runtime
from imapfw.constants import ARC

from imapfw.types.account import loadAccount, Account
from imapfw.types.repository import Repository


class TestRascalAccount(unittest.TestCase):

    DEF_ACCOUNT = None
    LOG = None

    account = None
    repositories = []

    def setUp(self):
        print()

    def test_00_loadAccount(self):
        account = loadAccount(self.DEF_ACCOUNT)
        runtime.ui.debugC(ARC, repr(account))
        self.assertIsInstance(account, Account)
        self.__class__.account = account

    def test_01_getRight(self):
        repository = self.__class__.account.fw_getRight()
        runtime.ui.debugC(ARC, repr(repository))
        self.assertIsInstance(repository, Repository)
        self.__class__.repositories.append(repository)

    def test_02_getLeft(self):
        repository = self.__class__.account.fw_getLeft()
        runtime.ui.debugC(ARC, repr(repository))
        self.assertIsInstance(repository, Repository)
        self.__class__.repositories.append(repository)
