"""

The concurrency module defines common interfaces to whatever backend is used
(multiprocessing, Python threading, etc).

A worker is the generic term used to define a thread (for Python threading) or a
process (for multiprocessing).

"""

import time


class BasicWorkerInterface(object):
    def getName(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def join(self):
        raise NotImplementedError


class QueueInterface(object):
    def get(self):
        raise NotImplementedError

    def get_nowait(self):
        raise NotImplementedError

    def put(self, data):
        raise NotImplementedError


class LockInterface(object):
    def acquire(self):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError


class ConcurrencyInterface(object):
    def createLock(self):
        raise NotImplementedError

    def createQueue(self):
        raise NotImplementedError

    def createBasicWorker(self, name, target, args):
        raise NotImplementedError

    def getCurrentWorkerNameFunction(self):
        raise NotImplementedError


class LockBase(LockInterface):
    """All locks support the 'with' statement."""

    def __enter__(self):
        self.lock.acquire()

    def __exit(self, t, v, tb):
        self.lock.release()



class ThreadingBackend(ConcurrencyInterface):
    def createBasicWorker(self, name, target, args):
        from threading import Thread

        class BasicWorker(BasicWorkerInterface):
            def __init__(self, name, target, args):
                self._thread = Thread(name=name, target=target, args=args,
                    daemon=True)
                self._name = name

            def getName(self):
                return self._name

            def kill(self):
                # No kill possible with threading. That's why we set the threads
                # in daemon mode: workers get's killed once the main thread
                # stop.
                pass

            def start(self):
                self._thread.start()

            def join(self):
                self._thread.join() # Block until process is done.

        return BasicWorker(name, target, args)

    def createLock(self):
        from threading import Lock

        class TLock(LockBase):
            def __init__(self, lock):
                self.lock = lock

            def acquire(self):
                self.lock.acquire()

            def release(self):
                self.lock.release()

        return TLock(Lock())

    def createQueue(self):
        from collections import deque # Thread-safe.

        from ..constants import Constants

        class TQueue(QueueInterface):
            def __init__(self):
                self._queue = deque()

            def get(self):
                # Must be "blocking" to match multiprocessing.
                while True:
                    try:
                        return self._queue.pop() # At right side.
                    except IndexError:
                        time.sleep(Constants.SLEEP)

            def get_nowait(self):
                try:
                    return self._queue.pop() # At right side.
                except IndexError:
                    return None

            def put(self, data):
                self._queue.appendleft(data)

        return TQueue()

    def getCurrentWorkerNameFunction(self):
        from threading import current_thread

        def currentWorkerName():
            return current_thread().name
        return currentWorkerName


class MultiProcessingBackend(ConcurrencyInterface):
    def createBasicWorker(self, name, target, args):
        from multiprocessing import Process

        class BasicWorker(BasicWorkerInterface):
            def __init__(self, name, target, args):
                self._process = Process(name=name, target=target, args=args)
                self._name = name

            def getName(self):
                return self._name

            def kill(self):
                self._process.terminate() # Send SIGTERM.
                self._process.join()

            def start(self):
                self._process.start()

            def join(self):
                self._process.join() # Block until process is done.

        return BasicWorker(name, target, args)

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
                return self._queue.get()

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
    try:
        return ConcurrencyBackends[backendName]()
    except KeyError:
        raise Exception("unkown backend: %s"% backendName)
