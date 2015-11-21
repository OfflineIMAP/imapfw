# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors

"""

Overview
========

This module allows event-driven communication between workers. "edmp" stands for
"Event-Driven Message Passing".

This follows the "passing by message" design with improved events.

In order to interact with other workers, the `newEmitterReceiver` function
returns:
    - one `Receiver` instance;
    - one `Emitter` instance.

The emitter sends events to the receiver with simple method calls.

:Example:

>>> emitter.doSomething(whatever, parameter=optional, to=send)

The code implementing the "doSomething" event is run by the receiver.

The receiver and the emitter support two kinds of communication:
    - asynchronous;
    - synchronous (actually pseudo-synchronous but you don't have to care).


The receiver
============

The receiver must define the callable to each supported event.

:Example:

>>> def on_printInfo(info):
>>>     print(info)
>>> 
>>> receiver, emitter = emp.newEmitterReceiver('test')
>>> receiver.accept('printInfo', on_printInfo)
>>> emitter.printInfo('It works!')
>>> emitter.stopServing()
>>> 
>>> while receiver.react():
>>>     pass
It works!
>>> 

In this extract, the emitter is sending the event 'printInfo'. The receiver
reacts by calling the function 'on_printInfo'.

The receiver has only two public methods:
    - accept: to define what to do on events.
    - react: to react on events.

The `Receiver.react` method will process all the received events. This returns
True or False whether it should continue reacting or not.

:Example:

>>> while receiver.react():
>>>     pass

Each event reaction ends before the next is processed in the order they are
sent by the emitter (they are internally put in a queue). The processing is
sequential. So, it's fine to use a receiver like that:

:Example:

>>> class EventHandler(object):
>>>     def __init__(self, receiver):
>>>         self._receiver = receiver
>>> 
>>>         receiver.accept('longRequest', self._longRequest)
>>>         receiver.accept('getResult_longRequest', self._withResult_longRequest)
>>> 
>>>         self._result = None
>>> 
>>>     def _longRequest(self):
>>>         # Code taking a very long time; self._result gets True or
>>>         # False.
>>>         if condition:
>>>             self._result = False
>>>         self._result = True
>>> 
>>>     def _withResult_longRequest(self):
>>>         if self._result is True: # Real value set by longRequest().
>>>             doSomething()
>>> 
>>>     def serve(self):
>>>         while self._receiver.react():
>>>             pass

The emitter does not have to worry about the order of execution since it's
guaranted they are executed in the same order of the calls.

**However, if the emitter is used in more than one worker, the order of
execution for the methods is undefined accross the emitters.**


The emitter
===========

Sending asynchronous events
---------------------------

The easiest way to send events is to not worry about what is done. This is
achieved with a call to a method of the emitter. The name of the method is the
name of the event.


Sending synchronous events
--------------------------

If you need a result to the event, it's possible to get this by appending
'_sync' to the method of the emitter.

:Example:

>>> result = emitter.doSomething_sync(whatever, parameter=optional, to=send)

Stopping the receiver
---------------------

The receiver has one pre-defined event: 'stopServing' which allows to make the
react method to return False instead of True.


Error handling
==============

Asynchronous mode
-----------------

The receiver won't raise any unhandled exception while reacting on events. The
errors are logged-out.


Synchronous mode
----------------

In synchronous mode, any error is logged-out and then passed to the emitter.

Because queues can't pass exceptions, only the class and the reason are passed
to the emitter (without the stack trace which was logged-out). The emitter will
make its best to re-raise the exact same exception.

To get proper exception handling, you must import all unhandled exception
classes before using the emitter. Unkown exception classes will raise a
RuntimeError.


Limitations
===========

Passed values
-------------

The main limitation is about the parameters and the returned values whose must
be accepted by the internal queues. Don't expect to pass your SO_WONDERFULL
objects. Take this limitation as a chance to write good code and objects with
simple APIs. :-)

However, if you really need to pass objects, consider implementing the
`emp.serializer.SerializerInterface` class.


Effectively using the receiver and emitters
-------------------------------------------

Because communication internally relies on queues and that queues must be
**passed** to the workers, they must be created and pass to the worker.


Receiver and emitter in the same worker
---------------------------------------

The emitter and receiver objects are usually aimed at being run in different
workers, one of them possibly being the main worker. However, it's possible to
use them to handle advanced communication between objects.

If you do this, don't ever use the synchronous mode. This will loop indefinitely
and block (deadlock).


There are good demos at the end of the module. ,-)

"""

import time
from typing import TypeVar

from imapfw import runtime
from imapfw.constants import EMT, SLEEP

# Annotations.
from imapfw.annotation import ExceptionClass
from imapfw.concurrency import Queue


#TODO: expose
_SILENT_TIMES = 100


# Outlined.
def _raiseError(cls_Exception: ExceptionClass, reason: str):
    """Default callback for errors."""

    try:
        raise cls_Exception(reason)
    except NameError as e:
        runtime.ui.exception(e)
        raise RuntimeError("exception from receiver cannot be raised %s: %s"%
            (cls_Exception.__name__, reason))


class Channel(object):
    """Queue made iterable."""

    def __init__(self, queue: Queue):
        self._queue = queue

    def __iter__(self):
        return self

    def __next__(self):
        elem = self._queue.get_nowait()
        if elem is None:
            raise StopIteration
        return elem


class Emitter(object):
    """Send events."""

    def __init__(self, name: str, event: Queue, result: Queue, error: Queue):
        self._name = name
        self._eventQueue = event
        self._resultQueue = result
        self._errorQueue = error

        self._previousTopic = None
        self._previousTopicCount = 0

    def __getattr__(self, topic: str):
        """Dynamically create methods to send events."""

        def send_event(*args, **kwargs):
            request = (topic, args, kwargs)

            if self._previousTopic != topic:
                if self._previousTopicCount > 0:
                    runtime.ui.debugC(EMT, "emitter [%s] sent %i times %s"%
                        (self._name, _SILENT_TIMES, self._previousTopic))
                self._previousTopicCount = 0
                self._previousTopic = topic
                runtime.ui.debugC(EMT, "emitter [%s] sends %s"%
                    (self._name, request))
            else:
                self._previousTopicCount += 1
                if self._previousTopicCount == 2:
                    runtime.ui.debugC(EMT, "emitter [%s] sends %s again,"
                        " further sends for this topic made silent"%
                        (self._name, request))
                if self._previousTopicCount > (_SILENT_TIMES - 1):
                    runtime.ui.debugC(EMT,
                        "emitter [%s] sends for the %ith time %s"%
                        (self._name, _SILENT_TIMES, self._previousTopic))
                    self._previousTopicCount = 0
            self._eventQueue.put(request)

        def async(topic):
            return send_event

        def sync(topic):
            def sync_event(*args, **kwargs):
                send_event(*args, **kwargs)

                while True:
                    error = self._errorQueue.get_nowait()
                    if error is None:
                        result = self._resultQueue.get_nowait()
                        if result is None:
                            time.sleep(SLEEP) # Don't eat all CPU.
                            continue
                        if len(result) > 1:
                            return result
                        return result[0]
                    else:
                        # Error occured.
                        cls_Exception, reason = error
                        _raiseError(cls_Exception, reason)

            return sync_event

        if topic.endswith('_sync'):
            setattr(self, topic, sync(topic))
        else:
            setattr(self, topic, async(topic))
        return getattr(self, topic)


class Receiver(object):
    """Honor events."""

    def __init__(self, name: str, event: Queue, result: Queue, error: Queue):
        self._name = name
        self._eventChan = Channel(event)
        self._resultQueue = result
        self._errorQueue = error

        self._reactMap = {}
        self._previousTopic = None
        self._previousTopicCount = 0

    def _debug(self, msg: str):
        runtime.ui.debugC(EMT, "receiver [%s] %s"% (self._name, msg))

    def _react(self, topic: str, args, kwargs):
        func, rargs = self._reactMap[topic]
        args = rargs + args

        # Make debug retention is too many messages.
        if self._previousTopic != topic:
            if self._previousTopicCount > 0:
                self._debug("reacted %i times to '%s'"%
                    (self._previousTopicCount, self._previousTopic))
            self._previousTopicCount = 0
            self._previousTopic = topic
            self._debug("reacting to '%s' with '%s', %s, %s"%
                (topic, func.__name__, args, kwargs))

        else:
            self._previousTopicCount += 1
            if self._previousTopicCount == 2:
                self._debug("reacting to '%s' again, further messages made"
                        " silent"% (topic))
            if self._previousTopicCount > (_SILENT_TIMES - 1):
                self._debug(
                    "reacting for the %ith time to '%s' with '%s', %s, %s"%
                    (_SILENT_TIMES, topic, func.__name__, args, kwargs))
                self._previousTopicCount = 0

        return func(*args, **kwargs)

    def accept(self, event: str, func: callable, *args) -> None:
        self._reactMap[event] = (func, args)

    def react(self) -> bool:
        """Process events in order.

        The order of events is the order of the **available** events in the
        queue. This is relevant only when *sending* events concurrently (from
        different workers)."""

        for event in self._eventChan:
            topic, args, kwargs = event
            try:

                if topic == 'stopServing':
                    self._debug("marked as stop serving")
                    return False

                if topic in self._reactMap:
                    self._react(topic, args, kwargs)
                    return True

                elif topic.endswith('_sync'):
                    realTopic = topic[:-5]
                    if realTopic in self._reactMap:
                        result = self._react(realTopic, args, kwargs)
                        if type(result) != tuple:
                            result = (result,)
                        self._resultQueue.put(result)
                        return True
                    else:
                        reason = "%s got unkown event '%s'"% (self._name, topic)
                        self._errorQueue.put((AttributeError, reason))

                runtime.ui.error("receiver %s unhandled event %s"%
                        (self._name, event))

            except KeyboardInterrupt:
                raise
            except Exception as e:
                runtime.ui.critical("%s unhandled error occurred while"
                    " reacting to event %s: %s: %s"%
                    (self._name, event, e.__class__.__name__, e))
                runtime.ui.exception(e)
                if topic.endswith('_sync'):
                    self._errorQueue.put((e.__class__, str(e)))

        time.sleep(SLEEP) # Don't eat all CPU if caller is looping here.
        return True


class SyncEmitter(object):
    """Adaptater emitter to turn an emitter into sync mode only."""

    def __init__(self, emitter):
        self._emitter = emitter

    def __getattr__(self, name):
        return getattr(self._emitter, "%s_sync"% name)


def newEmitterReceiver(debugName: str) -> (Receiver, Emitter):
    eventQueue = runtime.concurrency.createQueue()
    resultQueue = runtime.concurrency.createQueue()
    errorQueue = runtime.concurrency.createQueue()

    emitter = Emitter(debugName, eventQueue, resultQueue, errorQueue)
    receiver = Receiver(debugName, eventQueue, resultQueue, errorQueue)
    return receiver, emitter


if __name__ == '__main__':
    # Run this demo like this (from the root directory):
    # python3 -m imapfw.governor
    #
    # We catch exception since it's run as a test in travis.

    _DEBUG = True # Set to True for more output and stack trace on error.

    import sys
    from imapfw.concurrency.concurrency import Concurrency
    from imapfw.ui.tty import TTY

    c = Concurrency('multiprocessing')
    ui = TTY(c.createLock())
    ui.configure()
    if _DEBUG:
        ui.enableDebugCategories(['emitters'])
    ui.setCurrentWorkerNameFunction(c.getCurrentWorkerNameFunction())

    runtime.set_module('ui', ui)
    runtime.set_module('concurrency', c)


    def run_async():
        ui.info("******** running run_async()")

        __REMOTE__ = 'http://imapfw.github.io'
        __CONNECTED__ = 'would be connected'
        driverReceiver, driverEmitter = newEmitterReceiver('driver')

        def connect(remote, port):
            print("would connect to %s:%s"% (remote, port))
            assert remote == __REMOTE__
            assert port == 80
            return __CONNECTED__

        driverReceiver.accept('connect', connect)

        driverEmitter.connect(__REMOTE__, 80)
        driverEmitter.stopServing()

        # Blocking loop to react to all events.
        react = True
        while react:
            react = driverReceiver.react()
        print('driver stopped reacting')


    def run_sync():
        ui.info("******** running run_sync()")

        __REMOTE__ = 'http://imapfw.github.io'
        __CONNECTED__ = 'would be connected'

        def runner(receiver):
            def connect(remote, port):
                print("would connect to %s:%s"% (remote, port))
                assert remote == __REMOTE__
                assert port == 80
                return __CONNECTED__

            receiver.accept('connect', connect)

            # Blocking loop to react to all events.
            react = True
            while react:
                react = driverReceiver.react()
            print('driver stopped reacting')

        def onConnect(result):
            print("result: %s"% result)
            assert result == __CONNECTED__

        driverReceiver, driverEmitter = newEmitterReceiver('driver')


        worker = c.createWorker(
            'Worker', runner, (driverReceiver,))
        worker.start()

        try:
            driverEmitter.connect(__REMOTE__, 80)
            value = driverEmitter.connect_sync(__REMOTE__, 80)
            onConnect(value)
            driverEmitter.stopServing()
        except:
            worker.kill()
            raise
        worker.join()

    try:
        run_async()
        run_sync()
        sys.exit(0)
    except Exception as e:
        ui.exception(e)
        sys.exit(1)
