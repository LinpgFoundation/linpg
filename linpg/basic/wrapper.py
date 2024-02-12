import enum
from random import randint as RANDINT

# 粘贴板内容模块
from tkinter import Tk

# 导入pygame组件
import pygame
import pygame.gfxdraw

# 加载颜色模块
from PIL import Image as PILImage
from PIL import ImageColor as PILImageColor
from PIL import ImageFilter as PILImageFilter

from .coordinates import *

# 初始化pygame
pygame.init()

"""linpg自带属性"""
# 颜色类
color_liked = Sequence[int] | str
# 图形类
ImageSurface = pygame.Surface
# path or pygame.Surface
PoI = str | pygame.Surface
# 事件 type alias
PG_Event = pygame.event.Event


# 图形类
class UniversalImageSurface:
    def __init__(self, obj: pygame.Surface, file_path: str = "") -> None:
        self._wrapped_obj: pygame.Surface = obj
        self.__path: Final[str] = file_path

    def __getattr__(self, attr: str) -> Any:
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._wrapped_obj, attr)

    @property
    def path(self) -> str:
        return self.__path


# 图像库数据
class GraphicLibrary:
    PYGAME: Final[int] = 0
    PYGAME_CE: Final[int] = 1

    # 是否正在使用pygame_ce
    __IS_CE: Final[bool] = getattr(pygame, "IS_CE", False) is not False

    @classmethod
    def is_using_pygame(cls) -> bool:
        return not cls.__IS_CE

    @classmethod
    def is_using_pygame_ce(cls) -> bool:
        return cls.__IS_CE

    @classmethod
    def get_name(cls) -> str:
        return "Pygame-ce" if cls.__IS_CE else "Pygame"


# 指向pygame事件的指针
@enum.verify(enum.UNIQUE)
class Events(enum.IntEnum):
    # 鼠标
    MOUSE_BUTTON_DOWN = pygame.MOUSEBUTTONDOWN
    MOUSE_BUTTON_UP = pygame.MOUSEBUTTONUP
    # 手柄
    JOYSTICK_BUTTON_DOWN = pygame.JOYBUTTONDOWN
    JOYSTICK_BUTTON_UP = pygame.JOYBUTTONUP
    # 键盘
    KEY_DOWN = pygame.KEYDOWN
    KEY_UP = pygame.KEYUP


# 表示方向的enum
@enum.verify(enum.UNIQUE)
class Axis(enum.IntEnum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


# 表示位置
@enum.verify(enum.UNIQUE)
class Locations(enum.IntEnum):
    BEGINNING = enum.auto()
    END = enum.auto()
    MIDDLE = enum.auto()
    EVERYWHERE = enum.auto()


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
    def convert_percentage(percentage: str | float | int) -> float:
        if isinstance(percentage, str) and percentage.endswith("%"):
            return float(percentage.strip("%")) / 100
        elif isinstance(percentage, int):
            return float(percentage)
        elif isinstance(percentage, float):
            return percentage
        else:
            EXCEPTION.fatal(f'"{percentage}" is not a valid percentage that can be converted')


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
    # 淡蓝色
    LIGHT_SKY_BLUE: Final[tuple[int, int, int, int]] = (135, 206, 250, 255)
    # 深蓝色
    DODGER_BLUE: Final[tuple[int, int, int, int]] = (30, 144, 255, 255)

    # 转换至rgba颜色tuple
    @staticmethod
    def __to_rgba_color(color: Sequence) -> tuple[int, int, int, int]:
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
            try:
                return cls.__to_rgba_color(PILImageColor.getrgb(color))
            except ValueError:
                EXCEPTION.fatal(f'The color "{color}" is currently not available!')
        else:
            return cls.__to_rgba_color(color)


class Keys:
    # 按键常量
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
    def get_pressed(cls, key_name: str | int) -> bool:
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
    def rect(
        _surface: ImageSurface,
        color: tuple[int, int, int, int],
        rect: tuple[int, int, int, int] | tuple[tuple[int, int], tuple[int, int]],
        thickness: int = 0,
        radius: int = -1,
    ) -> None:
        if thickness <= 0 and radius <= 0:
            pygame.gfxdraw.box(_surface, rect, color)
        else:
            pygame.draw.rect(_surface, color, rect, thickness, radius)

    # 根据给与的中心点画出一个圆
    @staticmethod
    def circle(_surface: ImageSurface, color: tuple[int, int, int, int], center_pos: tuple[int, int], radius: int, thickness: int = 0) -> None:
        if thickness <= 0:
            pygame.gfxdraw.filled_circle(_surface, center_pos[0], center_pos[1], radius, color)
        else:
            pygame.draw.circle(_surface, color, center_pos, radius, thickness)

    # 根据给与的中心点画出一个椭圆
    @staticmethod
    def ellipse(_surface: ImageSurface, color: tuple[int, int, int, int], center_pos: tuple[int, int], radius: tuple[int, int], thickness: int = 0) -> None:
        if thickness <= 0:
            pygame.gfxdraw.filled_ellipse(_surface, center_pos[0], center_pos[1], radius[0], radius[1], color)
        else:
            pygame.draw.ellipse(_surface, color, ((center_pos[0] - radius[0], center_pos[1] - radius[1]), (radius[0] * 2, radius[1] * 2)), thickness)

    # 画一条抗锯齿线
    @staticmethod
    def aaline(_surface: ImageSurface, color: tuple[int, int, int, int], start_pos: tuple[int, int], end_pos: tuple[int, int], blend: int = 1) -> None:
        if start_pos[0] == end_pos[0]:
            pygame.gfxdraw.vline(_surface, start_pos[0], start_pos[1], end_pos[1], color)
        elif start_pos[1] == end_pos[1]:
            pygame.gfxdraw.hline(_surface, start_pos[0], end_pos[0], end_pos[1], color)
        else:
            pygame.draw.aaline(_surface, color, start_pos, end_pos, blend)

    # 画一条线
    @staticmethod
    def line(_surface: ImageSurface, color: tuple[int, int, int, int], start_pos: tuple[int, int], end_pos: tuple[int, int], width: int = 1) -> None:
        if width <= 1:
            pygame.gfxdraw.line(_surface, start_pos[0], start_pos[1], end_pos[0], end_pos[1], color)
        else:
            pygame.draw.line(_surface, color, start_pos, end_pos, width)

    # 画多边形
    @staticmethod
    def polygon(_surface: ImageSurface, _color: tuple[int, int, int, int], _points: tuple[tuple[int, int], ...], thickness: int = 0) -> None:
        if thickness <= 0:
            pygame.gfxdraw.filled_polygon(_surface, _points, _color)
        else:
            pygame.draw.polygon(_surface, _color, _points, thickness)


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
        Draw.rect(texture_missing_surface, Colors.VIOLET, (half_width, 0, texture_missing_surface.get_width() - half_width, half_height))
        Draw.rect(texture_missing_surface, Colors.VIOLET, (0, half_height, half_width, texture_missing_surface.get_height() - half_height))
        return texture_missing_surface

    # 检测图层是否是任何形式的null
    @classmethod
    def is_not_null(cls, _surface: ImageSurface | None) -> bool:
        return _surface is not None and _surface is not cls.NULL


# 滤镜效果
class Filters:
    # blur a surface using gaussian blur 毛玻璃效果
    @staticmethod
    def gaussian_blur(_surface: ImageSurface, radius: int = 10, repeat_edge_pixels: bool = True, dest_surface: ImageSurface | None = None) -> ImageSurface:
        # if is using pygame-ce
        if GraphicLibrary.is_using_pygame_ce():
            return pygame.transform.gaussian_blur(
                _surface, radius, repeat_edge_pixels, dest_surface if dest_surface is not None else Surfaces.new(_surface.get_size())
            )
        # if is using pygame not ce, then use pillow GaussianBlur instead
        new_surf: ImageSurface = Surfaces.from_array(
            numpy.asarray(PILImage.fromarray(Surfaces.to_array(_surface)).filter(PILImageFilter.GaussianBlur(radius)).convert("RGBA"))
        ).convert_alpha()
        if dest_surface is not None:
            return pygame.transform.smoothscale(new_surf, dest_surface.get_size(), dest_surface)
        return new_surf

    # blur a surface using box blur
    @classmethod
    def box_blur(cls, _surface: ImageSurface, radius: int = 10, repeat_edge_pixels: bool = True, dest_surface: ImageSurface | None = None) -> ImageSurface:
        # if is using pygame-ce
        if GraphicLibrary.is_using_pygame_ce():
            return pygame.transform.box_blur(
                _surface, radius, repeat_edge_pixels, dest_surface if dest_surface is not None else Surfaces.new(_surface.get_size())
            )
        # box blur is not supported for other graphic
        if Debug.get_developer_mode():
            EXCEPTION.warn('The "box_blur" filter is only supported when using pygame-ce, gaussian_blur will be used.')
        return cls.gaussian_blur(_surface, radius, repeat_edge_pixels, dest_surface)

    # 增加图层暗度
    @staticmethod
    def add_darkness(img: ImageSurface, value: int) -> ImageSurface:
        newImg: ImageSurface = img.copy()
        newImg.fill((value, value, value), special_flags=pygame.BLEND_RGB_SUB)
        return newImg

    # 减少图层暗度
    @staticmethod
    def subtract_darkness(img: ImageSurface, value: int) -> ImageSurface:
        newImg: ImageSurface = img.copy()
        newImg.fill((value, value, value), special_flags=pygame.BLEND_RGB_ADD)
        return newImg
