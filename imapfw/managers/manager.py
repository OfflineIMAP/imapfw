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

Managers are handy objects to handle both how a worker is managed (`start`,
`join`, `kill`) and how the worker interacts with other workers. They must
derivate from the `Manager` class.

In order to interact with other workers, each manager aims to be splitted via a
call to `split` which returns two new objects::
    - the emitter
    - the receiver

Both objects aims at running in different workers. They are the "passing by
message" implementation to communicate intuitively between workers.

The emitter controls the receiver with simple method calls like this:

    result = emitter.doSomething(any, parameter, to=send)

The code implemented in "doSomething" is run by the receiver.

The limitation is about the parameters and the returned values whose must
be accepted by the queues. Don't expect to pass your SO_WONDERFULL objects.
Take this limitation as a chance to write good code and objects with simple
APIs. However, if you really need to pass objects, consider implementing the
.serializer.SerializerInterface class.


Name conventions
================

Because the manager gets splitted, the methods of a manager can intend different
purposes:
    - factorized code for the manager;
    - factorized code for the derivated classes;
    - code for the caller of the manager instance;
    - code for the caller of the receiver instance;
    - code to expose with the emitter.

Name conventions helps to know what how the method will be used.  Also, the
`split` operation relies on those name conventions.

- 'exposed_' (prefix): will be available in the emitter.
- 'manager_' (prefix): factorized code.
- _nowait' (suffix): the emitter won't wait for a result from the receiver.
  This is how aync calls must be done. Returns None.

The prefix 'exposed_' and suffix '_nowait' are stripped on the emmiter side.


The receiver
============

The receiver executes the orders. It is added the method `serve_nowait` so it
can serve the emitter. This method returns True or False whether it should
continue serving or not.

All the requested methods are executed and the results sent back to the Emmiter.
This is sequential: each request ends before the next is started (they are
internally put in a queue). So, it's fine to implement methods like this in the
manager:

    def __init__(self):
        self.result = None

    def exposed_longRequest_nowait(self):
        # Code taking a very long time; self.result gets True or
        # False.
        self.result = theResultIsTrueOrFalse()

    def exposed_getLongRequestResult(self):
        return self.result

The emitter won't have to worry at all.

Case A
------

    emitter.longRequest() # async
    this_is_called_NOW() # don't wait here
    result = emitter.getLongRequestResult() # wait here (1)
    doSomethingWith(result) # result is either True or False but
                            # NEVER None

(1) The "emmiter code" will wait at emitter.getLongRequestResult() and get the
CORRECT result because the receiver won't even start the method
getLongRequestResult() before the previous call to longRequest() is done.

Case B
------

    emitter.longRequest() # async
    this_is_called_NOW() # don't wait here
    emitter.doAnythinElse() # wait here (2)
    result = emitter.getLongRequestResult() # don't wait here
    doSomethingWith(result) # result is either True or False but
                            # NEVER None

(2) The above code would wait here for emitter.longRequest() to finish.

Case C
------

    emitter.longRequest() # async, don't wait here
    this_is_called_NOW() # don't wait here
    emitter.doAnotherThing() # async, don't wait here (3)

    result = emitter.getLongRequestResult() # wait here

    doSomethingWith(result) # result is either True or False but
                            # NEVER None

(3) The above code would neither wait for longRequest() nor doAnotherThing(). It
would wait for BOTH to be done at the getLongRequestResult() call. The returned
value is CORRECT.

"""

import inspect

from ..constants import WRK, EMT
from ..error import InterruptionError


class ManagerCallerInterface(object):
    def join(self):                 raise NotImplementedError
    def kill(self):                 raise NotImplementedError
    def split(self):                raise NotImplementedError
    def start(self, target, args):  raise NotImplementedError


class ManagerEmitterInterface(object):
    def interruptAll(self): raise NotImplementedError
    def stopServing(self):  raise NotImplementedError


class Manager(ManagerCallerInterface, ManagerEmitterInterface):
    """The manager base class."""

    def __init__(self, ui, concurrency, workerName):
        self.ui = ui
        self.concurrency = concurrency
        self.workerName = workerName

        self._worker = None
        self._stopServing = False
        self._emitter = None

    def manager_setEmitter(self, emitter):
        self._emitter = emitter

    def manager_shouldServe(self):
        return not self._stopServing


    def exposed_unkownInterruptionError(self, reason):
        raise Exception("%s got following interruption: %s"%
            (self.workerName, reason))


    def exposed_interruptionError(self, reason):
        raise InterruptionError("%s got following interruption: %s"%
            (self.workerName, reason))

    def exposed_stopServing(self):
        self._stopServing = True


    def getEmitter(self):
        return self._emitter

    def getWorkerName(self):
        return self.workerName

    def join(self):
        self.ui.debugC(WRK, "%s join"% self.workerName)
        self._worker.join()
        self.ui.debugC(WRK, "%s stopped"% self.workerName)

    def kill(self):
        self._worker.kill()
        self.ui.debugC(WRK, "%s killed"% self.workerName)

    def split(self):
        """Split this manager

        :returns: a tuple of instances of an Emitter and a Receiver."""

        class Receiver(object):
            """Receiver base class. Executes the orders of the emitter."""

            def __init__(self, incomingQueue, resultQueue, manager):
                self.__incomingQueue = incomingQueue
                self.__resultQueue = resultQueue
                self.__obj = manager # Embedd the full manager.

            def __getattr__(self, name):
                # Return the requested method of the embedded manager.
                return getattr(self.__obj, name)

            def get_obj(self):
                return self.__obj

            def serve_nowait(self):
                """Serve the pending requests."""

                while self.__obj.manager_shouldServe():
                    # Read each pending incoming request.
                    request = self.__incomingQueue.get_nowait()
                    if request is None:
                        break

                    # Execute the request.
                    method, args, kwargs = request
                    if len(args) > 0:
                        if len(kwargs) > 0:
                            result = getattr(
                                self.__obj, method)(*args, **kwargs)
                        else:
                            result = getattr(
                                self.__obj, method)(*args)
                    else:
                        if len(kwargs) > 0:
                            result = getattr(
                                self.__obj, method)(**kwargs)
                        else:
                            result = getattr(
                                self.__obj, method)()
                    if not method.endswith('_nowait'):
                        # Send the results back to the emitter.
                        self.__resultQueue.put(result)
                # Let the caller know if the receiver should continue to serve.
                return self.__obj.manager_shouldServe()

        def Emitter(ui, incomingQueue, resultQueue, manager):
            """The emitter factory."""

            def proxy_method(name, waitResult):
                def nowait(self, *args, **kwargs):
                    ui.debugC(EMT, "calling %s: %s %s %s"%
                        (self.__class__.__name__, name, args, kwargs))
                    self.__incomingQueue.put((name, args, kwargs))
                    return None

                def wait(self, *args, **kwargs):
                    ui.debugC(EMT, "calling %s: %s %s %s"%
                        (self.__class__.__name__, name, args, kwargs))
                    self.__incomingQueue.put((name, args, kwargs))
                    return self.__resultQueue.get()

                if waitResult is True:
                    return wait
                return nowait

            # Build the class.
            cls_Emitter = type(
                "emitter%s"% manager.__class__.__name__, (object,), {})

            # Add the methods to the emitter.
            for name in [attr[0] for attr in inspect.getmembers(manager)]:
                if name.startswith('exposed_'):
                    exposedName = name[8:] # Remove 'exposed_' from the name.
                    if name.endswith('_nowait'):
                        exposedName = exposedName[:-7]
                        setattr(cls_Emitter, exposedName,
                            proxy_method(name, waitResult=False))
                    else:
                        setattr(cls_Emitter, exposedName,
                            proxy_method(name, waitResult=True))
            emitter = cls_Emitter()
            # Fix attributes of the emitter.
            emitter.__incomingQueue = incomingQueue
            emitter.__resultQueue = resultQueue

            ui.debugC(EMT, "new instance %s: %s"% (emitter.__class__.__name__,
                [x for x in dir(emitter) if not x.startswith('_')]))
            return emitter # The instance.

        # split() really starts here.
        incomingQueue = self.concurrency.createQueue()
        resultQueue = self.concurrency.createQueue()

        receiver = Receiver(incomingQueue, resultQueue, self)
        emitter = Emitter(self.ui, incomingQueue, resultQueue, self)

        receiver.manager_setEmitter(emitter) # Let the receiver keep track on his emitter.
        return emitter, receiver

    def start(self, target, args):
        self._worker = self.concurrency.createBasicWorker(
            name=self.workerName, target=target, args=args)
        self._worker.start()
        self.ui.debugC(WRK, "%s started"% self.workerName)


if __name__ == '__main__':
    #
    # Run this demo like this (from the root directory):
    # python3 -m imapfw.managers.manager
    #

    import sys
    import time

    import imapfw

    from imapfw.concurrency.concurrency import Concurrency
    from imapfw.managers.manager import Manager
    from imapfw.ui.tty import TTY


    c = Concurrency('multiprocessing')
    q = c.createQueue()
    q.get_nowait()

    ui = TTY(c.createLock())


    def output(args):
        print(args)
        sys.stdout.flush()


    def runner(emitter):
        output('runner started')

        output('initA')
        emitter.initA()

        output('initB')
        emitter.initB()

        output('readA')
        output(emitter.readA())

        #output('sleeping')
        #time.sleep(5)

        #output('readA')
        #output(emitter.readA())

        output('readB')
        output(emitter.readB())

        emitter.stopServing()



    class TT(Manager):
        def __init__(self):
            super(TT, self).__init__(ui, c, 'ttworker')
            self.A = 'OopsA'
            self.B = 'OopsB'

        def exposed_readA(self):
            output('in receiver: returning A: %s'% self.A)
            return self.A

        def exposed_readB(self):
            output('in receiver: returning B: %s'% self.B)
            return self.B

        def exposed_initA_nowait(self):
            output('sleeping 5 in initA_nowait')
            time.sleep(5)
            self.A = 'A'

        def exposed_initB_nowait(self):
            output('sleeping 3 in initB_nowait')
            time.sleep(3)
            self.B = 'B'

        #def exposed_initB(self):
            #output('sleeping 3 in initB')
            #time.sleep(3)
            #self.B = 'B'

    tt = TT()

    e, r = tt.split()
    r.start(runner, (e,))

    while r.serve_nowait():
        pass
