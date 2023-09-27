from .mixer import *


# 文字渲染模块
class FontGenerator:
    __FONT_IS_NOT_INITIALIZED_MSG: Final[str] = "Font is not initialized!"

    def __init__(self) -> None:
        self.__FONT: pygame.font.Font | None = None
        self.__size: int = 0

    # 是否加粗
    @property
    def bold(self) -> bool:
        if self.__FONT is not None:
            return self.__FONT.bold
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 是否斜体
    @property
    def italic(self) -> bool:
        if self.__FONT is not None:
            return self.__FONT.italic
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 文字大小
    @property
    def size(self) -> int:
        if self.__FONT is not None:
            return self.__size
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 更新文字模块
    def update(self, size: int_f, ifBold: bool = False, ifItalic: bool = False) -> None:
        if size <= 0:
            EXCEPTION.fatal("Font size must be greater than 0!")
        self.__size = int(size)
        # 根据类型处理
        match Setting.get_font_type():
            case "default":
                self.__FONT = pygame.font.SysFont(Setting.get_font(), self.__size)
            case "custom":
                font_path: str = Specification.get_directory("font", f"{Setting.get_font()}.ttf")
                if not os.path.exists(font_path):
                    EXCEPTION.fatal(f"Cannot find the {Setting.get_font()}.ttf file!")
                self.__FONT = pygame.font.Font(font_path, self.__size)
            case _:
                EXCEPTION.fatal("FontType option in setting file is incorrect!")
        self.__FONT.bold = ifBold
        self.__FONT.italic = ifItalic

    # 估计文字的宽度
    def estimate_text_width(self, text: str | int) -> int:
        if self.__FONT is not None:
            return self.__FONT.size(str(text))[0]
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 估计文字的高度
    def estimate_text_height(self, text: str | int) -> int:
        if self.__FONT is not None:
            return self.__FONT.size(str(text))[1]
        else:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)

    # 检测是否需要更新
    def check_for_update(self, _size: int, ifBold: bool = False, ifItalic: bool = False) -> None:
        if self.__FONT is None or _size != self.__size:
            self.update(_size, ifBold, ifItalic)
        else:
            self.__FONT.bold = ifBold
            self.__FONT.italic = ifItalic

    # 渲染文字
    def render(self, txt: str | int, color: color_liked, background_color: color_liked | None = None) -> ImageSurface:
        if not isinstance(txt, (str, int)):
            EXCEPTION.fatal(f"The text must be a unicode or bytes, not {txt}")
        if self.__FONT is None:
            EXCEPTION.fatal(self.__FONT_IS_NOT_INITIALIZED_MSG)
        return self.__FONT.render(str(txt), Setting.get_antialias(), Colors.get(color), Colors.get(background_color) if background_color is not None else None)


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
            EXCEPTION.fatal(f"Font size must be positive integer not {size}!")

    # 获取全局文字
    @classmethod
    def get_global_font(cls, key: str) -> FontGenerator:
        _font: FontGenerator | None = cls.__LINPG_GLOBAL_FONTS.get(key)
        if _font is not None:
            return _font
        else:
            EXCEPTION.fatal(f'You did not set any font named "{key}".')

    # 获取全局文字
    @classmethod
    def get_global_font_size(cls, key: str) -> int:
        return cls.get_global_font(key).size

    # 获取全局文字
    @classmethod
    def render_global_font(cls, key: str, txt: str, color: color_liked, background_color: color_liked | None = None) -> ImageSurface:
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
        cls, txt: str | int, color: color_liked, size: int_f, ifBold: bool = False, ifItalic: bool = False, background_color: color_liked | None = None
    ) -> ImageSurface:
        cls.__LINPG_LAST_FONT.check_for_update(int(size), ifBold, ifItalic)
        return cls.__LINPG_LAST_FONT.render(txt, color, background_color)


# 艺术字效果
class ArtisticFont:
    # 描述框效果
    @staticmethod
    def render_description_box(
        txt: str | int,
        color: color_liked,
        size: int,
        padding: int,
        background_color: color_liked,
        ifBold: bool = False,
        ifItalic: bool = False,
        outline_color: color_liked | None = None,
        thickness: int = 2,
    ) -> ImageSurface:
        font_surface: ImageSurface = Font.render(txt, color, size, ifBold, ifItalic)
        des_surface: ImageSurface = Surfaces.colored((font_surface.get_width() + padding * 2, font_surface.get_height() + padding * 2), background_color)
        Draw.rect(des_surface, Colors.get(color if outline_color is None else outline_color), (ORIGIN, des_surface.get_size()), thickness)
        des_surface.blit(font_surface, (padding, padding))
        return des_surface

    # 渲染有轮廓的文字
    @staticmethod
    def render_with_outline(
        _text: str | int,
        color: color_liked,
        size: int,
        outline_thickness: int = 1,
        outline_color: color_liked = Colors.BLACK,
        ifBold: bool = False,
        ifItalic: bool = False,
    ) -> ImageSurface:
        # 文字图层
        text_surface: ImageSurface = Font.render(_text, color, size, ifBold, ifItalic).convert_alpha()
        # 外框图层
        outline_surface: ImageSurface = Font.render(_text, outline_color, size, ifBold, ifItalic).convert_alpha()
        # 用于返回最终结果的图层
        result_surface: ImageSurface = Surfaces.transparent(
            (text_surface.get_width() + 2 * outline_thickness, text_surface.get_height() + 2 * outline_thickness)
        )
        # 生成圆角的像素坐标
        x: int = outline_thickness
        y: int = 0
        e: int = 1 - outline_thickness
        points: set[tuple[int, int]] = set()
        while x >= y:
            points.add((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points.update([(y, x) for x, y in points if x > y], [(-x, y) for x, y in points if x], [(x, -y) for x, y in points if y])
        # 多次渲染外框图层
        for dx, dy in points:
            result_surface.blit(outline_surface, (dx + outline_thickness, dy + outline_thickness))
        # 渲染文字图层
        result_surface.blit(text_surface, (outline_thickness, outline_thickness))
        # 返回结果
        return result_surface
