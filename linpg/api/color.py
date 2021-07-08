# cython: language_level=3
from PIL import ImageColor
from .key import *

#加载颜色字典
THECOLORS:dict
if is_using_pygame():
    try:
        from pygame.colordict import THECOLORS
    except Exception:
        THECOLORS = {}
else:
    THECOLORS = {}

#颜色管理
class ColorManager:
    def __init__(self) -> None:
        # 白色
        self.__WHITE: tuple[int] = (255, 255, 255, 255)
        # 灰色
        self.__GRAY: tuple[int] = (105, 105, 105, 255)
        # 黑色
        self.__BLACK: tuple[int] = (0, 0, 0, 255)
        # 红色
        self.__RED: tuple[int] = (255, 0, 0, 255)
        # 橙色
        self.__ORANGE: tuple[int] = (255, 127, 0, 255)
        # 黄色
        self.__YELLOW: tuple[int] = (255, 255, 0, 255)
        # 绿色
        self.__GREEN: tuple[int] = (0, 255, 0, 255)
        # 蓝色
        self.__BLUE: tuple[int] = (0, 0, 255, 255)
        # 靛蓝色
        self.__INDIGO: tuple[int] = (75, 0, 130, 255)
        # 紫色
        self.__VIOLET: tuple[int] = (148, 0, 211, 255)
    """常用颜色"""
    @property
    def WHITE(self) -> tuple[int]: return self.__WHITE
    @property
    def GRAY(self) -> tuple[int]: return self.__GRAY
    @property
    def BLACK(self) -> tuple[int]: return self.__BLACK
    @property
    def RED(self) -> tuple[int]: return self.__RED
    @property
    def ORANGE(self) -> tuple[int]: return self.__ORANGE
    @property
    def YELLOW(self) -> tuple[int]: return self.__YELLOW
    @property
    def GREEN(self) -> tuple[int]: return self.__GREEN
    @property
    def BLUE(self) -> tuple[int]: return self.__BLUE
    @property
    def INDIGO(self) -> tuple[int]: return self.__INDIGO
    @property
    def VIOLET(self) -> tuple[int]: return self.__VIOLET
    """获取颜色"""
    #给定一个颜色的名字或序号，返回对应的RGB列表
    def get(self, color:color_liked) -> tuple[int]:
        if isinstance(color, str):
            if color[0] == "#":
                return ImageColor.getrgb(color)
            elif color == "gray" or color == "grey":
                return self.__GRAY
            else:
                try:
                    return tuple(THECOLORS[color])
                except KeyError:
                    EXCEPTION.fatal('The color "{}" is currently not available!'.format(color))
        elif isinstance(color, (tuple, list)):
            return tuple(color)
        else:
            EXCEPTION.fatal("The color has to be a string, tuple or list, and {0} (type:{1}) is not acceptable!".format(color, type(color)))

Color: ColorManager = ColorManager()
