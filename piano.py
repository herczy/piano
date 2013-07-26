import sys
import inspect


if sys.hexversion < 0x03020000:
    raise ImportError("Module requires at least Python version 3.2")


def copy_args(dest, src):
    dest.__name__ = src.__name__
    dest.__doc__ = src.__doc__
    dest.__annotations__ = src.__annotations__


def abstract(func):
    def __wrapper(*args, **kwargs):
        raise NotImplementedError("%s not implemented" % func.__name__)

    copy_args(__wrapper, func)
    return __wrapper


class Validator(object):
    def is_valid(self, value, validator):
        if validator is None:
            return True

        elif isinstance(validator, type):
            return isinstance(value, validator)

        elif hasattr(validator, '__call__'):
            return validator(value)

        else:
            return True

    def _or_validate(self, value, validators):
        for validator in validators:
            if self.is_valid(value, validator):
                return True

        return False

    def _and_validate(self, value, validators):
        for validator in validators:
            if not self.is_valid(value, validator):
                return False

        return True


class CallValidator(object):
    use_validator = Validator
    enable_validation = True

    @classmethod
    def decorate(cls, func):
        validator = cls(func, cls.use_validator())

        def __wrapper(*args, **kwargs):
            if not cls.enable_validation:
                return func(*args, **kwargs)

            return validator(*args, **kwargs)

        copy_args(__wrapper, func)
        return __wrapper

    def __init__(self, function, validator):
        self.__function = function
        self.__validator = validator
        self.__spec = inspect.getfullargspec(function)

        self.__num_kwargs = len(self.__spec.defaults) if self.__spec.defaults else 0
        self.__num_args = len(self.__spec.args) - self.__num_kwargs

    def map_arguments(self, args, kwargs):
        for index, arg_name in enumerate(self.__spec.args):
            annotation = self.__spec.annotations.get(arg_name)
            if index < self.__num_args:
                yield index, args[index], annotation

            else:
                yield arg_name, args[index], annotation

    def __call__(self, *args, **kwargs):
        self.__validate_args(args, kwargs)
        res = self.__function(*args, **kwargs)
        self.__validate_retval(res)

        return res

    def __validate_args(self, args, kwargs):
        for key, value, validator in self.map_arguments(args, kwargs):
            if validator is None:
                continue

            if not self.__validator.is_valid(value, validator):
                key_name = ("#%d" % value) if isinstance(value, int) else repr(key)
                func_name = self.__function.__name__
                raise TypeError("Argument %s of function %r invalid" % (key_name, func_name))

    def __validate_retval(self, retval):
        if retval is not None and \
           not self.__validator.is_valid(retval, self.__spec.annotations.get('return')):
            func_name = self.__function.__name__
            raise TypeError("Return value of function %s is invalid" % func_name)


class ModuleFinder(object):
    @classmethod
    def install(cls):
        cls.uninstall()
        sys.meta_path.insert(0, cls())

    @classmethod
    def uninstall(cls):
        sys.meta_path = [loader for loader in sys.meta_path
                                if not isinstance(loader, cls)]

    def find_module(self, fullname, path=None):
        return self

    def load_module(self, fullname):
        module = self.__import(fullname)
        self.__decorate_methods(module)
        return module

    def __import(self, name):
        self.__uninstall_object()
        try:
            module = __import__(name)

        finally:
            self.__install_object()

        for comp in name.split('.')[1:]:
            module = getattr(module, comp)

        return module

    def __decorate_methods(self, module, use_dict=None, call_validator=CallValidator):
        if use_dict is None:
            use_dict = module.__dict__

        for key, value in use_dict.items():
            if inspect.isfunction(value):
                # Only decorate if has annotations
                if not hasattr(value, '__annotations__') or \
                   not value.__annotations__:
                    continue

                setattr(module, key, call_validator.decorate(value))

            elif inspect.isclass(value):
                self.__decorate_methods(value, call_validator=call_validator)

            elif inspect.ismodule(value) and inspect.ismodule:
                if self.__submodule_of(value, module):
                    self.__decorate_methods(value, call_validator=call_validator)

            elif isinstance(value, property):
                res = property()

                if value.fget is not None:
                    res = property(call_validator.decorate(value.fget))

                else:
                    res = property()

                if value.fset is not None:
                    res.setter(call_validator.decorate(value.fset))

                if value.fdel is not None:
                    res.deleter(call_validator.decorate(value.fdel))

                setattr(module, key, res)

    def __install_object(self):
        self.__class__.uninstall()
        sys.meta_path.insert(0, self)

    def __uninstall_object(self):
        self.__class__.uninstall()

    def __submodule_of(self, basemodule, submodule):
        return submodule.__name__.startswith(basemodule.__name__ + '.')


def array_of(value_type):
    def __validator(values):
        if not isinstance(values, tuple) and \
           not isinstance(values, list):
            return False

        for value in values:
            if not isinstance(value, value_type):
                return False

        return True

    return __validator
