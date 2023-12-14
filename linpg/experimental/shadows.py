from ..interface import *

# 阴影
class Shadows:
    @staticmethod
    def render(img: AbstractImageSurface, target_surface: ImageSurface) -> None:
        tans_rect: Rectangle = img.get_bounding_rect()
        print(img.x + tans_rect.centerx, img.y + tans_rect.bottom, tans_rect.get_width() // 2, tans_rect.get_height() // 4)
        Draw.ellipse(
            target_surface,
            (*Colors.GRAY[:3], 100),
            (img.x + tans_rect.centerx, img.y + tans_rect.bottom),
            (tans_rect.get_width() // 2, tans_rect.get_height() // 4),
        )
