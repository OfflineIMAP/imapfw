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


class DriverInternalInterface(object):
    """Users must NOT change those methods."""

    def fw_init(self):          raise NotImplementedError
    def fw_sanityChecks(self):  raise NotImplementedError


class DriverInterface(DriverInternalInterface):

    conf = {} # The configuration of the type has to be there.
    isLocal = None

    def connect(self):      raise NotImplementedError
    def getFolders(self):   raise NotImplementedError
    def getName(self):      raise NotImplementedError
    def getOwner(self):     raise NotImplementedError
    def logout(self):       raise NotImplementedError


class DriverBase(DriverInterface):
    def fw_init(self, ui, conf, owner):
        self.ui = ui
        self.conf = conf # Comes from the type.
        self._owner = owner

    @staticmethod
    def fw_sanityChecks(inst):
        if not isinstance(inst, DriverInterface):
            raise Exception("driver class %s does not satisfy DriverInterface"%
                inst.__class__.__name__)

    def getName(self):
        return self.__class__.__name__

    def getOwner(self):
        return self._owner
