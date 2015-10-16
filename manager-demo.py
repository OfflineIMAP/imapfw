#
# runnern this file like this:
# python3 -m imapfw.managers.demo
#

import sys
import time


import imapfw

from imapfw.concurrency.concurrency import Concurrency
from imapfw.managers.manager import Manager
from imapfw.ui.tty import TTY
from imapfw.managers.trigger import Trigger


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

    def handleTigger(trigger):
        def simpleResult(value):
            output('readA')
            output(value)
            return False

        triggersMap = {
            'expectInt': simpleResult(trigger.getResult()),
        }
        return triggersMap[trigger.getName()]

    emitter.resultWithTrigger()
    emitter.triggerWithException()
    while True:
        trigger = emitter.getTrigger()
        if trigger is None:
            continue
        try:
            handleTigger(trigger)
        except Exception as e:
            output('got error: %s'% str(e))
            emitter.stopServing()
            break



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

    def exposed_triggerWithException(self):
        output('sleeping 5 in triggerWithException')
        time.sleep(5)
        trigger = Trigger('expectInt', 77)
        trigger.setError(RuntimeError, 'trigger oops')
        self.trigger(trigger)

    def exposed_resultWithTrigger(self):
        output('sleeping 2 in resultWithTrigger')
        time.sleep(2)
        self.trigger(Trigger('expectInt', 77))

tt = TT()

e, r = tt.split()
r.start(runner, (e,))

while r.serve_nowait():
    pass
