# cython: language_level=3
from .movie import *

#ui路径
DIALOG_UI_PATH:str = "Assets/image/UI"

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
    def __init__(self, imgPath:str, x:Union[int,float], y:Union[int,float], width:int, height:int, fontSize:int):
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
        self.dialoguebox = flipImg(self.dialoguebox,True,False)
        self.__flipped = not self.__flipped

#对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        #从设置中读取信息
        window_x,window_y = display.get_size()
        self.FONTSIZE:int = int(window_x*0.0175)
        self.FONT = createFont(self.FONTSIZE)
        #从语言文件中读取按钮文字
        dialog_txt = get_lang("Dialog")
        #生成跳过按钮
        tempButtonIcon = loadImg(os.path.join(DIALOG_UI_PATH,"dialog_skip.png"),(self.FONTSIZE,self.FONTSIZE))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_fontMode(),(255, 255, 255))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.choiceTxt = dialog_txt["choice"]
        self.skipButton = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.skipButtonHovered = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.icon_y = (tempButtonTxt.get_height()-tempButtonIcon.get_height())/2
        self.skipButtonHovered.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButtonHovered.blit(tempButtonTxt,(0,0))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_fontMode(),(105, 105, 105))
        tempButtonIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.skipButton.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButton.blit(tempButtonTxt,(0,0))
        self.skipButton = ImageSurface(self.skipButton,window_x*0.9,window_y*0.05)
        self.skipButtonHovered = ImageSurface(self.skipButtonHovered,window_x*0.9,window_y*0.05)
        #生成自动播放按钮
        self.autoIconHovered = loadImg(os.path.join(DIALOG_UI_PATH,"dialog_auto.png"),(self.FONTSIZE,self.FONTSIZE))
        self.autoIcon = self.autoIconHovered.copy()
        self.autoIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.autoIconDegree = 0
        self.autoIconDegreeChange = (2**0.5-1)*self.FONTSIZE/45
        self.autoMode:bool = False
        tempButtonTxt = self.FONT.render(dialog_txt["auto"],get_fontMode(),(105, 105, 105))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.autoButton = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.autoButtonHovered = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.autoButton.blit(tempButtonTxt,(0,0))
        self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"],get_fontMode(),(255, 255, 255)),(0,0))
        self.autoButton = ImageSurface(self.autoButton,window_x*0.8,window_y*0.05)
        self.autoButton.tag = int(self.autoButton.x+self.autoButton.img.get_width()-self.FONTSIZE)
        self.autoButtonHovered = ImageSurface(self.autoButtonHovered,window_x*0.8,window_y*0.05)
        self.autoButtonHovered.tag = int(self.autoButtonHovered.x+self.autoButtonHovered.img.get_width()-self.FONTSIZE)
        #隐藏按钮
        self.hideButton = loadButton(
            os.path.join(DIALOG_UI_PATH,"dialog_hide.png"), (window_x*0.05, window_y*0.05),(self.FONTSIZE,self.FONTSIZE), 150
            )
        #取消隐藏按钮
        self.showButton = loadButton(
            os.path.join(DIALOG_UI_PATH,"dialog_show.png"), (window_x*0.05, window_y*0.05),(self.FONTSIZE,self.FONTSIZE), 150
        )
        #历史回溯按钮
        self.historyButton = loadButton(
            os.path.join(DIALOG_UI_PATH,"dialog_history.png"), (window_x*0.1, window_y*0.05),(self.FONTSIZE,self.FONTSIZE), 150
        )
    def draw(self, surface: pygame.Surface, isHidden: bool) -> str:
        if isHidden is True:
            self.showButton.draw(surface)
            return "hide" if self.showButton.is_hover() else ""
        else:
            self.hideButton.draw(surface)
            self.historyButton.draw(surface)
            action = ""
            if self.skipButton.is_hover():
                self.skipButtonHovered.draw(surface)
                action = "skip"
            else:
                self.skipButton.draw(surface)
            if self.autoButton.is_hover():
                self.autoButtonHovered.draw(surface)
                if self.autoMode:
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.tag+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    surface.blit(self.autoIconHovered,(self.autoButtonHovered.tag,self.autoButtonHovered.y+self.icon_y))
                action = "auto"
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(surface)
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.tag+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    self.autoButton.draw(surface)
                    surface.blit(self.autoIcon,(self.autoButton.tag,self.autoButton.y+self.icon_y))
            if self.hideButton.is_hover():
                action = "hide"
            elif self.historyButton.is_hover():
                action = "history"
            return action
    def autoModeSwitch(self) -> None:
        if not self.autoMode:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0

#未保存离开时的警告
class LeaveWithoutSavingWarning(AbstractImage):
    def __init__(self, img: any, x: int, y: int, width: int, height: int):
        super().__init__(StaticImageSurface(img,0,0), x, y, width, height)
        font_size:int = int(height/10)
        #警告-标题
        self.__warning_title = TextSurface(fontRender(get_lang("Global","warning"),"white",font_size),0,font_size)
        self.__warning_title.set_centerx(self._width/2)
        #内容
        self.__text_1 = TextSurface(fontRender(get_lang("Dialog","leave_without_save1"),"white",font_size),0,font_size*2.5)
        self.__text_1.set_centerx(self._width/2)
        self.__text_2 = TextSurface(fontRender(get_lang("Dialog","leave_without_save2"),"white",font_size),0,font_size*4)
        self.__text_2.set_centerx(self._width/2)
        font_size = int(font_size*1.5)
        #保存按钮
        self.save_button = loadButtonWithTextInCenter(
            os.path.join(DIALOG_UI_PATH,"menu.png"), get_lang("Global","save"), "black", font_size, (0,0), 150
            )
        self.save_button.set_bottom(self._height*0.9)
        #取消按钮
        self.cancel_button = loadButtonWithTextInCenter(
            os.path.join(DIALOG_UI_PATH,"menu.png"), get_lang("Global","cancel"), "black", font_size, (0,0), 150
            )
        self.cancel_button.set_bottom(self._height*0.9)
        #不要保存按钮
        self.dont_save_button = loadButtonWithTextInCenter(
            os.path.join(DIALOG_UI_PATH,"menu.png"), get_lang("Global","dont_save"), "black", font_size, (0,0), 150
            )
        self.dont_save_button.set_bottom(self._height*0.9)
        #计算间距
        panding:int = int((self._width-self.save_button.get_width()-self.cancel_button.get_width()-self.dont_save_button.get_width())/4)
        #设置x轴坐标
        self.save_button.set_left(panding)
        self.cancel_button.set_left(self.save_button.get_right()+panding)
        self.dont_save_button.set_left(self.cancel_button.get_right()+panding)
        #默认隐藏
        self.hidden:bool = True
        #触碰的按钮
        self.__button_hovered:int = 0
    @property
    def button_hovered(self) -> str:
        if self.__button_hovered == 1:
            return "save"
        elif self.__button_hovered == 2:
            return "cancel"
        elif self.__button_hovered == 3:
            return "dont_save"
        else:
            return ""
    def display(self, surface: pygame.Surface, offSet:tuple=(0,0)) -> None:
        self.__button_hovered = 0
        if not self.hidden:
            pos = add_pos(self.pos,offSet)
            #画出背景
            self.img.set_size(self._width,self._height)
            self.img.display(surface,pos)
            #画出内容
            self.__warning_title.display(surface,pos)
            self.__text_1.display(surface,pos)
            self.__text_2.display(surface,pos)
            """按钮"""
            #保存
            if isHover(self.save_button, local_x=pos[0], local_y=pos[1]): self.__button_hovered = 1
            self.save_button.display(surface,pos)
            #取消
            if isHover(self.cancel_button, local_x=pos[0], local_y=pos[1]): self.__button_hovered = 2
            self.cancel_button.display(surface,pos)
            #不要保存
            if isHover(self.dont_save_button, local_x=pos[0], local_y=pos[1]): self.__button_hovered = 3
            self.dont_save_button.display(surface,pos)
