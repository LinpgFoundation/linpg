from .color import *


class Draw:

    # 根据给与的rect画出轮廓
    @staticmethod
    def rect(
        surface: ImageSurface,
        color: tuple[int, int, int, int],
        rect: Union[tuple[int, int, int, int], tuple[tuple[int, int], tuple[int, int]]],
        thickness: int = 0,
    ) -> None:
        pygame.draw.rect(surface, color, rect, thickness)

    # 根据给与的中心点画出一个圆
    @staticmethod
    def circle(
        surface: ImageSurface, color: tuple[int, int, int, int], center_pos: tuple[int, int], radius: int, thickness: int = 0
    ) -> None:
        pygame.draw.circle(surface, color, center_pos, radius, thickness)

    # 画抗锯齿线条
    @staticmethod
    def aaline(
        surface: ImageSurface,
        color: tuple[int, int, int, int],
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        blend: int = 1,
    ) -> None:
        pygame.draw.aaline(surface, color, start_pos, end_pos, blend)
