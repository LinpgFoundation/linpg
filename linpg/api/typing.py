# cython: language_level=3

#导入pygame组件
import pygame
from pygame.locals import *
#初始化pygame
pygame.init()

#导入核心组件
from ..lang import *

ImageSurface = pygame.Surface
ShapeRect = pygame.Rect

"""指向pygame事件的指针"""
#键盘
KEY_DOWN = pygame.KEYDOWN
KEY_UP = pygame.KEYUP
KEY_ESCAPE = pygame.K_ESCAPE
KEY_SPACE = pygame.K_SPACE
KEY_BACKSPACE = pygame.K_BACKSPACE
KEY_ARROW_UP = pygame.K_UP
KEY_ARROW_DOWN = pygame.K_DOWN
KEY_ARROW_LEFT = pygame.K_LEFT
KEY_ARROW_RIGHT = pygame.K_RIGHT
#鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
#手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN