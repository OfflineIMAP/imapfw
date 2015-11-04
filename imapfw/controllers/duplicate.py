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

from imapfw import runtime

from .controller import Controller

#TODO
class Duplicate(Controller):
    """Controller to duplicate writes to another driver."""

    conf = None

    def fw_initController(self):
        self.duplicateDriver = None #TODO: setup driver...
        self.ui = runtime.ui

        self.mode = self.conf.get('exception').lower() # fatal, warn or pass.

    def __getattr__(self, name):
        raise AttributeError("method '%s' missing in Duplicate controller"% name)

    def _call(self, name, *args, **kwargs):
        try:
            values = getattr(self.duplicateDriver, name)(*args, **kwargs)
        except Exception as e:
            if self.mode == 'pass':
                pass
            elif self.mode == 'warn':
                self.ui.warn('TODO: warning not implemented')
            else:
                raise
        finally:
            return getattr(self.driver, name)(*args, **kwargs)

    def connect(self):
            values = self._call('connect')

    #TODO: implement DriverInterface.

