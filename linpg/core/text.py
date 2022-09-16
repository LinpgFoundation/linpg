from .surface import *


class AbstractTextSurface(GameObject2d, HidableSurface, metaclass=ABCMeta):
    def __init__(
        self,
        text: str,
        x: int_f,
        y: int_f,
        size: int_f,
        _color: color_liked = Colors.BLACK,
        _bold: bool = False,
        _italic: bool = False,
        _with_bounding: bool = False,
    ) -> None:
        GameObject2d.__init__(self, x, y)
        HidableSurface.__init__(self)
        self.__text: str = text
        self.__size: int = int(size)
        self.__color: tuple[int, int, int, int] = Colors.get(_color)
        self.__bold: bool = _bold
        self.__italic: bool = _italic
        self.__with_bounding: bool = _with_bounding
        self.__alpha: int = 255

    def _update_text_surface(self) -> None:
        EXCEPTION.fatal("_update_text_surface()", 1)

    def get_text(self) -> str:
        return self.__text

    def set_text(self, value: str) -> None:
        self.__text = value
        self._update_text_surface()

    def get_font_size(self) -> int:
        return self.__size

    def set_font_size(self, value: int) -> None:
        self.__size = value
        self._update_text_surface()

    def get_color(self) -> tuple[int, int, int, int]:
        return self.__color

    def set_color(self, _color: str) -> None:
        self.__color = Colors.get(_color)
        self._update_text_surface()

    def get_bold(self) -> bool:
        return self.__bold

    def set_bold(self, value: bool) -> None:
        self.__bold = value
        self._update_text_surface()

    def get_italic(self) -> bool:
        return self.__italic

    def set_italic(self, value: bool) -> None:
        self.__italic = value
        self._update_text_surface()

    def get_with_bounding(self) -> bool:
        return self.__with_bounding

    def set_with_bounding(self, value: bool) -> None:
        self.__with_bounding = value
        self._update_text_surface()

    def get_alpha(self) -> int:
        return self.__alpha

    # 设置透明度
    def set_alpha(self, value: int) -> None:
        self.__alpha = value


# 高级文字类
class StaticTextSurface(AbstractTextSurface):
    def __init__(
        self,
        text: str,
        x: int_f,
        y: int_f,
        size: int_f,
        _color: color_liked = Colors.BLACK,
        _bold: bool = False,
        _italic: bool = False,
        _with_bounding: bool = False,
    ) -> None:
        super().__init__(text, x, y, size, _color, _bold, _italic, _with_bounding)
        self.__text_surface: Optional[ImageSurface] = None
        self._update_text_surface()

    def _update_text_surface(self) -> None:
        self.__text_surface = (
            Font.render(self.get_text(), self.get_color(), self.get_font_size(), self.get_bold(), self.get_italic(), with_bounding=self.get_with_bounding())
            if self.get_text() != ""
            else None
        )

    def _get_text_surface(self) -> Optional[ImageSurface]:
        return self.__text_surface

    def set_text(self, value: str) -> None:
        if value != self.get_text():
            super().set_text(value)
            if self.__text_surface is not None and self.get_alpha() != 255:
                self.__text_surface.set_alpha(self.get_alpha())

    def set_font_size(self, value: int) -> None:
        if value != self.__size:
            super().set_font_size(value)

    def set_bold(self, value: bool) -> None:
        if self.get_bold() != value:
            super().set_bold(value)

    def set_italic(self, value: bool) -> None:
        if self.get_italic() != value:
            super().set_italic(value)

    def set_alpha(self, value: int) -> None:
        super().set_alpha(value)
        if self.__text_surface is not None:
            self.__text_surface.set_alpha(self.get_alpha())

    def get_width(self) -> int:
        return self.__text_surface.get_width() if self.__text_surface is not None else 0

    def get_height(self) -> int:
        return self.__text_surface.get_height() if self.__text_surface is not None else 0

    # 画出
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible() and self.__text_surface is not None:
            _surface.blit(self.__text_surface, Coordinates.add(self.pos, offSet))


class DynamicTextSurface(AbstractTextSurface):
    def __init__(
        self,
        text: str,
        x: int_f,
        y: int_f,
        size: int_f,
        _color: color_liked = Colors.BLACK,
        _bold: bool = False,
        _italic: bool = False,
        _with_bounding: bool = False,
    ) -> None:
        super().__init__(text, x, y, size, _color, _bold, _italic, _with_bounding)
        self.__FONT_GENERATOR: FontGenerator = FontGenerator()
        self.__FONT_GENERATOR.update(self.get_font_size(), self.get_bold(), self.get_italic())

    def _update_text_surface(self) -> None:
        self.__FONT_GENERATOR.update(self.get_font_size(), self.get_bold(), self.get_italic())

    def get_width(self) -> int:
        return self.__FONT_GENERATOR.estimate_text_width(self.get_text())

    def get_height(self) -> int:
        return self.__FONT_GENERATOR.estimate_text_height(self.get_text())

    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            _text_surface: ImageSurface = self.__FONT_GENERATOR.render(self.get_text(), self.get_color(), with_bounding=self.get_with_bounding())
            if self.get_alpha() != 255:
                _text_surface.set_alpha(255)
            _surface.blit(_text_surface, Coordinates.add(self.pos, offSet))


# 动态文字类
class ResizeWhenHoveredTextSurface(StaticTextSurface):
    def __init__(
        self,
        text: str,
        x: int_f,
        y: int_f,
        original_size: int_f,
        size_when_hovered: int_f,
        _color: color_liked = Colors.BLACK,
        _bold: bool = False,
        _italic: bool = False,
        _with_bounding: bool = False,
    ) -> None:
        super().__init__(text, x, y, original_size, _color, _bold, _italic, _with_bounding)
        self.__text_when_hovered = StaticTextSurface(text, 0, 0, size_when_hovered, _color, _bold, _italic, _with_bounding)
        self.__text_when_hovered.set_center(self.centerx, self.centery)
        self.__is_hovered: bool = False

    def set_color(self, _color: str) -> None:
        super().set_color(_color)
        self.__text_when_hovered.set_color(_color)

    def set_left(self, value: int_f) -> None:
        super().set_left(value)
        self.__text_when_hovered.set_centerx(self.centerx)

    def set_top(self, value: int_f) -> None:
        super().set_top(value)
        self.__text_when_hovered.set_centery(self.centery)

    def set_text(self, value: str) -> None:
        super().set_text(value)
        self.__text_when_hovered.set_text(value)

    def set_font_size(self, value: int) -> None:
        super().set_font_size(value)
        self.__text_when_hovered.set_font_size(value)

    def set_bold(self, value: bool) -> None:
        super().set_bold(value)
        self.__text_when_hovered.set_bold(value)

    def set_italic(self, value: bool) -> None:
        super().set_italic(value)
        self.__text_when_hovered.set_italic(value)

    def set_alpha(self, value: int) -> None:
        super().set_alpha(value)
        self.__text_when_hovered.set_alpha(value)

    # 用于检测触碰的快捷
    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    # 画出
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            self.__is_hovered = self.is_hovered(offSet)
            if not self.__is_hovered:
                super().display(_surface, offSet)
            else:
                self.__text_when_hovered.display(_surface, offSet)
        else:
            self.__is_hovered = False
