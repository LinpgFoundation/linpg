from .convert import *


class Transformer:
    def __init__(self) -> None:
        pass

    def flip(self, img: ImageSurface, horizontal: bool, vertical: bool) -> ImageSurface:
        return IMG.flip(img, horizontal, vertical)

    def rotate(self, img: ImageSurface, angle: int) -> ImageSurface:
        return IMG.rotate(img, angle)

    def resize(self, img: ImageSurface, size: tuple[number]) -> ImageSurface:
        return (
            IMG.smoothly_resize(img, size)
            if Setting.antialias is True
            else IMG.resize(img, size)
        )

    def crop(
        self, img: ImageSurface, pos: tuple[number], size: tuple[number]
    ) -> ImageSurface:
        return IMG.crop(img, pos, size)

    # 移除掉图片周围的透明像素
    def crop_bounding(self, img: ImageSurface) -> ImageSurface:
        return IMG.crop(img, img.get_bounding_rect())


transform = Transformer()
