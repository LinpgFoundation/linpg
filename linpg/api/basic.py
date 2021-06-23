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
def is_using_pygame() -> bool: return True if not _LIBRARY_INDICATOR else False
#是否正在使用pyglet库
def is_using_pyglet() -> bool: return True if _LIBRARY_INDICATOR is True else False

#int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]

"""指向pygame事件的指针"""
#鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
#手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN

#字典合并
def merge_dict(dict1:dict, dict2:dict) -> dict: return {**dict1, **dict2}

#随机数
def get_random_int(start:int, end:int) -> int: return random.randint(start, end)

#转换坐标
def convert_pos(pos:any) -> tuple:
    #检测坐标
    if isinstance(pos, (list, tuple, numpy.ndarray)):
        return pos[0],pos[1]
    elif isinstance(pos, dict):
        return pos["x"],pos["y"]
    else:
        try:
            return pos.x,pos.y
        except Exception:
            throw_exception("error", 'Cannot convert position "{}".'.format(pos))

#判断2个坐标是否相同
def is_same_pos(pos1:any, pos2:any) -> bool: return convert_pos(pos1) == convert_pos(pos2)

#相加2个坐标
def add_pos(*positions:any) -> tuple:
    x = 0
    y = 0
    for pos in positions:
        convetred_pos = convert_pos(pos)
        x += convetred_pos[0]
        y += convetred_pos[1]
    return x,y

#相减2个坐标
def subtract_pos(position:any, *positions:any) -> tuple:
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
def keep_in_range(number:Union[int,float], min_value:Union[int,float], max_value:Union[int,float]) -> Union[int,float]:
    return max(min(max_value, number), min_value)

#转换string形式的百分比
def convert_percentage(percentage:Union[str,float]) -> float:
    if isinstance(percentage, str) and percentage.endswith("%"):
        return float(percentage.strip('%'))/100
    elif isinstance(percentage, float):
        return percentage
    else:
        throw_exception("error", '"{}" is not a valid percentage that can be converted'.format(percentage))

#获取帧数控制器
def get_clock() -> pygame.time.Clock: return pygame.time.Clock()
