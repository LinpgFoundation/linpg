# cython: language_level=3
from .font import *

"""（即将弃置）"""
# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_dynamic_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> DynamicImage:
    return DynamicImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag
        )

"""（即将弃置）"""
# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_static_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> StaticImage:
    return StaticImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag
        )

"""（即将弃置）"""
# 高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_movable_image(
    path: Union[str, ImageSurface],
    position: tuple,
    target_position: tuple,
    moveSpeed: tuple = (0, 0),
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag="default",
    ifConvertAlpha: bool = True
    ) -> MovableImage:
    return MovableImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        target_position[0],
        target_position[1],
        moveSpeed[0],
        moveSpeed[1],
        int(width),
        int(height),
        tag
        )
