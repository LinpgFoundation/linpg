# cython: language_level=3
from ..api import *

#坐标类
class Coordinate:
    def __init__(self, x:Union[int,float], y:Union[int,float]):
        self.x = x
        self.y = y
    #坐标信息
    @property
    def pos(self) -> tuple: return self.x,self.y
    def get_pos(self) -> tuple: return self.x,self.y
    def set_pos(self, x:Union[int,float], y:Union[int,float]) -> None:
        self.x = int(x)
        self.y = int(y)
    #检测是否在给定的位置上
    def on_pos(self, pos:any) -> bool: return is_same_pos(self.pos,pos)

#游戏对象接口
class GameObject(Coordinate):
    def __init__(self, x:Union[int,float], y:Union[int,float]):
        super().__init__(x,y)
    def __lt__(self, other:Coordinate) -> bool: return self.y+self.x < other.y+other.x
    #左侧位置
    @property
    def left(self) -> int: return int(self.x)
    def get_left(self) -> int: return int(self.x)
    def set_left(self, value:Union[int,float]) -> None: self.x = int(value)
    #右侧位置
    @property
    def top(self) -> int: return int(self.y)
    def get_top(self) -> int: return int(self.y)
    def set_top(self, value:Union[int,float]) -> None: self.y = int(value)

#2d游戏对象接口
class GameObject2d(GameObject):
    def __init__(self, x:Union[int,float], y:Union[int,float]):
        super().__init__(x,y)
    #宽
    @property
    def width(self) -> int: return self.get_width()
    def get_width(self) -> int: throw_exception("error","The child class has to implement get_width() function!")
    #高
    @property
    def height(self) -> int: return self.get_height()
    def get_height(self) -> int: throw_exception("error","The child class has to implement get_height() function!")
    #尺寸
    @property
    def size(self) -> tuple: return self.get_width(),self.get_height()
    def get_size(self) -> tuple: return self.get_width(),self.get_height()
    #右侧位置
    @property
    def right(self) -> int: return int(self.x+self.get_width())
    def get_right(self) -> int: return int(self.x+self.get_width())
    def set_right(self, value:Union[int,float]) -> None: self.x = int(value-self.get_width())
    #底部位置
    @property
    def bottom(self) -> int: return int(self.y+self.get_height())
    def get_bottom(self) -> int: return int(self.y+self.get_height())
    def set_bottom(self, value:Union[int,float]) -> None: self.y = int(value-self.get_height())
    #中心位置
    @property
    def centerx(self) -> int: return int(self.x+self.get_width()/2)
    def get_centerx(self) -> int: return int(self.x+self.get_width()/2)
    def set_centerx(self, centerx:Union[int,float]) -> None: self.x = int(centerx-self.get_width()/2)
    @property
    def centery(self) ->  int: return int(self.y+self.get_height()/2)
    def get_centery(self) -> int: return int(self.y+self.get_height()/2)
    def set_centery(self, centery:Union[int,float]) -> None: self.y = int(centery-self.get_height()/2)
    @property
    def center(self) -> tuple: return self.centerx,self.centery
    def get_center(self) -> tuple: return self.centerx,self.centery
    def set_center(self, centerx:Union[int,float], centery:Union[int,float]) -> None:
        self.set_centerx(centerx)
        self.set_centery(centery)
    #是否被鼠标触碰
    def is_hover(self, mouse_pos:Union[tuple,list]=(-1,-1)) -> bool:
        if mouse_pos == (-1,-1): mouse_pos = controller.get_mouse_pos()
        return 0 < mouse_pos[0]-self.x < self.get_width() and 0 < mouse_pos[1]-self.y < self.get_height()
    #将图片直接画到surface上
    def draw(self, surface:ImageSurface) -> None: self.display(surface)
    #根据offSet将图片展示到surface的对应位置上 - 子类必须实现
    def display(self, surface:ImageSurface, offSet:tuple=(0,0)) -> None:
        throw_exception("error","The child class does not implement display() function!")
    #忽略现有坐标，将图片画到surface的指定位置上，不推荐使用
    def blit(self, surface:ImageSurface, pos:tuple) -> None: 
        old_pos = self.get_pos()
        self.set_pos(pos)
        self.draw(surface)
        self.set_pos(old_pos)

#2.5d游戏对象接口 - 使用z轴判断图案的图层
class GameObject2point5d(GameObject):
    def __init__(self, x:Union[int,float], y:Union[int,float], z:Union[int,float]):
        super().__init__(x,y)
        self.z = z
    def __lt__(self, other:GameObject) -> bool:
        if self.z != other.z:
            return self.z < other.z
        else:
            return self.y+self.x < other.y+other.x
    #设置坐标
    def set_pos(self, x:Union[int,float], y:Union[int,float], z:Union[int,float]=None) -> None:
        super().set_pos(x,y)
        if z is not None: self.z = round(z)

#3d游戏对象接口
class GameObject3d(GameObject2point5d):
    def __init__(self, x:Union[int,float], y:Union[int,float], z:Union[int,float]):
        super().__init__(x,y,z)
    def __lt__(self,other) -> bool: return self.y+self.x+self.z < other.y+other.x+other.z
    #获取坐标
    @property
    def pos(self) -> tuple: return self.x,self.y,self.z
    def get_pos(self) -> tuple: return self.x,self.y,self.z
    #设置坐标
    def set_pos(self, x:Union[int,float], y:Union[int,float], z:Union[int,float]) -> None:
        super().set_pos(x,y,z)

#需要被打印的物品
class ItemNeedBlit(GameObject2point5d):
    def __init__(self, image:object, weight:Union[int,float], pos:Union[tuple,list], offSet:Union[tuple,list]):
        super().__init__(pos[0],pos[1],weight)
        self.image = image
        self.offSet = offSet
    def draw(self, surface:ImageSurface) -> None:
        if isinstance(self.image, pygame.Surface):
            surface.blit(self.image,add_pos(self.pos,self.offSet))
        else:
            try:
                self.image.display(surface,self.offSet)
            except BaseException:
                self.image.draw(surface)
