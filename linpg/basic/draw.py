from .color import *


class Draw:

    # 根据给与的rect画出轮廓
    @staticmethod
    def rect(surface: ImageSurface, color: tuple, rect: tuple, thickness: int = 0) -> None:
        pygame.draw.rect(surface, color, rect, thickness)

    # 根据给与的中心点画出一个圆
    @staticmethod
    def circle(surface: ImageSurface, color: tuple, center_pos: tuple, radius: int, thickness: int = 0) -> None:
        pygame.draw.circle(surface, color, center_pos, radius, thickness)

    # 画抗锯齿线条
    @staticmethod
    def aaline(
        surface: ImageSurface, color: color_liked, start_pos: tuple[int, int], end_pos: tuple[int, int], blend: int = 1
    ) -> None:
        pygame.draw.aaline(surface, Colors.get(color), start_pos, end_pos, blend)
