# cython: language_level=3
from .module import *

RectLiked = Union[Rect, pygame.Rect, tuple]

# 正方形类
class Square(GameObject2d):
    def __init__(self, x: Union[int, float], y: Union[int, float], width:int):
        super().__init__(x, y)
        self._width:int = int(width)
    #宽度
    def get_width(self) -> int: return self._width
    def set_width(self, value:Union[int,float]) -> None: self._width = int(value)
    #高度
    def get_height(self) -> int: return self._width
    def set_height(self, value:Union[int,float]) -> None: self._width = int(value)
    #尺寸
    def set_size(self, width:Union[int,float], height:Union[int,float]) -> None:
        self.set_width(width)
        self.set_height(height)
    #获取rect
    def get_rect(self) -> tuple: return self.x, self.y, self._width, self._width
    #画出轮廓
    def draw_outline(self, surface:ImageSurface, offSet:pos_liked=Origin, color:str="red", thickness:int=2) -> None:
        draw_rect(surface, Color.get(color), (add_pos(self.pos,offSet),self.size), thickness)

# 用于兼容的长方类
class Rect(Square):
    def __init__(self, left:Union[int,float], top:Union[int,float], width:int, height:int):
        super().__init__(left, top, width)
        self._height:int = int(height)
    #高度
    def get_height(self) -> int: return self._height
    def set_height(self, value:Union[int,float]) -> None: self._height = int(value)
    #获取rect
    def get_rect(self) -> tuple: return self.x, self.y, self._width, self.height

#新建一个形状类
def new_rect(pos:tuple, size:tuple) -> Rect: return Rect(pos[0], pos[1], size[0], size[1])

# 画正方形（的方块）
def draw_rect(surface:ImageSurface, color:any, rect:RectLiked, thickness:int=0) -> None:
    if isinstance(rect, (pygame.Rect, tuple)):
        pygame.draw.rect(surface, Color.get(color), rect, thickness)
    elif isinstance(rect, Rect):
        pygame.draw.rect(surface, Color.get(color), rect.get_rect(), thickness)

# 转换pygame的rect类至linpg引擎的rect类
def convert_rect(rect: RectLiked) -> Rect:
    #确认是pygame.Rect类再转换
    if isinstance(rect, pygame.Rect):
        return Rect(rect.x, rect.y, rect.width, rect.height)
    #如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return new_rect(rect[0], rect[1])
        elif len(rect) == 4:
            return Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.throw("error", 'Invalid length for forming a rect.')
    #如果是Rect类，则没必要转换
    elif isinstance(rect, Rect):
        return rect
    else:
        EXCEPTION.throw("error", 'The rect has to be RectLiked object, not "{}".'.format(type(rect)))

#转换linpg.Rect至pygame.Rect
def convert_to_pygame_rect(rect:RectLiked) -> pygame.Rect:
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
            EXCEPTION.throw("error", 'Invalid length for forming a rect.')
    else:
        EXCEPTION.throw("error", 'The rect has to be RectLiked object, not "{}".'.format(type(rect)))

# 是否形状一样
def is_same_rect(rect1: RectLiked, rect2: RectLiked) -> bool:
    # 确保两个输入的类rect的物品都不是tuple
    if isinstance(rect1, tuple): convert_rect(rect1)
    if isinstance(rect2, tuple): convert_rect(rect2)
    # 比较并返回结果
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height

# 检测图片是否被点击
def is_hover(
    imgObject: object, objectPos: pos_liked = Origin, off_set_x: Union[int, float] = 0, off_set_y: Union[int, float] = 0
    ) -> bool:
    mouse_x, mouse_y = controller.get_mouse_pos()
    # 如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    if isinstance(imgObject, GameObject2d):
        return imgObject.is_hover((mouse_x - off_set_x, mouse_y - off_set_y))
    else:
        return is_hover_pygame_object(imgObject, objectPos, off_set_x, off_set_y)

# 圆形类
class Circle(Square):
    def __init__(self, x: Union[int, float], y: Union[int, float], diameter: int):
        super().__init__(x, y, diameter)
    @property
    def radius(self) -> Union[int, float]: return self._width/2
    #画出轮廓
    def draw_outline(self, surface:ImageSurface, offSet:pos_liked=Origin, color:str="red", thickness:int=2) -> None:
        draw_circle(surface, Color.get(color), add_pos(self.center, offSet), self.radius, thickness)

# 画圆形
def draw_circle(surface:ImageSurface, color:any, center_pos:tuple, radius:int, thickness:int=0):
    pygame.draw.circle(surface, Color.get(color), center_pos, radius, thickness)
