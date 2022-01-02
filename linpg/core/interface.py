from .system import *

# 可隐藏的Surface
class HiddenableSurface:
    def __init__(self, visible: bool = True) -> None:
        self.__hidden: bool = not visible

    def set_visible(self, visible: bool) -> None:
        self.__hidden = not visible

    def is_visible(self) -> bool:
        return not self.__hidden

    def is_hidden(self) -> bool:
        return self.__hidden


# 有本地坐标的Surface (警告，子类必须实现get_left()和get_top()方法)
class SurfaceWithLocalPos:
    def __init__(self) -> None:
        self.__local_x: int = 0
        self.__local_y: int = 0

    # 获取x坐标（子类需实现）
    def get_left(self) -> int:
        EXCEPTION.fatal("get_left()", 1)

    # 获取y坐标（子类需实现）
    def get_top(self) -> int:
        EXCEPTION.fatal("get_top()", 1)

    # 获取本地坐标
    @property
    def local_x(self) -> int:
        return self.__local_x

    def get_local_x(self) -> int:
        return self.__local_x

    @property
    def local_y(self) -> int:
        return self.__local_y

    def get_local_y(self) -> int:
        return self.__local_y

    @property
    def local_pos(self) -> tuple[int, int]:
        return self.__local_x, self.__local_y

    def get_local_pos(self) -> tuple[int, int]:
        return self.__local_x, self.__local_y

    # 设置本地坐标
    def set_local_x(self, value: int_f) -> None:
        self.__local_x = int(value)

    def set_local_y(self, value: int_f) -> None:
        self.__local_y = int(value)

    def set_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.set_local_x(local_x)
        self.set_local_y(local_y)

    def locally_move_to(self, local_pos: tuple) -> None:
        self.set_local_pos(local_pos[0], local_pos[1])

    # 增加本地坐标
    def add_local_x(self, value: int_f) -> None:
        self.set_local_x(self.__local_x + value)

    def add_local_y(self, value: int_f) -> None:
        self.set_local_y(self.__local_y + value)

    def add_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.add_local_x(local_x)
        self.add_local_y(local_y)

    # 减少本地坐标
    def subtract_local_x(self, value: int_f) -> None:
        self.set_local_x(self.__local_x - value)

    def subtract_local_y(self, value: int_f) -> None:
        self.set_local_y(self.__local_y - value)

    def subtract_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.subtract_local_x(local_x)
        self.subtract_local_y(local_y)

    # 绝对的本地坐标
    @property
    def abs_x(self) -> int:
        return int(self.get_left() + self.__local_x)

    @property
    def abs_y(self) -> int:
        return int(self.get_top() + self.__local_y)

    @property
    def abs_pos(self) -> tuple[int, int]:
        return self.abs_x, self.abs_y

    def get_abs_pos(self) -> tuple[int, int]:
        return self.abs_x, self.abs_y
