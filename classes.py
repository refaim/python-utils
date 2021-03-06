import inspect
import functools

def copy_args(func):
    '''
        Decorator.
        Initializes object attributes by the initializer signature.
        Usage:

        class foo(bar):
            @copy_args
            def __init__(self, arg1, arg2): pass

        foobar = foo(1, 2)
        foobar.arg1 == 1 and foobar.arg2 == 2 # True
    '''
    argspec = inspect.getargspec(func)
    argnames = argspec.args[1:]
    if argspec.defaults:
        defaults = dict(zip(argnames[-len(argspec.defaults):], argspec.defaults))
    else:
        defaults = {}

    @functools.wraps(func)
    def __init__(self, *args, **kwargs):
        args_it = iter(args)
        for key in argnames:
            if key in kwargs:
                value = kwargs[key]
            else:
                try:
                    value = next(args_it)
                except StopIteration:
                    value = defaults[key]
            setattr(self, key, value)
        func(self, *args, **kwargs)
    return __init__
