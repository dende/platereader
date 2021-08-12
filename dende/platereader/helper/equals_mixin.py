import abc


class EqualsMixin:

    @abc.abstractmethod
    def __key(self):
        pass

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__key() == other.__key()
        return NotImplemented
