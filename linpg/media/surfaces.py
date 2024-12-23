import numpy
import pygame.gfxdraw
from PIL import Image as PILImage
from PIL import ImageFilter as PILImageFilter

from ..basic.debug import Debug
from .wrapper import *


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
    def circle(
        _surface: ImageSurface, color: tuple[int, int, int, int], center_pos: tuple[int, int], radius: int, thickness: int = 0
    ) -> None:
        if thickness <= 0:
            pygame.gfxdraw.filled_circle(_surface, center_pos[0], center_pos[1], radius, color)
        else:
            pygame.draw.circle(_surface, color, center_pos, radius, thickness)

    # 根据给与的中心点画出一个椭圆
    @staticmethod
    def ellipse(
        _surface: ImageSurface,
        color: tuple[int, int, int, int],
        center_pos: tuple[int, int],
        radius: tuple[int, int],
        thickness: int = 0,
    ) -> None:
        if thickness <= 0:
            pygame.gfxdraw.filled_ellipse(_surface, center_pos[0], center_pos[1], radius[0], radius[1], color)
        else:
            pygame.draw.ellipse(
                _surface,
                color,
                ((center_pos[0] - radius[0], center_pos[1] - radius[1]), (radius[0] * 2, radius[1] * 2)),
                thickness,
            )

    # 画一条抗锯齿线
    @staticmethod
    def aaline(
        _surface: ImageSurface, color: tuple[int, int, int, int], start_pos: tuple[int, int], end_pos: tuple[int, int]
    ) -> None:
        if start_pos[0] == end_pos[0]:
            pygame.gfxdraw.vline(_surface, start_pos[0], start_pos[1], end_pos[1], color)
        elif start_pos[1] == end_pos[1]:
            pygame.gfxdraw.hline(_surface, start_pos[0], end_pos[0], end_pos[1], color)
        else:
            pygame.draw.aaline(_surface, color, start_pos, end_pos)

    # 画一条线
    @staticmethod
    def line(
        _surface: ImageSurface,
        color: tuple[int, int, int, int],
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        width: int = 1,
    ) -> None:
        if width <= 1:
            pygame.gfxdraw.line(_surface, start_pos[0], start_pos[1], end_pos[0], end_pos[1], color)
        else:
            pygame.draw.line(_surface, color, start_pos, end_pos, width)

    # 画多边形
    @staticmethod
    def polygon(
        _surface: ImageSurface, _color: tuple[int, int, int, int], _points: tuple[tuple[int, int], ...], thickness: int = 0
    ) -> None:
        if thickness <= 0:
            pygame.gfxdraw.filled_polygon(_surface, _points, _color)
        else:
            pygame.draw.polygon(_surface, _color, _points, thickness)


class Surfaces:

    class _NULL_SURFACE(ImageSurface):
        def __init__(self) -> None:
            pass

        def get_width(self) -> int:
            return 0

        def get_height(self) -> int:
            return 0

    # null图层占位符
    NULL: ImageSurface = _NULL_SURFACE()

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
        Draw.rect(
            texture_missing_surface,
            Colors.VIOLET,
            (half_width, 0, texture_missing_surface.get_width() - half_width, half_height),
        )
        Draw.rect(
            texture_missing_surface,
            Colors.VIOLET,
            (0, half_height, half_width, texture_missing_surface.get_height() - half_height),
        )
        return texture_missing_surface

    # 检测图层是否是任何形式的null
    @classmethod
    def is_not_null(cls, _surface: ImageSurface | None) -> bool:
        return _surface is not None and _surface is not cls.NULL


# 滤镜效果
class Filters:
    # blur a surface using gaussian blur 毛玻璃效果
    @staticmethod
    def gaussian_blur(
        _surface: ImageSurface, radius: int = 10, repeat_edge_pixels: bool = True, dest_surface: ImageSurface | None = None
    ) -> ImageSurface:
        # if is using pygame-ce
        if GraphicLibrary.is_using_pygame_ce():
            return pygame.transform.gaussian_blur(
                _surface,
                radius,
                repeat_edge_pixels,
                dest_surface if dest_surface is not None else Surfaces.new(_surface.get_size()),
            )
        # if is using pygame not ce, then use pillow GaussianBlur instead
        new_surf: ImageSurface = Surfaces.from_array(
            numpy.asarray(
                PILImage.fromarray(Surfaces.to_array(_surface)).filter(PILImageFilter.GaussianBlur(radius)).convert("RGBA")
            )
        ).convert_alpha()
        if dest_surface is not None:
            return pygame.transform.smoothscale(new_surf, dest_surface.get_size(), dest_surface)
        return new_surf

    # blur a surface using box blur
    @classmethod
    def box_blur(
        cls, _surface: ImageSurface, radius: int = 10, repeat_edge_pixels: bool = True, dest_surface: ImageSurface | None = None
    ) -> ImageSurface:
        # if is using pygame-ce
        if GraphicLibrary.is_using_pygame_ce():
            return pygame.transform.box_blur(
                _surface,
                radius,
                repeat_edge_pixels,
                dest_surface if dest_surface is not None else Surfaces.new(_surface.get_size()),
            )
        # box blur is not supported for other graphic
        if Debug.get_developer_mode():
            Exceptions.warn('The "box_blur" filter is only supported when using pygame-ce, gaussian_blur will be used.')
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
