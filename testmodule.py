import piano


class AverageCalculator(object):
    def __init__(self):
        self.__value = 0
        self.__count = 0

    def feed(self, value : int) -> type(None):
        self.__value += value
        self.__count += 1

    @property
    def value(self) -> float:
        return float(self.__value) / float(self.__count)


def calc_averages(values : piano.array_of(int)) -> float:
    avg = AverageCalculator()
    for item in values:
        avg.feed(item)

    return avg.value
