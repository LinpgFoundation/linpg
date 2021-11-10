from typing import overload
from .shape import *

# 新建一个形状类
def new_rect(pos: tuple, size: tuple) -> Rect:
    return Rect(pos[0], pos[1], size[0], size[1])


# 画正方形（的方块）
def draw_rect(surface: ImageSurface, color: color_liked, rect: RectLiked, thickness: int = 0) -> None:
    if isinstance(rect, (pygame.Rect, tuple)):
        Square.draw_(surface, Color.get(color), rect, thickness)
    elif isinstance(rect, Rect):
        Square.draw_(surface, Color.get(color), rect.get_rect(), thickness)
    else:
        EXCEPTION.fatal('You need to put in a rect liked object, and "{0}" is a "{1}".'.format(rect, type(rect)))


# 转换pygame的rect类至linpg引擎的rect类
def convert_rect(rect: RectLiked) -> Rect:
    # 确认是pygame.Rect类再转换
    if isinstance(rect, pygame.Rect):
        return Rect(rect.x, rect.y, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return new_rect(rect[0], rect[1])
        elif len(rect) == 4:
            return Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.fatal("Invalid length for forming a rect.")
    # 如果是Rect类，则没必要转换
    elif isinstance(rect, Rect):
        return rect
    else:
        EXCEPTION.fatal('The rect has to be RectLiked object, not "{}".'.format(type(rect)))


# 转换linpg.Rect至pygame.Rect
def convert_to_pygame_rect(rect: RectLiked) -> pygame.Rect:
    # 如果是pygame.Rect类，则没必要转换
    if isinstance(rect, pygame.Rect):
        return rect
    # 确认是linpg.Rect类再转换
    elif isinstance(rect, Rect):
        return pygame.Rect(rect.left, rect.top, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return pygame.Rect(rect[0], rect[1])
        elif len(rect) == 4:
            return pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.fatal("Invalid length for forming a rect.")
    else:
        EXCEPTION.fatal('The rect has to be RectLiked object, not "{}".'.format(type(rect)))


# 是否形状一样
def is_same_rect(rect1: RectLiked, rect2: RectLiked) -> bool:
    # 确保两个输入的类rect的物品都不是tuple
    if isinstance(rect1, tuple):
        convert_rect(rect1)
    if isinstance(rect2, tuple):
        convert_rect(rect2)
    # 比较并返回结果
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height


# 检测图片是否被点击
def is_hover(imgObject: object, objectPos: Iterable = Pos.ORIGIN, off_set_x: number = 0, off_set_y: number = 0) -> bool:

    """将会在3.2中弃置"""

    return is_hovering(imgObject, objectPos, off_set_x, off_set_y)


# 检测图片是否被点击
def is_hovering(imgObject: object, objectPos: Iterable = Pos.ORIGIN, off_set_x: number = 0, off_set_y: number = 0) -> bool:
    # 如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    if isinstance(imgObject, GameObject2d):
        return imgObject.is_hovered(Controller.mouse.pos, (off_set_x, off_set_y))
    # 如果是pygame类
    else:
        mouse_pos: tuple[number]
        # 如果是Surface类
        if isinstance(imgObject, ImageSurface):
            mouse_pos = Pos.subtract(Controller.mouse.pos, (off_set_x, off_set_y), objectPos)
        # 如果是Rect类
        elif isinstance(imgObject, pygame.Rect):
            mouse_pos = Pos.subtract(Controller.mouse.pos, (off_set_x, off_set_y), (imgObject.x, imgObject.y))
        else:
            EXCEPTION.fatal("Unable to check current object: {0} (type:{1})".format(imgObject, type(imgObject)))
        # 返回结果
        return 0 < mouse_pos[0] < imgObject.get_width() and 0 < mouse_pos[1] < imgObject.get_height()


# 获取图片的subsurface
def get_img_subsurface(img: ImageSurface, rect: RectLiked) -> ImageSurface:
    return img.subsurface(rect if isinstance(rect, pygame.Rect) else convert_to_pygame_rect(rect))


# 画圆形
def draw_circle(surface: ImageSurface, color: color_liked, center_pos: tuple[int], radius: int, thickness: int = 0) -> None:
    Circle.draw_(surface, Color.get(color), center_pos, radius, thickness)