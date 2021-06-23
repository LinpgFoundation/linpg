# cython: language_level=3
from ..battle import *

class Loader:
    def __init__(self) -> None:
        pass
    # 原始图片
    def img(self, path:str, size:tuple=tuple(), alpha:int=255, ifConvertAlpha:bool=True) -> ImageSurface:
        return load_img(path, size, alpha, ifConvertAlpha)
    # 静态图片
    def static_image(self, path:str, position:tuple, size:tuple=(-1,-1), tag:str="deafult") -> StaticImage:
        return StaticImage(path, position[0], position[1], size[0], size[1], tag)
    # 动态图片
    def dynamic_image(self, path:str, position:tuple, size:tuple=(-1,-1), tag:str="deafult") -> DynamicImage:
        return DynamicImage(path, position[0], position[1], size[0], size[1], tag)
    # 可自行移动的图片
    def movable_image(self, path:str, position:tuple, target_position:tuple, move_speed:tuple=(0,0), size:tuple=(-1,-1), tag="default") -> MovableImage:
        return MovableImage(path, position[0], position[1], target_position[0], target_position[1], move_speed[0], move_speed[1], size[0], size[1], tag)
    def button(self, path:str, position:tuple, size:tuple, alpha_when_not_hover:int=255) -> Button:
        return load_button(path, position, size, alpha_when_not_hover)
    def button_with_text_in_center(
        self, path:str, txt: any, font_color: any, font_size: int, position: tuple, alpha_when_not_hover: int = 255
        ) -> Button:
        return load_button_with_text_in_center(path, txt, font_color, font_size, position, alpha_when_not_hover)

load:Loader = Loader()