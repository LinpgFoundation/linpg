# cython: language_level=3
import random, re, numpy
from ..lang import *

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

#是否正在使用pygame库
def is_using_pygame() -> bool: return _LIBRARY_INDICATOR is False
#是否正在使用pyglet库
def is_using_pyglet() -> bool: return _LIBRARY_INDICATOR is True

"""linpg自带属性"""
#int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]
#number，即数字，建议int但接受float
number = Union[int, float]
pos_liked = Union[tuple, list, numpy.ndarray]
size_liked = Union[tuple, list, numpy.ndarray]
color_liked = Union[tuple[int], str, list[int]]
#图形类
ImageSurface = pygame.Surface if not _LIBRARY_INDICATOR else pyglet.image
"""linpg自带常量"""
Origin:tuple[int] = (0, 0)
NoSize:tuple[int] = (-1, -1)
NoPos:tuple[int] = (-1, -1)

"""指向pygame事件的指针"""
#鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
#手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN

#随机数
def get_random_int(start:int, end:int) -> int: return random.randint(start, end)

#转换坐标
def convert_pos(pos:any) -> tuple:
    #检测坐标
    if isinstance(pos, (list, tuple, numpy.ndarray)):
        return pos[0], pos[1]
    elif isinstance(pos, dict):
        return pos["x"], pos["y"]
    else:
        try:
            return pos.x, pos.y
        except Exception:
            EXCEPTION.fatal('Cannot convert position "{}".'.format(pos))

#判断2个坐标是否相同
def is_same_pos(pos1:any, pos2:any) -> bool: return convert_pos(pos1) == convert_pos(pos2)

#相加2个坐标
def add_pos(*positions:any) -> tuple[number]:
    x = 0
    y = 0
    for pos in positions:
        convetred_pos = convert_pos(pos)
        x += convetred_pos[0]
        y += convetred_pos[1]
    return x,y

#int化坐标
def int_pos(pos:tuple[number]) -> tuple[int]: return int(pos[0]), int(pos[1])

#相减2个坐标
def subtract_pos(position:any, *positions:any) -> tuple[number]:
    x,y = convert_pos(position)
    for pos in positions:
        convetred_pos = convert_pos(pos)
        x -= convetred_pos[0]
        y -= convetred_pos[1]
    return x,y

#多段数字字符串排序 - by Jeff Atwood
def natural_sort(l:list) -> list:
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

#检测数值是否越界
def keep_in_range(number:number, min_value:number, max_value:number) -> number:
    return max(min(max_value, number), min_value)

#转换string形式的百分比
def convert_percentage(percentage:Union[str, float]) -> float:
    if isinstance(percentage, str) and percentage.endswith("%"):
        return float(percentage.strip('%'))/100
    elif isinstance(percentage, float):
        return percentage
    else:
        EXCEPTION.fatal('"{}" is not a valid percentage that can be converted'.format(percentage))

#获取Surface
def new_surface(size:size_liked, surface_flags:any=None) -> ImageSurface:
    return pygame.Surface(size, flags=surface_flags) if surface_flags is not None else pygame.Surface(size)

#获取透明的Surface
def new_transparent_surface(size:size_liked) -> ImageSurface:
    return new_surface(size, pygame.SRCALPHA).convert_alpha()

#获取材质缺失的临时警示材质
def get_texture_missing_surface(size:size_liked) -> ImageSurface:
    texture_missing_surface:ImageSurface = new_surface(size).convert()
    texture_missing_surface.fill(Color.BLACK)
    half_width:int = int(size[0]/2)
    half_height:int = int(size[1]/2)
    purple_color_rbga:tuple = Color.VIOLET
    pygame.draw.rect(
        texture_missing_surface, purple_color_rbga, pygame.Rect(half_width, 0, texture_missing_surface.get_width()-half_width, half_height)
        )
    pygame.draw.rect(
        texture_missing_surface, purple_color_rbga, pygame.Rect(0, half_height, half_width, texture_missing_surface.get_height()-half_height)
        )
    return texture_missing_surface

#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def display_in_center(
    item1:ImageSurface, item2:ImageSurface, x:number, y:number, screen:ImageSurface, off_set_x:number = 0, off_set_y:number = 0
    ) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+off_set_x,y+added_y+off_set_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def display_within_center(
    item1:ImageSurface, item2:ImageSurface, x:number, y:number, screen:ImageSurface, off_set_x:number = 0, off_set_y:number = 0
    ) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+off_set_x,y+off_set_y))
    screen.blit(item1,(x+added_x+off_set_x,y+added_y+off_set_y))

#是否触碰pygame类
def is_hover_pygame_object(imgObject:object, objectPos:pos_liked=Origin, off_set_x:number=0, off_set_y:number=0) -> bool:
    mouse_x,mouse_y = pygame.mouse.get_pos()
    #如果是pygame的Surface类
    if isinstance(imgObject, ImageSurface):
        return True if 0 < mouse_x-off_set_x-objectPos[0] < imgObject.get_width() and 0 < mouse_y-off_set_y-objectPos[1] < imgObject.get_height()\
            else False
    #如果是Rect类
    elif isinstance(imgObject,pygame.Rect):
        return True if 0 < mouse_x-off_set_x-imgObject.x < imgObject.width and 0 < mouse_y-off_set_y-imgObject.y < imgObject.height\
            else False
    else:
        EXCEPTION.fatal("Unable to check current object: {0} (type:{1})".format(imgObject,type(imgObject)))