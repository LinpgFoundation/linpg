# cython: language_level=3
from .progressbar import *

# 按钮
class Button(AbstractImage):
    def __init__(self, img: ImageSurface, x: int, y: int, width: int = -1, height: int = -1, tag:str=""):
        if width < 0: width = img.get_width()
        if height < 0: height = img.get_height()
        super().__init__(img, x, y, width, height, tag)
        # self.img是未被触碰时的默认图片，img2是被鼠标触碰时展示的图片
        self.img2 = None
        self.__is_hovered: bool = False
    def set_hover_img(self, img: ImageSurface) -> None:
        self.img2 = img
    def has_been_hovered(self) -> bool:
        return self.__is_hovered
    def display(self, surface: ImageSurface, offSet: pos_liked = Origin) -> None:
        self.__is_hovered = self.is_hover(subtract_pos(Controller.mouse.pos, offSet))
        surface.blit(resize_img(
            self.img2 if self.__is_hovered is True and self.img2 is not None else self.img,
            self.size
            ),
            add_pos(self.pos, offSet)
            )

# 加载按钮
def load_button(
    path: Union[str, ImageSurface],
    position: tuple,
    size: tuple,
    alpha_when_not_hover: int = 255
    ) -> Button:
    if alpha_when_not_hover < 255:
        fading_button = Button(
            load_img(path, alpha=alpha_when_not_hover),
            position[0], position[1],
            size[0], size[1]
            )
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return Button(load_img(path), position[0], position[1], size[0], size[1])

# 加载中间有文字按钮
def load_button_with_text_in_center(
    path: Union[str, ImageSurface],
    txt: any,
    font_color: any,
    font_size: int,
    position: tuple,
    alpha_when_not_hover: int = 255
    ) -> Button:
    txt_surface = render_font_without_bounding(txt, Color.get(font_color), font_size)
    panding: int = int(font_size * 0.3)
    img = load_img(path,size=(txt_surface.get_width()+panding*2,txt_surface.get_height()+panding*2))
    img.blit(txt_surface, (panding, panding))
    return load_button(img, position, img.get_size(), alpha_when_not_hover)

# 带描述的按钮
class ButtonWithDes(Button):
    def __init__(self, img: ImageSurface, des: str, x: int, y: int, width: int = -1, height: int = -1, tag:str=""):
        super().__init__(img, x, y, width, height, tag)
        self.des = des
        font_surface = render_font_without_bounding(des, "black", self._height * 0.5)
        panding: int = int(font_surface.get_height() / 2)
        self.des_surface = new_surface((font_surface.get_width()+panding*2, font_surface.get_height()+panding*2)).convert_alpha()
        self.des_surface.fill(Color.WHITE)
        draw_rect(self.des_surface, Color.BLACK, new_rect((0, 0), self.des_surface.get_size()), 2)
        self.des_surface.blit(font_surface, (panding, panding))
    def display(self, surface: ImageSurface, offSet: pos_liked = Origin) -> None:
        super().display(surface, offSet)
        if self.has_been_hovered():
            surface.blit(self.des_surface, Controller.mouse.pos)

# 带描述的按钮
class ButtonWithDes(Button):
    def __init__(self, img: ImageSurface, des: str, x: int, y: int, width: int = -1, height: int = -1, tag:str=""):
        super().__init__(img, x, y, width, height, tag)
        self.des = des
        font_surface = render_font_without_bounding(des, "black", self._height * 0.5)
        panding: int = int(font_surface.get_height() / 2)
        self.des_surface = new_surface((font_surface.get_width()+panding*2, font_surface.get_height()+panding*2)).convert_alpha()
        self.des_surface.fill(Color.WHITE)
        draw_rect(self.des_surface, Color.BLACK, new_rect((0, 0), self.des_surface.get_size()), 2)
        self.des_surface.blit(font_surface, (panding, panding))
    def display(self, surface: ImageSurface, offSet: pos_liked = Origin) -> None:
        super().display(surface, offSet)
        if self.has_been_hovered(): surface.blit(self.des_surface, Controller.mouse.pos)

# 加载按钮
def load_button_with_des(
    path: Union[str, ImageSurface],
    tag: str,
    position: tuple,
    size: tuple,
    alpha_when_not_hover: int = 255
    ) -> ButtonWithDes:
    if alpha_when_not_hover < 255:
        fading_button = ButtonWithDes(
            load_img(path, alpha=alpha_when_not_hover),
            tag,
            position[0],
            position[1],
            size[0],
            size[1]
            )
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return ButtonWithDes(load_img(path), tag, position[0], position[1], size[0], size[1])
