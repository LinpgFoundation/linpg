from .color import *

# 源图形处理
class RawImageManafer:
    # 识快速加载图片
    @staticmethod
    def quickly_load(path: PoI, convert_alpha: bool = True) -> ImageSurface:
        if isinstance(path, ImageSurface):
            return path
        elif isinstance(path, str):
            path = os.path.join(path)
            if convert_alpha is True:
                try:
                    return pygame.image.load(path).convert_alpha() if is_using_pygame() else pyglet.image.load(path)
                except Exception:
                    if Setting.developer_mode is True:
                        EXCEPTION.fatal("Cannot load image from path: {}".format(path))
                    else:
                        return get_texture_missing_surface((192, 108))
            else:
                try:
                    return pygame.image.load(path) if is_using_pygame() else pyglet.image.load(path)
                except Exception:
                    if Setting.developer_mode is True:
                        EXCEPTION.fatal("Cannot load image from path: {}".format(path))
                    else:
                        return get_texture_missing_surface((192, 108))
        else:
            EXCEPTION.fatal("The path '{}' has to be a string or at least a ImageSurface!".format(path))

    # 图片加载模块：接收图片路径,长,高,返回对应图片
    def load(self, path: PoI, size: size_liked = tuple(), alpha: int = 255, convert_alpha: bool = True) -> ImageSurface:
        # 加载图片
        img = IMG.quickly_load(path, convert_alpha)
        # 根据参数编辑图片
        if alpha < 255:
            img.set_alpha(alpha)
        # 如果没有给size,则直接返回Surface
        if len(size) == 0:
            return img
        else:
            return self.smoothly_resize(img, size) if Setting.antialias is True else self.resize(img, size)

    # 重新编辑尺寸
    @staticmethod
    def resize(img: ImageSurface, size: size_liked = (None, None)) -> ImageSurface:
        # 转换尺寸
        if isinstance(size, (list, tuple)):
            if len(size) == 1:
                width = size[0]
                height = None
            else:
                width = size[0]
                height = size[1]
        elif isinstance(size, (int, float)):
            width = size
            height = None
        else:
            EXCEPTION.fatal("The size '{}' is not acceptable.".format(size))
        # 编辑图片
        if height is not None and height >= 0 and width is None:
            img = pygame.transform.scale(img, (round(height / img.get_height() * img.get_width()), round(height)))
        elif height is None and width is not None and width >= 0:
            img = pygame.transform.scale(img, (round(width), round(width / img.get_width() * img.get_height())))
        elif width >= 0 and height >= 0:
            img = pygame.transform.scale(img, (round(width), round(height)))
        elif width < 0 or height < 0:
            EXCEPTION.fatal("Both width and height must be positive interger!")
        return img

    # 精准地缩放尺寸
    @staticmethod
    def smoothly_resize(img: ImageSurface, size: size_liked = (None, None)):
        # 转换尺寸
        if isinstance(size, (list, tuple)):
            if len(size) == 1:
                width = size[0]
                height = None
            else:
                width = size[0]
                height = size[1]
        elif isinstance(size, (int, float)):
            width = size
            height = None
        else:
            EXCEPTION.fatal("The size '{}' is not acceptable.".format(size))
        # 编辑图片
        if height is not None and height >= 0 and width is None:
            img = pygame.transform.smoothscale(img, (round(height / img.get_height() * img.get_width()), round(height)))
        elif height is None and width is not None and width >= 0:
            img = pygame.transform.smoothscale(img, (round(width), round(width / img.get_width() * img.get_height())))
        elif width >= 0 and height >= 0:
            img = pygame.transform.smoothscale(img, (round(width), round(height)))
        elif width < 0 or height < 0:
            EXCEPTION.fatal("Both width and height must be positive interger!")
        return img

    # 增加图片暗度
    @staticmethod
    def add_darkness(img: ImageSurface, value: int) -> ImageSurface:
        newImg: ImageSurface = img.copy()
        newImg.fill((value, value, value), special_flags=pygame.BLEND_RGB_SUB)
        return newImg

    # 减少图片暗度
    @staticmethod
    def subtract_darkness(img: ImageSurface, value: int) -> ImageSurface:
        newImg: ImageSurface = img.copy()
        newImg.fill((value, value, value), special_flags=pygame.BLEND_RGB_ADD)
        return newImg

    # 翻转图片
    @staticmethod
    def flip(img: ImageSurface, horizontal: bool, vertical: bool) -> ImageSurface:
        return pygame.transform.flip(img, horizontal, vertical)

    # 旋转图片
    @staticmethod
    def rotate(img: ImageSurface, angle: int) -> ImageSurface:
        return pygame.transform.rotate(img, angle)

    # 按照给定的位置对图片进行剪裁
    @staticmethod
    def crop(img: ImageSurface, pos: pos_liked = Pos.ORIGIN, size: size_liked = (1, 1)) -> ImageSurface:
        if isinstance(pos, pygame.Rect):
            cropped = new_transparent_surface(pos.size)
            cropped.blit(img, (-pos.x, -pos.y))
        else:
            cropped = new_transparent_surface((round(size[0]), round(size[1])))
            cropped.blit(img, (-pos[0], -pos[1]))
        return cropped


IMG = RawImageManafer()
