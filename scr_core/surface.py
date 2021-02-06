# cython: language_level=3
from tkinter import Tk
from .module import *

#图形接口
class ImageInterface(GameObject2d):
    def __init__(self,img:pygame.Surface,x:float,y:float,width:int,height:int) -> None:
        GameObject2d.__init__(self,x,y)
        self.img = img
        self._width = width
        self._height = height
    #透明度
    def get_alpha(self) -> int: return self.img.get_alpha()
    def set_alpha(self,value:int) -> None: self.img.set_alpha(value)
    #宽度
    def get_width(self) -> int: return self._width
    def set_width(self,value:float) -> None: self._width = round(value)
    #高度
    def get_height(self) -> int: return self._height
    def set_height(self,value:float) -> None: self._height = round(value)
    #尺寸
    def set_size(self,width:int,height:int) -> None:
        self.set_width(width)
        self.set_height(height)
    
#用于处理有大面积透明像素的图片surface
class SrcalphaSurface(ImageInterface):
    def __init__(self,path_or_surface,x,y,width=None,height=None):
        ImageInterface.__init__(self,None,x,y,width,height)
        self._alpha = 255
        self.img_original = loadImg(path_or_surface)
        self.__local_x = 0
        self.__local_y = 0
        self.__isFlipped = False
        self.__needUpdate = True if self._width != None and self._height != None else False
    #透明度
    def get_alpha(self) -> int: return self._alpha
    def set_alpha(self,value:int) -> None:
        if value < 0:
            self._alpha = 0
        elif value > 255:
            self._alpha = 255
        else:
            self._alpha = round(value)
        if self.img != None and self.img.get_alpha() != self._alpha: super().set_alpha(self._alpha)
    #宽度
    def set_width(self,value:float) -> None:
        value = round(value)
        if self._width != value:
            super().set_width(value)
            self.__needUpdate = True
    def set_width_with_size_locked(self,width:float) -> None:
        height = round(width/self.img_original.get_width()*self.img_original.get_height())
        width = round(width)
        self.set_size(width,height)
    #高度
    def set_height(self,value:float) -> None:
        value = round(value)
        if self._height != value:
            super().set_height(value)
            self.__needUpdate = True
    def set_height_with_size_locked(self,height:float) -> None:
        width = round(height/self.img_original.get_height()*self.img_original.get_width())
        height = round(height)
        self.set_size(width,height)
    #更新图片
    def _update_img(self):
        imgTmp = resizeImg(self.img_original,(self._width,self._height))
        rect = imgTmp.get_bounding_rect()
        self.img = getSurface(rect.size,pygame.SRCALPHA).convert_alpha()
        self.__local_x = rect.x
        self.__local_y = rect.y
        self.img.blit(imgTmp,(-self.__local_x,-self.__local_y))
        if self._alpha != 255:
            self.img.set_alpha(self._alpha)
        self.__needUpdate = False
    #反转原图，并打上已反转的标记
    def flip(self):
        self.__isFlipped = not self.__isFlipped
        self.flip_original()
    #反转原图
    def flip_original(self):
        self.img_original = pygame.transform.flip(self.img_original,True,False)
        self.__needUpdate = True
    #如果不处于反转状态，则反转
    def flip_if_not(self) -> None:
        if not self.__isFlipped: self.flip()
    #反转回正常状态
    def flip_back_to_normal(self) -> None:
        if self.__isFlipped: self.flip()
    #展示
    def draw(self,screen,debug:bool=False) -> None: self.display(screen,debug)
    def display(self,screen,debug:bool=False,offSet:tuple=(0,0)) -> None:
        if self.__needUpdate:
            self._update_img()
        pos = (self.x+self.__local_x+offSet[0], self.y+self.__local_y+offSet[1])
        screen.blit(self.img, pos)
        #如果是debug模式
        if debug: pygame.draw.rect(screen,findColorRGBA("red"),pygame.Rect(pos,self.img.get_size()),2)
    #是否被鼠标触碰
    def isHover(self,mouse_x:int,mouse_y:int) -> bool:
        return 0 < mouse_x-self.x-self.__local_x < self.img.get_width() and 0 < mouse_y-self.y-self.__local_y < self.img.get_height()
    #返回local坐标
    def get_local_pos(self) -> tuple: return self.x+self.__local_x,self.y+self.__local_y
    #返回一个复制品
    def copy(self): return SrcalphaSurface(self.img_original.copy(),self.x,self.y,self._width,self._height)
    #加暗度
    def addDarkness(self,value:int) -> None:
        self.img_original.fill((value, value, value),special_flags=pygame.BLEND_RGB_SUB)
        self.__needUpdate = True

#高级图形类
class ImageSurface(ImageInterface):
    def __init__(self,img,x,y,width=None,height=None,description="Default"):
        ImageInterface.__init__(self,img,x,y,width,height)
        self.xTogo = x
        self.yTogo = y
        self.items = []
        self.description = description
        if self._width == None and self._height == None:
            self._width,self._height = self.img.get_size()
        elif self._width == None and self._height != None:
            self._width = self._height/self.img.get_height()*self.img.get_width()
        elif self._width != None and self._height == None:
            self._height = self._width/self.img.get_width()*self.img.get_height()
    def drawOnTheCenterOf(self,surface):
        surface.blit(resizeImg(self.img, (self._width,self._height)),((surface.get_width()-self._width)/2,(surface.get_height()-self._height)/2))
    def display(self,screen,local_x=0,local_y=0):
        screen.blit(resizeImg(self.img, (self._width,self._height)),(self.x+local_x,self.y+local_y))
    #旋转
    def rotate(self,angle) -> None: self.img = pygame.transform.rotate(self.img,angle)
    #反转
    def flip(self,vertical=False,horizontal=False) -> None: self.img = pygame.transform.flip(self.img,vertical,horizontal)
    #是否被鼠标触碰
    def isHover(self,mouse_x:int,mouse_y:int) -> bool: return 0 < mouse_x-self.x < self._width and 0 < mouse_y-self.y < self._height 
    #淡出
    def fade_out(self,speed):
        alphaTmp = self.get_alpha()
        if alphaTmp > 0: self.set_alpha(alphaTmp-speed)

#需要移动的动态图片
class DynamicImageSurface(ImageSurface):
    def __init__(self,img,x,y,target_x,target_y,moveSpeed_x,moveSpeed_y,width=None,height=None,description="Default") -> None:
        ImageSurface.__init__(self,img,x,y,width,height,description)
        self.default_x = x
        self.default_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.moveSpeed_x = moveSpeed_x
        self.moveSpeed_y = moveSpeed_y
        self.__towardTargetPos = False
    def display(self,screen,local_x=0,local_y=0) -> None:
        super().display(screen,local_x,local_y)
        if self.__towardTargetPos == True:
            if self.default_x < self.target_x and self.x < self.target_x:
                self.x += self.moveSpeed_x
            elif self.default_x > self.target_x and self.x > self.target_x:
                self.x -= self.moveSpeed_x
            if self.default_y < self.target_y and self.y < self.target_y:
                self.y += self.moveSpeed_y
            elif self.default_y > self.target_y and self.y > self.target_y:
                self.y -= self.moveSpeed_y
        else:
            if self.default_x < self.target_x and self.x > self.default_x:
                self.x -= self.moveSpeed_x
            elif self.default_x > self.target_x and self.x < self.default_x:
                self.x += self.moveSpeed_x
            if self.default_y < self.target_y and self.y > self.default_y:
                self.y -= self.moveSpeed_y
            elif self.default_y > self.target_y and self.y < self.default_y:
                self.y += self.moveSpeed_y
    def switch(self) -> None: self.__towardTargetPos = not self.__towardTargetPos
    def ifToward(self) -> bool: return self.__towardTargetPos

#进度条
class ProgressBar(ImageInterface):
    def __init__(self,x,y,max_width,height,color) -> None:
        ImageInterface.__init__(self,None,x,y,max_width,height)
        self.percentage = 0
        self.color = findColorRGBA(color)
    def display(self,screen,offSet:tuple=(0,0)) -> None:
        pygame.draw.rect(screen,self.color,(self.x+offSet[0],self.y+offSet[1],self._width*self.percentage,self._height))

#进度条Surface
class ProgressBarSurface(ImageInterface):
    def __init__(self,imgOnTop,imgOnBottom,x,y,max_width,height,mode="width"):
        ImageInterface.__init__(self,imgLoadFunction(imgOnTop,True),x,y,max_width,height)
        self.img2 = imgLoadFunction(imgOnBottom,True)
        self.__current_percentage = 0
        self.__percentage_to_be = 0
        self.__perecent_update_each_time = 0
        self.__total_update_intervals = 10
        self.__mode = True if mode == "width" else False
    #数据准确度
    @property
    def accuracy(self) -> int: return self.__total_update_intervals*100
    #百分比
    @property
    def percentage(self) -> float: return self.__percentage_to_be/self.accuracy
    def get_percentage(self) -> float: return self.__percentage_to_be/self.accuracy
    def set_percentage(self,value:float) -> None:
        if 0 <= value <= 1:
            self.__percentage_to_be = value*self.accuracy
            self.__perecent_update_each_time = (self.__percentage_to_be-self.__current_percentage)/self.__total_update_intervals
        else:
            raise Exception('LinpgEngine-Error: The percentage must be <= 1 and >= 0!')
    #模式
    @property
    def mode(self) -> str: return self.get_mode()
    def get_mode(self) -> str: return "height" if self.__mode else "width"
    def set_mode(self,mode:str):
        if mode == "width":
            self.__mode = True
        elif mode == "height":
            self.__mode = False
        else:
            raise Exception('LinpgEngine-Error: Mode {} is not supported!'.format(mode))
    #展示
    def display(self, screen, offSet:tuple=(0,0)) -> None:
        pos = (self.x+offSet[0],self.y+offSet[1])
        screen.blit(resizeImg(self.img2,self.size),pos)
        if self.__current_percentage < self.__percentage_to_be and self.__perecent_update_each_time > 0 or\
            self.__current_percentage > self.__percentage_to_be and self.__perecent_update_each_time < 0:
            self.__current_percentage += self.__perecent_update_each_time
        if self.__current_percentage > 0:
            imgOnTop = resizeImg(self.img,self.size)
            if self.__mode:
                screen.blit(imgOnTop.subsurface((0,0,int(self._width*self.__current_percentage/self.accuracy),self._height)),pos)
            else:
                screen.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self.__current_percentage/self.accuracy))),pos)

#按钮
class Button(GameObject2d):
    def __init__(self,path,x,y):
        GameObject2d.__init__(self,x,y)
        self.img = loadImg(path)
        self.img2 = None
        self.hoverEventTriggered = False
    def setHoverImg(self,img): self.img2 = img
    def display(self,screen,local_x=0,local_y=0): screen.blit(self.img,(self.x+local_x,self.y+local_y))
    def hoverEventOn(self):
        if self.img2 != None and self.hoverEventTriggered == False:
            tempSurface = self.img
            self.img = self.img2
            self.img2 = tempSurface
            self.hoverEventTriggered = True
    def hoverEventOff(self):
        if self.img2 != None and self.hoverEventTriggered == True:
            tempSurface = self.img
            self.img = self.img2
            self.img2 = tempSurface
            self.hoverEventTriggered = False
    def get_width(self) -> int: return self.img.get_width()
    def get_height(self) -> int: return self.img.get_height()

class ButtonWithDes(Button):
    def __init__(self,path,x,y,width,height,des) -> None:
        Button.__init__(self,path,x,y)
        width = int(width)
        height = int(height)
        self.img = resizeImg(self.img,(width,height))
        self.img2 = self.img.copy()
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
    def displayDes(self,screen) -> None:
        if self.hoverEventTriggered: screen.blit(self.des_surface,pygame.mouse.get_pos())

class ButtonWithFadeInOut(Button):
    def __init__(self,buttonImgPath,txt,txt_color,alphaWhenNotHovered,x,y,height) -> None:
        Button.__init__(self,buttonImgPath,x,y)
        txtSurface = fontRenderWithoutBound(txt,txt_color,height*0.6)
        self.img = resizeImg(self.img,(txtSurface.get_width()+height,height))
        self.img.blit(txtSurface,(height*0.5,(height-txtSurface.get_height())/2))
        self.img2 = self.img.copy()
        self.img.set_alpha(alphaWhenNotHovered)

#gif图片管理
class GifObject(ImageInterface):
    def __init__(self,imgList:tuple,x,y,width,height,updateGap) -> None:
        ImageInterface.__init__(self,imgList,x,y,width,height)
        self.imgId = 0
        self.updateGap = updateGap
        self.countDown = 0
        self._alpha = 255
    #透明度
    def get_alpha(self) -> int: return self._alpha
    def set_alpha(self,value) -> None:
        if value < 0:
            self._alpha = 0
        elif value > 255:
            self._alpha = 255
        else:
            self._alpha = round(value)
    def display(self,screen,offSet:tuple=(0,0)):
        img = resizeImg(self.img[self.imgId],self.size)
        #设置透明度
        if self._alpha != 255: img.set_alpha(self._alpha)
        screen.blit(img,(self.x+offSet[0],self.y+offSet[1]))
        if self.countDown >= self.updateGap:
            self.countDown = 0
            self.imgId += 1
            if self.imgId >= len(self.img): self.imgId = 0
        else:
            self.countDown += 1

#对话框基础模块
class DialogInterface:
    def __init__(self,img,fontSize):
        self.dialoguebox = img
        self.FONTSIZE = int(fontSize)
        self.FONT = createFont(self.FONTSIZE)
        self.content = []
        self.narrator = None
        self.textIndex = None
        self.displayedLine = None
    def update(self,txt,narrator):
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
    def play_all(self):
        if not self.is_all_played():
            self.displayedLine = len(self.content)-1
            self.textIndex = len(self.content[self.displayedLine])-1

#对话框和对话框内容
class DialogBox(DialogInterface,GameObject2d):
    def __init__(self,imgPath,width,height,x,y,fontSize):
        DialogInterface.__init__(self,loadImg(imgPath,(width,height)),fontSize)
        GameObject2d.__init__(self,x,y)
        self.__surface = None
        self.deafult_x = x
        self.deafult_y = y
        self.txt_x = fontSize
        self.txt_y = fontSize*2
        self.narrator_icon = None
        self.narrator_x = fontSize*3
        self.narrator_y = fontSize/2
        self.updated = False
        self.__drew = False
        self.__flipped = False
    def get_width(self) -> int: return self.dialoguebox.get_width()
    def get_height(self)-> int:  return self.dialoguebox.get_height()
    def set_size(self,width,height) -> tuple: self.dialoguebox = resizeImg(self.dialoguebox,(width,height))
    def display(self,screen,characterInfoBoardUI=None):
        #如果对话框需要继续更新
        if self.__drew == False:
            self.__surface = self.dialoguebox.copy()
            if self.__flipped == True:
                #讲述人名称
                if self.narrator != None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.get_width()*0.6+self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon != None and characterInfoBoardUI != None:
                    img = characterInfoBoardUI.characterIconImages[self.narrator_icon]
                    self.__surface.blit(img,(self.get_width()-self.txt_x,self.txt_y))
                x = self.txt_x
            else:
                #讲述人名称
                if self.narrator != None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon != None and characterInfoBoardUI != None:
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
        screen.blit(self.__surface,(self.x,self.y))
    def update(self,txt,narrator,narrator_icon=None):
        super().update(txt,narrator)
        self.updated = True
        self.__drew = False
        self.narrator_icon = narrator_icon
    def reset(self):
        self.x = self.deafult_x
        self.y = self.deafult_y
        self.updated = False
        #刷新对话框surface防止上一段的对话还残留在surface上
        self.content = []
        self.__surface = self.dialoguebox.copy()
    def flip(self):
        self.dialoguebox = pygame.transform.flip(self.dialoguebox,True,False)
        self.__flipped = not self.__flipped