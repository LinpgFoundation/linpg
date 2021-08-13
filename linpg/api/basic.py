from typing import Iterable
from random import randint as RANDINT
from re import split as RE_SPLIT
from ..lang import *

# 用于辨识基础游戏库的参数，True为默认的pyglet，False则为Pygame
_LIBRARY_INDICATOR: int = 0

# 默认使用pygame库（直到引擎完全支持pyglet）
try:
    # 导入pygame组件
    import pygame
    from pygame.locals import *

    # 初始化pygame
    pygame.init()
except ModuleNotFoundError:
    import pyglet

    _LIBRARY_INDICATOR = 1

# 是否正在使用pygame库
def is_using_pygame() -> bool:
    return _LIBRARY_INDICATOR == 0


# 是否正在使用pyglet库
def is_using_pyglet() -> bool:
    return _LIBRARY_INDICATOR == 1


# 获取正在使用的库的信息
def get_library_info() -> str:
    return "Pygame {}".format(pygame.version.ver) if _LIBRARY_INDICATOR == 0 else "Pyglet {}".format(pyglet.version)


"""linpg自带属性"""
# int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]
# number，即数字，建议int但接受float
number = Union[int, float]
color_liked = Union[Iterable[int], str]
# 图形类
ImageSurface = pygame.Surface if _LIBRARY_INDICATOR == 0 else pyglet.image
"""linpg自带常量"""
NoSize: tuple[int] = (-1, -1)
NoPos: tuple[int] = (-1, -1)
PoI = Union[str, ImageSurface]

"""指向pygame事件的指针"""
# 鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
# 手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN

# 随机数
def get_random_int(start: int, end: int) -> int:
    return RANDINT(start, end)


# 多段数字字符串排序 - by Jeff Atwood
def natural_sort(l: list) -> list:
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in RE_SPLIT("([0-9] )", key)]
    return sorted(l, key=alphanum_key)


# 检测数值是否越界
def keep_in_range(number: number, min_value: number, max_value: number) -> number:
    return max(min(max_value, number), min_value)


# 转换string形式的百分比
def convert_percentage(percentage: Union[str, float]) -> float:
    if isinstance(percentage, str) and percentage.endswith("%"):
        return float(percentage.strip("%")) / 100
    elif isinstance(percentage, float):
        return percentage
    else:
        EXCEPTION.fatal('"{}" is not a valid percentage that can be converted'.format(percentage))


# 获取Surface
def new_surface(size: Iterable, surface_flags: any = None) -> ImageSurface:
    return pygame.Surface(size, flags=surface_flags) if surface_flags is not None else pygame.Surface(size)


# 获取透明的Surface
def new_transparent_surface(size: Iterable) -> ImageSurface:
    return new_surface(size, pygame.SRCALPHA).convert_alpha()


# 中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def display_in_center(
    item1: ImageSurface,
    item2: ImageSurface,
    x: number,
    y: number,
    screen: ImageSurface,
    off_set_x: number = 0,
    off_set_y: number = 0,
) -> None:
    screen.blit(
        item1,
        (
            x + (item2.get_width() - item1.get_width()) / 2 + off_set_x,
            y + (item2.get_height() - item1.get_height()) / 2 + off_set_y,
        ),
    )


# 中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def display_within_center(
    item1: ImageSurface,
    item2: ImageSurface,
    x: number,
    y: number,
    screen: ImageSurface,
    off_set_x: number = 0,
    off_set_y: number = 0,
) -> None:
    screen.blits(
        (item2, (int(x + off_set_x), int(y + off_set_y))),
        (
            item1,
            (
                int(x + (item2.get_width() - item1.get_width()) / 2 + off_set_x),
                int(y + (item2.get_height() - item1.get_height()) / 2 + off_set_y),
            ),
        ),
    )
