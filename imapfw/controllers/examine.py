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
class ExamineController(Controller):
    """Controller to examine a repository."""

    def connect(self, *args):
        runtime.ui.info("## Configuration")
        runtime.ui.info("")
        for k, v in self.driver.conf.items():
            if k == 'password' and isinstance(v, (str, bytes)):
                v = '<hidden>'
            runtime.ui.info("* %s: %s"% (k, v))
        return self.driver.connect(*args)

    def getFolders(self):
        folders = self.driver.getFolders()
        runtime.ui.info("")
        runtime.ui.info("## Infos")
        runtime.ui.info("")
        runtime.ui.info("Found %i folders: %s"%(len(folders), folders))
        runtime.ui.info("")
        return folders
