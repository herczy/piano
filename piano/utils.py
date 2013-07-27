def copy_args(dest, src):
    dest.__name__ = src.__name__
    dest.__doc__ = src.__doc__
    dest.__annotations__ = src.__annotations__


def abstract(func):
    def __wrapper(*args, **kwargs):
        raise NotImplementedError("%s not implemented" % func.__name__)

    copy_args(__wrapper, func)
    return __wrapper
