from .mixer import *

_FONT_IS_NOT_INITIALIZED_MSG: str = "Font is not initialized!"

# 文字渲染模块
class FontGenerator:
    def __init__(self) -> None:
        self.__SIZE: int = 0
        self.__FONT: Optional[pygame.font.Font] = None

    # 是否加粗
    @property
    def bold(self) -> bool:
        if self.__FONT is not None:
            return self.__FONT.bold
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)

    # 是否斜体
    @property
    def italic(self) -> bool:
        if self.__FONT is not None:
            return self.__FONT.italic
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)

    # 文字大小
    @property
    def size(self) -> int:
        if self.__SIZE > 0:
            return self.__SIZE
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)

    # 更新文字模块
    def update(self, size: int_f, ifBold: bool = False, ifItalic: bool = False) -> None:
        if size <= 0:
            EXCEPTION.fatal("Font size must be greater than 0!")
        self.__SIZE = int(size)
        # 根据类型处理
        if Setting.get_font_type() == "default":
            self.__FONT = pygame.font.SysFont(Setting.get_font(), self.__SIZE, ifBold, ifItalic)
        elif Setting.get_font_type() == "custom":
            if os.path.exists(font_path := Specification.get_directory("font", "{}.ttf".format(Setting.get_font()))):
                self.__FONT = pygame.font.Font(font_path, self.__SIZE)
            else:
                EXCEPTION.warn(
                    "Cannot find the {}.ttf file, the engine's font has been changed to default.".format(Setting.get_font())
                )
                Setting.set_font("arial")
                Setting.set_font_type("default")
                self.__FONT = pygame.font.SysFont(Setting.get_font(), self.__SIZE, ifBold, ifItalic)
            # 加粗
            if ifBold is True:
                self.__FONT.set_bold(ifBold)
            # 斜体
            if ifItalic is True:
                self.__FONT.set_italic(ifItalic)
        else:
            EXCEPTION.fatal("FontType option in setting file is incorrect!")

    # 估计文字的宽度
    def estimate_text_width(self, text: strint) -> int:
        if self.__FONT is not None:
            return self.__FONT.size(str(text))[0]
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)

    # 估计文字的高度
    def estimate_text_height(self, text: strint) -> int:
        if self.__FONT is not None:
            return self.__FONT.size(str(text))[1]
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)

    # 检测是否需要更新
    def check_for_update(self, size: int, ifBold: bool = False, ifItalic: bool = False) -> None:
        if self.__FONT is None or self.__SIZE != size or self.__FONT.bold != ifBold or self.__FONT.italic != ifItalic:
            self.update(size, ifBold, ifItalic)

    # 渲染文字
    def render(
        self, txt: strint, color: color_liked, background_color: Optional[color_liked] = None, with_bounding: bool = False
    ) -> ImageSurface:
        if self.__SIZE > 0:
            if not isinstance(txt, (str, int)):
                EXCEPTION.fatal("The text must be a unicode or bytes, not {}".format(txt))
            if self.__FONT is not None:
                font_surface_t: ImageSurface = (
                    self.__FONT.render(str(txt), Setting.get_antialias(), Colors.get(color))
                    if background_color is None
                    else self.__FONT.render(str(txt), Setting.get_antialias(), Colors.get(color), Colors.get(background_color))
                )
                return font_surface_t.subsurface(font_surface_t.get_bounding_rect()) if not with_bounding else font_surface_t
            else:
                EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)


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

    # 文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
    @classmethod
    def render(
        cls,
        txt: strint,
        color: color_liked,
        size: int_f,
        ifBold: bool = False,
        ifItalic: bool = False,
        background_color: color_liked = None,
        with_bounding: bool = False,
    ) -> ImageSurface:
        cls.__LINPG_LAST_FONT.check_for_update(int(size), ifBold, ifItalic)
        return cls.__LINPG_LAST_FONT.render(txt, color, background_color, with_bounding)

    @classmethod
    def render_description_box(
        cls,
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
        font_surface = cls.render(txt, color, size, ifBold, ifItalic, with_bounding=True)
        des_surface = Surfaces.colored(
            (font_surface.get_width() + padding * 2, font_surface.get_height() + padding * 2), background_color
        )
        Draw.rect(
            des_surface,
            Colors.get(color if outline_color is None else outline_color),
            ((0, 0), des_surface.get_size()),
            thickness,
        )
        des_surface.blit(font_surface, (padding, padding))
        return des_surface
