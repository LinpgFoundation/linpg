from .shape import *

RectLiked = Union[Rectangle, pygame.rect.Rect, tuple]

# Rectangle方法管理
class Rectangles:
    # 是否2个Rectangle形状一样
    @staticmethod
    def equal(rect1: Optional[Rectangle], rect2: Optional[Rectangle]) -> bool:
        if rect1 is not None and rect2 is not None:
            return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height
        else:
            return rect1 == rect2

    # 转换pygame的rect类至linpg引擎的rect类
    @staticmethod
    def create(rect: RectLiked) -> Rectangle:
        # 如果是Rect类，则没必要转换
        if isinstance(rect, Rectangle):
            return rect
        # 如果是pygame.Rect类则需转换
        elif isinstance(rect, pygame.Rect):
            return Rectangle(rect.x, rect.y, rect.width, rect.height)
        # 如果是tuple类，则需要创建
        elif isinstance(rect, tuple):
            if len(rect) == 2:
                return Rectangle(rect[0][0], rect[0][1], rect[1][0], rect[1][1])
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
