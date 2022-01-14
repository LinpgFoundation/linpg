from ..core import *


class ButtonText(StaticTextSurface):
    def __init__(
        self,
        text: str,
        size: int_f,
        _color: color_liked = Colors.BLACK,
        _bold: bool = False,
        _italic: bool = False,
        alpha_when_not_hover: int = 255,
    ) -> None:
        super().__init__(text, 0, 0, size, _color=_color, _bold=_bold, _italic=_italic)
        self.__text_surface_2: Optional[ImageSurface] = None
        self.__alpha_when_not_hover: int = alpha_when_not_hover
        if self.__alpha_when_not_hover != 255:
            self.__text_surface_2 = self._get_text_surface().copy()
            self.__text_surface_2.set_alpha(self.__alpha_when_not_hover)
        # 是否被触碰的flag
        self.__is_hovered: bool = False

    def _update_text_surface(self) -> None:
        super()._update_text_surface()
        if self.__alpha_when_not_hover != 255:
            self.__text_surface_2 = self._get_text_surface().copy()
            self.__text_surface_2.set_alpha(self.__alpha_when_not_hover)

    def set_is_hovered(self, value: bool) -> None:
        self.__is_hovered = value

    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.__text_surface_2 is None or self.__is_hovered is True:
            super().display(surface, offSet)
        else:
            surface.blit(self.__text_surface_2, Coordinates.add(self.pos, offSet))


# 多态按钮（请勿在引擎外实体化）
class AbstractButton(AbstractImageSurface):
    def __init__(self, img: ImageSurface, x: int, y: int, width: int = -1, height: int = -1, tag: str = ""):
        if width < 0:
            width = img.get_width()
        if height < 0:
            height = img.get_height()
        super().__init__(img, x, y, width, height, tag)
        # self.img是未被触碰时的默认图片，img2是被鼠标触碰时展示的图片
        self.__img2: ImageSurface = NULL_SURFACE

    def has_been_hovered(self) -> bool:
        return False

    def set_hover_img(self, img: ImageSurface) -> None:
        self.__img2 = img

    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.has_been_hovered() is True and self.__img2 is not NULL_SURFACE:
            surface.blit(IMG.resize(self.__img2, self.size), Coordinates.add(self.pos, offSet))
        elif self.img is not NULL_SURFACE:
            surface.blit(IMG.resize(self.img, self.size), Coordinates.add(self.pos, offSet))


# 按钮的简单实现
class ButtonComponent(AbstractButton):
    def __init__(self, img: ImageSurface, width: int = -1, height: int = -1, tag: str = ""):
        super().__init__(img, 0, 0, width=width, height=height, tag=tag)
        # 是否被触碰的flag
        self.__is_hovered: bool = False

    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    def set_is_hovered(self, value: bool) -> None:
        self.__is_hovered = value

    # 加载按钮图标
    @staticmethod
    def icon(path: PoI, size: tuple[int, int], alpha_when_not_hover: int = 255) -> "ButtonComponent":
        if alpha_when_not_hover < 255:
            fading_button = ButtonComponent(IMG.load(path, alpha=alpha_when_not_hover), size[0], size[1])
            img2 = fading_button.get_image_copy()
            img2.set_alpha(255)
            fading_button.set_hover_img(img2)
            return fading_button
        else:
            return ButtonComponent(IMG.quickly_load(path), size[0], size[1])

    @staticmethod
    def text(
        text: str,
        size: int_f,
        _color: color_liked = Colors.BLACK,
        _bold: bool = False,
        _italic: bool = False,
        alpha_when_not_hover: int = 255,
    ) -> ButtonText:
        return ButtonText(text, size, _color, _bold, _italic, alpha_when_not_hover)


# 按钮的简单实现
class Button(AbstractButton):
    def __init__(self, img: ImageSurface, x: int, y: int, width: int = -1, height: int = -1, tag: str = ""):
        super().__init__(img, x, y, width=width, height=height, tag=tag)
        # 是否被触碰的flag
        self.__is_hovered: bool = False
        # 图标
        self.__icon: Optional[ButtonComponent] = None
        # 文字
        self.__text: Optional[ButtonText] = None
        # 描述
        self.__description: str = ""
        self.__description_surface: Optional[ImageSurface] = None
        # 是否根据component自动改变宽度
        self.__resize_based_on_components: bool = False
        self.__scale_for_resizing_width : number = 1.2
        self.__scale_for_resizing_height : number = 2

    # 加载按钮
    @staticmethod
    def load(path: PoI, position: tuple[int, int], size: tuple[int, int], alpha_when_not_hover: int = 255) -> "Button":
        if alpha_when_not_hover < 255:
            fading_button: Button = Button(IMG.load(path, alpha=alpha_when_not_hover), position[0], position[1], size[0], size[1])
            img2 = fading_button.get_image_copy()
            img2.set_alpha(255)
            fading_button.set_hover_img(img2)
            return fading_button
        else:
            return Button(IMG.quickly_load(path), position[0], position[1], size[0], size[1])

    # 自动缩放
    def set_auto_resize(self, value: bool) -> None:
        if self.__resize_based_on_components is False and value is True:
            self.__resize_based_on_components = True
            self.__check_if_resize_needed()
        else:
            self.__resize_based_on_components = value
    
    def set_scale_for_resizing_width(self, value: number = 1.2) -> None:
        self.__scale_for_resizing_width = value
        self.__check_if_resize_needed()
    
    def set_scale_for_resizing_height(self, value: number = 2) -> None:
        self.__scale_for_resizing_height = value
        self.__check_if_resize_needed()

    # 检测是否需要更新
    def __check_if_resize_needed(self) -> None:
        if self.__resize_based_on_components is True:
            if self.__icon is not None and self.__text is not None:
                self.set_size(
                    (self.__icon.get_width() + self.__text.get_width()) * self.__scale_for_resizing_width,
                    max(self.__icon.get_height(), self.__text.get_height()) * self.__scale_for_resizing_height,
                )
            elif self.__icon is not None:
                self.set_size(self.__icon.get_width() * self.__scale_for_resizing_width, self.__icon.get_height() * self.__scale_for_resizing_height)
            elif self.__text is not None:
                self.set_size(self.__text.get_width() * self.__scale_for_resizing_width, self.__text.get_height() * self.__scale_for_resizing_height)
            else:
                self.set_size(0, 0)

    # 设置图标
    def set_icon(self, _icon: Optional[ButtonComponent] = None) -> None:
        self.__icon = _icon
        self.__check_if_resize_needed()

    # 获取图标
    def get_icon(self) -> Optional[ButtonComponent]:
        return self.__icon

    # 获取描述
    def get_description(self) -> str:
        return self.__description

    # 设置描述
    def set_description(self, value: str = "") -> None:
        self.__description = value
        self.__description_surface = (
            Font.render_description_box(
                self.__description, Colors.BLACK, int(self.get_height() / 5 * 2), int(self.get_height() / 5), Colors.WHITE
            )
            if len(self.__description) > 0
            else None
        )

    # 获取文字
    def get_text(self) -> Optional[ButtonText]:
        return self.__text

    # 设置文字
    def set_text(self, text_surface: Optional[ButtonText] = None) -> None:
        self.__text = text_surface
        self.__check_if_resize_needed()

    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            self.__is_hovered = self.is_hovered(offSet)
            super().display(surface, offSet)
            # 计算x坐标轴
            if self.__icon is not None and self.__text is not None:
                # 计算真实尺寸
                self.__icon.set_left(
                    self.x + int((self.get_width() - self.__icon.get_width() - self.__text.get_width()) / 2) + offSet[0]
                )
                self.__text.set_left(self.__icon.right)
            elif self.__icon is not None:
                self.__icon.set_centerx(self.centerx + offSet[0])
            elif self.__text is not None:
                self.__text.set_centerx(self.centerx + offSet[0])
            # 画出图标
            if self.__icon is not None:
                self.__icon.set_is_hovered(self.__is_hovered)
                self.__icon.set_centery(self.centery + offSet[1])
                self.__icon.draw(surface)
            # 画出文字
            if self.__text is not None:
                self.__text.set_is_hovered(self.__is_hovered)
                self.__text.set_centery(self.centery + offSet[1])
                self.__text.draw(surface)
            # 画出描述（如果有的话）
            if self.__is_hovered and self.__description_surface is not None:
                surface.blit(self.__description_surface, Controller.mouse.pos)
        else:
            self.__is_hovered = False
