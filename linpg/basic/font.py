import pygame.freetype

from .mixer import *

# 确保freetype模块已经初始化
if not pygame.freetype.get_init():
    pygame.freetype.init(128, 144)

# 文字渲染模块
class FontGenerator:

    __FONT_IS_NOT_INITIALIZED_MSG: Final[str] = "Font is not initialized!"

    def __init__(self) -> None:
        self.__SIZE: int = 0
        self.__FONT: Optional[pygame.freetype.Font] = None
        self.__outline_thickness: int = 0
        self.__outline_color: tuple[int, int, int, int] = Colors.BLACK

    # 是否加粗
    @property
    def bold(self) -> bool:
        if self.__FONT is not None:
            return bool(self.__FONT.strong)
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 是否斜体
    @property
    def italic(self) -> bool:
        if self.__FONT is not None:
            return bool(self.__FONT.oblique)
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 文字大小
    @property
    def size(self) -> int:
        if self.__FONT is not None:
            return self.__SIZE
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 设置轮廓
    def set_outline(self, _thickness: int, _color: color_liked = Colors.BLACK) -> None:
        self.__outline_thickness = max(_thickness, 1)
        self.__outline_color = Colors.get(_color)

    # 关闭轮廓渲染
    def disable_outline(self) -> None:
        self.__outline_thickness = 0

    # 更新文字模块
    def update(self, size: int_f, ifBold: bool = False, ifItalic: bool = False) -> None:
        if size <= 0:
            EXCEPTION.fatal("Font size must be greater than 0!")
        self.__SIZE = max(int(size), 0)
        # 根据类型处理
        if Setting.get_font_type() == "default":
            self.__FONT = pygame.freetype.SysFont(Setting.get_font(), self.__SIZE)
        elif Setting.get_font_type() == "custom":
            font_path: str = Specification.get_directory("font", "{}.ttf".format(Setting.get_font()))
            if not os.path.exists(font_path):
                EXCEPTION.fatal("Cannot find the {}.ttf file!".format(Setting.get_font()))
            self.__FONT = pygame.freetype.Font(font_path, self.__SIZE)
        else:
            EXCEPTION.fatal("FontType option in setting file is incorrect!")
        self.__FONT.antialiased = Setting.get_antialias()
        self.__FONT.strong = ifBold
        self.__FONT.oblique = ifItalic

    # 估计文字的宽度
    def estimate_text_width(self, text: strint) -> int:
        if self.__FONT is not None:
            return self.__FONT.get_rect(str(text)).width
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 估计文字的高度
    def estimate_text_height(self, text: strint) -> int:
        if self.__FONT is not None:
            return self.__FONT.get_rect(str(text)).height
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 检测是否需要更新
    def check_for_update(self, size: int, ifBold: bool = False, ifItalic: bool = False) -> None:
        if self.__FONT is None or self.__SIZE != size:
            self.update(size, ifBold, ifItalic)
        else:
            self.__FONT.strong = ifBold
            self.__FONT.oblique = ifItalic

    # 渲染文字
    def render(self, txt: strint, color: color_liked, background_color: Optional[color_liked] = None) -> ImageSurface:
        if not isinstance(txt, (str, int)):
            EXCEPTION.fatal("The text must be a unicode or bytes, not {}".format(txt))
        if self.__FONT is None:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)
        if self.__outline_thickness <= 0:
            return (
                self.__FONT.render(str(txt), Colors.get(color))[0]
                if background_color is None
                else self.__FONT.render(str(txt), Colors.get(color), Colors.get(background_color))[0]
            )
        else:
            font_surface_t: ImageSurface = (
                self.__FONT.render(str(txt), self.__outline_color, size=self.__SIZE + self.__outline_thickness)[0]
                if background_color is None
                else self.__FONT.render(str(txt), self.__outline_color, Colors.get(background_color), size=self.__SIZE + self.__outline_thickness)[0]
            )
            self.__FONT.render_to(font_surface_t, (self.__outline_thickness, self.__outline_thickness), str(txt), Colors.get(color))
            return font_surface_t


# 文字渲染器管理模块
class Font:

    # 引擎标准文件渲染器
    __LINPG_GLOBAL_FONTS: Final[dict[str, FontGenerator]] = {}
    # 上一次render的字体
    __LINPG_LAST_FONT: Final[FontGenerator] = FontGenerator()

    # 设置全局文字
    @classmethod
    def set_global_font(cls, key: str, size: int, ifBold: bool = False, ifItalic: bool = False) -> None:
        if isinstance(size, int) and size > 0:
            if key not in cls.__LINPG_GLOBAL_FONTS:
                cls.__LINPG_GLOBAL_FONTS[key] = FontGenerator()
            cls.__LINPG_GLOBAL_FONTS[key].update(size, ifBold, ifItalic)
        else:
            EXCEPTION.fatal("Font size must be positive integer not {}!".format(size))

    # 获取全局文字
    @classmethod
    def get_global_font(cls, key: str) -> FontGenerator:
        _font: Optional[FontGenerator] = cls.__LINPG_GLOBAL_FONTS.get(key)
        if _font is not None:
            return _font
        else:
            EXCEPTION.fatal('You did not set any font named "{}".'.format(key))

    # 获取全局文字
    @classmethod
    def get_global_font_size(cls, key: str) -> int:
        return cls.get_global_font(key).size

    # 获取全局文字
    @classmethod
    def render_global_font(cls, key: str, txt: str, color: color_liked, background_color: color_liked = None) -> ImageSurface:
        return cls.get_global_font(key).render(txt, color, background_color)

    # 删除全局文字
    @classmethod
    def remove_global_font(cls, key: str) -> None:
        if key in cls.__LINPG_GLOBAL_FONTS:
            del cls.__LINPG_GLOBAL_FONTS[key]

    # 创建字体
    @staticmethod
    def create(size: int_f, ifBold: bool = False, ifItalic: bool = False) -> FontGenerator:
        new_font_t = FontGenerator()
        new_font_t.update(size, ifBold, ifItalic)
        return new_font_t

    # 接受文字，颜色，文字大小，样式等信息，返回制作完的文字
    @classmethod
    def render(
        cls, txt: strint, color: color_liked, size: int_f, ifBold: bool = False, ifItalic: bool = False, background_color: color_liked = None
    ) -> ImageSurface:
        cls.__LINPG_LAST_FONT.check_for_update(int(size), ifBold, ifItalic)
        return cls.__LINPG_LAST_FONT.render(txt, color, background_color)


# 艺术字效果
class ArtisticFont:

    # 描述框效果
    @staticmethod
    def render_description_box(
        txt: strint,
        color: color_liked,
        size: int,
        padding: int,
        background_color: color_liked,
        ifBold: bool = False,
        ifItalic: bool = False,
        outline_color: color_liked = None,
        thickness: int = 2,
    ) -> ImageSurface:
        font_surface = Font.render(txt, color, size, ifBold, ifItalic)
        des_surface = Surfaces.colored((font_surface.get_width() + padding * 2, font_surface.get_height() + padding * 2), background_color)
        Draw.rect(des_surface, Colors.get(color if outline_color is None else outline_color), ((0, 0), des_surface.get_size()), thickness)
        des_surface.blit(font_surface, (padding, padding))
        return des_surface
