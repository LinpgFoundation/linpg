from .draw import *


class Surfaces:

    # null图层占位符
    NULL: ImageSurface = pygame.surface.Surface((0, 0))

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
            surface: ImageSurface = cls.transparent((int(_shape[0]), int(_shape[1])))
            # Copy the rgb part of array to the new surface.
            pygame.pixelcopy.array_to_surface(surface, surface_array[:, :, 0:3])
            # Copy the alpha part of array to the surface using a pixels-alpha
            # view of the surface.
            surface_alpha = numpy.array(surface.get_view("A"), copy=False)
            surface_alpha[:, :] = surface_array[:, :, 3]
            return surface

    # 根据Surface生成array
    @staticmethod
    def to_array(surface: ImageSurface, with_alpha: bool = True, swap_axes: bool = True) -> numpy.ndarray:
        surface_3d_rgb_array: numpy.ndarray = pygame.surfarray.array3d(surface)
        if with_alpha is True:
            surface_3d_rgb_array = numpy.dstack((surface_3d_rgb_array, pygame.surfarray.array_alpha(surface)))
        return surface_3d_rgb_array.swapaxes(0, 1) if swap_axes is True else surface_3d_rgb_array

    # 获取材质缺失的临时警示材质
    @classmethod
    def texture_is_missing(cls, size: tuple[int, int]) -> ImageSurface:
        texture_missing_surface: ImageSurface = cls.colored(size, Colors.BLACK)
        half_width: int = size[0] // 2
        half_height: int = size[1] // 2
        pygame.draw.rect(
            texture_missing_surface,
            Colors.VIOLET,
            pygame.Rect(half_width, 0, texture_missing_surface.get_width() - half_width, half_height),
        )
        pygame.draw.rect(
            texture_missing_surface,
            Colors.VIOLET,
            pygame.Rect(0, half_height, half_width, texture_missing_surface.get_height() - half_height),
        )
        return texture_missing_surface
