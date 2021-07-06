# cython: language_level=3
from PIL import ImageColor
from .key import *
if is_using_pygame():
    try:
        from pygame.colordict import THECOLORS
    except Exception:
        THECOLORS = {}
else:
    THECOLORS = {}

ColorType = tuple[int]

class ColorManager:
    def __init__(self) -> None:
        # 白色
        self.__WHITE: ColorType = (255, 255, 255, 255)
        # 灰色
        self.__GRAY: ColorType = (105, 105, 105, 255)
        # 黑色
        self.__BLACK: ColorType = (0, 0, 0, 255)
        # 红色
        self.__RED: ColorType = (255, 0, 0, 255)
        # 橙色
        self.__ORANGE: ColorType = (255, 127, 0, 255)
        # 黄色
        self.__YELLOW: ColorType = (255, 255, 0, 255)
        # 绿色
        self.__GREEN: ColorType = (0, 255, 0, 255)
        # 蓝色
        self.__BLUE: ColorType = (0, 0, 255, 255)
        # 靛蓝色
        self.__INDIGO: ColorType = (75, 0, 130, 255)
        # 紫色
        self.__VIOLET: ColorType = (148, 0, 211, 255)
    """常用颜色"""
    @property
    def WHITE(self) -> ColorType: return self.__WHITE
    @property
    def GRAY(self) -> ColorType: return self.__GRAY
    @property
    def BLACK(self) -> ColorType: return self.__BLACK
    @property
    def RED(self) -> ColorType: return self.__RED
    @property
    def ORANGE(self) -> ColorType: return self.__ORANGE
    @property
    def YELLOW(self) -> ColorType: return self.__YELLOW
    @property
    def GREEN(self) -> ColorType: return self.__GREEN
    @property
    def BLUE(self) -> ColorType: return self.__BLUE
    @property
    def INDIGO(self) -> ColorType: return self.__INDIGO
    @property
    def VIOLET(self) -> ColorType: return self.__VIOLET
    """获取颜色"""
    #给定一个颜色的名字或序号，返回对应的RGB列表
    def get(self, color:color_liked) -> ColorType:
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
