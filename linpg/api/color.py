# cython: language_level=3
if is_using_pygame():
    try:
        from pygame.colordict import THECOLORS
    except Exception:
        THECOLORS = {}
else:
    THECOLORS = {}
from PIL import ImageColor
from .key import *

class ColorManager:
    def __init__(self) -> None:
        # 白色
        self.__WHITE: tuple = (255, 255, 255, 255)
        # 灰色
        self.__GRAY: tuple = (105, 105, 105, 255)
        # 黑色
        self.__BLACK: tuple = (0, 0, 0, 255)
        # 红色
        self.__RED: tuple = (255, 0, 0, 255)
        # 橙色
        self.__ORANGE: tuple = (255, 127, 0, 255)
        # 黄色
        self.__YELLOW: tuple = (255, 255, 0, 255)
        # 绿色
        self.__GREEN: tuple = (0, 255, 0, 255)
        # 蓝色
        self.__BLUE: tuple = (0, 0, 255, 255)
        # 靛蓝色
        self.__INDIGO: tuple = (75, 0, 130, 255)
        # 紫色
        self.__VIOLET: tuple = (148, 0, 211, 255)
    """常用颜色"""
    @property
    def WHITE(self) -> tuple: return self.__WHITE
    @property
    def GRAY(self) -> tuple: return self.__GRAY
    @property
    def BLACK(self) -> tuple: return self.__BLACK
    @property
    def RED(self) -> tuple: return self.__RED
    @property
    def ORANGE(self) -> tuple: return self.__ORANGE
    @property
    def YELLOW(self) -> tuple: return self.__YELLOW
    @property
    def GREEN(self) -> tuple: return self.__GREEN
    @property
    def BLUE(self) -> tuple: return self.__BLUE
    @property
    def INDIGO(self) -> tuple: return self.__INDIGO
    @property
    def VIOLET(self) -> tuple: return self.__VIOLET
    """获取颜色"""
    #给定一个颜色的名字或序号，返回对应的RGB列表
    def get(self, color:Union[str, tuple, list]) -> tuple:
        if isinstance(color, str):
            if color[0] == "#":
                return ImageColor.getrgb(color)
            elif color == "gray" or color == "grey":
                return self.__GRAY
            else:
                try:
                    return tuple(THECOLORS[color])
                except KeyError:
                    throw_exception("error", 'The color "{}" is currently not available!'.format(color))
        elif isinstance(color, (tuple, list)):
            return tuple(color)
        else:
            throw_exception("error", "The color has to be a string, tuple or list, and {0} (type:{1}) is not acceptable!".format(color, type(color)))

Color: ColorManager = ColorManager()

"""即将弃置"""
#给定一个颜色的名字，返回对应的RGB列表
def get_color_rbga(color:Union[str, tuple, list]) -> tuple: return Color.get(color)