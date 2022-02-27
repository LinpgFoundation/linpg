from random import randint as RANDINT
from typing import Sequence

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
color_liked = Union[Sequence[int], str]
# 图形类
ImageSurface = pygame.surface.Surface
PoI = Union[str, pygame.surface.Surface]
# 声音 type alias
PG_Sound = pygame.mixer.Sound
# 频道 type alias
PG_Channel = pygame.mixer.Channel
# 事件 type alias
PG_Event = pygame.event.Event

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


# 检测int数值是否越界
def keep_int_in_range(number: int, min_value: int, max_value: int) -> int:
    return max(min(max_value, number), min_value)


# 检测int或float数值是否越界
def keep_number_in_range(number: number, min_value: number, max_value: number) -> number:
    return max(min(max_value, number), min_value)


# 转换string形式的百分比
def convert_percentage(percentage: Union[str, float]) -> float:
    if isinstance(percentage, str) and percentage.endswith("%"):
        return float(percentage.strip("%")) / 100
    elif isinstance(percentage, float):
        return percentage
    else:
        EXCEPTION.fatal('"{}" is not a valid percentage that can be converted'.format(percentage))
