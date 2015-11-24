# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from functools import total_ordering
from collections import UserDict

from imapfw.interface import implements, Interface, checkInterfaces

# Annotations.
from imapfw.annotation import List


#TODO: interface.
class MessageAttributes(object):
    def __init__(self):
        self.flags = []
        self.internaldate = None

    def getFlags(self) -> List[str]:
        return self.flags

    def getInternaldate(self):
        return self.internaldate

    def setFlags(self, flags: List[str]) -> None:
        self.flags = flags

    def setInternaldate(self, internaldate: str):
        #TODO: make python date
        self.internaldate = internaldate


#TODO: interface.
@total_ordering
class Message(object):
    def __init__(self, uid: int):
        self.uid = uid

        self.fd = None
        self.attributes = MessageAttributes()

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

    def getAttributes(self) -> MessageAttributes:
        return self.attributes

    def getFd(self):
        return self.fd

    def getUID(self) -> int:
        return self.uid

    def setFd(self, fd) -> None:
        self.fd = fd

    def setAttributes(self, attributes: MessageAttributes) -> None:
        self.attributes = attributes


#TODO: interface.
class Messages(UserDict):
    """A collection of messages, by UID."""

    def __init__(self, *args):
        self.data = {}
        for message in args:
            self.data[message.getUID()] = message

    def add(self, message: Message) -> None:
        self.update({message.getUID(): message})

    def coalesceUIDs(self) -> str:
        """Return a string of coalesced continous ranges and UIDs.

        E.g.: '1,3:7,9'
        """

        uids = [] # List of UIDs and coalesced sub-sequences ['1', '3:7', '9'].

        def coalesce(start, end):
            if start == end:
                return str(start) # Non-coalesced UID: '1'.
            return "%s:%s"% (start, end) # Coalesced sub-sequence: '3:7'.

        start = None
        end = None
        for uid in self.keys():
            if start is None:
                # First item.
                start, end = uid, uid
                continue

            if uid == end + 1:
                end = uid
                continue

            uids.append(coalesce(start, end))
            start, end = uid, uid # Current uid is the next item to coalesce.
        uids.append(coalesce(start, end))

        return ','.join(uids) # '1,3:7,9'

    def getAttributes(self, uid: int) -> MessageAttributes:
        return self.data[uid].getAttributes()

    def remove(self, message: Message) -> None:
        self.pop(message.getUID())

    def setAttributes(self, uid: int, attributes: MessageAttributes) -> None:
        self.data[uid].setAttributes(attributes)
