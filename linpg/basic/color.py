from PIL import ImageColor  # type: ignore

# 加载颜色字典
from pygame.colordict import THECOLORS
from .key import *

# 颜色管理
class ColorManager:

    """常用颜色"""

    # 白色
    __WHITE: tuple[int, int, int, int] = (255, 255, 255, 255)
    # 灰色
    __GRAY: tuple[int, int, int, int] = (105, 105, 105, 255)
    # 淡灰色
    __LIGHT_GRAY: tuple[int, int, int, int] = (83, 83, 83, 255)
    # 黑色
    __BLACK: tuple[int, int, int, int] = (0, 0, 0, 255)
    # 红色
    __RED: tuple[int, int, int, int] = (255, 0, 0, 255)
    # 橙色
    __ORANGE: tuple[int, int, int, int] = (255, 127, 0, 255)
    # 黄色
    __YELLOW: tuple[int, int, int, int] = (255, 255, 0, 255)
    # 绿色
    __GREEN: tuple[int, int, int, int] = (0, 255, 0, 255)
    # 蓝色
    __BLUE: tuple[int, int, int, int] = (0, 0, 255, 255)
    # 靛蓝色
    __INDIGO: tuple[int, int, int, int] = (75, 0, 130, 255)
    # 紫色
    __VIOLET: tuple[int, int, int, int] = (148, 0, 211, 255)
    # 透明
    __TRANSPARENT: tuple[int, int, int, int] = (0, 0, 0, 0)

    # 白色
    @classmethod
    @property
    def WHITE(cls) -> tuple[int, int, int, int]:
        return cls.__WHITE

    # 灰色
    @classmethod
    @property
    def GRAY(cls) -> tuple[int, int, int, int]:
        return cls.__GRAY

    # 淡灰色
    @classmethod
    @property
    def LIGHT_GRAY(cls) -> tuple[int, int, int, int]:
        return cls.__LIGHT_GRAY

    # 黑色
    @classmethod
    @property
    def BLACK(cls) -> tuple[int, int, int, int]:
        return cls.__BLACK

    # 红色
    @classmethod
    @property
    def RED(cls) -> tuple[int, int, int, int]:
        return cls.__RED

    # 橙色
    @classmethod
    @property
    def ORANGE(cls) -> tuple[int, int, int, int]:
        return cls.__ORANGE

    # 黄色
    @classmethod
    @property
    def YELLOW(cls) -> tuple[int, int, int, int]:
        return cls.__YELLOW

    # 绿色
    @classmethod
    @property
    def GREEN(cls) -> tuple[int, int, int, int]:
        return cls.__GREEN

    # 蓝色
    @classmethod
    @property
    def BLUE(cls) -> tuple[int, int, int, int]:
        return cls.__BLUE

    # 靛蓝色
    @classmethod
    @property
    def INDIGO(cls) -> tuple[int, int, int, int]:
        return cls.__INDIGO

    # 紫色
    @classmethod
    @property
    def VIOLET(cls) -> tuple[int, int, int, int]:
        return cls.__VIOLET

    # 透明
    @classmethod
    @property
    def TRANSPARENT(cls) -> tuple[int, int, int, int]:
        return cls.__TRANSPARENT

    # 转换至rgba颜色tuple
    @staticmethod
    def __to_rgba_color(color: tuple) -> tuple[int, int, int, int]:
        _r: int = int(color[0])
        _g: int = int(color[1])
        _b: int = int(color[2])
        _a: int = int(color[3]) if len(color) >= 4 else 255
        return _r, _g, _b, _a

    """获取颜色"""
    # 给定一个颜色的名字或序号，返回对应的RGB列表
    @classmethod
    def get(cls, color: color_liked) -> tuple[int, int, int, int]:
        if isinstance(color, str):
            if color.startswith("#"):
                return cls.__to_rgba_color(ImageColor.getrgb(color))
            else:
                try:
                    return cls.__to_rgba_color(tuple(THECOLORS[color]))
                except KeyError:
                    EXCEPTION.fatal('The color "{}" is currently not available!'.format(color))
        else:
            try:
                return cls.__to_rgba_color(tuple(color))
            except Exception:
                EXCEPTION.fatal(
                    "The color has to be a string, tuple or list, and {0} (type:{1}) is not acceptable!".format(
                        color, type(color)
                    )
                )


Colors: ColorManager = ColorManager()
