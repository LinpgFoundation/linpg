# cython: language_level=3
from .surface import *

#进度条
class ProgressBar(AbstractImage):
    def __init__(
        self,
        x: Union[int, float],
        y: Union[int, float],
        max_width: int,
        height: int,
        color: any
        ):
        super().__init__(None,x,y,max_width,height)
        self.percentage = 0
        self.color:tuple = get_color_rbga(color)
    def display(self, surface: ImageSurface, offSet: Union[tuple, list] = (0, 0)) -> None:
        if not self.hidden:
            pygame.draw.rect(surface, self.color, pygame.Rect(add_pos(self.pos, offSet), (int(self._width*self.percentage), self._height)))

#进度条Surface
class ProgressBarSurface(AbstractImage):
    def __init__(
        self,
        imgOnTop: ImageSurface,
        imgOnBottom: ImageSurface,
        x: Union[int, float],
        y: Union[int, float],
        max_width: int,
        height: int,
        mode: str = "horizontal"
        ):
        if imgOnTop is not None: imgOnTop = imgLoadFunction(imgOnTop, True)
        super().__init__(imgOnTop,x,y,max_width,height)
        self.img2 = imgLoadFunction(imgOnBottom,True) if imgOnBottom is not None else None
        self._current_percentage = 0
        self._mode:bool = True
        self.set_mode(mode)
    #百分比
    @property
    def percentage(self) -> float: return self._current_percentage
    def get_percentage(self) -> float: return self._current_percentage
    def set_percentage(self, value:float) -> None:
        if 0 <= value <= 1:
            self._current_percentage = value
        else:
            throwException("error","The percentage must be <= 1 and >= 0!")
    #模式
    @property
    def mode(self) -> str: return self.get_mode()
    def get_mode(self) -> str: return "horizontal" if self._mode else "vertical"
    def set_mode(self, mode:str) -> None:
        if mode == "horizontal":
            self._mode = True
        elif mode == "vertical":
            self._mode = False
        else:
            throwException("error","Mode '{}' is not supported!".format(mode))
    #克隆
    def copy(self): return ProgressBarSurface(self.img.copy(),self.img2.copy(),self.x,self.y,self._width,self._height,self.get_mode())
    def light_copy(self): return ProgressBarSurface(self.img,self.img2,self.x,self.y,self._width,self._height,self.get_mode())
    #展示
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden:
            pos = add_pos(self.pos, offSet)
            surface.blit(resize_img(self.img2,self.size),pos)
            if self._current_percentage > 0:
                imgOnTop = resize_img(self.img,self.size)
                if self._mode:
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._current_percentage),self._height)),pos)
                else:
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._current_percentage))),pos)

# 动态进度条Surface
class DynamicProgressBarSurface(ProgressBarSurface):
    def __init__(
        self,
        imgOnTop: ImageSurface,
        imgOnBottom: ImageSurface,
        x: Union[int, float],
        y: Union[int, float],
        max_width: int,
        height: int,
        mode: str = "horizontal"
        ):
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode)
        self._percentage_to_be = 0
        self.__perecent_update_each_time = 0
        self.__total_update_intervals = 10
    #数据准确度
    @property
    def accuracy(self) -> int: return self.__total_update_intervals*100
    #百分比
    @property
    def percentage(self) -> float: return self._percentage_to_be/self.accuracy
    def get_percentage(self) -> float: return self._percentage_to_be/self.accuracy
    def set_percentage(self, value:float) -> None:
        if 0 <= value <= 1:
            self._percentage_to_be = value*self.accuracy
            self.__perecent_update_each_time = (self._percentage_to_be-self._current_percentage)/self.__total_update_intervals
        else:
            throwException("error","The percentage must be <= 1 and >= 0, not {}!".format(value))
    def copy(self): return DynamicProgressBarSurface(self.img.copy(),self.img2.copy(),self.x,self.y,self._width,self._height,self.get_mode())
    def light_copy(self): return DynamicProgressBarSurface(self.img,self.img2,self.x,self.y,self._width,self._height,self.get_mode())
    #检查并更新百分比
    def _check_and_update_percentage(self) -> None:
        if self._current_percentage < self._percentage_to_be and self.__perecent_update_each_time > 0 or\
            self._current_percentage > self._percentage_to_be and self.__perecent_update_each_time < 0:
            self._current_percentage += self.__perecent_update_each_time
    #展示
    def display(self, surface:ImageSurface, offSet:Union[tuple,list]=(0,0)) -> None:
        if not self.hidden:
            pos:tuple = add_pos(self.pos,offSet)
            surface.blit(resize_img(self.img2,self.size),pos)
            self._check_and_update_percentage()
            if self._current_percentage > 0:
                imgOnTop = resize_img(self.img,self.size)
                if self._mode:
                    if self._current_percentage < self._percentage_to_be:
                        img2 = crop_img(imgOnTop,size=(int(self._width*self._percentage_to_be/self.accuracy),self._height))
                        img2.set_alpha(100)
                        surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._current_percentage/self.accuracy),self._height)),pos)
                    else:
                        if self._current_percentage > self._percentage_to_be:
                            img2 = crop_img(imgOnTop,size=(int(self._width*self._current_percentage/self.accuracy),self._height))
                            img2.set_alpha(100)
                            surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._percentage_to_be/self.accuracy),self._height)),pos)
                else:
                    if self._current_percentage < self._percentage_to_be:
                        img2 = crop_img(imgOnTop,size=(self._width,int(self._height*self._percentage_to_be/self.accuracy)))
                        img2.set_alpha(100)
                        surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._current_percentage/self.accuracy))),pos)
                    else:
                        if self._current_percentage > self._percentage_to_be:
                            img2 = crop_img(imgOnTop,size=(self._width,int(self._height*self._current_percentage/self.accuracy)))
                            img2.set_alpha(100)
                            surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._percentage_to_be/self.accuracy))),pos)