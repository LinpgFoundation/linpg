from .battle import *


class _Loader:
    # 原始图片
    @staticmethod
    def img(path: str, size: tuple = tuple(), alpha: int = 255, ifConvertAlpha: bool = True) -> ImageSurface:
        return Images.load(path, size, alpha, ifConvertAlpha)

    # 静态图片
    @staticmethod
    def static_image(path: str, _position: tuple = (0, 0), size: tuple = (-1, -1), tag: str = "") -> StaticImage:
        return StaticImage(path, _position[0], _position[1], size[0], size[1], tag)

    # 可自行移动的图片
    @staticmethod
    def movable_static_image(path: str, _position: tuple, target_position: tuple, move_speed: tuple, size: tuple, tag: str = "") -> MovableStaticImage:
        return MovableStaticImage(path, _position[0], _position[1], target_position[0], target_position[1], move_speed[0], move_speed[1], size[0], size[1], tag)

    # 进度条Surface
    @staticmethod
    def progress_bar_surface(
        img_on_top_path: str, img_on_bottom_path: str, _position: tuple[int, int], size: tuple[int, int], mode: Axis = Axis.HORIZONTAL, tag: str = ""
    ) -> ProgressBarSurface:
        return ProgressBarSurface(img_on_top_path, img_on_bottom_path, _position[0], _position[1], size[0], size[1], mode, tag)

    # gif图片
    @staticmethod
    def gif(gif_path_or_img_list: str | Sequence[PoI], _position: tuple[int, int], size: tuple[int, int], fps: int | None = None) -> AnimatedImage:
        imgList: tuple
        # 如果是gif文件
        if isinstance(gif_path_or_img_list, str):
            _animated_image = PILImage.open(gif_path_or_img_list)
            imgList = tuple(
                StaticImage(Surfaces.from_array(numpy.asarray(frame.convert("RGBA"))).convert_alpha(), 0, 0, size[0], size[1])
                for frame in PILImageSequence.Iterator(PILImage.open(gif_path_or_img_list))
            )
            if fps is None:
                fps = _animated_image.info["duration"] // len(imgList)
        # 如果是一个列表的文件路径
        elif isinstance(gif_path_or_img_list, Sequence):
            imgList = tuple(StaticImage(surf, 0, 0, size[0], size[1]) for surf in gif_path_or_img_list)
            if fps is None:
                fps = 1
        else:
            EXCEPTION.fatal(f'Invalid input for "gif_path_or_img_list": {gif_path_or_img_list}')
        return AnimatedImage(imgList, _position[0], _position[1], size[0], size[1], fps)

    @staticmethod
    def button(path: str, _position: tuple[int, int], size: tuple[int, int], alpha_when_not_hover: int = 255) -> Button:
        return Button.load(path, _position, size, alpha_when_not_hover)

    # 普通文字模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class
    @staticmethod
    def text(txt: str | int, _color: color_liked, pos: tuple, size: int, ifBold: bool = False, ifItalic: bool = False) -> TextSurface:
        return TextSurface(str(txt), pos[0], pos[1], size, _color, ifBold, ifItalic)

    # 高级文字模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
    @staticmethod
    def resize_when_hovered_text(
        txt: str | int, _color: color_liked, pos: tuple[int, int], size: int, _bold: bool = False, _italic: bool = False
    ) -> ResizeWhenHoveredTextSurface:
        return ResizeWhenHoveredTextSurface(str(txt), pos[0], pos[1], size, size * 3 / 2, _color, _bold, _italic)


"""创建小写的模块引用名称，以方便使用"""
display = Display
lang = Lang
setting = Setting
info = Info
keys = Keys
config = Config
colors = Colors
global_variables = GlobalVariables
sounds = Sounds
music = Music
volume = Volume
media = Media
images = Images
controller = Controller
ui = UI
font = Font
position = Positions
coordinates = Coordinates
surfaces = Surfaces
debug = Debug
load = _Loader
numbers = Numbers
saves = Saves
db = DataBase


# 兼容 -- 将于3.8移除
AbstractVisualNovelSystem = AbstractVisualNovelPlayer
VisualNovelSystem = VisualNovelPlayer
DialogEditor = VisualNovelEditor
