from .surface import *


class AbstractTextSurface(GameObject2d, Hidable, metaclass=ABCMeta):
    def __init__(self, text: str, x: int_f, y: int_f, size: int_f, _color: color_liked = Colors.BLACK, _bold: bool = False, _italic: bool = False) -> None:
        GameObject2d.__init__(self, x, y)
        Hidable.__init__(self)
        self.__text: str = text
        self.__size: int = int(size)
        self.__color: tuple[int, int, int, int] = Colors.get(_color)
        self.__bold: bool = _bold
        self.__italic: bool = _italic
        self.__alpha: int = 255

    @abstractmethod
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

    def get_alpha(self) -> int:
        return self.__alpha

    # 设置透明度
    def set_alpha(self, value: int) -> None:
        self.__alpha = value


# 高级文字类
class TextSurface(AbstractTextSurface):
    def __init__(self, text: str, x: int_f, y: int_f, size: int_f, _color: color_liked = Colors.BLACK, _bold: bool = False, _italic: bool = False) -> None:
        super().__init__(text, x, y, size, _color, _bold, _italic)
        self.__text_surface: ImageSurface | None = None
        self.__outline_thickness: int = 0
        self.__outline_color: tuple[int, int, int, int] = Colors.BLACK
        # 更新文字图层（需作为初始化的最后一步）
        self._update_text_surface()

    def _update_text_surface(self) -> None:
        if len(self.get_text()) == 0:
            self.__text_surface = None
        else:
            self.__text_surface = (
                Font.render(self.get_text(), self.get_color(), self.get_font_size(), self.get_bold(), self.get_italic())
                if self.__outline_thickness <= 0
                else ArtisticFont.render_with_outline(
                    self.get_text(), self.get_color(), self.get_font_size(), self.__outline_thickness, self.__outline_color, self.get_bold(), self.get_italic()
                )
            )

    def _get_text_surface(self) -> ImageSurface | None:
        return self.__text_surface

    # 设置轮廓粗细
    def set_outline_thickness(self, _thickness: int) -> None:
        self.__outline_thickness = max(_thickness, 1)
        self._update_text_surface()

    # 设置轮廓颜色
    def set_outline_color(self, _color: color_liked) -> None:
        self.__outline_color = Colors.get(_color)
        self._update_text_surface()

    # 关闭轮廓渲染
    def disable_outline(self) -> None:
        self.__outline_thickness = 0
        self._update_text_surface()

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
            _surface.blit(self.__text_surface, Coordinates.add(self.pos, offSet, (-self.__outline_thickness, -self.__outline_thickness)))


# 动态文字类
class ResizeWhenHoveredTextSurface(TextSurface):
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
    ) -> None:
        super().__init__(text, x, y, original_size, _color, _bold, _italic)
        self.__text_when_hovered = TextSurface(text, 0, 0, size_when_hovered, _color, _bold, _italic)
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

    # 设置轮廓粗细
    def set_outline_thickness(self, _thickness: int) -> None:
        super().set_outline_thickness(_thickness)
        self.__text_when_hovered.set_outline_thickness(_thickness)

    # 设置轮廓颜色
    def set_outline_color(self, _color: color_liked) -> None:
        super().set_outline_color(_color)
        self.__text_when_hovered.set_outline_color(_color)

    # 关闭轮廓渲染
    def disable_outline(self) -> None:
        super().disable_outline()
        self.__text_when_hovered.disable_outline()

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
