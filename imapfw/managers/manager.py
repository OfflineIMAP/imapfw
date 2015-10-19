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

Overview
========

Managers are handy objects to communicate between workers, implementing the
"passing by message" design. They must derivate from the `Manager` class.

In order to interact with other workers, each manager aims to be splitted via a
call to `split` which returns two new objects::
    - the `Emitter` instance
    - the `Receiver` instance

The emitter controls the receiver with simple method calls.

:Example:

>>> result = emitter.doSomething(whatever, parameter=optional, to=send)


The code implemented in the "doSomething" method is run by the receiver.

The managers support three kinds of communication:
    - synchronized mode;
    - partially asynchronized mode;
    - asynchronized mode.

The communication mode to use relies on optional arguments given to the emitter
(_nowait and _trigger).

Synchronized mode
-----------------

In synchronized mode, the emitter blocks until the receiver send the result.

:Example:

>>> # Waits for the result.
>>> result = emitter.doSomething(whatever, parameter=optional, to=send)

Partially aynchronized mode
---------------------------

In partially synchronized mode, the emitter won't wait for a result. The emitter
will wait for the receiver to finish the task at the next call to any
synchronized method.

:Example:

>>> emitter.longRequest(_nowait=True) # no wait
>>> whatever_statements
>>> result = emitter.getLongRequestResult()
>>> doSomethingWith(result) # result is correct

The "emmiter code" will wait at emitter.getLongRequestResult() and get the
CORRECT result because the receiver won't even start the method
getLongRequestResult() before the previous call to longRequest() is done.

:Example:

>>> emitter.longRequest(_nowait=True) # no wait
>>> whatever_statements
>>> result_of_doAnythingElse = emitter.doAnythinElse() # wait here

The above code would wait here for emitter.longRequest() to finish be.

:Example:

>>> emitter.longRequest(_nowait) # no wait
>>> whatever_statements
>>> emitter.doAnotherThing(arg_for_receiver=whatever, _nowait=True) # no wait
>>> result = emitter.getLongRequestResult() # wait here

The above code would neither wait for longRequest() nor doAnotherThing(). It
would wait for BOTH to be done at the getLongRequestResult() call. The returned
value result is CORRECT.

Asynchronized mode
------------------

Asynchronized mode relies on triggers. They must be callable and are defined at
the emitter side at the time of the call with the special '_trigger' parameter.

:Example:

>>> emitter.longRequest(_trigger=(emitter_side_callable, (args), kw={})) # no wait
>>> whatever_statements
>>> emitter.doAnotherThing(arg_for_receiver, _trigger=(another_callable)) # no wait
>>> result = emitter.async() # honor triggers, wait here
>>> other_statements # emitter_side_callable and another_callable are finished

The triggers "emitter_side_callable" and "another_callable" defined at
longRequest() and doAnotherThing() respectively are executed when
emitter.async() is called. The returned value "result" is always None. The order
the triggers are executed is **undefined**. emitter.async() blocks until all the
previous triggers are executed.

Optionally, you can define when the emitter.async() stop blocking by passing the
callable to wait for. TODO, not imlemented yet.

:Example:

>>> emitter.longRequest(_trigger=(emitter_side_callable, params)) # no wait
>>> whatever_statements
>>> emitter.doAnotherThing(arg_for_receiver, _trigger=(another_callable)) # no wait
>>> emitter.async(another_callable) # wait here for another_callable() to be executed
>>> other_statements
>>> emitter.async() # honor remaining triggers, wait here for emitter_side_callable()

If emitter.async() is call while there is no pending trigger to honor,
emitter.async() is noop.


The manager
===========

All the code implemented in the manager is executed by the receiver. What methods get
exposed and callable by the emitter relies on name conventions.

Name conventions

Because the manager gets splitted, the methods of a manager can intend different
purposes:
    - factorized code for the manager;
    - factorized code for the derivated classes;
    - code for the caller of the manager instance;
    - code for the caller of the receiver instance;
    - code to expose with the emitter.

Name conventions helps to know what how the method will be used. Also, the
`split` operation relies on those name conventions.

:'exposed_' (prefix): mandatory: will be exposed, callable from in the emitter.
:'manager_' (prefix): optional: factorized code for the manager, gets removed
    in the receiver.
:no prefix: code for the user of the receiver (or manager) instance.

When exposing a method, the prefix "exposed_" is stripped from the name.

For easier usage, the method `exposed_stopServing` is already implemented.


The receiver
============

The receiver executes the orders. It is added the method `serve_next` so it
can serve the emitter. This method returns True or False whether it should
continue serving or not.

:Example:

>>> while receiver.serve_next():
>>>     pass

The serve_next() blocks while a request is being executed, one per loop.

Whatever communication mode is used by the emitter, each request ends before the
next is started in the order they are called by the emitter (they are internally
put in a queue). The processing is a sequential. So, it's fine to implement
methods like this in the manager:

:Example:

>>> def __init__(self):
>>>     self.result = None
>>> 
>>> def exposed_longRequest(self):
>>>     # Code taking a very long time; self.result gets True or
>>>     # False.
>>>     if condition:
>>>         self.result = True
>>>     self.result = True
>>> 
>>> def exposed_getLongRequestResult(self):
>>>     return self.result

The emitter will get the correct result as long as it calls
longRequest() before getLongRequestResult().

The emitter does not have to worry about the order of execution since it's
guaranted they are executed in the same order of the calls.


Error handling
==============

The manager supports error handling. The emitter is exposed the method
`interruptionError` to allow relaying the exception to the receiver.


Limitations
===========

:passed values: The main limitation is about the parameters and the returned values whose must
be accepted by the queues. Don't expect to pass your SO_WONDERFULL objects. Take
this limitation as a chance to write good code and objects with simple APIs.
+
However, if you really need to pass objects, consider implementing the
`.serializer.SerializerInterface` class.


:same worker: The emitter and receiver objects are usually aimed at running in
different workers, one of them possibly being the main worker. However, it's
possible to implement a manager only to handle advanced communication between
objects. If you do this, the sync and async mode will both deadock. You must
only use the partially asynchrone mode (with "_nowait).


"""

import inspect
from datetime import datetime

from imapfw import runtime

from ..constants import EMT


class ManagerInterface(object):
    def getEmitter(self):   raise NotImplementedError
    def split(self):        raise NotImplementedError


class ManagerEmitterInterface(object):
    def stopServing(self):  raise NotImplementedError


class Manager(ManagerInterface, ManagerEmitterInterface):
    """The manager base class."""

    def __init__(self):
        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self._stopServing = False
        self._emitter = None

    def manager_shouldServe(self):
        return not self._stopServing


    def exposed_interruptionError(self, cls_exception, reason):
        """Raise the exception cls_exception with the reason."""

        raise cls_exception(reason)

    def exposed_stopServing(self):
        """You should not ovrerride this method."""

        self._stopServing = True


    def getEmitter(self):
        return self._emitter

    def split(self):
        """Split this manager

        :returns: a tuple of instances of an Emitter and a Receiver."""

        class Receiver(object):
            """Receiver base class. Executes the orders of the emitter."""

            def __init__(self, inQueue, outQueue, triggerOutQueue, manager):
                self.__inQueue = inQueue
                self.__outQueue = outQueue
                self.__triggerOutQueue = triggerOutQueue
                self.__obj = manager # Embedd the full manager.

            def __getattr__(self, name):
                # Return the requested method of the embedded manager.
                if name.startswith('manager_'):
                    raise AttributeError("attempted to call '%s' from the"
                        " receiver"% name)
                return getattr(self.__obj, name)

            def get_obj(self):
                return self.__obj

            def serve_next(self):
                """Serve the pending requests."""

                # Read one pending incoming request.
                request = self.__inQueue.get_nowait()
                if request is None:
                    return self.__obj.manager_shouldServe()

                # Execute the request.
                (mode, triggerId), (name, args, kwargs) = request[0]
                for flagMode in ['_nowait', '_trigger']:
                    if flagMode in kwargs:
                        kwargs.pop(flagMode)
                result = getattr(self.__obj, name)(*args, **kwargs)

                if mode == '_trigger':
                    self.__triggerOutQueue.put((triggerId, result))
                elif mode == '_sync':
                    self.__outQueue.put(result)

                # Send the result back to the emitter.
                # Let the caller know if the receiver should continue to serve.
                return self.__obj.manager_shouldServe()

        def Emitter(inQueue, outQueue, triggerOutQueue, manager):
            """The Emitter factory."""

            def expose_method(name):
                def attached_method(self, *args, **kwargs):
                    from imapfw import runtime
                    ui = runtime.ui
                    mode = '_sync' # Default.
                    triggerId = None
                    # Handle the communication modes.
                    if '_nowait' in kwargs:
                        mode = '_nowait'
                        kwargs.pop('_nowait')
                    elif '_trigger' in kwargs:
                        # Store the trigger so it can be retrieved later.
                        mode = '_async'
                        trigger, targs, tkwargs = kwargs.pop('_trigger')
                        triggerId = datetime.now().timestamp()
                        self.__triggers[triggerId] = (trigger, targs, tkwargs)
                        kwargs['_trigger'] = triggerId

                    request = (mode, triggerId), (name, args, kwargs)

                    ui.debugC(EMT, "{} sending (({}, {}), ({}, {}, {})",
                        self.__class__.__name__, mode, triggerId,
                        name, args, kwargs)

                    self.__inQueue.put((request,))

                    if mode == '_sync':
                        values = self.__outQueue.get()
                        ui.debugC(EMT, "{} result for {}: ({})",
                            self.__class__.__name__, name, values)
                        return values
                    return None

                return attached_method

            def expose_async():
                def async(self, *args, **kwargs):
                    from imapfw import runtime
                    ui = runtime.ui
                    while len(self.__triggers) > 0:
                        triggerId, result = self.__triggerOutQueue.get()
                        ui.debugC(EMT, "{} trigger ({}, {})",
                            self.__class__.__name__, triggerId, result)
                        func, trigger_args, trigger_kwargs = self.__triggers.pop(
                            triggerId)
                        func(result, *trigger_args, **trigger_kwargs) # Execute trigger.
                return async

            # Build the class.
            cls_Emitter = type(
                "emitter%s"% manager.__class__.__name__, (object,), {})

            # Add the methods to the emitter.
            for name in [attr[0] for attr in inspect.getmembers(manager)]:
                if name.startswith('exposed_'):
                    exposedName = name[8:] # Remove 'exposed_' from the name.
                    if exposedName in ['async']:
                        raise Exception("the manager %s implements the"
                            " forbidden 'exposed_%s' method"%
                            (self.__class__.__name__, exposedName))
                    setattr(cls_Emitter, exposedName, expose_method(name))
            setattr(cls_Emitter, 'async', expose_async())
            emitter = cls_Emitter()
            # Fix attributes of the emitter.
            emitter.__triggers = {}
            emitter.__inQueue = inQueue
            emitter.__outQueue = outQueue
            emitter.__triggerOutQueue = triggerOutQueue

            self.ui.debugC(EMT, "new instance %s: %s"% (emitter.__class__.__name__,
                [x for x in dir(emitter) if not x.startswith('_')]))
            return emitter # The instance.

        # split() really starts here.
        inQueue = self.concurrency.createQueue()
        outQueue = self.concurrency.createQueue()
        triggerOutQueue = self.concurrency.createQueue()

        emitter = Emitter(inQueue, outQueue, triggerOutQueue, self)
        self._emitter = emitter
        receiver = Receiver(inQueue, outQueue, triggerOutQueue, self)

        return receiver, emitter


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
            super(TT, self).__init__(c, 'ttworker')
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

    while r.serve_next():
        pass
