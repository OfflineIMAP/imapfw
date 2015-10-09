
import sys
import time

import imapfw

from imapfw.concurrency.concurrency import Concurrency
from imapfw.managers.manager import Manager
from imapfw.ui.tty import TTY


c = Concurrency('multiprocessing')
q = c.createQueue()
q.get_nowait()

ui = TTY()

def output(args):
    print(args)
    sys.stdout.flush()

def runner(emitter):
    output('initA_nowait')
    emitter.initA_nowait()

    output('initB_nowait')
    emitter.initB_nowait()

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
        output('sleeping 5')
        time.sleep(5)
        self.A = 'A'

    def exposed_initB_nowait(self):
        output('sleeping 3')
        time.sleep(3)
        self.B = 'B'

    def exposed_initB(self):
        output('sleeping 3')
        time.sleep(3)
        self.B = 'B'

tt = TT()

e, r = tt.split()
r.start(runner, (e,))

print(dir(e))
while r.serve_nowait():
    pass
