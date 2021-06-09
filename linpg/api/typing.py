# cython: language_level=3

# 用于辨识基础游戏库的参数，True为默认的pyglet，False则为Pygame
_LIBRARY_INDICATOR:bool = False

#默认使用pygame库（直到引擎完全支持pyglet）
try:
    #导入pygame组件
    import pygame
    from pygame.locals import *
    # 初始化pygame
    pygame.init()
except ModuleNotFoundError:
    import pyglet
    _LIBRARY_INDICATOR = True

# 导入语言组件
from ..lang import *

#是否正在使用pygame库
def is_using_pygame() -> bool: return True if not _LIBRARY_INDICATOR else False
#是否正在使用pyglet库
def is_using_pyglet() -> bool: return True if _LIBRARY_INDICATOR is True else False

# 源库自带的图形类
ImageSurface = pygame.Surface if is_using_pygame() else pyglet.image

#int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]

"""指向pygame事件的指针"""
#鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
#手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN