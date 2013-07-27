import inspect
from . import validator
from . import utils


class CallValidator(object):
    use_validator = validator.Validator
    enable_validation = True

    @classmethod
    def decorate(cls, func):
        validator = cls(func, cls.use_validator())

        def __wrapper(*args, **kwargs):
            if not cls.enable_validation:
                return func(*args, **kwargs)

            return validator(*args, **kwargs)

        utils.copy_args(__wrapper, func)
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
