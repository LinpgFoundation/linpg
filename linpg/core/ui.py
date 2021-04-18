# cython: language_level=3
from .container import *

#暂停菜单
class PauseMenu:
    def __init__(self) -> None:
        self.white_bg = None
        self.button_resume = None
        self.button_save = None
        self.button_setting = None
        self.button_back = None
        self.screenshot = None
    def __initial(self, surface:pygame.Surface) -> None:
        width,height = display.get_size()
        surfaceTmp = pygame.Surface((width,height),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(surfaceTmp,(0,0,0),(0,0,width,height))
        self.white_bg = ImageSurface(surfaceTmp,0,0,width,height)
        self.white_bg.set_alpha(50)
        #按钮-继续
        self.button_resume = fontRenderPro(
            get_lang("MainMenu","menu_main")["0_continue"],
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.4,surface.get_width()/38)
        )
        #按钮-保存游戏
        self.button_save = fontRenderPro(
            get_lang("SaveGame"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.5,surface.get_width()/38)
        )
        #按钮-设置
        self.button_setting = fontRenderPro(
            get_lang("MainMenu","menu_main")["5_setting"],
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.6,surface.get_width()/38)
        )
        #按钮-返回
        self.button_back = fontRenderPro(
            get_lang("DialogCreator","back"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.7,surface.get_width()/38)
        )
    def draw(self, surface:pygame.Surface, pygame_events=pygame.event.get()) -> None:
        #展示原先的背景
        if self.screenshot is None:
            self.screenshot = surface.copy()
        surface.blit(self.screenshot,(0,0))
        #展示暂停菜单的背景层
        if self.white_bg is None:
            self.__initial(surface)
        self.white_bg.draw(surface)
        #展示按钮
        self.button_resume.draw(surface)
        self.button_save.draw(surface)
        self.button_setting.draw(surface)
        self.button_back.draw(surface)
        #判定按键
        for event in pygame_events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "Break"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #判定按钮
                if self.button_resume.is_hover():
                    return "Break"
                elif self.button_save.is_hover():
                    return "Save"
                elif self.button_setting.is_hover():
                    return "Setting"
                elif self.button_back.is_hover():
                    set_glob_value("BackToMainMenu",True)
                    return "BackToMainMenu"
        return False

#设置UI
class SettingContoller:
    def __init__(self) -> None:
        self.isDisplaying = False
    def init(self, size:Union[tuple,list]) -> None:
        self.baseImgWidth = round(size[0]/3)
        self.baseImgHeight = round(size[0]/3)
        self.baseImg = loadImg("Assets/image/UI/setting_baseImg.png",(self.baseImgWidth,self.baseImgHeight))
        self.baseImg.set_alpha(200)
        self.baseImgX = int((size[0]-self.baseImgWidth)/2)
        self.baseImgY = int((size[1]-self.baseImgHeight)/2)
        self.bar_height = round(size[0]/60)
        self.bar_width = round(size[0]/5)
        self.button = loadImg("Assets/image/UI/setting_bar_circle.png",(self.bar_height,self.bar_height*2))
        self.bar_img1 = DynamicProgressBarSurface(
            "Assets/image/UI/setting_bar_full.png",
            "Assets/image/UI/setting_bar_empty.png",
            0,0,self.bar_width,self.bar_height)
        self.bar_img2 = self.bar_img1.light_copy()
        self.bar_img3 = self.bar_img2.light_copy()
        self.bar_x = int(self.baseImgX+(self.baseImgWidth-self.bar_width)/2)
        self.bar_y0 = self.baseImgY + self.baseImgHeight*0.2
        self.bar_y1 = self.baseImgY + self.baseImgHeight*0.4
        self.bar_y2 = self.baseImgY + self.baseImgHeight*0.6
        self.bar_y3 = self.baseImgY + self.baseImgHeight*0.8
        #音量数值
        self.soundVolume_background_music = 0
        self.soundVolume_sound_effects = 0
        self.soundVolume_sound_environment = 0
        self.__update_sound()
        #设置UI中的文字
        self.FONTSIZE = round(size[0]/50)
        self.fontSizeBig = round(size[0]/50*1.5)
        self.normalFont = createFont(self.FONTSIZE)
        self.bigFont = createFont(self.fontSizeBig)
        langTxt = get_lang("SettingUI")
        self.settingTitleTxt = self.bigFont.render(langTxt["setting"],True,(255, 255, 255))
        self.settingTitleTxt_x = int(self.baseImgX+(self.baseImgWidth-self.settingTitleTxt.get_width())/2)
        self.settingTitleTxt_y = self.baseImgY+self.baseImgHeight*0.05
        #语言
        self.languageTxt = self.normalFont.render(langTxt["language"]+": "+langTxt["currentLang"],True,(255, 255, 255))
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["sound_environment"]
        #确认
        self.confirmTxt_n = self.normalFont.render(langTxt["confirm"],True,(255, 255, 255))
        self.confirmTxt_b = self.bigFont.render(langTxt["confirm"],True,(255, 255, 255))
        #取消
        self.cancelTxt_n = self.normalFont.render(langTxt["cancel"],True,(255, 255, 255))
        self.cancelTxt_b = self.bigFont.render(langTxt["cancel"],True,(255, 255, 255))
        #确认和取消按钮的位置
        self.buttons_y = self.baseImgY + self.baseImgHeight*0.88
        self.buttons_x1 = self.baseImgX + self.baseImgWidth*0.2
        self.buttons_x2 = self.buttons_x1 + self.cancelTxt_n.get_width()*1.7
    def __update_sound(self):
        self.soundVolume_background_music = keepInRange(get_setting("Sound","background_music"),0,100)
        self.soundVolume_sound_effects = keepInRange(get_setting("Sound","sound_effects"),0,100)
        self.soundVolume_sound_environment = keepInRange(get_setting("Sound","sound_environment"),0,100)
    def draw(self, surface:pygame.Surface, pygame_events=pygame.event.get()) -> bool:
        if self.isDisplaying:
            #底部图
            surface.blit(self.baseImg,(self.baseImgX,self.baseImgY))
            surface.blit(self.settingTitleTxt,(self.settingTitleTxt_x,self.settingTitleTxt_y))
            #语言
            surface.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            surface.blit(self.normalFont.render(
                self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255, 255, 255)),
                (self.bar_x,self.bar_y1-self.FONTSIZE*1.4)
            )
            self.bar_img1.set_pos(self.bar_x,self.bar_y1)
            self.bar_img1.set_percentage(self.soundVolume_background_music/100)
            self.bar_img1.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img1.percentage*self.bar_img1.width-self.button.get_width()/2,
                self.bar_y1-self.bar_height/2
                )
            )
            #音效
            surface.blit(self.normalFont.render(
                self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),True,(255, 255, 255)),
                (self.bar_x,self.bar_y2-self.FONTSIZE*1.4)
            )
            self.bar_img2.set_pos(self.bar_x,self.bar_y2)
            self.bar_img2.set_percentage(self.soundVolume_sound_effects/100)
            self.bar_img2.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img2.percentage*self.bar_img2.width-self.button.get_width()/2,
                self.bar_y2-self.bar_height/2
                )
            )
            #环境声
            surface.blit(self.normalFont.render(
                self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),True,(255, 255, 255)),
                (self.bar_x,self.bar_y3-self.FONTSIZE*1.4)
            )
            self.bar_img3.set_pos(self.bar_x,self.bar_y3)
            self.bar_img3.set_percentage(self.soundVolume_sound_environment/100)
            self.bar_img3.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img3.percentage*self.bar_img3.width-self.button.get_width()/2,
                self.bar_y3-self.bar_height/2
                )
            )
            #获取鼠标坐标
            mouse_x,mouse_y=pygame.mouse.get_pos()
            #取消按钮
            if 0<mouse_x-self.buttons_x1<self.cancelTxt_n.get_width() and 0<mouse_y-self.buttons_y<self.cancelTxt_n.get_height():
                surface.blit(self.cancelTxt_b,(self.buttons_x1,self.buttons_y))
                if controller.get_event(pygame_events) == "comfirm":
                    self.__update_sound()
                    self.isDisplaying = False
            else:
                surface.blit(self.cancelTxt_n,(self.buttons_x1,self.buttons_y))
            #确认按钮
            if 0<mouse_x-self.buttons_x2<self.confirmTxt_n.get_width() and 0<mouse_y-self.buttons_y<self.confirmTxt_n.get_height():
                surface.blit(self.confirmTxt_b,(self.buttons_x2,self.buttons_y))
                if controller.get_event(pygame_events) == "comfirm":
                    set_setting("Sound","background_music",self.soundVolume_background_music)
                    set_setting("Sound","sound_effects",self.soundVolume_sound_effects)
                    set_setting("Sound","sound_environment",self.soundVolume_sound_environment)
                    save_setting()
                    pygame.mixer.music.set_volume(self.soundVolume_background_music/100.0)
                    self.isDisplaying = False
                    return True
            else:
                surface.blit(self.confirmTxt_n,(self.buttons_x2,self.buttons_y))
            #其他按键的判定按钮
            if pygame.mouse.get_pressed()[0] and 0<=mouse_x-self.bar_x<=self.bar_width:
                #如果碰到背景音乐的音量条
                if -self.bar_height/2<mouse_y-self.bar_y1<self.bar_height*1.5:
                    self.soundVolume_background_music = round(100*(mouse_x-self.bar_x)/self.bar_width)
                #如果碰到音效的音量条
                elif -self.bar_height/2<mouse_y-self.bar_y2<self.bar_height*1.5:
                    self.soundVolume_sound_effects = round(100*(mouse_x-self.bar_x)/self.bar_width)
                #如果碰到环境声的音量条
                elif -self.bar_height/2<mouse_y-self.bar_y3<self.bar_height*1.5:
                    self.soundVolume_sound_environment = round(100*(mouse_x-self.bar_x)/self.bar_width)
        return False

setting:SettingContoller = SettingContoller()