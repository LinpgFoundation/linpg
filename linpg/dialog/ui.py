# cython: language_level=3
from .movie import *

#ui路径
DIALOG_UI_PATH:str = "Assets/image/UI"

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
        self.autoButton.description = int(self.autoButton.x+self.autoButton.img.get_width()-self.FONTSIZE)
        self.autoButtonHovered = ImageSurface(self.autoButtonHovered,window_x*0.8,window_y*0.05)
        self.autoButtonHovered.description = int(self.autoButtonHovered.x+self.autoButtonHovered.img.get_width()-self.FONTSIZE)
        #隐藏按钮
        hideUI_img = loadImg(os.path.join(DIALOG_UI_PATH,"dialog_hide.png"),(self.FONTSIZE,self.FONTSIZE))
        hideUI_imgTemp = hideUI_img.copy()
        hideUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.hideButton = Button(hideUI_imgTemp,window_x*0.05,window_y*0.05)
        self.hideButton.set_hover_img(hideUI_img)
        showUI_img = loadImg(os.path.join(DIALOG_UI_PATH,"dialog_show.png"),(self.FONTSIZE,self.FONTSIZE))
        showUI_imgTemp = showUI_img.copy()
        showUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.showButton = Button(showUI_imgTemp,window_x*0.05,window_y*0.05)
        self.showButton.set_hover_img(showUI_img)
        #历史回溯按钮
        history_img = loadImg(os.path.join(DIALOG_UI_PATH,"dialog_history.png"),(self.FONTSIZE,self.FONTSIZE))
        history_imgTemp = history_img.copy()
        history_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.historyButton = Button(history_imgTemp,window_x*0.1,window_y*0.05)
        self.historyButton.set_hover_img(history_img)
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
                        self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    surface.blit(self.autoIconHovered,(self.autoButtonHovered.description,self.autoButtonHovered.y+self.icon_y))
                action = "auto"
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(surface)
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    self.autoButton.draw(surface)
                    surface.blit(self.autoIcon,(self.autoButton.description,self.autoButton.y+self.icon_y))
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
    def __init__(self, img: any, font_size: int, x: int, y: int, width: int, height: int):
        super().__init__(StaticImageSurface(img,0,0), x, y, width, height)
        #警告-标题
        self.__warning_title = TextSurface(fontRender(get_lang("Global","warning"),"white",font_size),0,font_size)
        self.__warning_title.set_centerx(self._width/2)
        #内容
        self.__text_1 = TextSurface(fontRender(get_lang("Dialog","leave_without_save1"),"white",font_size),0,font_size*2.5)
        self.__text_1.set_centerx(self._width/2)
        self.__text_2 = TextSurface(fontRender(get_lang("Dialog","leave_without_save2"),"white",font_size),0,font_size*4)
        self.__text_2.set_centerx(self._width/2)
        #保存按钮
        self.save_button = ButtonWithFadeInOut(os.path.join(DIALOG_UI_PATH,"menu.png"),get_lang("Global","save"),"black",200,0,0,font_size*2)
        self.save_button.set_bottom(self._height*0.9)
        #取消按钮
        self.cancel_button = ButtonWithFadeInOut(os.path.join(DIALOG_UI_PATH,"menu.png"),get_lang("Global","cancel"),"black",200,0,0,font_size*2)
        self.cancel_button.set_bottom(self._height*0.9)
        #不要保存按钮
        self.dont_save_button = ButtonWithFadeInOut(os.path.join(DIALOG_UI_PATH,"menu.png"),get_lang("Global","dont_save"),"black",200,0,0,font_size*2)
        self.dont_save_button.set_bottom(self._height*0.9)
        #计算间距
        panding_on_side:int = int(self._width*0.1)
        panding_between_button:int = int(
            (self._width-panding_on_side*2-self.save_button.get_width()-self.cancel_button.get_width()-self.dont_save_button.get_width())/2
        )
        #设置x轴坐标
        self.save_button.set_left(panding_on_side)
        self.cancel_button.set_left(self.save_button.get_right()+panding_between_button)
        self.dont_save_button.set_left(self.cancel_button.get_right()+panding_between_button)
        #默认隐藏
        self.hidden:bool = True
    def display(self, surface: pygame.Surface, offSet:tuple=(0,0)) -> None:
        if not self.hidden:
            #画出背景
            self.img.set_size(self._width,self._height)
            self.img.display(surface,add_pos(self.pos,offSet))
            #画出内容
            self.__warning_title.display(surface,add_pos(self.pos,offSet))
            self.__text_1.display(surface,add_pos(self.pos,offSet))
            self.__text_2.display(surface,add_pos(self.pos,offSet))
            #按钮
            self.save_button.display(surface,add_pos(self.pos,offSet))
            self.cancel_button.display(surface,add_pos(self.pos,offSet))
            self.dont_save_button.display(surface,add_pos(self.pos,offSet))
