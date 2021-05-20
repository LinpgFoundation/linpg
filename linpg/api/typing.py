# cython: language_level=3

#导入pygame组件
import pygame
from pygame.locals import *
#初始化pygame
pygame.init()

#导入核心组件
from ..lang import *

ImageSurface = pygame.Surface

"""指向pygame事件的指针"""
#鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
#手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN