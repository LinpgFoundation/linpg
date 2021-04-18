# cython: language_level=3
from ..api import *

#与pygame.Rect类似的形状类
class Shape(GameObject2d):
    def __init__(self, left:Union[int,float], top:Union[int,float], width:Union[int,float], height:Union[int,float]):
        super().__init__(left,top)
        self._width = int(width)
        self._height = int(height)
    #宽度
    def get_width(self) -> int: return self._width
    def set_width(self, value:Union[int,float]) -> None: self._width = round(value)
    #高度
    def get_height(self) -> int: return self._height
    def set_height(self, value:Union[int,float]) -> None: self._height = round(value)
    #尺寸
    def set_size(self, width:float, height:float) -> None:
        self.set_width(width)
        self.set_height(height)
    #画出轮廓
    def draw_outline(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0), color:str="red", line_width:int=2) -> None:
        pygame.draw.rect(surface,findColorRGBA(color),pygame.Rect(add_pos(self.pos,offSet),self.size),line_width)

#图形接口
class AbstractImage(Shape):
    def __init__(self, img:any, x:Union[int,float], y:Union[int,float], width:any, height:any):
        super().__init__(x,y,0,0)
        self.img = img
        self._width = width
        self._height = height
    #透明度
    @property
    def alpha(self) -> int: return self.get_alpha()
    def get_alpha(self) -> int: return self.img.get_alpha()
    def set_alpha(self, value:int) -> None: self.img.set_alpha(value)

#用于静态图片的surface
class StaticImageSurface(AbstractImage):
    def __init__(self, path_or_surface:Union[str,pygame.Surface], x:any, y:any, width:any=None, height:any=None):
        super().__init__(None,x,y,width,height)
        self._alpha:int = 255
        self.img_original = loadImg(path_or_surface)
        self.__local_x = 0
        self.__local_y = 0
        self.__isFlipped:bool = False
        self.__needUpdate:bool = True if self._width is not None and self._height is not None else False
        self.__crop_rect:object = None
    #透明度
    def get_alpha(self) -> int: return self._alpha
    def set_alpha(self, value:float) -> None:
        self._alpha = keepInRange(int(value),0,255)
        if self.img is not None and self.img.get_alpha() != self._alpha: super().set_alpha(self._alpha)
    #宽度
    def set_width(self, value:float) -> None:
        value = round(value)
        if self._width != value:
            super().set_width(value)
            self.__needUpdate = True
    def set_width_with_size_locked(self, width:float) -> None:
        height = round(width/self.img_original.get_width()*self.img_original.get_height())
        width = round(width)
        self.set_size(width,height)
    #高度
    def set_height(self, value:float) -> None:
        value = round(value)
        if self._height != value:
            super().set_height(value)
            self.__needUpdate = True
    def set_height_with_size_locked(self, height:float) -> None:
        width = round(height/self.img_original.get_height()*self.img_original.get_width())
        height = round(height)
        self.set_size(width,height)
    #自定义crop范围
    @property
    def crop_rect(self) -> object: return self.__crop_rect
    def get_crop_rect(self) -> object: return self.__crop_rect
    def set_crop_rect(self, rect:Union[pygame.Rect,Shape,None]) -> None:
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
        imgTmp = resizeImg(self.img_original,(self._width,self._height))
        rect = imgTmp.get_bounding_rect()
        if self.__crop_rect is not None:
            new_x:int = max(rect.x,self.__crop_rect.x)
            new_y:int = max(rect.y,self.__crop_rect.y)
            rect = Shape(new_x,new_y,min(rect.right,self.__crop_rect.right)-new_x,min(rect.bottom,self.__crop_rect.bottom)-new_y)
        self.img = getSurface(rect.size,pygame.SRCALPHA).convert_alpha()
        self.__local_x = rect.x
        self.__local_y = rect.y
        self.img.blit(imgTmp,(-self.__local_x,-self.__local_y))
        if self._alpha != 255:
            self.img.set_alpha(self._alpha)
        self.__needUpdate = False
    #反转原图，并打上已反转的标记
    def flip(self) -> None:
        self.__isFlipped = not self.__isFlipped
        self.flip_original()
    #反转原图
    def flip_original(self) -> None:
        self.img_original = pygame.transform.flip(self.img_original,True,False)
        self.__needUpdate = True
    #如果不处于反转状态，则反转
    def flip_if_not(self) -> None:
        if not self.__isFlipped: self.flip()
    #反转回正常状态
    def flip_back_to_normal(self) -> None:
        if self.__isFlipped: self.flip()
    #画出轮廓
    def draw_outline(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0), color:str="red", line_width:int=2) -> None:
        pygame.draw.rect(surface,findColorRGBA(color),pygame.Rect(
            (self.x+self.__local_x+offSet[0],self.y+self.__local_y+offSet[1]),self.img.get_size()
            ),line_width)
    #是否被鼠标触碰
    def is_hover(self, mouse_pos:Union[tuple,list]=(-1,-1)) -> bool:
        if mouse_pos == (-1,-1): mouse_pos = pygame.mouse.get_pos()
        if self.img is not None:
            return 0 < mouse_pos[0]-self.x-self.__local_x < self.img.get_width() and 0 < mouse_pos[1]-self.y-self.__local_y < self.img.get_height()
        else:
            return False
    #返回local坐标
    def get_local_pos(self) -> tuple: return self.x+self.__local_x,self.y+self.__local_y
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
        #如果图片需要更新，则先更新
        if self.__needUpdate: self._update_img()
        #将已经处理好的图片画在给定的图层上
        surface.blit(self.img,(self.x+self.__local_x+offSet[0], self.y+self.__local_y+offSet[1]))

#高级图形类
class ImageSurface(AbstractImage):
    def __init__(self, img:pygame.Surface, x:Union[int,float], y:Union[int,float], width:any=None, height:any=None, description:str="Default"):
        super().__init__(img,x,y,width,height)
        self.xTogo = x
        self.yTogo = y
        self.items = []
        self.description = description
        if self._width is None and self._height is None:
            self._width,self._height = self.img.get_size()
        elif self._width is None and self._height is not None:
            self._width = self._height/self.img.get_height()*self.img.get_width()
        elif self._width is not None and self._height is None:
            self._height = self._width/self.img.get_width()*self.img.get_height()
    #返回一个复制
    def copy(self) -> None:
        replica = ImageSurface(self.img.copy(),self.x,self.y,self._width,self._height,self.description)
        self.img.set_alpha(255)
        replica.xTogo = self.xTogo
        replica.yTogo = self.yTogo
        replica.items = self.items.copy()
        return replica
    #更新图片
    def update(self, img_path:Union[str,pygame.Surface], ifConvertAlpha:bool=True) -> None:
        self.img = imgLoadFunction(img_path,ifConvertAlpha)
    def drawOnTheCenterOf(self, surface:pygame.Surface) -> None:
        surface.blit(resizeImg(self.img,self.size),((surface.get_width()-self._width)/2,(surface.get_height()-self._height)/2))
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        surface.blit(resizeImg(self.img,self.size),add_pos(self.pos,offSet))
    #旋转
    def rotate(self, angle:int) -> None: self.img = pygame.transform.rotate(self.img,angle)
    #反转
    def flip(self, vertical:bool=False, horizontal:bool=False) -> None: self.img = pygame.transform.flip(self.img,vertical,horizontal)
    #淡出
    def fade_out(self, speed:int) -> None:
        alphaTmp = self.get_alpha()
        if alphaTmp > 0: self.set_alpha(alphaTmp-speed)

#需要移动的动态图片
class DynamicImageSurface(ImageSurface):
    def __init__(self, img:pygame.Surface, x:Union[int,float], y:Union[int,float], target_x:Union[int,float], target_y:Union[int,float],
        moveSpeed_x:Union[int,float], moveSpeed_y:Union[int,float], width:any=None, height:any=None, description:str="Default"):
        super().__init__(img,x,y,width,height,description)
        self.default_x = x
        self.default_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.moveSpeed_x = moveSpeed_x
        self.moveSpeed_y = moveSpeed_y
        self.__towardTargetPos = False
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        super().display(surface,offSet)
        if self.__towardTargetPos is True:
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
    def switch(self) -> None: self.__towardTargetPos = not self.__towardTargetPos
    def ifToward(self) -> bool: return self.__towardTargetPos

#进度条
class ProgressBar(AbstractImage):
    def __init__(self, x:Union[int,float], y:Union[int,float], max_width:Union[int,float], height:Union[int,float], color:any):
        super().__init__(None,x,y,max_width,height)
        self.percentage = 0
        self.color = findColorRGBA(color)
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        pygame.draw.rect(surface,self.color,pygame.Rect(add_pos(self.pos,offSet),(int(self._width*self.percentage),self._height)))

#进度条Surface
class ProgressBarSurface(AbstractImage):
    def __init__(self, imgOnTop:pygame.Surface, imgOnBottom:pygame.Surface, x:Union[int,float], y:Union[int,float],
        max_width:Union[int,float], height:Union[int,float], mode:str="horizontal"):
        if imgOnTop is not None: imgOnTop = imgLoadFunction(imgOnTop,True)
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
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        pos = add_pos(self.pos,offSet)
        surface.blit(resizeImg(self.img2,self.size),pos)
        if self._current_percentage > 0:
            imgOnTop = resizeImg(self.img,self.size)
            if self._mode:
                surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._current_percentage),self._height)),pos)
            else:
                surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._current_percentage))),pos)

#动态进度条Surface
class DynamicProgressBarSurface(ProgressBarSurface):
    def __init__(self, imgOnTop:pygame.Surface, imgOnBottom:pygame.Surface, x:Union[int,float], y:Union[int,float],
        max_width:Union[int,float], height:Union[int,float], mode:str="horizontal"):
        super().__init__(imgOnTop,imgOnBottom,x,y,max_width,height,mode)
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
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        pos:tuple = add_pos(self.pos,offSet)
        surface.blit(resizeImg(self.img2,self.size),pos)
        self._check_and_update_percentage()
        if self._current_percentage > 0:
            imgOnTop = resizeImg(self.img,self.size)
            if self._mode:
                if self._current_percentage < self._percentage_to_be:
                    img2 = cropImg(imgOnTop,size=(int(self._width*self._percentage_to_be/self.accuracy),self._height))
                    img2.set_alpha(100)
                    surface.blit(img2,pos)
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._current_percentage/self.accuracy),self._height)),pos)
                else:
                    if self._current_percentage > self._percentage_to_be:
                        img2 = cropImg(imgOnTop,size=(int(self._width*self._current_percentage/self.accuracy),self._height))
                        img2.set_alpha(100)
                        surface.blit(img2,pos)
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._percentage_to_be/self.accuracy),self._height)),pos)
            else:
                if self._current_percentage < self._percentage_to_be:
                    img2 = cropImg(imgOnTop,size=(self._width,int(self._height*self._percentage_to_be/self.accuracy)))
                    img2.set_alpha(100)
                    surface.blit(img2,pos)
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._current_percentage/self.accuracy))),pos)
                else:
                    if self._current_percentage > self._percentage_to_be:
                        img2 = cropImg(imgOnTop,size=(self._width,int(self._height*self._current_percentage/self.accuracy)))
                        img2.set_alpha(100)
                        surface.blit(img2,pos)
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._percentage_to_be/self.accuracy))),pos)

#按钮
class Button(GameObject2d):
    def __init__(self, path:Union[str,pygame.Surface], x:Union[int,float], y:Union[int,float]):
        super().__init__(x,y)
        self.img = loadImg(path)
        self.img2 = None
        self._hoverEventTriggered = False
    def get_width(self) -> int: return self.img.get_width()
    def get_height(self) -> int: return self.img.get_height()
    def set_hover_img(self, img:pygame.Surface) -> None: self.img2 = img
    def is_hover(self, mouse_pos:Union[tuple, list]=(-1,-1)) -> bool:
        if not super().is_hover(mouse_pos):
            if self.img2 is not None and self._hoverEventTriggered:
                tempSurface = self.img
                self.img = self.img2
                self.img2 = tempSurface
                self._hoverEventTriggered = False
            return False
        else:
            if self.img2 is not None and not self._hoverEventTriggered:
                tempSurface = self.img
                self.img = self.img2
                self.img2 = tempSurface
                self._hoverEventTriggered = True
            return True
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None: surface.blit(self.img,add_pos(self.pos,offSet))

class ButtonWithDes(Button):
    def __init__(self, path:str, x:Union[int,float], y:Union[int,float], width:Union[int,float], height:Union[int,float], des:str):
        super().__init__(path,x,y)
        width = int(width)
        height = int(height)
        self.img = resizeImg(self.img,(width,height))
        self.set_hover_img(self.img.copy())
        self.img.set_alpha(150)
        self._width = width
        self._height = height
        self.des = des
        self.des_font_surface = fontRenderWithoutBound(des,"black",self._height*0.4)
        self.des_surface = pygame.Surface((self.des_font_surface.get_width()*1.2,self._height*0.6),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.des_surface,(255,255,255),(0,0, self.des_surface.get_width(),self.des_surface.get_height()))
        self.des_surface.blit(self.des_font_surface,(self.des_font_surface.get_width()*0.1,self._height*0.1))
    def get_width(self) -> int: return self._width
    def get_height(self) -> int: return self._height
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)) -> None:
        super().display(surface, offSet)
        if self._hoverEventTriggered: surface.blit(self.des_surface,pygame.mouse.get_pos())

class ButtonWithFadeInOut(Button):
    def __init__(self, path:str, txt:str, txt_color:any, alphaWhenNotHover:int, x:Union[int,float], y:Union[int,float], height:Union[int,float]):
        super().__init__(path,x,y)
        txtSurface = fontRenderWithoutBound(txt,txt_color,height*0.6)
        padding = int((height-txtSurface.get_height())/2)
        self.img = resizeImg(self.img,(txtSurface.get_width()+padding*2,height))
        self.img.blit(txtSurface,(padding,padding))
        self.set_hover_img(self.img.copy())
        self.img.set_alpha(alphaWhenNotHover)

#gif图片管理
class GifObject(AbstractImage):
    def __init__(self,imgList:Union[tuple,list], x:Union[int,float], y:Union[int,float], width:Union[int,float], height:Union[int,float], updateGap:int):
        super().__init__(imgList,x,y,width,height)
        self.imgId = 0
        self.updateGap = updateGap
        self.countDown = 0
        self._alpha = 255
    #透明度
    def get_alpha(self) -> int: return self._alpha
    def set_alpha(self, value:Union[int,float]) -> None: self._alpha = keepInRange(int(value),0,255)
    def display(self, surface:pygame.Surface, offSet:Union[tuple,list]=(0,0)):
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

#对话框基础模块
class AbstractDialog:
    def __init__(self, img:pygame.Surface, fontSize:Union[int,float]):
        self.dialoguebox = img
        self.FONTSIZE = int(fontSize)
        self.FONT = createFont(self.FONTSIZE)
        self.content = []
        self.narrator = None
        self.textIndex = None
        self.displayedLine = None
    def update(self, txt:list, narrator:str) -> None:
        self.textIndex = 0
        self.displayedLine = 0
        self.content = txt
        self.narrator = narrator
    #是否所有内容均已展出
    def is_all_played(self) -> bool:
        #如果self.content是空的，也就是说没有任何内容，那么应当视为所有内容都被播放了
        if len(self.content) == 0:
            return True
        else:
            return self.displayedLine >= len(self.content)-1 and self.textIndex >= len(self.content[self.displayedLine])-1
    #立刻播出所有内容
    def play_all(self) -> None:
        if not self.is_all_played():
            self.displayedLine = len(self.content)-1
            self.textIndex = len(self.content[self.displayedLine])-1

#对话框和对话框内容
class DialogBox(AbstractDialog,GameObject2d):
    def __init__(self, imgPath:str, width:Union[int,float], height:Union[int,float], x:Union[int,float], y:Union[int,float], fontSize:int):
        AbstractDialog.__init__(self,loadImg(imgPath,(width,height)),fontSize)
        GameObject2d.__init__(self,x,y)
        self.__surface = None
        self.deafult_x = x
        self.deafult_y = y
        self.txt_x = fontSize
        self.txt_y = fontSize*2
        self.narrator_icon = None
        self.narrator_x = fontSize*3
        self.narrator_y = fontSize/2
        self.updated:bool = False
        self.__drew:bool = False
        self.__flipped:bool = False
    def get_width(self) -> int: return self.dialoguebox.get_width()
    def get_height(self)-> int:  return self.dialoguebox.get_height()
    def set_size(self, width:Union[int,float,None], height:Union[int,float,None]) -> None:
        self.dialoguebox = resizeImg(self.dialoguebox,(width,height))
    def draw(self, surface:pygame.Surface, characterInfoBoardUI:object=None):
        #如果对话框需要继续更新
        if not self.__drew:
            self.__surface = self.dialoguebox.copy()
            if self.__flipped is True:
                #讲述人名称
                if self.narrator is not None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.get_width()*0.6+self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon is not None and characterInfoBoardUI is not None:
                    self.__surface.blit(characterInfoBoardUI.characterIconImages[self.narrator_icon],(self.get_width()-self.txt_x,self.txt_y))
                x = self.txt_x
            else:
                #讲述人名称
                if self.narrator is not None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon is not None and characterInfoBoardUI is not None:
                    img = characterInfoBoardUI.characterIconImages[self.narrator_icon]
                    self.__surface.blit(img,(self.txt_x,self.txt_y))
                    x = self.txt_x+img.get_width() + self.FONTSIZE
                else:
                    x = self.txt_x
            y = self.txt_y
            if len(self.content)>0:
                #已经播放的行
                for i in range(self.displayedLine):
                    self.__surface.blit(self.FONT.render(self.content[i],get_fontMode(),(255,255,255)),(x,y))
                    y += self.FONTSIZE*1.2
                #正在播放的行
                self.__surface.blit(self.FONT.render(self.content[self.displayedLine][:self.textIndex],get_fontMode(),(255,255,255)),(x,y))
                if self.textIndex < len(self.content[self.displayedLine]):
                    self.textIndex += 1
                elif self.displayedLine < len(self.content)-1:
                    self.displayedLine += 1
                    self.textIndex = 0
                elif self.textIndex >= len(self.content[self.displayedLine]):
                    self.__drew = True
        surface.blit(self.__surface,(self.x,self.y))
    def update(self, txt:list, narrator:str, narrator_icon:str=None) -> None:
        super().update(txt,narrator)
        self.updated = True
        self.__drew = False
        self.narrator_icon = narrator_icon
    def reset(self) -> None:
        self.x = self.deafult_x
        self.y = self.deafult_y
        self.updated = False
        #刷新对话框surface防止上一段的对话还残留在surface上
        self.content = []
        self.__surface = self.dialoguebox.copy()
    def flip(self) -> None:
        self.dialoguebox = pygame.transform.flip(self.dialoguebox,True,False)
        self.__flipped = not self.__flipped
