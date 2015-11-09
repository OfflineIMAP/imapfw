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

Lightweight support for interfaces in Python code.

This is much lighter implementation for interfaces than any other library
out-there.

It is very flexible as it only targets on defining interfaces and implementing
them. User is not forced to use any design pattern.

"""

import inspect
import re

from imapfw.annotation import Iterable, Function


def _iterMehods(cls):
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        if name.startswith('__'):
            continue
        yield name, method

def _signature(method):
    sig = str(inspect.signature(method))
    return sig

def _iterDocImplements(doc: str) -> Iterable[str]:
    implements = []

    lines = doc.split('\n')
    for line in lines:
        for m in re.finditer('implements: (.*)', line):
            str_implements = m.group(1)
            lst_implements = [i.strip(' ') for i in str_implements.split(',')]
            implements += lst_implements
    for implement in implements:
        yield implement

def _getattrDeclareName(name: str, getattrMethod: Function) -> bool:
    for declaration in _iterDocImplements(getattrMethod.__doc__):
        if declaration == name:
            return True
    return False



def _checkImplementation(cls):
    """Check that the class implements its declared interfaces."""

    # Check the class implement all the interfaces.
    declaredByInterfaces = {}
    for interface in cls.__implements__:

        for name, method in _iterMehods(interface):
            if name not in declaredByInterfaces:
                declaredByInterfaces[name] = method

            if hasattr(cls, name):
                if method.__doc__ is not None:
                    # Attach documentation.
                    cls_method = getattr(cls, name)
                    if cls_method.__doc__ is None:
                        cls_method.__doc__ = method.__doc__
                    else:
                        cls_method.__doc__ += method.__doc__

            else:
                try:
                    if hasattr(cls, '__getattr__'):
                        if not _getattrDeclareName(name, cls.__getattr__):
                            raise TypeError()
                    else:
                        raise TypeError()
                except TypeError:
                    raise TypeError("class %s declares to implement %s"
                        " but %s is not implemented"% (cls.__name__,
                        interface.__name__, name))

    for name, method in _iterMehods(cls):
        if name in declaredByInterfaces:
            footprintCls = _signature(method)
            footprintInterface = _signature(declaredByInterfaces[name])
            if footprintCls != footprintInterface:
                raise TypeError("signature of %s.%s mismatch interface:"
                    " '%s' vs '%s'"%
                    (cls.__name__, name, footprintCls, footprintInterface))

        else:
            raise TypeError("class %s implements %s"
                " but %s is declared in any interface of %s"%
                (cls.__name__, name, name, cls.__implements__))


def implements(*interfaces):
    """Class decorator for supporting interfaces."""

    def cls_implements(cls):
        """Actually make class to implement the interfaces."""

        def inherit(tree, implements=[]):
            """Lookup the parents to inherit their interfaces."""

            try:
                cls_parent = tree.pop(0)[0]
                if hasattr(cls_parent, '__implements__'):
                    implements + cls_parent.__implements__
            except IndexError:
                return implements

            return inherit(tree, implements)

        newInterfaces = list(interfaces)
        inherited = inherit(inspect.getclasstree([cls]))
        newInterfaces += inherited

        if hasattr(cls, '__implements__'):
            cls.__implements__ + newInterfaces
        else:
            setattr(cls, '__implements__', newInterfaces)

        _checkImplementation(cls)
        return cls

    return cls_implements


class Interface(object):
    INTERNAL = '__INTERNAL__'
    PUBLIC = '__PUBLIC__'

    scope = None # Must be defined.
