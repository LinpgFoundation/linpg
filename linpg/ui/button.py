from ..core import *

# 按钮
class Button(AbstractImageSurface):
    def __init__(self, img: ImageSurface, x: int, y: int, width: int = -1, height: int = -1, tag: str = ""):
        if width < 0:
            width = img.get_width()
        if height < 0:
            height = img.get_height()
        super().__init__(img, x, y, width, height, tag)
        # self.img是未被触碰时的默认图片，img2是被鼠标触碰时展示的图片
        self.img2 = None
        self.__is_hovered: bool = False

    def set_hover_img(self, img: ImageSurface) -> None:
        self.img2 = img

    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    def display(self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN) -> None:
        if not self.hidden:
            self.__is_hovered = self.is_hovered(Controller.mouse.pos, offSet)
            surface.blit(
                IMG.resize(self.img2 if self.__is_hovered is True and self.img2 is not None else self.img, self.size),
                Pos.add(self.pos, offSet),
            )
        else:
            self.__is_hovered = False


# 加载按钮
def load_button(path: PoI, position: tuple, size: tuple, alpha_when_not_hover: int = 255) -> Button:
    if alpha_when_not_hover < 255:
        fading_button = Button(IMG.load(path, alpha=alpha_when_not_hover), position[0], position[1], size[0], size[1])
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return Button(IMG.load(path), position[0], position[1], size[0], size[1])


# 加载中间有文字按钮
def load_button_with_text_in_center(
    path: PoI, txt: str, font_color: color_liked, font_size: int, position: tuple, alpha_when_not_hover: int = 255
) -> Button:
    txt_surface = Font.render(txt, font_color, font_size)
    panding: int = int(font_size * 0.5)
    img = IMG.load(path, size=(txt_surface.get_width() + panding * 4, txt_surface.get_height() + panding * 2))
    img.blit(txt_surface, (panding * 2, panding))
    return load_button(img, position, img.get_size(), alpha_when_not_hover)


# 带描述的按钮
class ButtonWithDes(Button):
    def __init__(
        self, img: ImageSurface, des: str, x: int, y: int, width: int = -1, height: int = -1, tag: str = ""
    ) -> None:
        super().__init__(img, x, y, width, height, tag)
        self.des: str = str(des)
        self.des_surface = Font.render_description_box(
            self.des, Color.BLACK, self.get_height() * 0.4, self.get_height() * 0.2, Color.WHITE
        )

    def display(self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN) -> None:
        super().display(surface, offSet)
        if self.has_been_hovered():
            surface.blit(self.des_surface, Controller.mouse.pos)


# 加载按钮
def load_button_with_des(
    path: PoI, tag: str, position: tuple, size: tuple, alpha_when_not_hover: int = 255
) -> ButtonWithDes:
    if alpha_when_not_hover < 255:
        fading_button = ButtonWithDes(
            IMG.load(path, alpha=alpha_when_not_hover), tag, position[0], position[1], size[0], size[1]
        )
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return ButtonWithDes(IMG.load(path), tag, position[0], position[1], size[0], size[1])
