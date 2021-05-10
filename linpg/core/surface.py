# cython: language_level=3
from ..api import *

#与pygame.Rect类似的形状类
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
    def draw_outline(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0), color:str="red", line_width:int=2) -> None:
        pygame.draw.rect(surface,findColorRGBA(color),pygame.Rect(add_pos(self.pos,offSet),self.size),line_width)

#图形接口
class AbstractImage(Shape):
    def __init__(self, img:any, x:Union[int,float], y:Union[int,float], width:int, height:int):
        super().__init__(x, y, width, height)
        self.img = img
        self.hidden:bool = False
        self.tag:str = ""
    #透明度
    @property
    def alpha(self) -> int: return self.get_alpha()
    def get_alpha(self) -> int: return self.img.get_alpha()
    def set_alpha(self, value:int) -> None: self.img.set_alpha(value)
    #获取图片
    def get_image_pointer(self) -> any: return self.img
    def get_image_copy(self) -> any: return self.img.copy()

#有本地坐标的图形接口
class AdvancedAbstractImage(AbstractImage):
    def __init__(self, img: any, x:Union[int, float], y:Union[int, float], width:int, height:int):
        super().__init__(img, x, y, width, height)
        self._local_x:int = 0
        self._local_y:int = 0
        self._alpha:int = 255
    #透明度
    def get_alpha(self) -> int: return self._alpha
    def set_alpha(self, value:int) -> None:
        self._alpha = keepInRange(int(value),0,255)
        if isinstance(self.img, pygame.Surface) and self.img.get_alpha() != self._alpha: super().set_alpha(self._alpha)
    #本地坐标
    @property
    def local_pos(self) -> tuple: return self._local_x,self._local_y
    def get_local_pos(self) -> tuple: return self._local_x,self._local_y
    def set_local_pos(self, local_x:int, local_y:int) -> None:
        self._local_x = int(local_x)
        self._local_y = int(local_y)
    #绝对的本地坐标
    @property
    def abs_pos(self) -> tuple: return self.x+self._local_x,self.y+self._local_y
    def get_abs_pos(self) -> tuple: return self.x+self._local_x,self.y+self._local_y

#用于静态图片的surface
class StaticImageSurface(AdvancedAbstractImage):
    def __init__(self, img:Union[str,pygame.Surface], x:Union[int,float], y:Union[int,float], width:int=-1, height:int=-1):
        super().__init__(None,x,y,width,height)
        self.img_original = loadImg(img)
        self.__is_flipped:bool = False
        self.__needUpdate:bool = True if self._width >= 0 and self._height >= 0 else False
        self.__crop_rect:object = None
    #宽度
    def set_width(self, value:Union[int,float]) -> None:
        value = int(value)
        if self._width != value:
            super().set_width(value)
            self.__needUpdate = True
    def set_width_with_size_locked(self, width:Union[int,float]) -> None:
        height:int = int(width/self.img_original.get_width()*self.img_original.get_height())
        width = int(width)
        self.set_size(width,height)
    #高度
    def set_height(self, value:Union[int,float]) -> None:
        value = int(value)
        if self._height != value:
            super().set_height(value)
            self.__needUpdate = True
    def set_height_with_size_locked(self, height:Union[int,float]) -> None:
        width = int(height/self.img_original.get_height()*self.img_original.get_width())
        height = int(height)
        self.set_size(width,height)
    #截图的范围
    @property
    def crop_rect(self) -> object: return self.__crop_rect
    def get_crop_rect(self) -> object: return self.__crop_rect
    def set_crop_rect(self, rect:Union[pygame.Rect, Shape, None]) -> None:
        if rect is None or isinstance(rect,(pygame.Rect,Shape)):
            if self.__crop_rect != rect:
                self.__crop_rect = rect
                self.__needUpdate = True
            else:
                pass
        else:
            throwException("error","You have to input either a None or a Rect, not {}".format(type(rect)))
    #更新图片
    def _update_img(self) -> None:
        imgTmp = smoothscaleImg(self.img_original, self.size)
        rect = imgTmp.get_bounding_rect()
        if self.__crop_rect is not None:
            new_x:int = max(rect.x,self.__crop_rect.x)
            new_y:int = max(rect.y,self.__crop_rect.y)
            rect = Shape(new_x,new_y,min(rect.right,self.__crop_rect.right)-new_x,min(rect.bottom,self.__crop_rect.bottom)-new_y)
        self.img = getSurface(rect.size,pygame.SRCALPHA).convert_alpha()
        self.set_local_pos(rect.x,rect.y)
        self.img.blit(imgTmp,(-self._local_x,-self._local_y))
        if self._alpha != 255:
            self.img.set_alpha(self._alpha)
        self.__needUpdate = False
    #反转原图，并打上已反转的标记
    def flip(self) -> None:
        self.__is_flipped = not self.__is_flipped
        self.flip_original()
    #反转原图
    def flip_original(self) -> None:
        self.img_original = flipImg(self.img_original,True,False)
        self.__needUpdate = True
    #如果不处于反转状态，则反转
    def flip_if_not(self) -> None:
        if not self.__is_flipped: self.flip()
    #反转回正常状态
    def flip_back_to_normal(self) -> None:
        if self.__is_flipped: self.flip()
    #画出轮廓
    def draw_outline(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0), color:any="red", line_width:int=2) -> None:
        pygame.draw.rect(surface,findColorRGBA(color),pygame.Rect(add_pos(self.abs_pos,offSet),self.img.get_size()),line_width)
    #是否被鼠标触碰
    def is_hover(self, mouse_pos:Union[tuple,list]=(-1,-1)) -> bool:
        if mouse_pos == (-1,-1): mouse_pos = controller.get_mouse_pos()
        if self.img is not None:
            return 0 < mouse_pos[0]-self.x-self._local_x < self.img.get_width() and 0 < mouse_pos[1]-self.y-self._local_y < self.img.get_height()
        else:
            return False
    #返回一个复制品
    def copy(self): return StaticImageSurface(self.img_original.copy(),self.x,self.y,self._width,self._height)
    #返回一个浅复制品
    def light_copy(self): return StaticImageSurface(self.img_original,self.x,self.y,self._width,self._height)
    #加暗度
    def addDarkness(self, value:int) -> None:
        self.img_original.fill((value, value, value),special_flags=pygame.BLEND_RGB_SUB)
        self.__needUpdate = True
    def addBrightness(self, value:int) -> None:
        self.img_original.fill((value, value, value),special_flags=pygame.BLEND_RGB_ADD)
        self.__needUpdate = True
    #展示
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden:
            #如果图片需要更新，则先更新
            if self.__needUpdate: self._update_img()
            #将已经处理好的图片画在给定的图层上
            surface.blit(self.img,(self.x+self._local_x+offSet[0], self.y+self._local_y+offSet[1]))

#高级图形类
class ImageSurface(AbstractImage):
    def __init__(self, img:pygame.Surface, x:Union[int,float], y:Union[int,float], width:int=-1, height:int=-1, tag:str="default"):
        super().__init__(img,x,y,width,height)
        self.tag = tag
        if self._width < 0 and self._height < 0:
            self._width,self._height = self.img.get_size()
        elif self._width < 0 and self._height >= 0:
            self._width = self._height/self.img.get_height()*self.img.get_width()
        elif self._width >= 0 and self._height < 0:
            self._height = self._width/self.img.get_width()*self.img.get_height()
    #返回一个复制
    def copy(self) -> None:
        replica = ImageSurface(self.get_image_copy(),self.x,self.y,self._width,self._height,self.tag)
        self.img.set_alpha(255)
        return replica
    #更新图片
    def update(self, img_path:Union[str,pygame.Surface], ifConvertAlpha:bool=True) -> None:
        self.img = imgLoadFunction(img_path,ifConvertAlpha)
    def drawOnTheCenterOf(self, surface:pygame.Surface) -> None:
        surface.blit(resizeImg(self.img,self.size),((surface.get_width()-self._width)/2,(surface.get_height()-self._height)/2))
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden: surface.blit(resizeImg(self.img,self.size),add_pos(self.pos,offSet))
    #旋转
    def rotate(self, angle:int) -> None: self.img = pygame.transform.rotate(self.img,angle)
    #反转
    def flip(self, vertical:bool=False, horizontal:bool=False) -> None: self.img = flipImg(self.img,vertical,horizontal)
    #淡出
    def fade_out(self, speed:int) -> None:
        alphaTmp = self.get_alpha()
        if alphaTmp > 0: self.set_alpha(alphaTmp-speed)

#需要移动的动态图片
class DynamicImageSurface(ImageSurface):
    def __init__(self, img:pygame.Surface, x:Union[int,float], y:Union[int,float], target_x:Union[int,float], target_y:Union[int,float],
        moveSpeed_x:Union[int,float], moveSpeed_y:Union[int,float], width:int=-1, height:int=-1, tag:str="default"):
        super().__init__(img,x,y,width,height,tag)
        self.default_x = x
        self.default_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.moveSpeed_x = moveSpeed_x
        self.moveSpeed_y = moveSpeed_y
        self.__is_moving_toward_target:bool = False
    #控制
    def switch(self) -> None: self.__is_moving_toward_target = not self.__is_moving_toward_target
    def move_toward(self) -> None: self.__is_moving_toward_target = True
    def move_back(self) -> None: self.__is_moving_toward_target = False
    #移动状态
    def is_moving_toward_target(self) -> bool: return self.__is_moving_toward_target
    def has_reached_target(self) -> bool:
        return self.x == self.target_x and self.y == self.target_y if self.__is_moving_toward_target is True \
            else self.x == self.default_x and self.y == self.default_y
    #画出
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden:
            super().display(surface,offSet)
            if self.__is_moving_toward_target is True:
                if self.default_x < self.target_x:
                    if self.x < self.target_x: self.x += self.moveSpeed_x
                    if self.x > self.target_x: self.x = self.target_x
                elif self.default_x > self.target_x:
                    if self.x > self.target_x: self.x -= self.moveSpeed_x
                    if self.x < self.target_x: self.x = self.target_x
                if self.default_y < self.target_y:
                    if self.y < self.target_y: self.y += self.moveSpeed_y
                    if self.y > self.target_y: self.y = self.target_y
                elif self.default_y > self.target_y:
                    if self.y > self.target_y: self.y -= self.moveSpeed_y
                    if self.y < self.target_y: self.y = self.target_y
            else:
                if self.default_x < self.target_x:
                    if self.x > self.default_x: self.x -= self.moveSpeed_x
                    if self.x < self.default_x: self.x = self.default_x
                elif self.default_x > self.target_x:
                    if self.x < self.default_x: self.x += self.moveSpeed_x
                    if self.x > self.default_x: self.x = self.default_x
                if self.default_y < self.target_y:
                    if self.y > self.default_y: self.y -= self.moveSpeed_y
                    if self.y < self.default_y: self.y = self.default_y
                elif self.default_y > self.target_y:
                    if self.y < self.default_y: self.y += self.moveSpeed_y
                    if self.y > self.default_y: self.y = self.default_y

#gif图片管理
class GifObject(AdvancedAbstractImage):
    def __init__(self,imgList:numpy.ndarray, x:Union[int,float], y:Union[int,float], width:int, height:int, updateGap:int):
        super().__init__(imgList,x,y,width,height)
        self.imgId:int = 0
        self.updateGap:int = max(int(updateGap),0)
        self.countDown:int = 0
    #展示
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)):
        if not self.hidden:
            img = resizeImg(self.img[self.imgId],self.size)
            #设置透明度
            if self._alpha != 255: img.set_alpha(self._alpha)
            surface.blit(img,add_pos(self.pos,offSet))
            if self.countDown >= self.updateGap:
                self.countDown = 0
                self.imgId += 1
                if self.imgId >= len(self.img): self.imgId = 0
            else:
                self.countDown += 1
