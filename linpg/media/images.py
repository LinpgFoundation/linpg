import io

from ..io.settings import Settings
from .wrapper import *


# 源图形处理
class Images:
    # 加载
    @staticmethod
    def __load(_file: str | io.BytesIO) -> ImageSurface:
        return pygame.image.load(_file)

    # 识快速加载图片
    @classmethod
    def quickly_load(cls, path: PoI, convert_alpha: bool = True) -> ImageSurface:
        if isinstance(path, ImageSurface):
            return path
        elif isinstance(path, str):
            if path != "<NULL>":
                canBeNull: bool = False
                if path.endswith("?"):
                    canBeNull = True
                    path = path.rstrip("?")
                # 尝试加载图片
                _imageR: ImageSurface | None = None
                try:
                    _imageR = cls.__load(path)
                except Exception:
                    if Debug.get_developer_mode() is True and not canBeNull:
                        Exceptions.fatal(f"Cannot load image from path: {path}")
                    _imageR = None
                # 根据参数处理并返回加载好的图片
                if _imageR is not None:
                    return _imageR.convert_alpha() if convert_alpha is True else _imageR.convert()
                # 如果图片加载出错
                else:
                    return Surfaces.NULL if canBeNull else Surfaces.texture_is_missing((192, 108))
            else:
                return Surfaces.NULL
        else:
            Exceptions.fatal(f"The path '{path}' has to be a string or at least a ImageSurface!")

    # 图片加载模块：接收图片路径,长,高,返回对应图片
    @classmethod
    def load(cls, path: PoI, size: tuple = tuple(), alpha: int = 255, convert_alpha: bool = True) -> ImageSurface:
        # 加载图片
        img: ImageSurface = cls.quickly_load(path, convert_alpha)
        # 如果是null，则直接返回
        if not Surfaces.is_not_null(img):
            return img
        # 根据参数编辑图片
        if alpha < 255:
            img.set_alpha(alpha)
        # 如果没有给size,则直接返回Surface
        return img if len(size) == 0 else cls.smoothly_resize(img, size) if Settings.get_antialias() else cls.resize(img, size)

    # 重新编辑尺寸
    @staticmethod
    def resize(img: ImageSurface, size: tuple) -> ImageSurface:
        # 如果是null，则直接返回
        if not Surfaces.is_not_null(img):
            return img
        # 编辑图片
        if size[1] is not None and size[1] >= 0 and size[0] is None:
            return pygame.transform.scale(img, (round(size[1] / img.get_height() * img.get_width()), round(size[1])))
        elif size[1] is None and size[0] is not None and size[0] >= 0:
            return pygame.transform.scale(img, (round(size[0]), round(size[0] / img.get_width() * img.get_height())))
        elif size[0] >= 0 and size[1] >= 0:
            return pygame.transform.scale(img, (round(size[0]), round(size[1])))
        Exceptions.fatal("Both width and height must be positive integer!")

    # 精准地缩放尺寸
    @staticmethod
    def smoothly_resize(img: ImageSurface, size: tuple) -> ImageSurface:
        # 如果是null，则直接返回
        if not Surfaces.is_not_null(img):
            return img
        # 编辑图片
        if size[1] is not None and size[1] >= 0 and size[0] is None:
            return pygame.transform.smoothscale(img, (round(size[1] / img.get_height() * img.get_width()), round(size[1])))
        elif size[1] is None and size[0] is not None and size[0] >= 0:
            return pygame.transform.smoothscale(img, (round(size[0]), round(size[0] / img.get_width() * img.get_height())))
        elif size[0] >= 0 and size[1] >= 0:
            return pygame.transform.smoothscale(img, (round(size[0]), round(size[1])))
        Exceptions.fatal("Both width and height must be positive integer!")

    # 精准地缩放尺寸
    @classmethod
    def smoothly_resize_and_crop_to_fit(cls, img: ImageSurface, size: tuple[int, int]) -> ImageSurface:
        # 如果是null，则直接返回
        if not Surfaces.is_not_null(img):
            return img
        # 根据尺寸计算长宽
        if img.get_height() / img.get_width() > 1:
            img = cls.smoothly_resize(img, (None, size[1]))
            return img.subsurface(((img.get_width() - size[0]) // 2, 0), size)
        else:
            img = cls.smoothly_resize(img, (size[0], None))
            return img.subsurface((0, (img.get_height() - size[1]) // 2), size)

    # 翻转图片
    @staticmethod
    def flip(img: ImageSurface, horizontal: bool, vertical: bool) -> ImageSurface:
        return pygame.transform.flip(img, horizontal, vertical) if Surfaces.is_not_null(img) else img

    # 旋转图片
    @staticmethod
    def rotate(img: ImageSurface, angle: int) -> ImageSurface:
        return pygame.transform.rotate(img, angle) if Surfaces.is_not_null(img) else img

    # 移除掉图片周围的透明像素
    @classmethod
    def crop_bounding(cls, img: ImageSurface) -> ImageSurface:
        return img.subsurface(img.get_bounding_rect()) if Surfaces.is_not_null(img) else img

    # 保存图片
    @staticmethod
    def save(_surface: ImageSurface, path: str) -> None:
        # 如果是null，则报警
        if not Surfaces.is_not_null(_surface):
            Exceptions.fatal("You cannot save a null surface!")
        # 保存
        pygame.image.save(_surface, path)

    # 将BytesIO转换为图片
    @classmethod
    def from_bytes(cls, _bytes: io.BytesIO) -> ImageSurface:
        return cls.__load(_bytes)
