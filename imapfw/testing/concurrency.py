
import unittest

from imapfw.concurrency.concurrency import Concurrency, ConcurrencyInterface


class TestMultiProcessing(unittest.TestCase):

    def setUp(self):
        self.backend = Concurrency('multiprocessing')

    def test_00_instanciate(self):

        self.assertIsInstance(self.backend, ConcurrencyInterface)

    def test_01_worker(self):
        def runner(q):
             q.put(1)

        workerName = 'worker'
        queue = self.backend.createQueue()

        worker = self.backend.createBasicWorker(workerName, runner, (queue,))

        worker.start()
        self.assertEqual(worker.getName(), workerName)

        worker.join()
        self.assertEqual(queue.get(), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
