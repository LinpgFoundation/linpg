from functools import reduce
from operator import add, mul, sub

from ..basic.enums import Directions
from ..media import *

# 原点
ORIGIN: Final[tuple[int, int]] = (0, 0)


# 坐标类 - 更精准坐标
class Position:
    def __init__(self, x: number, y: number):
        # 坐标（注意，与Coordinate不同，Position坐标使用浮点数）
        self.__x: number = x
        self.__y: number = y

    def __lt__(self, other: "Position") -> bool:
        return self.__y + self.__x < other.y + other.x

    # 坐标信息
    @property
    def x(self) -> number:
        return self.__x

    @property
    def y(self) -> number:
        return self.__y

    @property
    def pos(self) -> tuple[number, number]:
        return self.__x, self.__y

    def get_pos(self) -> tuple[number, number]:
        return self.__x, self.__y

    # 设置坐标
    def set_x(self, value: number) -> None:
        self.__x = value if isinstance(value, int) else round(value, 5)

    def set_y(self, value: number) -> None:
        self.__y = value if isinstance(value, int) else round(value, 5)

    def set_pos(self, x: number, y: number) -> None:
        self.set_x(x)
        self.set_y(y)

    def move_to(self, pos: tuple[number, number]) -> None:
        self.set_x(pos[0])
        self.set_y(pos[1])


# 浮点坐标
class Positions:
    # 转换坐标
    @staticmethod
    def convert(pos: Any) -> tuple[number, number]:
        # 检测坐标
        if isinstance(pos, dict):
            return pos["x"], pos["y"]
        elif isinstance(pos, (Sequence, numpy.ndarray)):
            return pos[0], pos[1]
        else:
            try:
                return pos.x, pos.y
            except Exception:
                Exceptions.fatal(f'Unable to convert position "{pos}".')

    # 判断2个坐标是否相同
    @staticmethod
    def equal(pos1: Any, pos2: Any) -> bool:
        return Positions.convert(pos1) == Positions.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*positions: tuple[number, number]) -> tuple[number, number]:
        return tuple(reduce(add, elements) for elements in zip(*positions))

    # 相减2个坐标
    @staticmethod
    def subtract(*positions: tuple[number, number]) -> tuple[number, number]:
        return tuple(reduce(sub, elements) for elements in zip(*positions))

    # multiply two coordinates
    @staticmethod
    def multiply(*positions: tuple[number, number]) -> tuple[number, number]:
        return tuple(reduce(mul, elements) for elements in zip(*positions))


# 坐标类
class Coordinate:
    def __init__(self, x: int_f, y: int_f):
        self.__x: int = int(x)
        self.__y: int = int(y)

    def __lt__(self, other: "Coordinate") -> bool:
        return self.__y + self.__x < other.y + other.x

    # x轴坐标
    @property
    def x(self) -> int:
        return self.__x

    @property
    def left(self) -> int:
        return self.__x

    def get_left(self) -> int:
        return self.__x

    def set_left(self, value: int_f) -> None:
        self.__x = int(value)

    # 向左移动
    def move_left(self, value: int_f) -> None:
        self.set_left(int(self.__x - value))

    # 向右移动
    def move_right(self, value: int_f) -> None:
        self.set_left(self.__x + int(value))

    # y轴坐标
    @property
    def y(self) -> int:
        return self.__y

    @property
    def top(self) -> int:
        return self.__y

    def get_top(self) -> int:
        return self.__y

    def set_top(self, value: int_f) -> None:
        self.__y = int(value)

    # 向上移动
    def move_upward(self, value: int_f) -> None:
        self.set_top(int(self.__y - value))

    # 向下移动
    def move_downward(self, value: int_f) -> None:
        self.set_top(self.__y + int(value))

    # 坐标信息
    @property
    def pos(self) -> tuple[int, int]:
        return self.__x, self.__y

    def get_pos(self) -> tuple[int, int]:
        return self.__x, self.__y

    # 设置坐标
    def set_pos(self, _x: int_f, _y: int_f) -> None:
        self.set_left(_x)
        self.set_top(_y)

    def move_to(self, pos: tuple[int_f, int_f]) -> None:
        self.set_pos(pos[0], pos[1])

    # 检测是否在给定的位置上
    def on_pos(self, pos: object) -> bool:
        return Coordinates.equal(self.pos, pos)


# 整数坐标
class Coordinates:
    # 转换坐标
    @staticmethod
    def convert(pos: Any) -> tuple[int, int]:
        # 检测坐标
        if isinstance(pos, dict):
            return int(pos["x"]), int(pos["y"])
        elif isinstance(pos, (Sequence, numpy.ndarray)):
            return int(pos[0]), int(pos[1])
        else:
            try:
                return int(pos.x), int(pos.y)
            except Exception:
                Exceptions.fatal(f'Unable to convert position "{pos}".')

    # 判断2个坐标是否相同
    @staticmethod
    def equal(pos1: Any, pos2: Any) -> bool:
        return Coordinates.convert(pos1) == Coordinates.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*coordinates: tuple[int, int]) -> tuple[int, int]:
        return tuple(reduce(add, c) for c in zip(*coordinates))

    # 相减2个坐标
    @staticmethod
    def subtract(*coordinates: tuple[int, int]) -> tuple[int, int]:
        return tuple(reduce(sub, c) for c in zip(*coordinates))

    # multiply two coordinates
    @staticmethod
    def multiply(*coordinates: tuple[int, int]) -> tuple[int, int]:
        return tuple(reduce(mul, c) for c in zip(*coordinates))


class DynamicMovementController:
    def __init__(self, v_speed: int = 10, h_speed: int = 10, v_speed_deduction: int = 1, h_speed_deduction: int = 1):
        # speed for moving
        self.__current_vertical_speed: int = 0
        self.__current_horizontal_speed: int = 0
        # whether to move to a certain direction
        self.__moving_screen_in_directions: list[bool] = [False, False, False, False]
        # the movement speed
        self.__vertical_speed: int = v_speed
        self.__horizontal_speed: int = h_speed
        # the movement speed reduction pre frame
        self.__vertical_speed_deduction: int = v_speed_deduction
        self.__horizontal_speed_deduction: int = h_speed_deduction

    @property
    def current_vertical_speed(self) -> int:
        return self.__current_vertical_speed

    @property
    def current_horizontal_speed(self) -> int:
        return self.__current_horizontal_speed

    def move(self, direction: Directions, v: bool) -> None:
        self.__moving_screen_in_directions[direction] = v

    def is_moving(self) -> bool:
        return self.__current_vertical_speed != 0 or self.__current_horizontal_speed != 0

    # move according to speed
    def tick(self) -> None:
        # move current speed closer to 0
        if self.__current_horizontal_speed > 0:
            self.__current_horizontal_speed -= self.__horizontal_speed_deduction
        elif self.__current_horizontal_speed < 0:
            self.__current_horizontal_speed += self.__horizontal_speed_deduction
        if self.__current_vertical_speed > 0:
            self.__current_vertical_speed -= self.__vertical_speed_deduction
        elif self.__current_vertical_speed < 0:
            self.__current_vertical_speed += self.__vertical_speed_deduction
        # restore speed if continue to move
        if self.__moving_screen_in_directions[Directions.UP]:
            self.__current_vertical_speed = self.__vertical_speed
        if self.__moving_screen_in_directions[Directions.DOWN]:
            self.__current_vertical_speed = -self.__vertical_speed
        if self.__moving_screen_in_directions[Directions.LEFT]:
            self.__current_horizontal_speed = self.__horizontal_speed
        if self.__moving_screen_in_directions[Directions.RIGHT]:
            self.__current_horizontal_speed = -self.__horizontal_speed
