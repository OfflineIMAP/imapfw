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
        self.message2 = Message(2)
        self.message3 = Message(3)
        self.messagesI = Messages(self.message3, self.message2)

    def test_00_in(self):
        self.assertIn(self.message2, self.messagesI)


if __name__ == '__main__':
    unittest.main(verbosity=2)
