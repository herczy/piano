def copy_args(dest, src):
    if hasattr(src, '__name__'):
        dest.__name__ = src.__name__

    if hasattr(src, '__doc__'):
        dest.__doc__ = src.__doc__

    if hasattr(src, '__annotations__'):
        dest.__annotations__ = src.__annotations__


def abstract(func):
    def __wrapper(*args, **kwargs):
        raise NotImplementedError("%s not implemented" % func.__name__)

    copy_args(__wrapper, func)
    return __wrapper
