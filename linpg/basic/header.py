from random import randint as RANDINT
from typing import Iterable

import numpy

# 导入pygame组件
import pygame
from pygame.locals import *

from ..tools import *

# 初始化pygame
pygame.init()

# 获取正在使用的库的信息
def get_library_info() -> str:
    return "Pygame {}".format(pygame.version.ver)


"""linpg自带属性"""
# int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]
# number，即数字，建议int但接受float
number = Union[int, float]
# 颜色类
color_liked = Union[Iterable[int], str]

# 图形类
ImageSurface = pygame.surface.Surface
PoI = Union[str, pygame.surface.Surface]

"""linpg自带常量"""
NoSize: tuple[int, int] = (-1, -1)
NoPos: tuple[int, int] = (-1, -1)

"""指向pygame事件的指针"""
# 鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
# 手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN

# 随机数
def get_random_int(start: int, end: int) -> int:
    return RANDINT(start, end)


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


# 根据array生成Surface
def make_surface_from_array(surface_array: numpy.ndarray, swap_axes: bool = True) -> ImageSurface:
    if swap_axes is True:
        surface_array = surface_array.swapaxes(0, 1)
    if surface_array.shape[2] < 4:
        return pygame.surfarray.make_surface(surface_array).convert()
    else:
        # by llindstrom
        surface: ImageSurface = new_transparent_surface(surface_array.shape[0:2])
        # Copy the rgb part of array to the new surface.
        pygame.pixelcopy.array_to_surface(surface, surface_array[:, :, 0:3])
        # Copy the alpha part of array to the surface using a pixels-alpha
        # view of the surface.
        surface_alpha = numpy.array(surface.get_view("A"), copy=False)
        surface_alpha[:, :] = surface_array[:, :, 3]
        return surface


# 获取Surface
def new_surface(size: tuple, surface_flags: Any = None) -> ImageSurface:
    return pygame.Surface(size, flags=surface_flags) if surface_flags is not None else pygame.Surface(size).convert()


# 获取透明的Surface
def new_transparent_surface(size: tuple) -> ImageSurface:
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