from PIL import ImageColor
from .key import *

# 加载颜色字典
THECOLORS: dict
if is_using_pygame():
    try:
        from pygame.colordict import THECOLORS
    except Exception:
        THECOLORS = {}
else:
    THECOLORS = {}


# 颜色管理
class ColorManager:

    """常用颜色"""

    # 白色
    __WHITE: tuple[int] = (255, 255, 255, 255)
    # 灰色
    __GRAY: tuple[int] = (105, 105, 105, 255)
    # 黑色
    __BLACK: tuple[int] = (0, 0, 0, 255)
    # 红色
    __RED: tuple[int] = (255, 0, 0, 255)
    # 橙色
    __ORANGE: tuple[int] = (255, 127, 0, 255)
    # 黄色
    __YELLOW: tuple[int] = (255, 255, 0, 255)
    # 绿色
    __GREEN: tuple[int] = (0, 255, 0, 255)
    # 蓝色
    __BLUE: tuple[int] = (0, 0, 255, 255)
    # 靛蓝色
    __INDIGO: tuple[int] = (75, 0, 130, 255)
    # 紫色
    __VIOLET: tuple[int] = (148, 0, 211, 255)
    # 透明
    __TRANSPARENT: tuple[int] = (0, 0, 0, 0)

    # 白色
    @property
    def WHITE(self) -> tuple[int]:
        return self.__WHITE

    # 灰色
    @property
    def GRAY(self) -> tuple[int]:
        return self.__GRAY

    # 黑色
    @property
    def BLACK(self) -> tuple[int]:
        return self.__BLACK

    # 红色
    @property
    def RED(self) -> tuple[int]:
        return self.__RED

    # 橙色
    @property
    def ORANGE(self) -> tuple[int]:
        return self.__ORANGE

    # 黄色
    @property
    def YELLOW(self) -> tuple[int]:
        return self.__YELLOW

    # 绿色
    @property
    def GREEN(self) -> tuple[int]:
        return self.__GREEN

    # 蓝色
    @property
    def BLUE(self) -> tuple[int]:
        return self.__BLUE

    # 靛蓝色
    @property
    def INDIGO(self) -> tuple[int]:
        return self.__INDIGO

    # 紫色
    @property
    def VIOLET(self) -> tuple[int]:
        return self.__VIOLET

    # 透明
    @property
    def TRANSPARENT(self) -> tuple[int]:
        return self.__TRANSPARENT

    """获取颜色"""
    # 给定一个颜色的名字或序号，返回对应的RGB列表
    def get(self, color: color_liked) -> tuple[int]:
        if isinstance(color, str):
            if color.startswith("#"):
                return ImageColor.getrgb(color)
            elif color == "gray" or color == "grey":
                return self.__GRAY
            else:
                try:
                    return tuple(THECOLORS[color])
                except KeyError:
                    EXCEPTION.fatal('The color "{}" is currently not available!'.format(color))
        elif isinstance(color, Iterable):
            return tuple(color)
        else:
            EXCEPTION.fatal(
                "The color has to be a string, tuple or list, and {0} (type:{1}) is not acceptable!".format(
                    color, type(color)
                )
            )


Color: ColorManager = ColorManager()
