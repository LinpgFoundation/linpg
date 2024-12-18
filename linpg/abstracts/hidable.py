from abc import ABC


# an abstract implementation of a class that can be hidden and unhidden
class Hidable(ABC):
    def __init__(self, visible: bool = True) -> None:
        self.__hidden: bool = not visible

    def set_visible(self, visible: bool) -> None:
        self.__hidden = not visible

    def is_visible(self) -> bool:
        return not self.__hidden

    def is_hidden(self) -> bool:
        return self.__hidden
