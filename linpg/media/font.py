from .mixer import *


# 文字渲染模块
class Font:
    def __init__(self) -> None:
        self.__FONT: pygame.font.Font | None = None
        self.__size: int = 0

    # a wrapper for getting font safely
    @property
    def __font(self) -> pygame.font.Font:
        if self.__FONT is not None:
            return self.__FONT
        else:
            Exceptions.fatal("Font is not initialized!")

    # 是否加粗
    @property
    def bold(self) -> bool:
        return self.__font.bold

    # 是否斜体
    @property
    def italic(self) -> bool:
        return self.__font.italic

    # 文字大小
    @property
    def size(self) -> int:
        return self.__size

    # 更新文字模块
    def update(self, size: int, bold: bool = False, italic: bool = False, underline: bool = False) -> None:
        if size <= 0:
            Exceptions.fatal("Font size must be greater than 0!")
        if self.__FONT is None or size != self.__size:
            self.__size = size
            # 根据类型处理
            match Settings.get_font_type():
                case "default":
                    self.__FONT = pygame.font.SysFont(Settings.get_font(), self.__size)
                case "custom":
                    font_path: str = Specifications.get_directory("font", f"{Settings.get_font()}.ttf")
                    if not os.path.exists(font_path):
                        Exceptions.fatal(f"Cannot find the {Settings.get_font()}.ttf file!")
                    self.__FONT = pygame.font.Font(font_path, self.__size)
                case _:
                    Exceptions.fatal("FontType option in setting file is incorrect!")
        self.__FONT.set_bold(bold)
        self.__FONT.set_italic(italic)
        self.__FONT.set_underline(underline)

    # 估计文字的宽度
    def estimate_text_width(self, text: str | int) -> int:
        return self.__FONT.size(str(text))[0] if self.__FONT is not None else 0

    # 估计文字的高度
    def estimate_text_height(self, text: str | int) -> int:
        return self.__FONT.size(str(text))[1] if self.__FONT is not None else 0

    # 估计文字的大小
    def estimate_text_size(self, text: str | int) -> tuple[int, int]:
        return self.__FONT.size(str(text)) if self.__FONT is not None else (0, 0)

    # 渲染文字
    def render(self, txt: str | int | float, color: color_liked, background_color: color_liked | None = None) -> ImageSurface:
        if not isinstance(txt, (str, int, float)):
            Exceptions.fatal(f"The text must be a str or int, not {txt}")
        return self.__font.render(
            str(txt),
            Settings.get_antialias(),
            Colors.get(color),
            Colors.get(background_color) if background_color is not None else None,
        )


# 文字渲染器管理模块
class Fonts:
    # 引擎标准文件渲染器
    __LINPG_GLOBAL_FONTS: Final[dict[str, Font]] = {}
    # 上一次render的字体
    __LINPG_LAST_FONT: Final[Font] = Font()

    # 设置全局文字
    @classmethod
    def set_global_font(cls, key: str, size: int, bold: bool = False, italic: bool = False, underline: bool = False) -> None:
        if isinstance(size, int) and size > 0:
            if key not in cls.__LINPG_GLOBAL_FONTS:
                cls.__LINPG_GLOBAL_FONTS[key] = Font()
            cls.__LINPG_GLOBAL_FONTS[key].update(size, bold, italic, underline)
        else:
            Exceptions.fatal(f"Font size must be positive integer not {size}!")

    # 获取全局文字
    @classmethod
    def get_global_font(cls, key: str) -> Font:
        return cls.__LINPG_GLOBAL_FONTS[key]

    # 获取全局文字
    @classmethod
    def get_global_font_size(cls, key: str) -> int:
        return cls.get_global_font(key).size

    # 获取全局文字
    @classmethod
    def render_global_font(
        cls, key: str, txt: str, color: color_liked, background_color: color_liked | None = None
    ) -> ImageSurface:
        return cls.get_global_font(key).render(txt, color, background_color)

    # 删除全局文字
    @classmethod
    def remove_global_font(cls, key: str) -> None:
        if key in cls.__LINPG_GLOBAL_FONTS:
            del cls.__LINPG_GLOBAL_FONTS[key]

    # 创建字体
    @staticmethod
    def create(size: int, bold: bool = False, italic: bool = False, underline: bool = False) -> Font:
        new_font_t = Font()
        new_font_t.update(size, bold, italic, underline)
        return new_font_t

    # 接受文字，颜色，文字大小，样式等信息，返回制作完的文字
    @classmethod
    def render(
        cls,
        txt: str | int | float,
        color: color_liked,
        size: int,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        background_color: color_liked | None = None,
    ) -> ImageSurface:
        cls.__LINPG_LAST_FONT.update(size, bold, italic, underline)
        return cls.__LINPG_LAST_FONT.render(txt, color, background_color)


# 艺术字效果
class ArtisticFonts:
    # 描述框效果
    @staticmethod
    def render_description_box(
        txt: str | int,
        color: color_liked,
        size: int,
        padding: int,
        background_color: color_liked,
        bold: bool = False,
        italic: bool = False,
        outline_color: color_liked | None = None,
        thickness: int = 2,
    ) -> ImageSurface:
        font_surface: ImageSurface = Fonts.render(txt, color, size, bold, italic)
        des_surface: ImageSurface = Surfaces.colored(
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

    # 渲染有轮廓的文字
    @staticmethod
    def render_with_outline(
        _text: str | int,
        color: color_liked,
        size: int,
        outline_thickness: int = 1,
        outline_color: color_liked = Colors.BLACK,
        bold: bool = False,
        italic: bool = False,
    ) -> ImageSurface:
        # 文字图层
        text_surface: ImageSurface = Fonts.render(_text, color, size, bold, italic).convert_alpha()
        # 外框图层
        outline_surface: ImageSurface = Fonts.render(_text, outline_color, size, bold, italic).convert_alpha()
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
        points.update(
            [(y, x) for x, y in points if x > y], [(-x, y) for x, y in points if x], [(x, -y) for x, y in points if y]
        )
        # 多次渲染外框图层
        for dx, dy in points:
            result_surface.blit(outline_surface, (dx + outline_thickness, dy + outline_thickness))
        # 渲染文字图层
        result_surface.blit(text_surface, (outline_thickness, outline_thickness))
        # 返回结果
        return result_surface
