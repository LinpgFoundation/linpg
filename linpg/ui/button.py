from ..core import *

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
class IconForButton(AbstractButton):
    def __init__(self, img: ImageSurface, width: int = -1, height: int = -1, tag: str = ""):
        super().__init__(img, 0, 0, width=width, height=height, tag=tag)
        # 是否被触碰的flag
        self.__is_hovered: bool = False

    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    def set_is_hovered(self, value: bool) -> None:
        self.__is_hovered = value


# 按钮的简单实现
class Button(AbstractButton):
    def __init__(self, img: ImageSurface, x: int, y: int, width: int = -1, height: int = -1, tag: str = ""):
        super().__init__(img, x, y, width=width, height=height, tag=tag)
        # 是否被触碰的flag
        self.__is_hovered: bool = False
        # 图标
        self.__icon: Optional[IconForButton] = None

    def set_icon(self, _icon: IconForButton) -> None:
        self.__icon = _icon

    def get_icon(self) -> Optional[IconForButton]:
        return self.__icon

    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            self.__is_hovered = self.is_hovered(offSet)
            super().display(surface, offSet)
            if self.__icon is not None:
                self.__icon.set_is_hovered(self.has_been_hovered())
                self.__icon.set_right(self.x + offSet[0])
                self.__icon.set_centery(self.centery + offSet[1])
                self.__icon.draw(surface)
        else:
            self.__is_hovered = False


# 加载按钮
def load_button(path: PoI, position: tuple[int, int], size: tuple[int, int], alpha_when_not_hover: int = 255) -> Button:
    if alpha_when_not_hover < 255:
        fading_button = Button(IMG.load(path, alpha=alpha_when_not_hover), position[0], position[1], size[0], size[1])
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return Button(IMG.quickly_load(path), position[0], position[1], size[0], size[1])


# 加载按钮图标
def load_button_icon(path: PoI, size: tuple[int, int], alpha_when_not_hover: int = 255) -> IconForButton:
    if alpha_when_not_hover < 255:
        fading_button = IconForButton(IMG.load(path, alpha=alpha_when_not_hover), size[0], size[1])
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return IconForButton(IMG.quickly_load(path), size[0], size[1])


# 加载中间有文字按钮
def load_button_with_text_in_center(
    path: PoI, txt: str, font_color: color_liked, font_size: int, position: tuple[int, int], alpha_when_not_hover: int = 255
) -> Button:
    txt_surface = Font.render(txt, font_color, font_size)
    panding: int = int(font_size * 0.5)
    _img: ImageSurface = (
        IMG.load(path, size=(txt_surface.get_width() + panding * 4, txt_surface.get_height() + panding * 2))
        if path != "<!transparent>"
        else new_transparent_surface((txt_surface.get_width() + panding * 4, txt_surface.get_height() + panding * 2))
    )
    _img.blit(txt_surface, (panding * 2, panding))
    return load_button(_img, position, _img.get_size(), alpha_when_not_hover)


# 加载中间有文字按钮
def load_button_with_text_in_center_and_different_background(
    path: PoI,
    path2: PoI,
    txt: str,
    font_color: color_liked,
    font_size: int,
    position: tuple[int, int],
    alpha_when_not_hover: int = 255,
) -> Button:
    txt_surface = Font.render(txt, font_color, font_size)
    panding: int = int(font_size * 0.5)
    img = IMG.load(path, size=(txt_surface.get_width() + panding * 4, txt_surface.get_height() + panding * 2))
    img.blit(txt_surface, (panding * 2, panding))
    img2 = IMG.load(path2, size=(txt_surface.get_width() + panding * 4, txt_surface.get_height() + panding * 2))
    img2.blit(txt_surface, (panding * 2, panding))
    button_temp = load_button(img, position, img.get_size(), alpha_when_not_hover)
    button_temp.set_hover_img(img2)
    return button_temp


# 带描述的按钮
class ButtonWithDes(Button):
    def __init__(self, img: ImageSurface, des: str, x: int, y: int, width: int = -1, height: int = -1, tag: str = "") -> None:
        super().__init__(img, x, y, width, height, tag)
        self.des: str = str(des)
        self.des_surface = Font.render_description_box(
            self.des, Colors.BLACK, self.get_height() * 0.4, int(self.get_height() * 0.2), Colors.WHITE
        )

    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        super().display(surface, offSet)
        if self.has_been_hovered():
            surface.blit(self.des_surface, Controller.mouse.pos)


# 加载按钮
def load_button_with_des(
    path: PoI, tag: str, position: tuple[int, int], size: tuple[int, int], alpha_when_not_hover: int = 255
) -> ButtonWithDes:
    if alpha_when_not_hover < 255:
        imgT: ImageSurface = IMG.load(path, alpha=alpha_when_not_hover)
        fading_button = ButtonWithDes(imgT, tag, position[0], position[1], size[0], size[1])
        fading_button.set_hover_img(imgT.copy())
        return fading_button
    else:
        return ButtonWithDes(IMG.load(path), tag, position[0], position[1], size[0], size[1])
