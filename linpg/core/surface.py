# cython: language_level=3
from .shape import *

#图形接口
class AbstractImage(Rect):
    def __init__(self, img:any, x:Union[int,float], y:Union[int,float], width:int_f, height:int_f, tag:str):
        super().__init__(x, y, width, height)
        self.img:any = img
        self.hidden:bool = False
        self.tag:str = str(tag)
        #确保长宽均已输入且为正整数
        if self._width < 0 and self._height < 0:
            self._width, self._height = self.img.get_size()
        elif self._width < 0 and self._height >= 0:
            self.set_width(self._height/self.img.get_height()*self.img.get_width())
        elif self._width >= 0 and self._height < 0:
            self.set_height(self._width/self.img.get_width()*self.img.get_height())
    #透明度
    @property
    def alpha(self) -> int: return self.get_alpha()
    def get_alpha(self) -> int: return self.img.get_alpha()
    def set_alpha(self, value:int) -> None: self.img.set_alpha(value)
    def add_alpha(self, value:int) -> None: self.set_alpha(self.get_alpha()+value)
    def subtract_alpha(self, value:int) -> None: self.set_alpha(self.get_alpha()-value)
    #获取图片
    def get_image_pointer(self) -> any: return self.img
    def get_image_copy(self) -> any: return self.img.copy()
    #更新图片
    def update_image(self, img_path:Union[str, ImageSurface], ifConvertAlpha:bool=True) -> None:
        self.img = quickly_load_img(img_path, ifConvertAlpha)
    #淡入
    def fade_in(self, value:int) -> None: self.set_alpha(self.get_alpha()+value)
    #淡出
    def fade_out(self, value:int) -> None: self.set_alpha(self.get_alpha()-value)
    #旋转
    def rotate(self, angle:int) -> None: self.img = rotate_img(self.img, angle)

#高级图形类
class DynamicImage(AbstractImage):
    def __init__(self, img: Union[str,ImageSurface], x: Union[int, float], y: Union[int, float], width: int_f=-1, height: int_f=-1, tag: str=""):
        super().__init__(quickly_load_img(img), x, y, width, height, tag)
    #返回一个复制
    def copy(self):
        replica = DynamicImage(self.get_image_copy(), self.x, self.y, self._width, self._height, self.tag)
        self.img.set_alpha(255)
        return replica
    #返回一个浅复制品
    def light_copy(self): return DynamicImage(self.get_image_pointer(), self.x, self.y, self._width, self._height, self.tag)
    #反转
    def flip(self, vertical:bool=False, horizontal:bool=False) -> None: self.img = flip_img(self.img, vertical, horizontal)
    #展示
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden: surface.blit(resize_img(self.img, self.size), add_pos(self.pos, offSet))

#有本地坐标的图形接口
class AdvancedAbstractImage(AbstractImage):
    def __init__(self, img: any, x:Union[int,float], y:Union[int,float], width:int_f, height:int_f, tag:str=""):
        super().__init__(img, x, y, width, height, tag)
        self._local_x:int = 0
        self._local_y:int = 0
        self._alpha:int = 255
    #透明度
    def get_alpha(self) -> int: return self._alpha
    def set_alpha(self, value:int, update_original:bool=True) -> None:
        self._alpha = keep_in_range(int(value), 0, 255)
        if update_original is True and isinstance(self.img, pygame.Surface): super().set_alpha(self._alpha)
    #获取本地坐标
    @property
    def local_x(self) -> int: return self._local_x
    def get_local_x(self) -> int: return self._local_x
    @property
    def local_y(self) -> int: return self._local_y
    def get_local_y(self) -> int: return self._local_y
    @property
    def local_pos(self) -> tuple: return self._local_x, self._local_y
    def get_local_pos(self) -> tuple: return self._local_x, self._local_y
    #设置本地坐标
    def set_local_x(self, value:int_f) -> None: self._local_x = int(value)
    def set_local_y(self, value:int_f) -> None: self._local_y = int(value)
    def set_local_pos(self, local_x:int_f, local_y:int_f) -> None:
        self.set_local_x(local_x)
        self.set_local_y(local_y)
    #增加本地坐标
    def add_local_x(self, value:int_f) -> None: self.set_local_x(self._local_x + value)
    def add_local_y(self, value:int_f) -> None: self.set_local_y(self._local_y + value)
    def add_local_pos(self, local_x:int_f, local_y:int_f) -> None:
        self.add_local_x(local_x)
        self.add_local_y(local_y)
    #绝对的本地坐标
    @property
    def abs_x(self) -> Union[int,float]: return self.x + self._local_x
    @property
    def abs_y(self) -> Union[int,float]: return self.y + self._local_y
    @property
    def abs_pos(self) -> tuple: return self.abs_x, self.abs_y
    def get_abs_pos(self) -> tuple: return self.abs_x, self.abs_y

#用于静态图片的surface
class StaticImage(AdvancedAbstractImage):
    def __init__(self, img:Union[str,ImageSurface], x:Union[int,float], y:Union[int,float], width:int_f=-1, height:int_f=-1, tag:str="default"):
        super().__init__(quickly_load_img(img), x, y, width, height, tag)
        self.__processed_img:ImageSurface = None
        self.__is_flipped:bool = False
        self.__need_update:bool = True if self._width >= 0 and self._height >= 0 else False
        self.__crop_rect:object = None
    #更新图片
    def update_image(self, img_path:Union[str, ImageSurface], ifConvertAlpha:bool=True) -> None:
        super().update_image(img_path, ifConvertAlpha)
        self.__need_update = True
    #旋转
    def rotate(self, angle:int) -> None:
        super().rotate(angle)
        self.__need_update = True
    #设置透明度
    def set_alpha(self, value:int) -> None:
        super().set_alpha(value, False)
        if self.__processed_img is not None: self.__processed_img.set_alpha(self.get_alpha())
    #宽度
    def set_width(self, value:Union[int,float]) -> None:
        value = int(value)
        if self._width != value:
            super().set_width(value)
            self.__need_update = True
    def set_width_with_size_locked(self, width:Union[int,float]) -> None:
        height:int = int(width/self.img.get_width()*self.img.get_height())
        width = int(width)
        self.set_size(width, height)
    #高度
    def set_height(self, value:Union[int,float]) -> None:
        value = int(value)
        if self._height != value:
            super().set_height(value)
            self.__need_update = True
    def set_height_with_size_locked(self, height:Union[int,float]) -> None:
        width:int = int(height/self.img.get_height()*self.img.get_width())
        height = int(height)
        self.set_size(width, height)
    #截图的范围
    @property
    def crop_rect(self) -> object: return self.__crop_rect
    def get_crop_rect(self) -> object: return self.__crop_rect
    def set_crop_rect(self, rect:Union[Rect, None]) -> None:
        if rect is None or isinstance(rect, Rect):
            if self.__crop_rect != rect:
                self.__crop_rect = rect
                self.__need_update = True
            else:
                pass
        else:
            throw_exception("error","You have to input either a None or a Rect, not {}".format(type(rect)))
    #更新图片
    def _update_img(self) -> None:
        imgTmp = smoothly_resize_img(self.img, self.size) if get_antialias() is True else resize_img(self.img, self.size)
        rect = imgTmp.get_bounding_rect()
        if self.width != rect.width or self.height != rect.height or self.__crop_rect is not None:
            if self.__crop_rect is not None:
                new_x:int = max(rect.x, self.__crop_rect.x)
                new_y:int = max(rect.y, self.__crop_rect.y)
                rect = Rect(new_x, new_y, min(rect.right,self.__crop_rect.right)-new_x, min(rect.bottom,self.__crop_rect.bottom)-new_y)
            self.__processed_img = new_transparent_surface(rect.size)
            self.set_local_pos(rect.x,rect.y)
            self.__processed_img.blit(imgTmp,(-self._local_x,-self._local_y))
        else:
            self.__processed_img = imgTmp
        if self._alpha < 255:
            self.__processed_img.set_alpha(self._alpha)
        self.__need_update = False
    #反转原图，并打上已反转的标记
    def flip(self) -> None:
        self.__is_flipped = not self.__is_flipped
        self.flip_original_img()
    #反转原图
    def flip_original_img(self, horizontal:bool=True, vertical:bool=False) -> None:
        self.img = flip_img(self.img, horizontal, vertical)
        self.__need_update = True
    #如果不处于反转状态，则反转
    def flip_if_not(self) -> None:
        if not self.__is_flipped: self.flip()
    #反转回正常状态
    def flip_back_to_normal(self) -> None:
        if self.__is_flipped: self.flip()
    #画出轮廓
    def draw_outline(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0), color:any="red", line_width:int=2) -> None:
        draw_rect(surface, Color.get(color), (add_pos(self.abs_pos,offSet), self.__processed_img.get_size()), line_width)
    #是否被鼠标触碰
    def is_hover(self, mouse_pos:Union[tuple,list]=(-1,-1)) -> bool:
        if mouse_pos == (-1,-1): mouse_pos = controller.get_mouse_pos()
        if self.__processed_img is not None:
            return 0 < mouse_pos[0]-self.x-self._local_x < self.__processed_img.get_width() and 0 < mouse_pos[1]-self.y-self._local_y < self.__processed_img.get_height()
        else:
            return False
    #返回一个复制品
    def copy(self): return StaticImage(self.img.copy(),self.x,self.y,self._width,self._height)
    #返回一个浅复制品
    def light_copy(self): return StaticImage(self.img,self.x,self.y,self._width,self._height)
    #加暗度
    def add_darkness(self, value:int) -> None:
        self.img = add_darkness(self.img, value)
        self.__need_update = True
    def subtract_darkness(self, value:int) -> None:
        self.img = subtract_darkness(self.img, value)
        self.__need_update = True
    #展示
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden:
            #如果图片需要更新，则先更新
            if self.__need_update is True: self._update_img()
            #将已经处理好的图片画在给定的图层上
            surface.blit(self.__processed_img, add_pos(self.abs_pos, offSet))

#需要移动的动态图片
class MovableImage(StaticImage):
    def __init__(
        self, img:Union[str,ImageSurface],
        x:Union[int,float], y:Union[int,float],
        target_x:Union[int,float], target_y:Union[int,float],
        move_speed_x:Union[int,float], move_speed_y:Union[int,float],
        width:int_f=-1, height:int_f=-1,
        tag:str="default"
        ):
        super().__init__(img, x, y, width, height, tag)
        self.__default_x = x
        self.__default_y = y
        self.__target_x = target_x
        self.__target_y = target_y
        self.__move_speed_x = move_speed_x
        self.__move_speed_y = move_speed_y
        self.__is_moving_toward_target:bool = False
    #返回一个复制
    def copy(self): return MovableImage(
        self.get_image_copy(), self.x, self.y,
        self.__target_x, self.__target_y,
        self.__move_speed_x, self.__move_speed_y,
        self._width, self._height, self.tag
        )
    #返回一个浅复制品
    def light_copy(self): return MovableImage(
        self.get_image_pointer(), self.x, self.y,
        self.__target_x, self.__target_y,
        self.__move_speed_x, self.__move_speed_y,
        self._width, self._height, self.tag
        )
    #控制
    def switch(self) -> None: self.__is_moving_toward_target = not self.__is_moving_toward_target
    def move_toward(self) -> None: self.__is_moving_toward_target = True
    def move_back(self) -> None: self.__is_moving_toward_target = False
    #移动状态
    def is_moving_toward_target(self) -> bool: return self.__is_moving_toward_target
    def has_reached_target(self) -> bool:
        return self.x == self.__target_x and self.y == self.__target_y if self.__is_moving_toward_target is True \
            else self.x == self.__default_x and self.y == self.__default_y
    #画出
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden:
            super().display(surface, offSet)
            if self.__is_moving_toward_target is True:
                if self.__default_x < self.__target_x:
                    if self.x < self.__target_x: self.x += self.__move_speed_x
                    if self.x > self.__target_x: self.x = self.__target_x
                elif self.__default_x > self.__target_x:
                    if self.x > self.__target_x: self.x -= self.__move_speed_x
                    if self.x < self.__target_x: self.x = self.__target_x
                if self.__default_y < self.__target_y:
                    if self.y < self.__target_y: self.y += self.__move_speed_y
                    if self.y > self.__target_y: self.y = self.__target_y
                elif self.__default_y > self.__target_y:
                    if self.y > self.__target_y: self.y -= self.__move_speed_y
                    if self.y < self.__target_y: self.y = self.__target_y
            else:
                if self.__default_x < self.__target_x:
                    if self.x > self.__default_x: self.x -= self.__move_speed_x
                    if self.x < self.__default_x: self.x = self.__default_x
                elif self.__default_x > self.__target_x:
                    if self.x < self.__default_x: self.x += self.__move_speed_x
                    if self.x > self.__default_x: self.x = self.__default_x
                if self.__default_y < self.__target_y:
                    if self.y > self.__default_y: self.y -= self.__move_speed_y
                    if self.y < self.__default_y: self.y = self.__default_y
                elif self.__default_y > self.__target_y:
                    if self.y < self.__default_y: self.y += self.__move_speed_y
                    if self.y > self.__default_y: self.y = self.__default_y

#获取图片的subsurface
def get_img_subsurface(img:ImageSurface, rect:RectLiked) -> ImageSurface:
    if isinstance(rect, pygame.Rect):
        return img.subsurface(rect)
    else:
        return img.subsurface(convert_to_pygame_rect(rect))

#获取特定颜色的表面
def get_single_color_surface(color, size=None) -> StaticImage:
    # 如果size是none，则使用屏幕的尺寸
    if size is None: size = display.get_size()
    # 获取surface
    surfaceTmp = new_surface(size).convert()
    surfaceTmp.fill(color)
    return StaticImage(surfaceTmp, 0, 0, size[0], size[1])

# gif图片管理
class GifImage(AdvancedAbstractImage):
    def __init__(
        self,
        imgList: numpy.ndarray,
        x: Union[int, float],
        y: Union[int, float],
        width: int_f,
        height: int_f,
        updateGap: int_f,
        tag: str = "default"
        ):
        super().__init__(imgList, x, y, width, height, tag)
        self.imgId: int = 0
        self.updateGap: int = max(int(updateGap), 0)
        self.countDown: int = 0
    # 返回一个复制
    def copy(self):
        return GifImage(
            self.get_image_copy(),
            self.x,
            self.y,
            self._width,
            self._height,
            self.updateGap,
        )
    # 返回一个浅复制品
    def light_copy(self):
        return GifImage(
            self.get_image_pointer(),
            self.x,
            self.y,
            self._width,
            self._height,
            self.updateGap,
        )
    # 当前图片
    @property
    def current_image(self) -> StaticImage:
        return self.img[self.imgId]
    # 展示
    def display(self, surface: ImageSurface, offSet: Union[tuple, list] = (0, 0)):
        if not self.hidden:
            self.current_image.set_size(self.get_width(), self.get_height())
            self.current_image.set_alpha(self._alpha)
            self.current_image.display(surface, add_pos(self.pos, offSet))
            if self.countDown >= self.updateGap:
                self.countDown = 0
                self.imgId += 1
                if self.imgId >= len(self.img):
                    self.imgId = 0
            else:
                self.countDown += 1