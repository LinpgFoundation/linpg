from ..interface import *


# 阴影
class Shadows:
    @staticmethod
    def render(img: AbstractImageSurface, target_surface: ImageSurface, alpha: int = 100, percentage: int = 80) -> None:
        tans_rect: Rectangle = img.get_bounding_rect()
        Draw.ellipse(
            target_surface,
            (*Colors.GRAY[:3], alpha),
            (img.x + tans_rect.centerx, img.y + tans_rect.bottom),
            (tans_rect.get_width() * percentage // 200, tans_rect.get_height() * percentage // 400),
        )
