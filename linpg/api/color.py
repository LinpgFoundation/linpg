# cython: language_level=3
from PIL import ImageColor
from pygame.colordict import THECOLORS
from .key import *

class ColorManager:
    def __init__(self) -> None:
        #白色
        self.__WHITE: tuple = (255, 255, 255, 255)
        #灰色
        self.__GRAY: tuple = (105, 105, 105, 255)
        #黑色
        self.__BLACK: tuple = (0, 0, 0, 255)
        #红色
        self.__RED :tuple = (255, 0, 0, 255)
    """常用颜色"""
    @property
    def WHITE(self) -> tuple: return self.__WHITE
    @property
    def GRAY(self) -> tuple: return self.__GRAY
    @property
    def BLACK(self) -> tuple: return self.__BLACK
    @property
    def RED(self) -> tuple: return self.__RED
    """获取颜色"""
    #给定一个颜色的名字或序号，返回对应的RGB列表
    def get(self, color:Union[str, tuple, list]) -> tuple:
        if isinstance(color, str):
            if color == "gray" or color == "grey" or color == "disable":
                return self.__GRAY
            elif color == "white" or color == "enable":
                return self.__WHITE
            elif color[0] == "#":
                return ImageColor.getrgb(color)
            else:
                try:
                    return tuple(THECOLORS[color])
                except KeyError:
                    throw_exception("error", 'The color "{}" is currently not available!'.format(color))
        elif isinstance(color, (tuple, list)):
            return tuple(color)
        else:
            throw_exception(
                "error",
                "The color has to be a string, tuple or list! As a result, {0} (type:{1}) is not acceptable!".format(color, type(color))
                )

Color: ColorManager = ColorManager()

"""即将弃置"""
#给定一个颜色的名字，返回对应的RGB列表
def get_color_rbga(color:Union[str, tuple, list]) -> tuple: return Color.get(color)