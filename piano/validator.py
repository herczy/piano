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
