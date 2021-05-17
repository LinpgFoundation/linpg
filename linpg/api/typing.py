# cython: language_level=3

#导入pygame组件
import pygame
from pygame.locals import *
#初始化pygame
pygame.init()

#导入核心组件
from ..lang import *

ImageSurface = pygame.Surface

#指向pygame事件的指针
KEY_DOWN = pygame.KEYDOWN
KEY_UP = pygame.KEYUP
KEY_ESCAPE = pygame.K_ESCAPE
KEY_SPACE = pygame.K_SPACE
KEY_BACKSPACE = pygame.K_BACKSPACE
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP