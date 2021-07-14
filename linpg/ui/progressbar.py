# cython: language_level=3
from .inputbox import *

#进度条泛型
class AbstractProgressBar(AbstractImage):
    def __init__(self, img: any, x: number, y: number, width: int_f, height: int_f, tag: str):
        super().__init__(img, x, y, width, height, tag)
        self.__current_percentage:float = 0.0
    #百分比
    @property
    def percentage(self) -> float: return self.__current_percentage
    def get_percentage(self) -> float: return self.__current_percentage
    def set_percentage(self, value:float) -> None:
        if 0 <= value <= 1:
            self.__current_percentage = value
        else:
            EXCEPTION.fatal("The percentage must be <= 1 and >= 0, not {}!".format(value))

#进度条简单形式的实现
class ProgressBar(AbstractProgressBar):
    def __init__(self, x: number, y: number, max_width: int, height: int, color: color_liked, tag:str=""):
        super().__init__(None, x, y, max_width, height, tag)
        self.color:tuple = Color.get(color)
    def display(self, surface: ImageSurface, offSet: pos_liked = Origin) -> None:
        if not self.hidden:
            draw_rect(surface, self.color, new_rect(add_pos(self.pos, offSet), (int(self._width*self.percentage), self._height)))

#进度条Surface
class ProgressBarSurface(AbstractProgressBar):
    def __init__(
        self, imgOnTop: Union[str, ImageSurface], imgOnBottom: Union[str, ImageSurface],
        x: number, y: number, max_width: int, height: int, mode: str = "horizontal", tag:str=""
        ):
        if imgOnTop is not None: imgOnTop = quickly_load_img(imgOnTop)
        super().__init__(imgOnTop, x, y, max_width, height, tag)
        self.img2 = quickly_load_img(imgOnBottom) if imgOnBottom is not None else None
        self._mode:bool = True
        self.set_mode(mode)
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
            EXCEPTION.fatal("Mode '{}' is not supported!".format(mode))
    #克隆
    def copy(self): return ProgressBarSurface(self.img.copy(),self.img2.copy(),self.x,self.y,self._width,self._height,self.get_mode())
    def light_copy(self): return ProgressBarSurface(self.img,self.img2,self.x,self.y,self._width,self._height,self.get_mode())
    #展示
    def display(self, surface:ImageSurface, offSet:pos_liked = Origin) -> None:
        if not self.hidden:
            pos = add_pos(self.pos, offSet)
            surface.blit(resize_img(self.img2,self.size),pos)
            if self.percentage > 0:
                imgOnTop = resize_img(self.img,self.size)
                if self._mode:
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self.percentage),self._height)),pos)
                else:
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self.percentage))),pos)

#进度条形式的调整器
class ProgressBarAdjuster(ProgressBarSurface):
    def __init__(
        self, imgOnTop: Union[str, ImageSurface], imgOnBottom: Union[str, ImageSurface], indicator_img: Union[str, ImageSurface],
        x: number, y: number, max_width: int, height: int, indicator_width:int, indicator_height:int, mode: str = "horizontal", tag:str=""
        ) -> None:
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode=mode, tag=tag)
        self.__indicator:StaticImage = StaticImage(indicator_img, 0, 0, indicator_width, indicator_height)
    #展示
    def display(self, surface:ImageSurface, offSet:pos_liked = Origin) -> None:
        if not self.hidden:
            super().display(surface, offSet)
            abs_pos:tuple[number] = add_pos(self.pos, offSet)
            x: int; y: int
            if self._mode:
                x,y = int_pos(add_pos(
                    (int(self._width*self.percentage-self.__indicator.width/2), int((self._height-self.__indicator.height)/2)),
                    abs_pos
                    ))
                self.__indicator.set_pos(x, y)
                self.__indicator.draw(surface)
                value_font = Font.render(str(round(self.percentage*100)), Color.WHITE, self._height)
                surface.blit(
                    value_font,
                    int_pos(add_pos(abs_pos, (self._width+self.__indicator.width*0.7, (self._height-value_font.get_height())/2)))
                    )
            else:
                x,y = int_pos(add_pos(
                    (int((self._width-self.__indicator.width)/2), int(self._height*self.percentage-self.__indicator.height/2)),
                    abs_pos
                    ))
                self.__indicator.set_pos(x, y)
                self.__indicator.draw(surface)
                value_font = Font.render(str(round(self.percentage*100)), Color.WHITE, self._width)
                surface.blit(
                    value_font,
                    int_pos(add_pos(abs_pos, ((self._width-value_font.get_width())/2, self._height+self.__indicator.height*0.7)))
                    )
            mouse_x:int; mouse_y:int
            mouse_x, mouse_y = subtract_pos(Controller.mouse.pos, offSet)
            if self.is_hover((mouse_x, mouse_y)):
                if Controller.mouse.get_pressed(0):
                    self.set_percentage((mouse_x-self.x)/self._width if self._mode else (mouse_y-self.y)/self._height)
                elif Controller.get_event("scroll_down"):
                    self.set_percentage(min(round(self.percentage+0.01,2), 1.0))
                elif Controller.get_event("scroll_up"):
                    self.set_percentage(max(round(self.percentage-0.01,2), 0.0))

# 动态进度条Surface
class DynamicProgressBarSurface(ProgressBarSurface):
    def __init__(
        self, imgOnTop: Union[str, ImageSurface], imgOnBottom: Union[str, ImageSurface],
        x: number, y: number, max_width: int, height: int, mode: str = "horizontal"
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
            self.__perecent_update_each_time = (self._percentage_to_be - super().get_percentage()*self.accuracy)/self.__total_update_intervals
        else:
            EXCEPTION.fatal("The percentage must be <= 1 and >= 0, not {}!".format(value))
    def copy(self): return DynamicProgressBarSurface(self.img.copy(),self.img2.copy(),self.x,self.y,self._width,self._height,self.get_mode())
    def light_copy(self): return DynamicProgressBarSurface(self.img,self.img2,self.x,self.y,self._width,self._height,self.get_mode())
    #检查并更新百分比
    def _check_and_update_percentage(self) -> None:
        if super().get_percentage()*self.accuracy < self._percentage_to_be and self.__perecent_update_each_time > 0 or\
            super().get_percentage()*self.accuracy > self._percentage_to_be and self.__perecent_update_each_time < 0:
            super().set_percentage(super().get_percentage()+self.__perecent_update_each_time/self.accuracy)
    #展示
    def display(self, surface:ImageSurface, offSet:pos_liked = Origin) -> None:
        if not self.hidden:
            pos:tuple = add_pos(self.pos,offSet)
            surface.blit(resize_img(self.img2,self.size),pos)
            self._check_and_update_percentage()
            if self.percentage > 0:
                imgOnTop = resize_img(self.img,self.size)
                if self._mode:
                    if self.percentage < self._percentage_to_be:
                        img2 = crop_img(imgOnTop,size=(int(self._width*self._percentage_to_be/self.accuracy),self._height))
                        img2.set_alpha(100)
                        surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,int(self._width*self.percentage/self.accuracy),self._height)),pos)
                    else:
                        if self.percentage > self._percentage_to_be:
                            img2 = crop_img(imgOnTop,size=(int(self._width*self.percentage/self.accuracy),self._height))
                            img2.set_alpha(100)
                            surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._percentage_to_be/self.accuracy),self._height)),pos)
                else:
                    if self.percentage < self._percentage_to_be:
                        img2 = crop_img(imgOnTop,size=(self._width,int(self._height*self._percentage_to_be/self.accuracy)))
                        img2.set_alpha(100)
                        surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self.percentage/self.accuracy))),pos)
                    else:
                        if self.percentage > self._percentage_to_be:
                            img2 = crop_img(imgOnTop,size=(self._width,int(self._height*self.percentage/self.accuracy)))
                            img2.set_alpha(100)
                            surface.blit(img2,pos)
                        surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._percentage_to_be/self.accuracy))),pos)