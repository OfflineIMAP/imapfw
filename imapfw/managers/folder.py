
"""

Communication between workers can be done using managers.

A manager defines and implements all the actions of a receiver and what can be
remotely controlled.

The "splitManager" function takes a manager and returns both an emitter (with
the exposed methods) and a receiver which "execute the orders".

So, if an emitter is run within a worker keep in mind that there is an inversion
of control: the child worker will give orders.

At low level, communication between workers is done via two queues per worker:
- one to send data (from the emitter to the receiver)
- the other to send the result back (from the receiver to the emitter).
Internally, it really is "passing by message".

The manager module aims at making communication between workers cool and easy.
Communicating can be achieved like almost any other method call.

"""


import time

from ..static import Constant



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
