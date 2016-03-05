
from imapfw import runtime
from imapfw.constants import ARC

def debugArchitect(cls):
    """Decorate methods of an Architect for better debugging experience."""

    import inspect
    import functools

    def debugWrapper(func):
        @functools.wraps(func)
        def debugMethod(*args, **kwargs):
            runtime.ui.debugC(ARC, "D: %s.%s: %s %s"%
                    (cls.__name__, func.__name__, repr(args[1:]), repr(kwargs)))
            result = func(*args, **kwargs)
            return result

        return debugMethod

    for name, method in inspect.getmembers(cls, inspect.isfunction):
        setattr(cls, name, debugWrapper(method))
    return cls

