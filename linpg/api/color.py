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

"""常用颜色"""
# 白色
_WHITE: tuple[int] = (255, 255, 255, 255)
# 灰色
_GRAY: tuple[int] = (105, 105, 105, 255)
# 黑色
_BLACK: tuple[int] = (0, 0, 0, 255)
# 红色
_RED: tuple[int] = (255, 0, 0, 255)
# 橙色
_ORANGE: tuple[int] = (255, 127, 0, 255)
# 黄色
_YELLOW: tuple[int] = (255, 255, 0, 255)
# 绿色
_GREEN: tuple[int] = (0, 255, 0, 255)
# 蓝色
_BLUE: tuple[int] = (0, 0, 255, 255)
# 靛蓝色
_INDIGO: tuple[int] = (75, 0, 130, 255)
# 紫色
_VIOLET: tuple[int] = (148, 0, 211, 255)

# 颜色管理
class ColorManager:
    # 白色
    @property
    def WHITE(self) -> tuple[int]:
        return _WHITE

    # 灰色
    @property
    def GRAY(self) -> tuple[int]:
        return _GRAY

    # 黑色
    @property
    def BLACK(self) -> tuple[int]:
        return _BLACK

    # 红色
    @property
    def RED(self) -> tuple[int]:
        return _RED

    # 橙色
    @property
    def ORANGE(self) -> tuple[int]:
        return _ORANGE

    # 黄色
    @property
    def YELLOW(self) -> tuple[int]:
        return _YELLOW

    # 绿色
    @property
    def GREEN(self) -> tuple[int]:
        return _GREEN

    # 蓝色
    @property
    def BLUE(self) -> tuple[int]:
        return _BLUE

    # 靛蓝色
    @property
    def INDIGO(self) -> tuple[int]:
        return _INDIGO

    # 紫色
    @property
    def VIOLET(self) -> tuple[int]:
        return _VIOLET

    """获取颜色"""
    # 给定一个颜色的名字或序号，返回对应的RGB列表
    @staticmethod
    def get(color: color_liked) -> tuple[int]:
        if isinstance(color, str):
            if color.startswith("#"):
                return ImageColor.getrgb(color)
            elif color == "gray" or color == "grey":
                return _GRAY
            else:
                try:
                    return tuple(THECOLORS[color])
                except KeyError:
                    EXCEPTION.fatal(
                        'The color "{}" is currently not available!'.format(color)
                    )
        elif isinstance(color, (tuple, list)):
            return tuple(color)
        else:
            EXCEPTION.fatal(
                "The color has to be a string, tuple or list, and {0} (type:{1}) is not acceptable!".format(
                    color, type(color)
                )
            )


Color: ColorManager = ColorManager()
