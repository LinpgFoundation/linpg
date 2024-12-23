import enum
from random import randint
from tkinter import Tk
from typing import Final, Sequence

import pygame
from PIL import ImageColor as PILImageColor

from ..exception import Exceptions

"""linpg自带属性"""
# 颜色类
color_liked = Sequence[int] | str
# 图形类
ImageSurface = pygame.Surface
# path or pygame.Surface
PoI = str | pygame.Surface
# 事件 type alias
Event = pygame.event.Event
# int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = int | float
# number，即数字，建议int但接受float
number = int | float


# 图像库数据
class GraphicLibrary:
    PYGAME: Final[int] = 0
    PYGAME_CE: Final[int] = 1

    # 是否正在使用pygame_ce
    __IS_CE: Final[bool] = getattr(pygame, "IS_CE", False) is not False

    @classmethod
    def is_using_pygame(cls) -> bool:
        return not cls.__IS_CE

    @classmethod
    def is_using_pygame_ce(cls) -> bool:
        return cls.__IS_CE

    @classmethod
    def get_name(cls) -> str:
        return "Pygame-ce" if cls.__IS_CE else "Pygame"


# 指向pygame事件的指针
@enum.verify(enum.UNIQUE)
class Events(enum.IntEnum):
    # 鼠标
    MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
    MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
    # 手柄
    JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN
    JOYSTICK_BUTTON_UP = pygame.JOYBUTTONUP
    # 键盘
    KEY_DOWN = pygame.KEYDOWN
    KEY_UP = pygame.KEYUP


# 表示方向的enum
@enum.verify(enum.UNIQUE)
class Axis(enum.IntEnum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


# 表示位置
@enum.verify(enum.UNIQUE)
class Locations(enum.IntEnum):
    BEGINNING = enum.auto()
    END = enum.auto()
    MIDDLE = enum.auto()
    EVERYWHERE = enum.auto()


# 与数字有关的常用方法
class Numbers:
    # 随机数
    @staticmethod
    def get_random_int(start: int, end: int) -> int:
        return randint(start, end)

    # 检测int数值是否越界
    @staticmethod
    def keep_int_in_range(_number: int, min_value: int, max_value: int) -> int:
        return max(min(max_value, _number), min_value)

    # 检测int或float数值是否越界
    @staticmethod
    def keep_number_in_range(_number: number, min_value: number, max_value: number) -> number:
        return max(min(max_value, _number), min_value)

    # 转换string形式的百分比
    @staticmethod
    def convert_percentage(percentage: str | float | int) -> float:
        if isinstance(percentage, str) and percentage.endswith("%"):
            return float(percentage.strip("%")) / 100
        elif isinstance(percentage, int):
            return float(percentage)
        elif isinstance(percentage, float):
            return percentage
        else:
            Exceptions.fatal(f'"{percentage}" is not a valid percentage that can be converted')


# 颜色管理
class Colors:
    """常用颜色"""

    # 白色
    WHITE: Final[tuple[int, int, int, int]] = (255, 255, 255, 255)
    # 灰色
    GRAY: Final[tuple[int, int, int, int]] = (105, 105, 105, 255)
    # 淡灰色
    LIGHT_GRAY: Final[tuple[int, int, int, int]] = (83, 83, 83, 255)
    # 黑色
    BLACK: Final[tuple[int, int, int, int]] = (0, 0, 0, 255)
    # 红色
    RED: Final[tuple[int, int, int, int]] = (255, 0, 0, 255)
    # 橙色
    ORANGE: Final[tuple[int, int, int, int]] = (255, 127, 0, 255)
    # 黄色
    YELLOW: Final[tuple[int, int, int, int]] = (255, 255, 0, 255)
    # 绿色
    GREEN: Final[tuple[int, int, int, int]] = (0, 255, 0, 255)
    # 蓝色
    BLUE: Final[tuple[int, int, int, int]] = (0, 0, 255, 255)
    # 靛蓝色
    INDIGO: Final[tuple[int, int, int, int]] = (75, 0, 130, 255)
    # 紫色
    VIOLET: Final[tuple[int, int, int, int]] = (148, 0, 211, 255)
    # 透明
    TRANSPARENT: Final[tuple[int, int, int, int]] = (0, 0, 0, 0)
    # 淡蓝色
    LIGHT_SKY_BLUE: Final[tuple[int, int, int, int]] = (135, 206, 250, 255)
    # 深蓝色
    DODGER_BLUE: Final[tuple[int, int, int, int]] = (30, 144, 255, 255)

    # 转换至rgba颜色tuple
    @staticmethod
    def __to_rgba_color(color: Sequence) -> tuple[int, int, int, int]:
        _r: int = int(color[0])
        _g: int = int(color[1])
        _b: int = int(color[2])
        _a: int = int(color[3]) if len(color) >= 4 else 255
        return _r, _g, _b, _a

    """获取颜色"""

    # 给定一个颜色的名字或序号，返回对应的RGB列表
    @classmethod
    def get(cls, color: color_liked) -> tuple[int, int, int, int]:
        if isinstance(color, str):
            try:
                return cls.__to_rgba_color(PILImageColor.getrgb(color))
            except ValueError:
                Exceptions.fatal(f'The color "{color}" is currently not available!')
        else:
            return cls.__to_rgba_color(color)


class Keys:
    # 按键常量
    ESCAPE: Final[int] = pygame.K_ESCAPE
    SPACE: Final[int] = pygame.K_SPACE
    BACKSPACE: Final[int] = pygame.K_BACKSPACE
    DELETE: Final[int] = pygame.K_DELETE
    LEFT_CTRL: Final[int] = pygame.K_LCTRL
    ARROW_UP: Final[int] = pygame.K_UP
    ARROW_DOWN: Final[int] = pygame.K_DOWN
    ARROW_LEFT: Final[int] = pygame.K_LEFT
    ARROW_RIGHT: Final[int] = pygame.K_RIGHT
    RETURN: Final[int] = pygame.K_RETURN
    BACKQUOTE: Final[int] = pygame.K_BACKQUOTE
    F3: Final[int] = pygame.K_F3

    __root: Final[Tk] = Tk()
    __root.withdraw()

    # key是否被按下
    @classmethod
    def get_pressed(cls, key_name: str | int) -> bool:
        return pygame.key.get_pressed()[cls.get_key_code(key_name) if isinstance(key_name, str) else key_name]

    # 获取key的代号
    @staticmethod
    def get_key_code(key_name: str) -> int:
        return pygame.key.key_code(key_name)

    # 获取粘贴板内容
    @classmethod
    def get_clipboard(cls) -> str:
        return cls.__root.clipboard_get()
