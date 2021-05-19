# cython: language_level=3
from .progressbar import *

#按钮
class Button(AbstractImage):
    def __init__(self, img:ImageSurface, x:int, y:int, width:int=-1, height:int=-1):
        if width < 0: width = img.get_width()
        if height < 0: height = img.get_height()
        super().__init__(img, x, y, width, height)
        #self.img是未被触碰时的默认图片，img2是被鼠标触碰时展示的图片
        self.img2 = None
        self.__is_hovered:bool = False
    def set_hover_img(self, img:ImageSurface) -> None: self.img2 = img
    def has_been_hovered(self) -> bool: return self.__is_hovered
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        self.__is_hovered = self.is_hover(subtract_pos(controller.get_mouse_pos(), offSet))
        surface.blit(resize_img(
            self.img2 if self.__is_hovered is True and self.img2 is not None else self.img,
            self.size), add_pos(self.pos, offSet)
            )

#带描述的按钮
class ButtonWithDes(Button):
    def __init__(self, img:ImageSurface, des:str, x:int, y:int, width:int=-1, height:int=-1):
        super().__init__(img, x, y, width, height)
        self.des = des
        font_surface = render_font_without_bounding(des,"black",self._height*0.5)
        panding:int = int(font_surface.get_height()/2)
        self.des_surface = new_surface((font_surface.get_width()+panding*2,font_surface.get_height()+panding*2)).convert_alpha()
        self.des_surface.fill(get_color_rbga("white"))
        draw_rect(self.des_surface,get_color_rbga("black"), Shape(0,0,self.des_surface.get_width(),self.des_surface.get_height()), 2)
        self.des_surface.blit(font_surface,(panding,panding))
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        super().display(surface, offSet)
        if self.has_been_hovered(): surface.blit(self.des_surface, controller.get_mouse_pos())

