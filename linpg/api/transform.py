from .convert import *


class Transformer:
    def flip(self, img: ImageSurface, horizontal: bool, vertical: bool) -> ImageSurface:
        return RawImg.flip(img, horizontal, vertical)

    def rotate(self, img: ImageSurface, angle: int) -> ImageSurface:
        return RawImg.rotate(img, angle)

    def resize(self, img: ImageSurface, size: tuple) -> ImageSurface:
        return RawImg.smoothly_resize(img, size) if Setting.get_antialias() is True else RawImg.resize(img, size)

    def crop(self, img: ImageSurface, pos: tuple, size: tuple) -> ImageSurface:
        return RawImg.crop(img, pos, size)

    # 移除掉图片周围的透明像素
    def crop_bounding(self, img: ImageSurface) -> ImageSurface:
        rect_t = img.get_bounding_rect()
        return RawImg.crop(img, rect_t.topleft, rect_t.size)


transform = Transformer()
