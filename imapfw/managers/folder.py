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


#class FolderManager(AccountFolderManagerBase):
class FolderManager(object):
    """Manage a folder worker. This aims to become the referent."""

    # The interface for the folder runners.
    proxy_expose = [
        'declareStopped', # Inherited
        'getTask', # Inherited
        'interruptAll', # Inherited
        'appendTask', # Inherited
    ]

    def __init__(self,
        managerName, ui, concurrency, rascal, tasks):

        super(FolderManager, self).__init__(
            managerName, ui, concurrency, rascal, tasks)

    def kill(self):
        self.worker.kill()

    def start(self, folderProxy):
        self.worker = self.concurrency.createWorker(
            name=self.managerName,
            target=topRunner,
            args=(
                self.managerName,
                self.ui,
                self.rascal,
                folderProxy, # Manage this worker from inside the worker.
                folderRunner,
            )
        )
        self.worker.start()
