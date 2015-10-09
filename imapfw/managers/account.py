

"""

The Account Manager will always start both side drivers. It will start and serve
the folder workers on request.

"""


#from ..concurrency.task import Task
from ..managers.manager import Manager
from ..managers.driver import createSideDriverManager
from ..runners.driver import driverRunner


class AccountManager(Manager):
    """The account manager with both sides drivers.

    This object setup the ENVIRONMENT required by the worker which consume the
    account names from the task queue.

    It does NOT defines what the worker actually does since this is the purpose
    of the engines.

    All the code of this object is run into the caller's worker (likely the main
    thread)."""

    accountExpose = [
        'serve',
        'startFolderWorkers',
        ]

    def __init__(self, ui, concurrency, workerName, rascal):
        super(AccountManager, self).__init__(ui, concurrency, workerName)

        self._rascal = rascal

        self._leftEmitter = None
        self._leftReceiver = None
        self._rightEmitter = None
        self._rightReceiver = None

        self.expose(self.accountExpose)

    def exception(self, e):
        self._exitCode = 3

    # Caller API.
    def join(self):
        self._leftReceiver.join()
        self._rightReceiver.join()
        super(AccountManager, self).join()

    # Caller API.
    def getLeftDriverEmitter(self):
        return self._leftEmitter

    # Caller API.
    def getRightDriverEmitter(self):
        return self._rightEmitter

    # Caller API.
    def initialize(self):
        # Each account requires both side drivers.
        self._leftEmitter, self._leftReceiver = createSideDriverManager(
            self.ui,
            self.concurrency,
            self._rascal,
            self.workerName,
            0,
            )
        self._rightEmitter, self._rightReceiver = createSideDriverManager(
            self.ui,
            self.concurrency,
            self._rascal,
            self.workerName,
            1,
            )

    # Caller API.
    def startDrivers(self):
        self._leftReceiver.start(driverRunner, (
            self.ui,
            self._rascal,
            self._leftReceiver.getWorkerName(),
            self.getEmitter(), # Requires that split() was already called.
            self._leftReceiver,
            ))
        self._rightReceiver.start(driverRunner, (
            self.ui,
            self._rascal,
            self._rightReceiver.getWorkerName(),
            self.getEmitter(), # Requires that split() was already called.
            self._rightReceiver,
            ))

    # Caller API.
    def kill(self):
        self._leftReceiver.kill()
        self._rightReceiver.kill()
        super(AccountManager, self).kill()

    # Caller API.
    def start(self, runner, args):
        # Controllers are already started.
        super(AccountManager, self).start(runner, args)

    ## Emitter API.
    #def startFolderWorkers(self, accountName, pendingTasks):
        #"""Each accounts sync two folders. The starting job of the account
        #manager is to start managing both folderWorkers.
        #"""

        #self.ui.debug(WRK, "creating the folders workers for %s"% accountName)

        ## Feed the folder tasks before running the folder workers so that they
        ## have something to do as soon as they start.
        #tasks = Task()
        #for task in pendingTasks:
            #tasks.appendTask(task)

        ## Prepare the folder workers.
        #for i in range(self.rascal.getMaxConnections(accountName)):
            #workerName = "Folder.Worker.%s.%i"% (accountName, i)

            ## Each folder worker works with both sides end-drivers.
            #if self._reuseDrivers is not None:
                ## We have cached driver workers to re-use.
                #left, right = self._reuseDrivers
                #leftDriverEmitter, leftDriverReceiver = left
                #rightDriverReceiver, rightDriverEmitter = right
                #self._reuseDrivers = None
            #else:
                ## Create both end driver workers.
                #leftDriverEmitter, leftDriverReceiver =
                #self._createDriver(0)
                #rightDriverEmitter, rightDriverReceiver =
                #self._createDriver(1)

            ## Build a folder manager for each folder worker.
            #folderManager = FolderManager(workerName, self.ui,
                #self.concurrency, self.rascal, tasks)

            ## Emitter the folder manager.
            #folderWorker, folderProxy = splitManager(
                #self.ui, self.concurrency, folderManager, FolderManager.proxy_expose)

            ## Start the worker.
            #folderManager.start(folderProxy)
            ## Keep track of the workers so we can serve their worker later.
            #self._workers.append(folderWorker, leftDriverEmitter,
            #rightDriverReceiver)

    ## Caller API.
    #def serve(self):
        #while len(self._workers) > 0:
            #for referent in self._workers:
                #folder, left, right = referent
                #if folder.stopped():
                    ## The folder worker is done.
                    #folder.join()
                    ## The driver workers are already stopped.
                    #self._workers.remove(referent)
                    #continue
                #folder.serve_nowait()
                #left.serve_nowait()
                #right.serve_nowait()
