from .shape import *

# 无数据的RECT，用于规范化Typing
NULL_RECT: Rectangle = Rectangle(1, 1, -2, -2)

RectLiked = Union[Rectangle, pygame.Rect, tuple]

# 新建一个形状类
def new_rect(pos: tuple, size: tuple) -> Rectangle:
    return Rectangle(pos[0], pos[1], size[0], size[1])


# 画正方形（的方块）
def draw_rect(surface: ImageSurface, color: color_liked, rect: RectLiked, thickness: int = 0) -> None:
    if isinstance(rect, (pygame.Rect, tuple)):
        Square.draw_(surface, Colors.get(color), rect, thickness)
    elif isinstance(rect, Rectangle):
        Square.draw_(surface, Colors.get(color), rect.get_rect(), thickness)
    else:
        EXCEPTION.fatal('You need to put in a rect liked object, and "{0}" is a "{1}".'.format(rect, type(rect)))


# 转换pygame的rect类至linpg引擎的rect类
def convert_rect(rect: RectLiked) -> Rectangle:
    # 确认是pygame.RectSSS类再转换
    if isinstance(rect, pygame.Rect):
        return Rectangle(rect.x, rect.y, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return new_rect(rect[0], rect[1])
        elif len(rect) == 4:
            return Rectangle(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.fatal("Invalid length for forming a rect.")
    # 如果是Rect类，则没必要转换
    elif isinstance(rect, Rectangle):
        return rect
    else:
        EXCEPTION.fatal('The rect has to be RectLiked object, not "{}".'.format(type(rect)))


# 转换linpg.Rect至pygame.RectSSS
def convert_to_pygame_rect(rect: RectLiked) -> pygame.Rect:
    # 如果是pygame.RectSSS类，则没必要转换
    if isinstance(rect, pygame.Rect):
        return rect
    # 确认是linpg.Rect类再转换
    elif isinstance(rect, Rectangle):
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
    rect1_t: Rectangle = convert_rect(rect1) if not isinstance(rect1, Rectangle) else rect1
    rect2_t: Rectangle = convert_rect(rect2) if not isinstance(rect1, Rectangle) else rect2
    # 比较并返回结果
    return (
        rect1_t.x == rect2_t.x
        and rect1_t.y == rect2_t.y
        and rect1_t.width == rect2_t.width
        and rect1_t.height == rect2_t.height
    )


# 检测pygame类2d模型是否被点击
def is_hovering(imgObject: object, objectPos: Iterable = ORIGIN) -> bool:
    # 如果是Surface类
    if isinstance(imgObject, ImageSurface):
        mouse_pos = Positions.subtract(Controller.mouse.pos, objectPos)
    else:
        EXCEPTION.fatal("Unable to check current object: {0} (type:{1})".format(imgObject, type(imgObject)))
    # 返回结果
    return 0 < mouse_pos[0] < imgObject.get_width() and 0 < mouse_pos[1] < imgObject.get_height()


# 获取图片的subsurface
def get_img_subsurface(img: ImageSurface, rect: RectLiked) -> ImageSurface:
    return img.subsurface(rect if isinstance(rect, pygame.Rect) else convert_to_pygame_rect(rect))


# 画圆形
def draw_circle(
    surface: ImageSurface, color: color_liked, center_pos: tuple[int, int], radius: int, thickness: int = 0
) -> None:
    Circle.draw_(surface, Colors.get(color), center_pos, radius, thickness)
