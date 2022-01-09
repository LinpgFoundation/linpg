from ..asset import ASSET
from .draw import *

# 获取材质缺失的临时警示材质
def get_texture_missing_surface(size: tuple[int, int]) -> ImageSurface:
    texture_missing_surface: ImageSurface = new_surface(size)
    texture_missing_surface.fill(Colors.BLACK)
    half_width: int = int(size[0] / 2)
    half_height: int = int(size[1] / 2)
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


# null图层占位符
NULL_SURFACE: ImageSurface = pygame.surface.Surface((0, 0))

# 源图形处理
class RawImageManafer:
    # 识快速加载图片
    @staticmethod
    def quickly_load(path: PoI, convert_alpha: bool = True) -> ImageSurface:
        if isinstance(path, ImageSurface):
            return path
        elif isinstance(path, str):
            if path != "<!null>":
                path_t: str = ASSET.resolve_path(path)
                if convert_alpha is True:
                    try:
                        return pygame.image.load(path_t).convert_alpha()
                    except Exception:
                        if Setting.developer_mode is True:
                            EXCEPTION.fatal("Cannot load image from path: {}".format(path_t))
                        else:
                            return get_texture_missing_surface((192, 108))
                else:
                    try:
                        return pygame.image.load(path_t).convert()
                    except Exception:
                        if Setting.developer_mode is True:
                            EXCEPTION.fatal("Cannot load image from path: {}".format(path_t))
                        else:
                            return get_texture_missing_surface((192, 108))
            else:
                return NULL_SURFACE
        else:
            EXCEPTION.fatal("The path '{}' has to be a string or at least a ImageSurface!".format(path))

    # 图片加载模块：接收图片路径,长,高,返回对应图片
    def load(self, path: PoI, size: tuple = tuple(), alpha: int = 255, convert_alpha: bool = True) -> ImageSurface:
        # 加载图片
        img: ImageSurface = IMG.quickly_load(path, convert_alpha)
        # 根据参数编辑图片
        if alpha < 255:
            img.set_alpha(alpha)
        # 如果没有给size,则直接返回Surface
        return img if len(size) == 0 else self.smoothly_resize(img, size) if Setting.antialias is True else self.resize(img, size)

    # 重新编辑尺寸
    @staticmethod
    def resize(img: ImageSurface, size: tuple) -> ImageSurface:
        # 编辑图片
        if size[1] is not None and size[1] >= 0 and size[0] is None:
            img2 = pygame.transform.scale(img, (round(size[1] / img.get_height() * img.get_width()), round(size[1])))
        elif size[1] is None and size[0] is not None and size[0] >= 0:
            img2 = pygame.transform.scale(img, (round(size[0]), round(size[0] / img.get_width() * img.get_height())))
        elif size[0] >= 0 and size[1] >= 0:
            img2 = pygame.transform.scale(img, (round(size[0]), round(size[1])))
        elif size[0] < 0 or size[1] < 0:
            EXCEPTION.fatal("Both width and height must be positive interger!")
        return img2

    # 精准地缩放尺寸
    @staticmethod
    def smoothly_resize(img: ImageSurface, size: tuple) -> ImageSurface:
        # 编辑图片
        if size[1] is not None and size[1] >= 0 and size[0] is None:
            img = pygame.transform.smoothscale(img, (round(size[1] / img.get_height() * img.get_width()), round(size[1])))
        elif size[1] is None and size[0] is not None and size[0] >= 0:
            img = pygame.transform.smoothscale(img, (round(size[0]), round(size[0] / img.get_width() * img.get_height())))
        elif size[0] >= 0 and size[1] >= 0:
            img = pygame.transform.smoothscale(img, (round(size[0]), round(size[1])))
        elif size[0] < 0 or size[1] < 0:
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
    def crop(img: ImageSurface, pos: tuple = ORIGIN, size: tuple = (1, 1)) -> ImageSurface:
        cropped: ImageSurface = new_transparent_surface((round(size[0]), round(size[1])))
        cropped.blit(img, (-pos[0], -pos[1]))
        return cropped

    # 使用ImageFixer组件修复或优化png
    @staticmethod
    def fix(path: str) -> None:
        ImageFixer.fix(path)


IMG = RawImageManafer()
