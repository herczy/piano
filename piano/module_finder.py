import sys
import inspect
from . import call_validator


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

    def __decorate_methods(self, module, use_dict=None, call_validator=call_validator.CallValidator):
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
