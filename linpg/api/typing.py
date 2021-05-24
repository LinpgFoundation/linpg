# cython: language_level=3

#导入pygame组件
import pygame
from pygame.locals import *
#初始化pygame
pygame.init()

#导入核心组件
from ..lang import *

ImageSurface = pygame.Surface

#int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]

"""指向pygame事件的指针"""
#鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
#手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN