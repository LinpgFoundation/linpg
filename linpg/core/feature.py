from .shape import *

# 无数据的RECT，用于规范化Typing
NULL_RECT: Rectangle = Rectangle(1, 1, -2, -2)

RectLiked = Union[Rectangle, pygame.rect.Rect, tuple]

# 转换pygame的rect类至linpg引擎的rect类
def convert_rect(rect: RectLiked) -> Rectangle:
    # 如果是Rect类，则没必要转换
    if isinstance(rect, Rectangle):
        return rect
    # 如果是pygame.Rect类则需转换
    elif isinstance(rect, pygame.Rect):
        return Rectangle(rect.x, rect.y, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return Rectangle.new(rect[0], rect[1])
        elif len(rect) == 4:
            return Rectangle(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.fatal("Invalid length for forming a rect.")
    else:
        EXCEPTION.fatal('The rect has to be RectLiked object, not "{}".'.format(type(rect)))


# 转换linpg.Rect至pygame.Rect
def convert_to_pygame_rect(rect: RectLiked) -> pygame.rect.Rect:
    # 如果是pygame.Rect类，则没必要转换
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
    rect1_t: Rectangle = convert_rect(rect1)
    rect2_t: Rectangle = convert_rect(rect2)
    # 比较并返回结果
    return (
        rect1_t.x == rect2_t.x and rect1_t.y == rect2_t.y and rect1_t.width == rect2_t.width and rect1_t.height == rect2_t.height
    )


# 检测pygame类2d模型是否被点击
def is_hovering(imgObject: ImageSurface, objectPos: tuple = ORIGIN) -> bool:
    # 计算坐标
    mouse_pos: tuple = Positions.subtract(Controller.mouse.pos, objectPos)
    # 返回结果
    try:
        return bool(0 < mouse_pos[0] < imgObject.get_width() and 0 < mouse_pos[1] < imgObject.get_height())
    except Exception:
        EXCEPTION.fatal("Unable to check current object: {0} (type:{1})".format(imgObject, type(imgObject)))


# 获取图片的subsurface
def get_img_subsurface(img: ImageSurface, rect: RectLiked) -> ImageSurface:
    return img.subsurface(rect if isinstance(rect, pygame.Rect) else convert_to_pygame_rect(rect))
