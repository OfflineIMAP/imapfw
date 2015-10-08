
from ..constants import WRK, EMT


class ManagerCallerInterface(object):
    def join(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError

    def split(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError


class ManagerEmitterInterface(object):
    def interruptAll(self):
        raise NotImplementedError

    def stopServing(self):
        raise NotImplementedError


class Manager(ManagerCallerInterface, ManagerEmitterInterface):
    """The manager base class.

    A manager aims to be splitted via a call to Manager().split() which returns
    two new objects:
        - the emitter
        - the receiver

    Both can be run in different workers. The emitter controls the receiver with
    simple method calls like this:

        result = emitter.doSomething(any, parameter, to=send)

    The code implemented in "doSomething" is run by the receiver.

    The limitation is about the parameters and the returned values whose must
    be accepted by the queues. Don't expect to pass your SO_WONDERFULL objects.
    Take this limitation as a chance to write good code and objects with simple
    APIs.

    Learn more in the Emitter and Receiver docstrings.
    """

    def __init__(self, ui, concurrency, workerName):
        self.ui = ui
        self.concurrency = concurrency
        self.workerName = workerName

        self._worker = None
        self._stopServing = False
        self._emitter = None
        self._emitterExpose = [
            'interruptAll',
            'stopServing',
            ]

    def expose(self, exposeList):
        self._emitterExpose = self._emitterExpose + exposeList

    # Emitter API.
    def interruptAll(self, reason):
        raise Exception("%s got following interruption: %s (Press CTRL+C)"%
            (self.workerName, reason))

    # Caller API.
    def getEmitter(self):
        return self._emitter

    # Caller API.
    def join(self):
        self.ui.debug(WRK, "%s join"% self.workerName)
        self._worker.join()
        self.ui.debug(WRK, "%s stopped"% self.workerName)

    # Caller API.
    def kill(self):
        self._worker.kill()
        self.ui.debug(WRK, "%s killed"% self.workerName)

    def shouldServe(self):
        return not self._stopServing

    # Caller API.
    def split(self):
        """The "passing by message" communication system between workers.

        :returns: a tuple of instances of an Emitter and a Receiver."""

        class Receiver(object):
            """Execute the orders of the emitter.

            Executes all the requested methods and send the results back to the
            Emmiter. This is sequential: each request ends before the next is
            started. So, it's fine to implement methods like this in the
            manager:

                def __init__(self):
                    self.result = None

                def longRequest_nowait(self):
                    # Code taking a very long time; self.result gets True or
                    # False.
                    self.result = theResultIsTrueOrFalse()

                def getLongRequestResult(self):
                    return self.result

            The emitter won't have to worry at all.

            Case A:

                emitter.longRequest_nowait() # async
                this_is_called_NOW() # don't wait here
                result = emitter.getLongRequestResult() # wait here (1)
                doSomethingWith(result) # result is either True or False but
                                        # NEVER None

            (1) The "emmiter code" will wait at emitter.getLongRequestResult() and
            get the CORRECT result because the receiver won't even start the
            method getLongRequestResult() before the previous call to
            longRequest_nowait() is done.

            Case B:

                emitter.longRequest_nowait() # async
                this_is_called_NOW() # don't wait here
                emitter.doAnythinElse() # wait here (2)
                result = emitter.getLongRequestResult() # don't wait here
                doSomethingWith(result) # result is either True or False but
                                        # NEVER None

            (2) The above code would wait here for emitter.longRequest_nowait()
            to finish.

            Case C:

                emitter.longRequest_nowait() # async, don't wait here
                this_is_called_NOW() # don't wait here
                emitter.doAnotherThing_nowait() # async, don't wait here (3)

                result = emitter.getLongRequestResult() # wait here

                doSomethingWith(result) # result is either True or False but
                                        # NEVER None

            (3) The above code would neither wait for longRequest_nowait() nor
            doAnotherThing_nowait(). It would wait for BOTH to be done at
            the getLongRequestResult() call. The returned value is CORRECT.
            """

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

                while self.__obj.shouldServe():
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
                return self.__obj.shouldServe()

        def Emitter(ui, incomingQueue, resultQueue, manager, expose):
            """The emitter factory.

            Returns a emitter instance with all the exposed methods.

            If the name of the method ends with '_nowait', the emitter won't
            wait for a result from the receiver. Such method always returns None."""

            def proxy_method(name, waitResult):
                def nowait(self, *args, **kwargs):
                    ui.debug(EMT, "%s: %s %s %s"%
                        (self.__class__.__name__, name, args, kwargs))
                    self.__incomingQueue.put((name, args, kwargs))
                    return None

                def wait(self, *args, **kwargs):
                    ui.debug(EMT, "%s: %s %s %s"%
                        (self.__class__.__name__, name, args, kwargs))
                    self.__incomingQueue.put((name, args, kwargs))
                    return self.__resultQueue.get()

                if waitResult is True:
                    return wait
                return nowait

            ignoreMethods = [
                'expose',
                'getEmitter',
                'join',
                'kill',
                'shouldServe',
                'split',
                'start',
                ]

            if len(expose) < 1:
                expose = []
                for name in manager.__class__.__dict__:
                    # Ignore those methods.
                    if name.startswith('_') or name in ignoreMethods:
                        continue
                    expose.append(name)

            # Build the class.
            cls_Emitter = type(
                "emitter%s"% manager.__class__.__name__, (object,), {})

            # Add the methods to the emitter.
            for name in expose:
                if name in ignoreMethods:
                    raise Exception("method %s cannot be exposed"% name)
                if name.endswith('_nowait'):
                    setattr(cls_Emitter, name, proxy_method(name, waitResult=False))
                else:
                    setattr(cls_Emitter, name, proxy_method(name, waitResult=True))
            emitter = cls_Emitter()
            # Fix attributes of the emitter.
            emitter.__incomingQueue = incomingQueue
            emitter.__resultQueue = resultQueue

            ui.debug(EMT, "%s: %s"% (emitter.__class__.__name__, dir(emitter)))
            return emitter # The instance.

        # split() implementation starts here.
        incomingQueue = self.concurrency.createQueue()
        resultQueue = self.concurrency.createQueue()

        receiver = Receiver(incomingQueue, resultQueue, self)
        emitter = Emitter(self.ui, incomingQueue, resultQueue, self, self._emitterExpose)

        self._emitter = emitter # Keep track on this one.
        return emitter, receiver

    # Caller API.
    def start(self, target, args):
        self._worker = self.concurrency.createBasicWorker(
            name=self.workerName, target=target, args=args)
        self._worker.start()
        self.ui.debug(WRK, "%s started"% self.workerName)

    # Emitter API.
    def stopServing(self):
        self._stopServing = True
