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

The concurrency module defines common interfaces to whatever backend is used
(multiprocessing, Python threading, etc).

A worker is the generic term used to define a thread (for Python threading) or a
process (for multiprocessing).

"""

from imapfw import runtime

from ..constants import WRK


SimpleLock = None # Defined later.
TIMEOUT=30


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
    def get(self):          raise NotImplementedError
    def get_nowait(self):   raise NotImplementedError
    def put(self):          raise NotImplementedError


class LockInterface(object):
    def acquire(self):  raise NotImplementedError
    def release(self):  raise NotImplementedError


class ConcurrencyInterface(object):
    def createLock(self):                   raise NotImplementedError
    def createQueue(self):                  raise NotImplementedError
    def createWorker(self):            raise NotImplementedError
    def getCurrentWorkerNameFunction(self): raise NotImplementedError


class LockBase(LockInterface):
    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, t, v, tb):
        self.lock.release()


class ThreadingBackend(ConcurrencyInterface):
    def createWorker(self, name, target, args):
        from threading import Thread

        class Worker(WorkerInterface):
            def __init__(self, name, target, args):
                self._name = name

                self.ui = runtime.ui
                self._thread = Thread(name=name, target=target, args=args,
                    daemon=True)

            def getName(self):
                return self._name

            def kill(self):
                # No kill possible with threading. That's why we set the threads
                # in daemon mode: workers get's killed once the main thread
                # stop.
                self.ui.debugC(WRK, "%s killed"% self._name)

            def start(self):
                self._thread.start()
                self.ui.debugC(WRK, "%s started"% self._name)

            def join(self):
                self.ui.debugC(WRK, "%s join"% self._name)
                self._thread.join() # Block until process is done.
                self.ui.debugC(WRK, "%s stopped"% self._name)

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

            def get(self):
                return self._queue.get(timeout=TIMEOUT)

            def get_nowait(self):
                try:
                    return self._queue.get_nowait()
                except Empty:
                    return None

            def put(self, data):
                self._queue.put(data)

        return TQueue()

    def getCurrentWorkerNameFunction(self):
        from threading import current_thread

        def currentWorkerName():
            return current_thread().name
        return currentWorkerName


class MultiProcessingBackend(ConcurrencyInterface):
    def createWorker(self, name, target, args):
        from multiprocessing import Process

        class Worker(WorkerInterface):
            def __init__(self, name, target, args):
                self._name = name

                self.ui = runtime.ui
                self._process = Process(name=name, target=target, args=args)

            def getName(self):
                return self._name

            def kill(self):
                self._process.terminate() # Send SIGTERM.
                self.join(verbose=False)
                self.ui.debugC(WRK, "%s killed"% self._name)

            def start(self):
                self._process.start()
                self.ui.debugC(WRK, "%s started"% self._name)

            def join(self, verbose=True):
                if verbose is True:
                    self.ui.debugC(WRK, "%s join"% self._name)
                self._process.join() # Block until process is done.
                if verbose is True:
                    self.ui.debugC(WRK, "%s stopped"% self._name)

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

            def get(self):
                return self._queue.get(timeout=TIMEOUT)

            def get_nowait(self):
                try:
                    return self._queue.get_nowait()
                except queue.Empty:
                    return None

            def empty(self):
                return self._queue.empty()

            def put(self, data):
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
        SimpleLock = concurrency.createLock
        return concurrency
    except KeyError:
        raise Exception("unkown backend: %s"% backendName)
