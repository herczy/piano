import sys

from . import call_validator
from . import utils


def _run_test_function(func, args, kwargs, enable_validation):
    call_validator.CallValidator.enable_validation = enable_validation
    func(*args, **kwargs)


def _check_validation(func):
    def __wrapper(*args, **kwargs):
        previous_value = call_validator.CallValidator.enable_validation
        try:
            try:
                _run_test_function(func, args, kwargs, True)

            except TypeError as e:
                raise AssertionError(str(e))

            _run_test_function(func, args, kwargs, False)

        finally:
            call_validator.CallValidator.enable_validation = True

    utils.copy_args(__wrapper, func)
    return __wrapper


def call_validate(cls):
    for name, value in cls.__dict__.items():
        if name.startswith('test_'):
            setattr(cls, name, _check_validation(value))

    return cls
