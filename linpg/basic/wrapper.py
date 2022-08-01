from random import randint as RANDINT

# 粘贴板内容模块
from tkinter import Tk

# 导入pygame组件
import pygame

# 加载颜色模块
from PIL import ImageColor  # type: ignore
from pygame.colordict import THECOLORS

from .coordinates import *

# 初始化pygame
pygame.init()

"""linpg自带属性"""
# int_f指参数推荐输入int, 但一开始接受时可以为float，但最后会转换为int
int_f = Union[int, float]
# number，即数字，建议int但接受float
number = Union[int, float]
# 颜色类
color_liked = Union[Sequence[int], str]
# 图形类
ImageSurface = pygame.Surface
PoI = Union[str, pygame.Surface]
# 事件 type alias
PG_Event = pygame.event.Event
PG_TUPLE = Union[tuple[int, int, int, int], tuple[tuple[int, int], tuple[int, int]]]

"""指向pygame事件的指针"""
# 鼠标
MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
# 手柄
JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN


# 与数字有关的常用方法
class Numbers:

    # 随机数
    @staticmethod
    def get_random_int(start: int, end: int) -> int:
        return RANDINT(start, end)

    # 检测int数值是否越界
    @staticmethod
    def keep_int_in_range(_number: int, min_value: int, max_value: int) -> int:
        return max(min(max_value, _number), min_value)

    # 检测int或float数值是否越界
    @staticmethod
    def keep_number_in_range(_number: number, min_value: number, max_value: number) -> number:
        return max(min(max_value, _number), min_value)

    # 转换string形式的百分比
    @staticmethod
    def convert_percentage(percentage: Union[str, float, int]) -> float:
        if isinstance(percentage, str) and percentage.endswith("%"):
            return float(percentage.strip("%")) / 100
        elif isinstance(percentage, int):
            return float(percentage)
        elif isinstance(percentage, float):
            return percentage
        else:
            EXCEPTION.fatal('"{}" is not a valid percentage that can be converted'.format(percentage))


# 颜色管理
class Colors:

    """常用颜色"""

    # 白色
    WHITE: Final[tuple[int, int, int, int]] = (255, 255, 255, 255)
    # 灰色
    GRAY: Final[tuple[int, int, int, int]] = (105, 105, 105, 255)
    # 淡灰色
    LIGHT_GRAY: Final[tuple[int, int, int, int]] = (83, 83, 83, 255)
    # 黑色
    BLACK: Final[tuple[int, int, int, int]] = (0, 0, 0, 255)
    # 红色
    RED: Final[tuple[int, int, int, int]] = (255, 0, 0, 255)
    # 橙色
    ORANGE: Final[tuple[int, int, int, int]] = (255, 127, 0, 255)
    # 黄色
    YELLOW: Final[tuple[int, int, int, int]] = (255, 255, 0, 255)
    # 绿色
    GREEN: Final[tuple[int, int, int, int]] = (0, 255, 0, 255)
    # 蓝色
    BLUE: Final[tuple[int, int, int, int]] = (0, 0, 255, 255)
    # 靛蓝色
    INDIGO: Final[tuple[int, int, int, int]] = (75, 0, 130, 255)
    # 紫色
    VIOLET: Final[tuple[int, int, int, int]] = (148, 0, 211, 255)
    # 透明
    TRANSPARENT: Final[tuple[int, int, int, int]] = (0, 0, 0, 0)

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
                _the_color = THECOLORS.get(color)
                if isinstance(_the_color, Sequence):
                    return cls.__to_rgba_color(tuple(_the_color))
                else:
                    EXCEPTION.fatal('The color "{}" is currently not available!'.format(color))
        else:
            return cls.__to_rgba_color(tuple(color))


class Keys:

    # 按键常量
    DOWN: Final[int] = pygame.KEYDOWN
    UP: Final[int] = pygame.KEYUP
    ESCAPE: Final[int] = pygame.K_ESCAPE
    SPACE: Final[int] = pygame.K_SPACE
    BACKSPACE: Final[int] = pygame.K_BACKSPACE
    DELETE: Final[int] = pygame.K_DELETE
    LEFT_CTRL: Final[int] = pygame.K_LCTRL
    ARROW_UP: Final[int] = pygame.K_UP
    ARROW_DOWN: Final[int] = pygame.K_DOWN
    ARROW_LEFT: Final[int] = pygame.K_LEFT
    ARROW_RIGHT: Final[int] = pygame.K_RIGHT
    RETURN: Final[int] = pygame.K_RETURN
    BACKQUOTE: Final[int] = pygame.K_BACKQUOTE
    F3: Final[int] = pygame.K_F3

    __root: Final[Tk] = Tk()
    __root.withdraw()

    # key是否被按下
    @classmethod
    def get_pressed(cls, key_name: strint) -> bool:
        return pygame.key.get_pressed()[cls.get_key_code(key_name) if isinstance(key_name, str) else key_name]

    # 获取key的代号
    @staticmethod
    def get_key_code(key_name: str) -> int:
        return pygame.key.key_code(key_name)

    # 获取粘贴板内容
    @classmethod
    def get_clipboard(cls) -> str:
        return cls.__root.clipboard_get()


class Draw:

    # 根据给与的rect画出轮廓
    @staticmethod
    def rect(_surface: ImageSurface, color: tuple[int, int, int, int], rect: PG_TUPLE, thickness: int = 0) -> None:
        pygame.draw.rect(_surface, color, rect, thickness)

    # 根据给与的中心点画出一个圆
    @staticmethod
    def circle(_surface: ImageSurface, color: tuple[int, int, int, int], center_pos: tuple[int, int], radius: int, thickness: int = 0) -> None:
        pygame.draw.circle(_surface, color, center_pos, radius, thickness)

    # 画抗锯齿线条
    @staticmethod
    def aaline(_surface: ImageSurface, color: tuple[int, int, int, int], start_pos: tuple[int, int], end_pos: tuple[int, int], blend: int = 1) -> None:
        pygame.draw.aaline(_surface, color, start_pos, end_pos, blend)

    # 画多边形
    @staticmethod
    def polygon(_surface: ImageSurface, _color: tuple[int, int, int, int], _points: tuple[tuple[int, int], ...], _width: int = 0) -> None:
        pygame.draw.polygon(_surface, _color, _points, _width)


class Surfaces:

    # null图层占位符
    NULL: Final[ImageSurface] = pygame.surface.Surface((0, 0))

    # 获取Surface
    @staticmethod
    def new(size: tuple[int, int], surface_flags: int = -1) -> ImageSurface:
        return pygame.Surface(size, flags=surface_flags) if surface_flags >= 0 else pygame.Surface(size).convert()

    # 获取透明的Surface
    @staticmethod
    def transparent(size: tuple[int, int]) -> ImageSurface:
        return pygame.Surface(size, flags=pygame.SRCALPHA).convert_alpha()

    # 获取一个带颜色的Surface
    @staticmethod
    def colored(size: tuple[int, int], color: color_liked) -> ImageSurface:
        surface_t: ImageSurface = pygame.Surface(size).convert()
        surface_t.fill(Colors.get(color))
        return surface_t

    # 根据array生成Surface
    @classmethod
    def from_array(cls, surface_array: numpy.ndarray, swap_axes: bool = True) -> ImageSurface:
        if swap_axes is True:
            surface_array = surface_array.swapaxes(0, 1)
        if surface_array.shape[2] < 4:
            return pygame.surfarray.make_surface(surface_array).convert()
        else:
            # by llindstrom
            _shape: tuple = surface_array.shape
            _surface: ImageSurface = cls.transparent((int(_shape[0]), int(_shape[1])))
            # Copy the rgb part of array to the new _surface.
            pygame.pixelcopy.array_to_surface(_surface, surface_array[:, :, 0:3])
            # Copy the alpha part of array to the _surface using a pixels-alpha
            # view of the _surface.
            surface_alpha = numpy.array(_surface.get_view("A"), copy=False)
            surface_alpha[:, :] = surface_array[:, :, 3]
            return _surface

    # 根据Surface生成array
    @staticmethod
    def to_array(_surface: ImageSurface, with_alpha: bool = True, swap_axes: bool = True) -> numpy.ndarray:
        surface_3d_rgb_array: numpy.ndarray = pygame.surfarray.array3d(_surface)
        if with_alpha is True:
            surface_3d_rgb_array = numpy.dstack((surface_3d_rgb_array, pygame.surfarray.array_alpha(_surface)))
        return surface_3d_rgb_array.swapaxes(0, 1) if swap_axes is True else surface_3d_rgb_array

    # 获取材质缺失的临时警示材质
    @classmethod
    def texture_is_missing(cls, size: tuple[int, int]) -> ImageSurface:
        texture_missing_surface: ImageSurface = cls.colored(size, Colors.BLACK)
        half_width: int = size[0] // 2
        half_height: int = size[1] // 2
        pygame.draw.rect(texture_missing_surface, Colors.VIOLET, pygame.Rect(half_width, 0, texture_missing_surface.get_width() - half_width, half_height))
        pygame.draw.rect(texture_missing_surface, Colors.VIOLET, pygame.Rect(0, half_height, half_width, texture_missing_surface.get_height() - half_height))
        return texture_missing_surface

    # 检测图层是否是任何形式的null
    @classmethod
    def is_not_null(cls, _surface: Optional[ImageSurface]) -> bool:
        return _surface is not None and _surface is not cls.NULL
