# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors

import unittest

from imapfw.types.message import Messages, Message


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.messageA = Message(2)
        self.messageB = Message(2)
        self.message3 = Message(3)

    def test_00_message_equal(self):
        self.assertEqual(self.messageA, self.messageB)

    def test_01_message_greater(self):
        self.assertGreater(self.message3, self.messageA)


class TestMessages(unittest.TestCase):
    def setUp(self):
        self.message1 = Message(1)
        self.message2 = Message(2)
        self.message3 = Message(3)
        self.messagesI = Messages(self.message2, self.message1)

    def test_00_in(self):
        self.assertIn(self.message2, self.messagesI)

    def test_01_add(self):
        self.messagesI.add(self.message1)
        self.assertIn(self.message1, self.messagesI)

    def test_02_remove(self):
        self.messagesI.remove(self.message2)
        self.assertNotIn(self.message2, self.messagesI)


if __name__ == '__main__':
    unittest.main(verbosity=2)
