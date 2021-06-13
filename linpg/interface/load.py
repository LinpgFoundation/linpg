# cython: language_level=3

from ..battle import *

class Loader:
    def __init__(self) -> None:
        pass
    def img(self, path:str, size:tuple=tuple(), alpha:int=255, ifConvertAlpha:bool=True) -> ImageSurface:
        return load_img(path, size, alpha, ifConvertAlpha)
    def static_image(self, path:str, position:tuple, size:tuple=(-1,-1), tag:str="deafult", ifConvertAlpha:bool=True) -> StaticImage:
        return load_static_image(path, position, size[0], size[1], tag, ifConvertAlpha)
    def button(self, path:str, position:tuple, size:tuple, alpha_when_not_hover:int=255):
        return load_button(path, position, size, alpha_when_not_hover)
    def button_with_text_in_center(
        self, path:str, txt: any, font_color: any, font_size: int, position: tuple, alpha_when_not_hover: int = 255
        ) -> None:
        return load_button_with_text_in_center(path, txt, font_color, font_size, position, alpha_when_not_hover)

load:Loader = Loader()