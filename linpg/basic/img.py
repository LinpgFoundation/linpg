import io
import zipfile
from PIL import Image as PILImage  # type: ignore
from PIL import ImageSequence as PILImageSequence  # type: ignore
from .draw import *

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


class Surface:

    # null图层占位符
    NULL: ImageSurface = pygame.surface.Surface((0, 0))

    # 获取Surface
    @staticmethod
    def new(size: tuple[int, int], surface_flags: int = -1) -> ImageSurface:
        return pygame.Surface(size, flags=surface_flags) if surface_flags >= 0 else pygame.Surface(size).convert()

    # 获取透明的Surface
    @staticmethod
    def transparent(size: tuple[int, int]) -> ImageSurface:
        return pygame.Surface(size, flags=pygame.SRCALPHA).convert_alpha()

    # 获取一个带颜色的Surface
    @staticmethod
    def colored(size: tuple[int, int], color: color_liked) -> ImageSurface:
        surface_t: ImageSurface = pygame.Surface(size).convert()
        surface_t.fill(Colors.get(color))
        return surface_t

    # 根据array生成Surface
    @classmethod
    def from_array(cls, surface_array: numpy.ndarray, swap_axes: bool = True) -> ImageSurface:
        if swap_axes is True:
            surface_array = surface_array.swapaxes(0, 1)
        if surface_array.shape[2] < 4:
            return pygame.surfarray.make_surface(surface_array).convert()
        else:
            # by llindstrom
            _shape: tuple = surface_array.shape
            surface: ImageSurface = cls.transparent((int(_shape[0]), int(_shape[1])))
            # Copy the rgb part of array to the new surface.
            pygame.pixelcopy.array_to_surface(surface, surface_array[:, :, 0:3])
            # Copy the alpha part of array to the surface using a pixels-alpha
            # view of the surface.
            surface_alpha = numpy.array(surface.get_view("A"), copy=False)
            surface_alpha[:, :] = surface_array[:, :, 3]
            return surface

    # 根据Surface生成array
    @staticmethod
    def to_array(surface: ImageSurface, with_alpha: bool = True, swap_axes: bool = True) -> numpy.ndarray:
        surface_3d_rgb_array: numpy.ndarray = pygame.surfarray.array3d(surface)
        if with_alpha is True:
            surface_3d_rgb_array = numpy.dstack((surface_3d_rgb_array, pygame.surfarray.array_alpha(surface)))
        return surface_3d_rgb_array.swapaxes(0, 1) if swap_axes is True else surface_3d_rgb_array

    # 获取材质缺失的临时警示材质
    @classmethod
    def texture_is_missing(cls, size: tuple[int, int]) -> ImageSurface:
        texture_missing_surface: ImageSurface = cls.colored(size, Colors.BLACK)
        half_width: int = size[0] // 2
        half_height: int = size[1] // 2
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


_KEY: bytes = bytes("82&939DcaO6002#*", "utf-8")

# 源图形处理
class RawImg:

    # flag查询表
    __FLAG_LOOKUP_TABLE: dict[str, str] = {"env": "environment", "ui": "user_interface"}

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
                return (
                    os.path.join(linpgassets.get_image_location(), flag_key, file_name + ".zip")
                    if _LINPGASSETS_INITIALIZED is True
                    else ""
                )
            elif path[1] == "@":
                return Specification.get_directory(flag_key, file_name)
        EXCEPTION.fatal('Invaid tag: "{}"'.format(path))

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
                        _imageR = pygame.image.load(
                            io.BytesIO(zipfile.ZipFile(_path, "r").read(path[path.index(">") + 1 :], pwd=_KEY))
                        )
                    else:
                        EXCEPTION.fatal("Cannot load image from path: {}".format(_path))
                else:
                    EXCEPTION.fatal('Cannot find (essential) file "{}"'.format(path))
                # 根据参数处理并返回加载好的图片
                if _imageR is not None:
                    return _imageR.convert_alpha() if convert_alpha is True else _imageR.convert()
                # 如果图片加载出错
                else:
                    return Surface.texture_is_missing((192, 108))
            else:
                return Surface.NULL
        else:
            EXCEPTION.fatal("The path '{}' has to be a string or at least a ImageSurface!".format(path))

    # 图片加载模块：接收图片路径,长,高,返回对应图片
    @classmethod
    def load(cls, path: PoI, size: tuple = tuple(), alpha: int = 255, convert_alpha: bool = True) -> ImageSurface:
        # 加载图片
        img: ImageSurface = RawImg.quickly_load(path, convert_alpha)
        # 根据参数编辑图片
        if alpha < 255:
            img.set_alpha(alpha)
        # 如果没有给size,则直接返回Surface
        return img if len(size) == 0 else cls.smoothly_resize(img, size) if Setting.get_antialias() else cls.resize(img, size)

    # 动态图片加载模块
    @staticmethod
    def load_animated(path: str) -> list:
        return [
            Surface.from_array(numpy.asarray(frame.convert("RGBA"))).convert_alpha()
            for frame in PILImageSequence.Iterator(PILImage.open(path))
        ]

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
        cropped: ImageSurface = Surface.transparent((round(size[0]), round(size[1])))
        cropped.blit(img, (-pos[0], -pos[1]))
        return cropped

    # 使用ImageFixer组件修复或优化png
    @staticmethod
    def fix(path: str) -> None:
        ImageFixer.fix(path)

    # 保存图片
    @staticmethod
    def save(surface: ImageSurface, path: str) -> None:
        pygame.image.save(surface, path)
