# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

Where Python3 annotations must be defined.

"""

from typing import Any, Dict, Iterable, List, Tuple, TypeVar, Union

# Global.
Function = TypeVar('Function')

# actions.clioptions,
ActionClass = TypeVar('ActionClass')

# edmp,
ExceptionClass = TypeVar('Exception class')

# interface,
Requirement = Any
InterfaceClass = TypeVar('Interface class')
InterfaceDefinitions = Dict[InterfaceClass, Tuple['arguments']]

# drivers.driver,
DriverClass = TypeVar('Driver based class')

# actions.interface,
ExceptionClass = TypeVar('Exception class')
