from .module_finder import ModuleFinder
from .call_validator import CallValidator


def install():
    ModuleFinder.install()
    CallValidator.enable_validation = True


def uninstall():
    ModuleFinder.uninstall()
    CallValidator.enable_validation = False
