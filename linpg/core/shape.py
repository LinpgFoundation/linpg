# cython: language_level=3
from ..api import *

#用于兼容的形状类
class Shape(GameObject2d):
    def __init__(self, left:Union[int,float], top:Union[int,float], width:int, height:int):
        super().__init__(left,top)
        self._width:int = int(width)
        self._height:int = int(height)
    #宽度
    def get_width(self) -> int: return self._width
    def set_width(self, value:Union[int,float]) -> None: self._width = int(value)
    #高度
    def get_height(self) -> int: return self._height
    def set_height(self, value:Union[int,float]) -> None: self._height = int(value)
    #尺寸
    def set_size(self, width:Union[int,float], height:Union[int,float]) -> None:
        self.set_width(width)
        self.set_height(height)
    #画出轮廓
    def draw_outline(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0), color:str="red", line_width:int=2) -> None:
        draw_rect(surface, get_color_rbga(color), pygame.Rect(add_pos(self.pos,offSet),self.size), line_width)

#新建一个形状类
def new_shape(pos:tuple, size:tuple) -> Shape: return Shape(pos[0], pos[1], size[0], size[1])

ShapeLiked = Union[Shape, ShapeRect, tuple]

# 转换pygame的rect类至linpg引擎的shape类
def convert_to_shape(rect: ShapeLiked) -> Shape:
    #确认是pygame.Rect类再转换
    if isinstance(rect, pygame.Rect):
        return Shape(rect.x, rect.y, rect.width, rect.height)
    #如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return Shape(rect[0], rect[1])
        elif len(rect) == 4:
            return Shape(rect[0], rect[1], rect[2], rect[3])
        else:
            throw_exception("error", 'Invalid length for forming a rect.')
    #如果是Shape类，则没必要转换
    elif isinstance(rect, Shape):
        return rect
    else:
        throw_exception("error", 'The rect has to be ShapeLiked object, not "{}".'.format(type(rect)))

# 转换linpg引擎的shape类至pygame的rect类
def convert_to_rect(shape: ShapeLiked) -> ShapeRect:
    # 确认是Shape类再转换
    if isinstance(shape, Shape):
        return pygame.Rect(shape.left, shape.top, shape.width, shape.height)
    # 如果是tuple类，则需要创建
    elif isinstance(shape, tuple):
        if len(shape) == 2:
            return pygame.Rect(shape[0], shape[1])
        elif len(shape) == 4:
            return pygame.Rect(shape[0], shape[1], shape[2], shape[3])
        else:
            throw_exception("error", 'Invalid length for forming a rect.')
    # 如果是pygame.Rect类，则没必要转换
    elif isinstance(shape, pygame.Rect):
        return shape
    else:
        throw_exception("error", 'The shape has to be ShapeLiked object, not "{}".'.format(type(shape)))

# 是否形状一样
def is_same_shape(rect1: ShapeLiked, rect2: ShapeLiked) -> bool:
    # 确保两个输入的类shape的物品都不是tuple
    if isinstance(rect1, tuple): convert_to_shape(rect1)
    if isinstance(rect2, tuple): convert_to_shape(rect2)
    # 比较并返回结果
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height

# 画正方形（的方块）
def draw_rect(surface:ImageSurface, color:any, rect:ShapeLiked, width:int=0) -> None:
    pygame.draw.rect(surface, color, convert_to_rect(rect), width)

# 画圆形
def draw_circle(surface:ImageSurface, color:any, center_pos:tuple, width:int=0):
    pygame.draw.circle(surface, color, center_pos, width)

# 检测图片是否被点击
def is_hover(
    imgObject: object,
    objectPos: Union[tuple, list] = (0, 0),
    off_set_x: Union[int, float] = 0,
    off_set_y: Union[int, float] = 0
    ) -> bool:
    mouse_x, mouse_y = controller.get_mouse_pos()
    # 如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    if isinstance(imgObject, GameObject2d):
        return imgObject.is_hover((mouse_x - off_set_x, mouse_y - off_set_y))
    else:
        return is_hover_pygame_object(imgObject, objectPos, off_set_x, off_set_y)