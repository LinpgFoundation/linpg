# cython: language_level=3
from .mixer import *

_FONT_IS_NOT_INITIALIZED_MSG: str = "Font is not initialized!"

# 文字渲染模块
class FontGenerator:
    def __init__(self):
        self.__SIZE: int = 0
        self.__FONT = None
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
            EXCEPTION.fatal("Font size must be bigger than 0!")
        self.__SIZE = int(size)
        # 根据类型处理
        if Setting.font_type == "default":
            self.__FONT = pygame.font.SysFont(Setting.font, self.__SIZE, ifBold, ifItalic)
        elif Setting.font_type == "custom":
            font_path: str = os.path.join("Assets", "font", "{}.ttf".format(Setting.font))
            if os.path.exists(font_path):
                self.__FONT = pygame.font.Font(font_path, self.__SIZE)
            else:
                EXCEPTION.warn("Cannot find the {}.ttf file, the engine's font has been changed to default.".format(Setting.font))
                Setting.set_font("arial")
                Setting.set_font_type("default")
                self.__FONT = pygame.font.SysFont(Setting.font, self.__SIZE, ifBold, ifItalic)
            # 加粗
            if ifBold is True:
                self.__FONT.set_bold(ifBold)
            # 斜体
            if ifItalic is True:
                self.__FONT.set_italic(ifItalic)
        else:
            EXCEPTION.fatal("FontType option in setting file is incorrect!")
    # 渲染文字
    def render(self, txt: any, color: color_liked) -> ImageSurface:
        if self.__SIZE > 0:
            font_surface_t = self.__FONT.render(txt, Setting.antialias, Color.get(color))
            return font_surface_t.subsurface(font_surface_t.get_bounding_rect())
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)
    def render_to(self, surface: ImageSurface, pos: tuple[number], txt: any, color: color_liked) -> None:
        if self.__SIZE > 0:
            font_surface_t = self.__FONT.render(txt, Setting.antialias, Color.get(color))
            surface.blit(font_surface_t.subsurface(font_surface_t.get_bounding_rect()), pos)
        else:
            EXCEPTION.fatal(_FONT_IS_NOT_INITIALIZED_MSG)
    # 估计文字的宽度
    def estimate_text_width(self, text: any) -> int:
        return self.__FONT.size(text)[0]
    # 检测是否需要更新
    def check_for_update(self, size: int, ifBold: bool = False, ifItalic: bool = False) -> None:
        if self.__FONT is None or self.__SIZE != size or self.__FONT.bold != ifBold or self.__FONT.italic != ifItalic:
            self.update(size, ifBold, ifItalic)

# 文字渲染器管理模块
class FontManage:
    def __init__(self) -> None:
        # 引擎标准文件渲染器
        self.__LINPG_GLOBAL_FONTS: dict = {}
        # 上一次render的字体
        self.__LINPG_LAST_FONT: object = FontGenerator()
    # 设置全局文字
    def set_global_font(self, key: str, size: int, ifBold: bool = False, ifItalic: bool = False) -> None:
        if isinstance(size, int) and size > 0:
            if key not in self.__LINPG_GLOBAL_FONTS:
                self.__LINPG_GLOBAL_FONTS[key] = FontGenerator()
            self.__LINPG_GLOBAL_FONTS[key].update(size, ifBold, ifItalic)
        else:
            EXCEPTION.fatal("Font size must be positive interger not {}!".format(size))
    # 获取全局文字
    def get_global_font(self, key: str) -> FontGenerator:
        try:
            return self.__LINPG_GLOBAL_FONTS[key]
        except:
            EXCEPTION.fatal('You did not set any font named "{}".'.format(key))
    # 获取全局文字
    def get_global_font_size(self, key: str) -> int:
        return self.get_global_font(key).size
    # 获取全局文字
    def render_global_font(self, key: str, txt: str, color: color_liked) -> ImageSurface:
        return self.get_global_font(key).render(txt, color)
    # 删除全局文字
    def remove_global_font(self, key: str) -> bool:
        try:
            del self.__LINPG_GLOBAL_FONTS[key]
            return True
        except KeyError:
            EXCEPTION.warn('Cannot find font named "{}" when trying to remove the font.'.format(key))
            return False
    # 创建字体
    @staticmethod
    def create(size: int_f, ifBold: bool = False, ifItalic: bool = False) -> FontGenerator:
        new_font_t = FontGenerator()
        new_font_t.update(size, ifBold, ifItalic)
        return new_font_t
    # 文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
    def render(self, txt: any, color: color_liked, size: int_f, ifBold: bool = False, ifItalic: bool = False) -> ImageSurface:
        self.__LINPG_LAST_FONT.check_for_update(size, ifBold, ifItalic)
        return self.__LINPG_LAST_FONT.render(txt, color)
    # 文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
    def render_to(
        self, surface: ImageSurface, pos: tuple[number], txt: any, color: color_liked, size: int_f,
        ifBold: bool = False, ifItalic: bool = False
        ) -> None:
        self.__LINPG_LAST_FONT.check_for_update(size, ifBold, ifItalic)
        return self.__LINPG_LAST_FONT.render_to(surface, pos, txt, color)

Font: FontManage = FontManage()
