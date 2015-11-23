# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors

from functools import total_ordering
from collections import OrderedDict

from imapfw.interface import implements, Interface, checkInterfaces


@total_ordering
class Message(object):
    def __init__(self, uid: int):
        self.uid = uid

        self.fd = None

    # def __bytes__(self):
        # return self._name

    def __eq__(self, other):
        return self.uid == other

    def __hash__(self):
        return hash(self.uid)

    def __lt__(self, other):
        return self.uid < other

    def __repr__(self):
        return "<Message object '%i'>"% self.uid

    def __str__(self):
        return str(self.uid)

    def getFd(self):
        return self.fd

    def getUID(self) -> int:
        return self.uid

    def setFd(self, fd) -> None:
        self.fd = fd


class Messages(OrderedDict):
    """A collection of messages, by UID."""

    def __init__(self, *args):
        messages = {}
        for message in args:
            messages[message.getUID()] = message
        super(Messages, self).__init__(messages)

    def add(self, message: Message) -> None:
        self.update({message.getUID(): message})

    def remove(self, message: Message) -> None:
        self.pop(message.getUID())
