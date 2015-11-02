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


#
#TODO: remove all of this. Make engines functions.
#

from imapfw import runtime

from imapfw.types.repository import RepositoryBase

# Annotations.
from imapfw.types.account import Account

class EngineInterface(object):
    def getRepositories(self):  raise NotImplementedError
    def run(self):              raise NotImplementedError


class Engine(EngineInterface):
    @staticmethod
    def getRepositories(account: Account):
        """
        Return the left and right repositories instances for this account.
        """

        left = runtime.rascal.get(account.left.__name__, [RepositoryBase])
        rght = runtime.rascal.get(account.right.__name__, [RepositoryBase])
        left.fw_init()
        rght.fw_init()
        return left, rght
