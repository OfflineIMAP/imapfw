
import time

from worker import concurrency


class B:
    def bdo(self):
        print('in main: bdo')


# Managed by A
class A:
    def do(self):
        print('in main: aaa')
    def test(self, name):
        print('in main: test')
        print('in main', name)
        return 'main returned ok'


c = concurrency.Concurrency('multiprocessing')


def run(pa):

    print('in run: pa', pa)
    print(1)
    pa.do()
    print(2)
    v = pa.test('bla')
    print(3)
    print('in run: %s'% v)


a = A()

ra, pa = c.manager(a, 'do', 'test')

print('ra', ra)
print('pa', pa)
print('dir pa', dir(pa))


worker = c.getWorker(
    name='t',
    target=run,
    args=(pa,)
)

worker.start()


while True:
    time.sleep(0.001)
    ra.serve_nowait()

