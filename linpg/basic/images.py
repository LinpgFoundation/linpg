import io
import zipfile

from PIL import Image as PILImage  # type: ignore
from PIL import ImageSequence as PILImageSequence  # type: ignore

from .wrapper import *

# 尝试导入linpgassets
_LINPGASSETS_INITIALIZED: bool = False
if bool(Specification.get("ExtraAssets")) is True:
    try:
        import linpgassets  # type: ignore

        _LINPGASSETS_INITIALIZED = True
        # 初始化linpgassets的数据库
        DataBase.update(Config.load_file(linpgassets.get_database_path()))
    except Exception:
        _LINPGASSETS_INITIALIZED = False

# 初始化项目自带的数据库
DataBase.update(Config.resolve_path_and_load_file(os.path.join("Data", "database")))

_KEY: Final[bytes] = bytes("82&939DcaO6002#*", "utf-8")


# 源图形处理
class Images:

    # flag查询表
    __FLAG_LOOKUP_TABLE: Final[dict[str, str]] = {"env": "environment", "ui": "user_interface"}

    # 根据flag
    @classmethod
    def generate_path_according_to_prefix(cls, path: str) -> str:
        flag_end_index: int = path.index(">")
        file_name: str = path[flag_end_index + 1 :]
        flag_key: Optional[str] = cls.__FLAG_LOOKUP_TABLE.get(path[2:flag_end_index])
        if flag_key is not None:
            if path[1] == "&":
                if os.path.exists(real_path := Specification.get_directory(flag_key, file_name)):
                    return real_path
                elif _LINPGASSETS_INITIALIZED is True:
                    return os.path.join(linpgassets.get_image_location(), flag_key, file_name + ".zip")
                else:
                    return ""
            elif path[1] == "!":
                return os.path.join(linpgassets.get_image_location(), flag_key, file_name + ".zip") if _LINPGASSETS_INITIALIZED is True else ""
            elif path[1] == "@":
                return Specification.get_directory(flag_key, file_name)
        EXCEPTION.fatal('Invalid tag: "{}"'.format(path))

    # 识快速加载图片
    @classmethod
    def quickly_load(cls, path: PoI, convert_alpha: bool = True) -> ImageSurface:
        if isinstance(path, ImageSurface):
            return path
        elif isinstance(path, str):
            if path != "<NULL>":
                _imageR: Optional[ImageSurface] = None
                # 如果正在加载不属于linpgassets的图片
                if not path.startswith("<"):
                    try:
                        _imageR = pygame.image.load(path)
                    except Exception:
                        if Debug.get_developer_mode() is True:
                            EXCEPTION.fatal("Cannot load image from path: {}".format(path))
                        else:
                            _imageR = None
                # 如果需要加载属于linpgassets的图片
                elif os.path.exists(_path := cls.generate_path_according_to_prefix(path)):
                    if not _path.endswith(".zip"):
                        _imageR = pygame.image.load(_path)
                    elif "linpgassets" in _path:
                        _imageR = pygame.image.load(io.BytesIO(zipfile.ZipFile(_path, "r").read(path[path.index(">") + 1 :], pwd=_KEY)))
                    elif Debug.get_developer_mode() is True:
                        EXCEPTION.fatal("Cannot find essential image with path: {}".format(_path))
                # 根据参数处理并返回加载好的图片
                if _imageR is not None:
                    return _imageR.convert_alpha() if convert_alpha is True else _imageR.convert()
                # 如果图片加载出错
                else:
                    return Surfaces.texture_is_missing((192, 108))
            else:
                return Surfaces.NULL
        else:
            EXCEPTION.fatal("The path '{}' has to be a string or at least a ImageSurface!".format(path))

    # 图片加载模块：接收图片路径,长,高,返回对应图片
    @classmethod
    def load(cls, path: PoI, size: tuple = tuple(), alpha: int = 255, convert_alpha: bool = True) -> ImageSurface:
        # 加载图片
        img: ImageSurface = cls.quickly_load(path, convert_alpha)
        # 根据参数编辑图片
        if alpha < 255:
            img.set_alpha(alpha)
        # 如果没有给size,则直接返回Surface
        return img if len(size) == 0 else cls.smoothly_resize(img, size) if Setting.get_antialias() else cls.resize(img, size)

    # 动态图片加载模块
    @staticmethod
    def load_animated(path: str) -> list:
        return [Surfaces.from_array(numpy.asarray(frame.convert("RGBA"))).convert_alpha() for frame in PILImageSequence.Iterator(PILImage.open(path))]

    # 重新编辑尺寸
    @staticmethod
    def resize(img: ImageSurface, size: tuple) -> ImageSurface:
        # 编辑图片
        if size[1] is not None and size[1] >= 0 and size[0] is None:
            return pygame.transform.scale(img, (round(size[1] / img.get_height() * img.get_width()), round(size[1])))
        elif size[1] is None and size[0] is not None and size[0] >= 0:
            return pygame.transform.scale(img, (round(size[0]), round(size[0] / img.get_width() * img.get_height())))
        elif size[0] >= 0 and size[1] >= 0:
            return pygame.transform.scale(img, (round(size[0]), round(size[1])))
        EXCEPTION.fatal("Both width and height must be positive integer!")

    # 精准地缩放尺寸
    @staticmethod
    def smoothly_resize(img: ImageSurface, size: tuple) -> ImageSurface:
        # 编辑图片
        if size[1] is not None and size[1] >= 0 and size[0] is None:
            return pygame.transform.smoothscale(img, (round(size[1] / img.get_height() * img.get_width()), round(size[1])))
        elif size[1] is None and size[0] is not None and size[0] >= 0:
            return pygame.transform.smoothscale(img, (round(size[0]), round(size[0] / img.get_width() * img.get_height())))
        elif size[0] >= 0 and size[1] >= 0:
            return pygame.transform.smoothscale(img, (round(size[0]), round(size[1])))
        EXCEPTION.fatal("Both width and height must be positive integer!")

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

    # 移除掉图片周围的透明像素
    @classmethod
    def crop_bounding(cls, img: ImageSurface) -> ImageSurface:
        return img.subsurface(img.get_bounding_rect())

    # 使用ImageFixer组件修复或优化png
    @staticmethod
    def fix(path: str) -> None:
        ImageFixer.fix(path)

    # 保存图片
    @staticmethod
    def save(_surface: ImageSurface, path: str) -> None:
        pygame.image.save(_surface, path)
