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
"passing by message" design. Your managers must derivate from the `Manager`
class.

In order to interact with other workers, each manager aims to provide:
    - one `_Receiver` instance;
    - one `Emitter` instance, at least.

The emitter(s) controls the receiver with simple method calls.

:Example:

>>> emitter.doSomething(whatever, parameter=optional, to=send)

The code implementing the "doSomething_async" method is run by the receiver.

**The receiver and emitters only support one kind of communication:
ASYNCHRONOUS. By using this module you are forced to write event-driven code,
called requests (most preferably with callbacks)!**


The manager
===========

All the code implemented in the manager is executed by the receiver.

What methods of the manager get exposed through the emitter relies on name
conventions.


Name conventions
----------------

Because the manager will build the receiver and emitters from itself, the
methods of a manager can intend different purposes:
    - factorized code for the manager;
    - factorized code for the derivated classes;
    - code for the user of the manager instance;
    - code for the user of the receiver instance;
    - code to expose through emitters.

Name conventions helps to know what the method is for. Also, building the
receiver and emitters relies on those convention names.

:_mgr_*: namespace reserved for the `Manager` base class.
:_ex: namespace for methods to expose via the emitters.

The canonical form for exposed methods is:
    ex_<emitterName>_<methodName>

The 'ex_' prefix is mandatory.

The <emitterName> is the emitter name which this methods targets. This might
indifferently call it <apiName> since it defines the API of the emitter.

When exposing a method, the prefixes "ex_" and <emitterName> are stripped from
the name:

:Example:

>>> class MyManager(Manager):
>>>     def ex_thisEmitter_printInfo(self, info):
>>>         print(info)
>>> 
>>> manager = MyManager()
>>> handler = manager.getReceiver()
>>> emitter = manager.getEmitter('thisEmitter')
>>> emitter.printInfo('It works!')
>>> handler.serve_received()
It works!
>>> 

In this extract, the emitter 'thisEmitter' is sending the request 'printInfo'.


Helpers
-------

The `Manager` class has some facilities for your own managers.

:`stopServing`: allows to gracefully stop the receiver once called with `serve`.
This aims at being exposed.

:Example:

>>> class MyManager(Manager):
>>>     def ex_oneEmitter_stopServing(self):
>>>         self.stopServing()
>>> 
>>> oneEmitter.stopServing()

:`disable`: don't run the triggers for this emitter until `enable` is called.

>>> class MyManager(Manager):
>>>     def ex_oneEmitter_disable(self, emitterName):
>>>         self.disable(emitterName)
>>> 
>>>     def ex_anotherEmitter_parintInfo(self, emitterName):
>>>         print('info')
>>> 
>>> anotherEmitter.printInfo()
info
>>> oneEmitter.disable()
>>> anotherEmitter.printInfo()
WARNING: oneEmitter was disabled
>>> oneEmitter.enable()
info
>>> 


The emitter
===========

Requests
--------

The easiest way to send a request is to not worry about what is done. Simply
call any exposed method of the emitter.


Requests with callbacks
-----------------------

Writing asynchronized code usually requires callbacks. The callbacks must be
callable. They are defined on the emitter. They will be called once the request
was proceed and the response for this event was given back as a result.

There are 3 kinds of callbacks:

:onSuccess: executed when the receiver did not catch an exception while
    executing the request. The first argument of the callback is the result of the
    process.

:onError: executed when the receiver has catched an exception while executing
    the request. The first argument is the class of the exception, the second
    argument is the reason.

:onComplete: always executed. No argument is passed.

Callbacks are attached to a request like this:

:Example:

>>> def myCallback(result):
>>>     print("result of longRequest: %s"% result)
>>> 
>>> emitter.longRequest.addOnSuccess(myCallback)
>>> emitter.longRequest() # no wait
>>> # other statements
>>> emitter.honor() # block here.
result of longRequest: whatever
>>> 

At first, we assign myCallback to longRequest. Then, the emitter send the
request longRequest. At the end, honor will block until the longRequest send
back a result and will execute the callback myCallback.

There can be more than one callback of the same type for a request.

:Example:

>>> def myCallback(result):
>>>     print("result of longRequest: %s"% result)
>>> 
>>> emitter.longRequest.addOnSuccess(myCallback)
>>> emitter.longRequest.addOnSuccess(myCallback)
>>> emitter.longRequest() # no wait
>>> emitter.honor() # block here.
result of longRequest: whatever
result of longRequest: whatever
>>> 

Positional and named arguments are supported for the callbacks.


The receiver
============

The receiver executes the requests. It is added the method `serve_received` and
`serve` so it can serve emitters. The `serve_received` method returns True or
False whether it should continue serving or not.

:Example:

>>> while receiver.serve_received():
>>>     pass

The serve_received() blocks until all the requests events are handled. The
`serve` method is implemented exactly like that.

Each request ends before the next is started in the order they are called by the
emitter (they are internally put in a queue). The processing is sequential.
So, it's fine to implement methods like this in the manager:

:Example:

>>> class MyManager(Manager):
>>>     def __init__(self):
>>>         super(MyManager, self).__init__()
>>>         self.result = None
>>> 
>>>     def ex_oneEmitter_longRequest(self):
>>>         # Code taking a very long time; self.result gets True or
>>>         # False.
>>>         if condition:
>>>             self.result = False
>>>         self.result = True
>>> 
>>>     def ex_oneEmitter_getLongRequestResult(self):
>>>         if self.result is True: # Real value set by longRequest().
>>>             # doSomething()

The emitter will get the correct result as long as it calls
longRequest() before getLongRequestResult().

The emitter does not have to worry about the order of execution since it's
guaranted they are executed in the same order of the calls.

**However, if there are more than one emitter, the order of execution for the
methods is undefined accross the emitters.** Usually, hitting this case is a
good sign that the implementation needs a rewrite.


Error handling
==============

The receiver won't raise anything. Any error raised inside a receiver while
processing a request is logged-out.

Then, the exception class and the reason are passed to the emitter (without the
stack trace which is lost, for now). The emitter will call the callbacks defined
as onErrorCallbacks.

If no onError callback is defined, errors are re-thrown by the `honor` and
`process_results` methods.

:Example:

>>> def onError(error):
>>>     print("error %s"% str(e))
>>> 
>>> def myCallback(result):
>>>     print("result of longRequest: %s"% result)
>>> 
>>> emitter.longRequest.addOnSuccess(myCallback)
>>> emitter.longRequest()
>>> try:
>>>     emitter.honor() # wait here.
>>> except Exception as e:
>>>     onError(e)

However, it's best to make use of the callbacks because you konw exactly which
request failed and what type of errors it might raise.

:Example:

>>> def onError(error):
>>>     print("error %s"% str(e))
>>> 
>>> def myCallback(result):
>>>     print("result of longRequest: %s"% result)
>>> 
>>> emitter.longRequest.addOnSuccess(myCallback)
>>> emitter.longRequest.addOnError(onError)
>>> emitter.longRequest()
>>> emitter.honor() # wait here.

When a receiver get an exception, any pending request from this emitter is
ignored. When trying to recover from a failure, you have to think about that.


Limitations
===========

Passed values
-------------

The main limitation is about the parameters and the returned values whose must
be accepted by the internal queues. Don't expect to pass your SO_WONDERFULL
objects. Take this limitation as a chance to write good code and objects with
simple APIs. :-)

However, if you really need to pass objects, consider implementing the
`managers.serializer.SerializerInterface` class.


Effectively using the receiver and emitters
-------------------------------------------

Because communication internally relies on queues and that queues must be
**passed** to the workers, a manager is not helpfull in a worker. IOW, any
worker requiring emitters can only work with predefined emitters.


Receiver and emitter in the same worker
---------------------------------------

The emitter and receiver objects are usually aimed at being run in different
workers, one of them possibly being the main worker. However, it's possible to
implement a manager only to handle advanced communication between objects.

If you do this, don't use the `receiver.serve()` and `emitter.honor()` methods.
They will loop indefinitely and block. Instead, make sure to use
`receiver.serve_received` and `emitter.process_results`.

Be aware that even while using those methods there is a risk of race conditions.
This is because the receiver might not have received the requests when calling
`sever_next`. The same os true for `process_results`.  To avoid this case,
always implement the serving like this:

    >>> while emitter.process_results():
    >>>     receiver.serve_received()

There are good demos at the end of the module. ,-)

"""

# Format of requests and responses between emitters and receivers:
#
# The requests
# ============
#
# Canonical format:
#
# ((reqId, apiName), (realName, args, kwargs))
#
# The responses
# =============
#
# Canonical format differs with context:
#
# 1. Success: (reqId, 'SUCCESS', result)
#
# 2. Error: (reqId, 'ERROR', (cls_Exception, reason))
#
# The controls
# ============
#
# This queue is used when the receiver and emitter need a syn to clear out
# the pending requests.
#
# Canonical format:
#
# (action, (iterable))


import inspect
from datetime import datetime

from imapfw import runtime

from ..constants import EMT, CLB


# Outlined.
def _raiseError(cls_Exception, reason):
    """Default callback for errors."""

    try:
        raise cls_Exception(reason)
    except AttributeError:
        try:
            raise cls_Exception(reason)
        except AttributeError:
            raise RuntimeError("exception from receiver cannot be raised %s: %s"%
                (cls_Exception.__name__, reason))

def receiverRunner(receiver):
    name = receiver.getName()
    receiver.ui.debugC(EMT, "[runner] %s starts serving"% name)
    try:
        receiver.serve()
        receiver.ui.debugC(EMT, "[runner] %s stopped serving"% name)
    except Exception as e:
        receiver.ui.debugC(EMT, "[runner] %s interrupted: %s"% (name, e))
        raise


class _EmitterBase(object):
    def __init__(self):
        self._emt_triggers = {} # Triggers to waiting to be honored.
        self._emt_triggerMap = {} # Map of triggers.

        # Attributes fixed once instanciated.
        self.ui = None
        self._emt_inQueue = None
        self._emt_outQueue = None
        self._emt_controlQueue = None
        self._emt_name = None

    def _emt_send(self, meta, req):
        """Send the request to the receiver.

        :meta type: tuple.
        :req type: tuple.
        """

        self.ui.debugC(EMT, "{} sending (({}, {}), ({}, {}, {})",
            self._emt_name, meta[0], meta[1], req[0], req[1], req[2])

        self._emt_inQueue.put((meta, req))

    def _emt_setAttributes(self, ui, inQueue, outQueue,
            controlQueue):
        self.ui = ui
        self._emt_inQueue = inQueue
        self._emt_outQueue = outQueue
        self._emt_controlQueue = controlQueue
        self._emt_name = self.__class__.__name__

    def _emt_needAnotherPass(self):
        return len(self._emt_triggers)

    def process_results(self):
        """Process available results."""

        def runCallbacks(callbacks, which, reqId, *cargs):
            for callback in callbacks:
                self.ui.debugC(CLB, "running %s callback %s %s"%
                    (which, reqId, callback))

                func, args, kwargs = callback
                args = cargs + args

                func(*args, **kwargs)

        response = self._emt_outQueue.get_nowait()
        if response is None:
            # There are requests we still have any response.
            return self._emt_needAnotherPass()

        reqId, status, rargs = response

        self.ui.debugC(EMT, "{} got response ({}, {}, {})",
            self._emt_name, reqId, status, rargs)

        onCompleteCallbacks, onErrorCallbacks, onSuccessCallbacks = \
            self._emt_triggers.pop(reqId)

        if status == 'SUCCESS':
            # No exception, run callbacks for this reqId. rargs is result.
            runCallbacks(onSuccessCallbacks, 'onSuccess', reqId, *rargs)
            runCallbacks(onCompleteCallbacks, 'onComplete', reqId)

        else: # 'ERROR'
            # Got an exception: clear the triggers, execute callbacks
            # or re-throw.
            cls_Exception, reason = rargs

            # The receiver must clear out the remaining triggers ids.
            self._emt_controlQueue.put(
                    ('ignoreRequests', list(self._emt_triggers.keys()))
                    )
            # Clear out triggers ids.
            self._emt_triggers = {}

            if len(onErrorCallbacks) < 1:
                _raiseError(cls_Exception, reason)
            else:
                for callback in onErrorCallbacks:
                    self.ui.debugC(CLB, "running onError callback %s %s"%
                        (reqId, callback))
                    func, args, kwargs = callback
                    func(cls_Exception, reason, *args, **kwargs) # Execute.

            runCallbacks(onCompleteCallbacks, 'onComplete', reqId)

        return self._emt_needAnotherPass()

    def honor(self):
        """Block until all results are proccessed."""

        while self.process_results():
            pass
        return None


class _Receiver(object):
    """The receiver base class. Executes requests of emitters."""

    def __init__(self, ui, queues, manager):
        """
        :emitters type: dict
        :emitters: keys: emitterNames, values: tuple of 'in', 'out'
        and 'control' queues.
        """

        self.ui = ui

        self._obj = manager # Embedd the full manager.
        self._queues = queues

        self._delayedRequests = []
        self._waitForControlRequest = False
        self._ignoreIds = []
        self._name = "receiver%s"% manager.__class__.__name__

    def __getattr__(self, name):
        # Return the requested method of the embedded manager.
        if name.startswith('_mgr_'):
            raise AttributeError(
                "attempted to call '%s' from the receiver"% name)

        return getattr(self._obj, name)

    def _debug(self, msg):
        self.ui.debugC(EMT, "%s %s"% (self._name, msg))

    def _getIncomingRequests(self, requests):
        """Consider the requests available in the incoming queues.

        :requests: list of requests to update.
        :requests type: list:

        The caching process mix the requests from all the emitters into
        the same list but the apiName is stored with the request."""

        def formatRequest(request, outQueue, ctrlQueue):
            (meta), (req) = request
            reqId, apiName = meta
            name, args, kwargs = req

            obj = type("request", (object,), {})
            obj.apiName = apiName
            obj.reqId = reqId
            obj.name = name
            obj.args = args
            obj.kwargs = kwargs
            obj.outQueue = outQueue
            obj.ctrlQueue = ctrlQueue
            return obj

        for inQueue, outQueue, ctrlQueue in self._queues.values():
            while True:
                request = inQueue.get_nowait()
                if request is None:
                    break

                r = formatRequest(request, outQueue, ctrlQueue)

                if not self._obj._mgr_isLegitEmtter(r.apiName):
                    self.ui.warn("%s got request from '%s' while it is not a"
                        " legit emitter, delaying until reactivated: (%s, %s),"
                        " (%s, %s, %s)"% (self._name, r.apiName, r.apiName,
                        r.reqId, r.name, str(r.args), str(r.kwargs)))
                    self._delayedRequests.append(r)
                else:
                    requests.append(r)
        return requests

    def _send(self, outQueue, mode, arg1, arg2):
        outQueue.put((mode, arg1, arg2))

    def _shouldContinueServing(self):
        return not self._obj._msg_shouldStopServing()

    def getName(self):
        return self._name

    def serve(self):
        while self.serve_received():
            pass

    def serve_received(self):
        """Serve the next pending requests."""

        serveRequests = []

        # Move the delayed requests into the "serve" list.
        for r in self._delayedRequests:
            if self._obj._mgr_isLegitEmtter(r.apiName):
                serveRequests.append(r)
                self._delayedRequests.remove(r)

        # Add all the pending requests from queues to the "serve" list.
        serveRequests = self._getIncomingRequests(serveRequests)

        # Execute the available requests.
        for req in serveRequests:
            serveRequests.remove(req)

            try:
                if self._waitForControlRequest is True:
                    # We are expecting a list of trigger ids to ignore.
                    ctrlRequest = req.ctrlQueue.get_nowait()
                    if ctrlRequest is None:
                        # Need another serving pass.
                        return self._shouldContinueServing()

                    ignoreIds = ctrlRequest[1]
                    self._debug("will ignore %s"% ignoreIds)

                    # Ignore all the "to-be-served" requests for this emitter.
                    for ignoreId in ignoreIds:
                        for pendingRequest in serveRequests:
                            if pendingRequest.reqId == ignoreId:
                                serveRequests.remove(req)
                                ignoreIds.remove(ignoreId)
                    # We might still have "to-be-received" requests to ignore...
                    self._ignoreIds += ignoreIds

                    # Ok, we are in synced with the emitter.
                    self._waitForControlRequest is False

                # Should we ignore this request?
                if req.reqId in self._ignoreIds:
                    self._ignoreIds.remove(req.reqId)
                    self._debug("ignoring %s"% req.reqId)
                    continue

                self._debug("execute request %s(%s, %s)"%
                    (req.name, req.args, req.kwargs))

                # Execute the request.
                result = getattr(self._obj, req.name)(*req.args, **req.kwargs)

                if type(result) is not tuple:
                    result = (result,)
                # (outQ, reqId, 'SUCCESS', result)
                self._send(req.outQueue, req.reqId, 'SUCCESS', result)
            except Exception as e:
                # (outQ, reqId, cls_Exception, reason)
                self._send(req.outQueue, req.reqId, 'ERROR',
                    (e.__class__, str(e)))

                # In return we expect a control request so we can ignore ids.
                self._waitForControlRequest = True
                # Delay the current serveRequests.
                for r in serveRequests:
                    self._delayedRequests.append(r)

                self.ui.exception(e)

                if type(e) == KeyboardInterrupt:
                    raise

        return self._shouldContinueServing()


class ManagerInterface(object):
    def disable(self):      raise NotImplementedError
    def enable(self):       raise NotImplementedError
    def stopServing(self):  raise NotImplementedError
    def getEmitter(self):   raise NotImplementedError
    def getReceiver(self):  raise NotImplementedError


class Manager(ManagerInterface):
    """The manager base class."""

    def __init__(self):
        self.ui = runtime.ui
        self.concurrency = runtime.concurrency

        self.__emitters = {}

        self.__stop = False
        # Each emitter need a set of 'in' and 'out' queues.
        self.__queues = self.__buildQueues()
        self.__legitEmitters = list(self.__queues.keys())

    def __iterExposed(self):
        for name in [attr[0] for attr in inspect.getmembers(self)]:
            # Method names starting with 'ex_' are to be exposed.
            if name.startswith('ex_'):
                exposedName = name[3:] # Remove 'ex_' from the name.

                # Next part is the API name.
                list_exposedName = exposedName.split('_')
                apiName = list_exposedName[0]
                if len(list_exposedName) > 2:
                    exposedName = '_'.join(list_exposedName[1:])
                else:
                    exposedName = list_exposedName[1]

                yield name, apiName, exposedName

    def __buildQueues(self):
        queues = {}
        for real, api, exposed in self.__iterExposed():
            queues[api] = (
                self.concurrency.createQueue(),
                self.concurrency.createQueue(),
                self.concurrency.createQueue(),
                )
        if len(queues.keys()) < 1:
            raise Exception("manager '%s' has no method to expose"%
                self.__class__.__name__)
        return queues

    def _mgr_isLegitEmtter(self, emitterName):
        return emitterName in self.__legitEmitters

    def _msg_shouldStopServing(self):
        return self.__stop

    def disable(self, emitterName):
        """Facility to disable the emitter with this name.

        When disabled, a call to

        >>> emitter.honor()

        Will delay the triggers. You should avoid having delayed triggers,
        though.

        Implement this facility in your childs (see `stopServing`)."""

        if emitterName not in self.__queues:
            raise Exception("unknown emitter '%s'"% emitterName)

        if emitterName in self.__legitEmitters:
            self.__legitEmitters.remove(emitterName)

    def enable(self, emitterName):
        """Facility to enable the emitter with this name.

        Implement this facility in your childs (see `stopServing`)."""

        if emitterName not in self.__queues:
            raise Exception("unknown emitter '%s'"% emitterName)

        if emitterName not in self.__legitEmitters:
            self.__legitEmitters.append(emitterName)

    def stopServing(self):
        """Facility to stop serving.

        Implement this facility your your child like this:

        >>> class MyManager(Manager):
        >>>     def ex_toThisEmitter_stopReceiver(self):
        >>>         self.stopServing()

        >>> # Emitter side:
        >>> thisEmitter.stopReceiver()
        """

        self.__stop = True

    def getReceiver(self):
        return _Receiver(self.ui, self.__queues, self)

    def getEmitter(self, apiName):
        def Emitter(apiName, inQueue, outQueue, controlQueue, manager):
            """The Emitter factory."""

            def expose_method(realName, exposedName):
                """Attach method using a mapped trigger with name exposedName."""

                onErrorCallbacks = []
                onCompleteCallbacks = []
                onSuccessCallbacks = []

                def addOnComplete(cFunc, *cargs, **ckwargs):
                    onCompleteCallbacks.append((cFunc, cargs, ckwargs))

                def addOnError(eFunc, *eargs, **ekwargs):
                    onErrorCallbacks.append((eFunc, eargs, ekwargs))

                def addOnSuccess(sFunc, *sargs, **skwargs):
                    onSuccessCallbacks.append((sFunc, sargs, skwargs))

                def attached_method(self, *args, **kwargs):
                    reqId = datetime.now().timestamp()

                    # Store callbacks for latter use.
                    self._emt_triggers[reqId] = (onCompleteCallbacks,
                        onErrorCallbacks, onSuccessCallbacks)

                    # Build request.
                    meta = (reqId, apiName)
                    req = (realName, args, kwargs)
                    # Send request.
                    self._emt_send(meta, req)
                    return None

                attached_method.addOnError = addOnError
                attached_method.addOnComplete = addOnComplete
                attached_method.addOnSuccess = addOnSuccess

                return attached_method

            ### getEmitter() really starts here. ###

            if apiName in self.__emitters:
                return self.__emitters[apiName]

            # Build the class.
            emitterClassName = "emitter%s(%s)"% (
                manager.__class__.__name__, apiName)

            cls_Emitter = type(emitterClassName, (_EmitterBase,), {})

            # Attached the _ex* methods so they get exposed.
            exposedNames = []
            for realName, emitterName, exposedName in self.__iterExposed():
                if exposedName in ['serve', 'serve_received']:
                    raise Exception("%s tried to expose '%s' which is forbidden"
                        " name"% (self.__class__.__name__, exposedName))
                # Only expose the methods dedicated to this emitter. We know
                # this from the api part in the name of the method.
                if apiName == emitterName:
                    setattr(cls_Emitter, exposedName,
                        expose_method(realName, exposedName))

                    exposedNames.append(exposedName)

            emitter = cls_Emitter()
            # Set the attributes to the emitter instance.
            emitter._emt_setAttributes(manager.ui, inQueue, outQueue, controlQueue)

            self.ui.debugC(EMT, "new instance %s: %s"% (emitter.__class__.__name__,
                [x for x in dir(emitter) if not x.startswith('_')]))
            return emitter # The instance.

        emitter = Emitter(
            apiName,
            self.__queues[apiName][0],
            self.__queues[apiName][1],
            self.__queues[apiName][2],
            self)
        return emitter


#TODO
if __name__ == '__main__':
    #
    # Run this demo like this (from the root directory):
    # python3 -m imapfw.managers.manager
    #
    # We catch exception since it's run as a test in travis.
    #
    _DEBUG = True # Comment this for less output.
    try:

        import time, sys

        from imapfw.concurrency.concurrency import Concurrency
        from imapfw.ui.tty import TTY

        c = Concurrency('multiprocessing')
        ui = TTY(c.createLock())
        ui.configure()
        if _DEBUG is True:
            ui.enableDebugCategories(['workers', 'emitters'])
        ui.setCurrentWorkerNameFunction(c.getCurrentWorkerNameFunction())

        runtime.set_module('ui', ui)
        runtime.set_module('concurrency', c)


        def demo_simple():
            ui.info('******** starting simple')

            class Simple(Manager):
                def ex_one_printInfo(self, msg):
                    print(msg)

            simple = Simple()
            receiver = simple.getReceiver()
            emitter = simple.getEmitter('one')
            emitter.printInfo('this is a test')

            while emitter.process_results():
                receiver.serve_received()
            ### End Simple ###


        def demo_disable():
            ui.info('******** starting disable')

            class Simple(Manager):
                def ex_A_echo(self, msg):
                    return msg

            def printInfo(result):
                print(result)

            simple = Simple()
            receiver = simple.getReceiver()
            a = simple.getEmitter('A')

            a.echo.addOnSuccess(printInfo)

            a.echo('first event')
            ui.info('disabling A')

            while a.process_results():
                receiver.serve_received()

            simple.disable('A')
            a.echo('second event') # Just disabled...

            time.sleep(1) # Let the time for the events to arrive.
            receiver.serve_received() # Got the time, serving previous 'echo' request.

            ui.info('enabling A')
            simple.enable('A')

            ui.info('honor triggers')
            while a.process_results():
                receiver.serve_received()


        def demo_error_handling():
            ui.info('******** starting error handling')

            class MyDriverManager(Manager):
                def ex_engine_noop(self):
                    return None

                def ex_engine_error(self):
                    raise RuntimeError('oops!')

                def ex_engine_stopServing(self):
                    self.stopServing() # Special method.

            manager = MyDriverManager()
            receiver = manager.getReceiver()
            emitter = manager.getEmitter('engine')

            def handleError(cls, reason):
                print("callback for errors got: %s %s"% (cls.__name__, reason))

            emitter.error.addOnError(handleError)
            emitter.error()
            emitter.noop() # send a request which must be ignored.

            while emitter.process_results():
                receiver.serve_received()
            # Will print if noop is executed (should not).
            while emitter.process_results():
                receiver.serve_received()
            print("emitter remaining triggers: %s"% emitter._emt_triggers)
            receiver.serve_received()


        def demo_with_workers():
            ui.info('******** starting demo with workers')

            def driverRunner(receiver):
                print('driver serving')
                receiver.serve()
                print('driverRuner stopped')

            def engineRunner(receiver):
                print('engine serving')
                receiver.serve()
                print('engineRunner stopped')

            class MyDriverManager(Manager):
                def ex_engine_connect(self, server):
                    self.ui.info("connect to %s"% server)
                    return 'yes!'

                def ex_architect_stopServing(self):
                    self.stopServing() # Special method.

                def ex_engine_stopServing(self):
                    self.stopServing() # Special method.

            class MyEngineManager(Manager):
                def init(self, driver):
                    self._driver = driver

                def _onConnection(self, result, msg):
                    self.ui.info("%s: %s"% (msg, result))
                    self._driver.stopServing()

                def ex_architect_start(self):
                    remote = 'imap.imapfw.net'
                    self._driver.connect.addOnSuccess(self._onConnection,
                            'connected to %s'% remote)
                    self._driver.connect(remote)
                    self._driver.honor()

                def ex_architect_stopServing(self):
                    self.stopServing() # Special method.

            driverManager = MyDriverManager()

            driverWorker = c.createWorker('driver.0',
                driverRunner,
                (driverManager.getReceiver(),),
                )
            driverWorker.start()

            engineManager = MyEngineManager()
            engineManager.init(driverManager.getEmitter('engine'))

            engineWorker = c.createWorker('engine.0',
                engineRunner,
                (engineManager.getReceiver(),),
                )
            engineWorker.start()

            def stopNow():
                print('stop Now!')

            engine = engineManager.getEmitter('architect')
            driver = driverManager.getEmitter('architect')


            try:
                engine.start.addOnComplete(stopNow)
                engine.start()
                engine.honor()
            except Exception as e:
                ui.error("oops: %s"% e)
            finally:
                engine.stopServing()
                driver.stopServing() # Already stopped if all goes fine.

                engineWorker.join()
                driverWorker.join()

            ### End with workers ###


        demo_simple()
        demo_disable()
        demo_error_handling()
        demo_with_workers()

        sys.exit(0)

    except Exception as e:
        raise # Uncomment while working on this module!
        sys.exit(1)
