# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

The concurrency module defines a common interfaces to whatever backend is used
(multiprocessing, Python threading, etc).

"worker" is the generic term used to define a thread (for Python threading) or a
process (for multiprocessing).

"""

import pickle

from imapfw import runtime
from imapfw.constants import WRK


SimpleLock = None # Defined at runtime.


def WorkerSafe(lock):
    """Decorator for locking any callable."""

    def decorate(func):
        def safeFunc(*args, **kwargs):
            with lock:
                values = func(*args, **kwargs)
            return values
        return safeFunc

    return decorate


class WorkerInterface(object):
    def getName(self):  raise NotImplementedError
    def join(self):     raise NotImplementedError
    def kill(self):     raise NotImplementedError
    def start(self):    raise NotImplementedError


class QueueInterface(object):
    def empty(self):        raise NotImplementedError
    def get(self):          raise NotImplementedError
    def get_nowait(self):   raise NotImplementedError
    def put(self):          raise NotImplementedError


class LockInterface(object):
    def acquire(self):  raise NotImplementedError
    def release(self):  raise NotImplementedError


class ConcurrencyInterface(object):
    def createLock(self):                   raise NotImplementedError
    def createQueue(self):                  raise NotImplementedError
    def createWorker(self):                 raise NotImplementedError
    def getCurrentWorkerNameFunction(self): raise NotImplementedError


class LockBase(LockInterface):
    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, t, v, tb):
        self.lock.release()


class ThreadingBackend(ConcurrencyInterface):
    """
    Handling signals with threading
    ===============================

    SIGTERM
    -------

    Main thread get KeyboardInterrupt. Only daemon childs gets killed.

    SIGKILL
    -------

    Kills everything (the process is killed, so the threads).
    """

    def createWorker(self, name, target, args):
        from threading import Thread

        class Worker(WorkerInterface):
            def __init__(self, name, target, args):
                self._name = name

                self._thread = Thread(name=name, target=target, args=args,
                    daemon=True)

            def getName(self):
                return self._name

            def kill(self):
                """Kill a worker.

                This is only usefull for the workers working with a failed
                worker. In daemon mode: workers get's killed when the main thread
                gets killed."""

                runtime.ui.debugC(WRK, "%s killed"% self._name)

            def start(self):
                self._thread.start()
                runtime.ui.debugC(WRK, "%s started"% self._name)

            def join(self):
                runtime.ui.debugC(WRK, "%s join"% self._name)
                self._thread.join() # Block until thread is done.
                runtime.ui.debugC(WRK, "%s joined"% self._name)

        return Worker(name, target, args)

    def createLock(self):
        from threading import Lock

        class TLock(LockBase):
            def __init__(self, lock):
                self.lock = lock

            def __enter__(self):
                self.lock.acquire()

            def __exit__(self, t, v, tb):
                self.lock.release()

            def acquire(self):
                self.lock.acquire()

            def release(self):
                self.lock.release()

        return TLock(Lock())

    def createQueue(self):
        from queue import Queue, Empty # Thread-safe.

        class TQueue(QueueInterface):
            def __init__(self):
                self._queue = Queue()

            def empty(self):
                return self._queue.empty()

            def get(self):
                return self._queue.get()

            def get_nowait(self):
                try:
                    return self._queue.get_nowait()
                except Empty:
                    return None

            def put(self, data):
                # Fail now if data can't be pickled. Otherwise, error will be
                # raised at random time.
                pickle.dumps(data)
                self._queue.put(data)

        return TQueue()

    def getCurrentWorkerNameFunction(self):
        from threading import current_thread

        def currentWorkerName():
            return current_thread().name
        return currentWorkerName


class MultiProcessingBackend(ConcurrencyInterface):
    """
    Handling signals with multiprocessing
    =====================================

    SIGTERM
    -------

    Signal is sent to all workers by multiprocessing.

    SIGKILL
    -------

    Current process is killed. Other processes continue (orphaned if main
    process was killed).
    """

    def createWorker(self, name, target, args):
        from multiprocessing import Process

        class Worker(WorkerInterface):
            def __init__(self, name, target, args):
                self._name = name

                self._process = Process(name=name, target=target, args=args)

            def getName(self):
                return self._name

            def kill(self):
                """Kill a worker.

                This is only usefull for the workers working with a failed
                worker. KeyboardInterrupt is natively sent to all workers by
                multiprocessing."""

                self._process.terminate() # Send SIGTERM.
                self.join(verbose=False)
                runtime.ui.debugC(WRK, "%s killed"% self._name)

            def start(self):
                self._process.start()
                runtime.ui.debugC(WRK, "%s started"% self._name)

            def join(self, verbose=True):
                if verbose is True:
                    runtime.ui.debugC(WRK, "%s join"% self._name)
                self._process.join() # Block until process is done.
                if verbose is True:
                    runtime.ui.debugC(WRK, "%s joined"% self._name)

        return Worker(name, target, args)

    def createLock(self):
        from multiprocessing import Lock

        class MLock(LockBase):
            def __init__(self, lock):
                self.lock = lock

            def acquire(self):
                self.lock.acquire()

            def release(self):
                self.lock.release()

        return MLock(Lock())

    def createQueue(self):
        from multiprocessing import Queue
        import queue

        class MQueue(QueueInterface):
            def __init__(self):
                self._queue = Queue()

            def empty(self):
                return self._queue.empty()

            def get(self):
                return self._queue.get()

            def get_nowait(self):
                try:
                    return self._queue.get_nowait()
                except queue.Empty:
                    return None

            def put(self, data):
                # Fail now if data can't be pickled. Otherwise, error will be
                # raised at random time.
                pickle.dumps(data)
                self._queue.put(data)

        return MQueue()

    def getCurrentWorkerNameFunction(self):
        from multiprocessing import current_process

        def currentWorkerName():
            return current_process().name
        return currentWorkerName



ConcurrencyBackends = {
    'multiprocessing': MultiProcessingBackend,
    'threading': ThreadingBackend,
}

def Concurrency(backendName):
    global SimpleLock
    try:
        concurrency = ConcurrencyBackends[backendName]()
        if SimpleLock is None:
            SimpleLock = concurrency.createLock
        return concurrency
    except KeyError:
        raise Exception("unkown backend: %s"% backendName)
