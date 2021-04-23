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
            get_lang("Global","resume"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.4,surface.get_width()/38)
        )
        #按钮-保存游戏
        self.button_save = fontRenderPro(
            get_lang("Global","save_current_progress"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.5,surface.get_width()/38)
        )
        #按钮-设置
        self.button_setting = fontRenderPro(
            get_lang("OptionMenu","option_menu"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.6,surface.get_width()/38)
        )
        #按钮-返回
        self.button_back = fontRenderPro(
            get_lang("Global","back"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.7,surface.get_width()/38)
        )
    def draw(self, surface:pygame.Surface, pygame_events=pygame.event.get()) -> str:
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
        return ""

#设置UI
class OptionMenu(AbstractImage):
    def __init__(self, x:int, y:int,width:int, height:int):
        self.__ui_image_folder_path:str = "Assets/image/UI"
        #加载设置菜单的背景图片
        baseImgPath:str = os.path.join(self.__ui_image_folder_path,"setting_baseImg.png")
        if os.path.exists(baseImgPath):
            baseImg = loadImg(baseImgPath,(width,height))
        else:
            baseImg = getSurface((width,height)).convert()
            baseImg.fill((255,255,255))
            pygame.draw.rect(
                baseImg, findColorRGBA("gray"),
                pygame.Rect(width*0.05,height*0.05,width*0.9,height*0.9)
                )
        super().__init__(baseImg,x,y,width,height)
        #默认隐藏
        self.hidden = True
        #物品尺寸
        self.__item_height:int = int(self.height*0.05)
        #划动条的宽度
        self.bar_width:int = int(self.width*0.6)
        self.button = loadImg(os.path.join(self.__ui_image_folder_path,"setting_bar_circle.png"),(self.__item_height,self.__item_height*2))
        self.bar_img1 = DynamicProgressBarSurface(
            os.path.join(self.__ui_image_folder_path,"setting_bar_full.png"),
            os.path.join(self.__ui_image_folder_path,"setting_bar_empty.png"),
            0,0,self.bar_width,self.__item_height)
        self.bar_img2 = self.bar_img1.light_copy()
        self.bar_img3 = self.bar_img2.light_copy()
        self.bar_x = int(self.x+(width-self.bar_width)/2)
        self.bar_y0 = self.y + self.__item_height*4
        self.bar_y1 = self.y + self.__item_height*7.5
        self.bar_y2 = self.y + self.__item_height*11
        self.bar_y3 = self.y + self.__item_height*14.5
        #音量数值
        self.soundVolume_background_music = 0
        self.soundVolume_sound_effects = 0
        self.soundVolume_sound_environment = 0
        self.__update_sound()
        #设置UI中的文字
        langTxt = get_lang("OptionMenu")
        self.__NORMAL_FONT = createFont(self.__item_height)
        self.settingTitleTxt = TextSurface(fontRender(langTxt["setting"],"white",self.__item_height*1.5),0,height*0.1)
        self.settingTitleTxt.set_centerx(width/2)
        #语言
        self.languageTxt = fontRender(langTxt["language"]+": "+langTxt["currentLang"],"white",self.__item_height)
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["sound_environment"]
        button_y:int = int(height*0.9-self.__item_height*1.5)
        #确认
        self.__confirm_button = fontRenderPro(langTxt["confirm"],"white",(0,button_y),self.__item_height)
        #取消
        self.__cancel_button = fontRenderPro(langTxt["cancel"],"white",(0,button_y),self.__item_height)
        #按钮位置
        panding:int = int((width-self.__confirm_button.get_width()-self.__cancel_button.get_width())/3)
        self.__confirm_button.set_left(panding)
        self.__cancel_button.set_left(self.__confirm_button.right+panding)
        self.need_update:bool = False
    #更新音乐
    def __update_sound(self):
        self.soundVolume_background_music = keepInRange(get_setting("Sound","background_music"),0,100)
        self.soundVolume_sound_effects = keepInRange(get_setting("Sound","sound_effects"),0,100)
        self.soundVolume_sound_environment = keepInRange(get_setting("Sound","sound_environment"),0,100)
    def draw(self, surface:pygame.Surface) -> None:
        if not self.hidden:
            #底部图
            surface.blit(self.img,(self.x,self.y))
            self.settingTitleTxt.display(surface,self.pos)
            #语言
            surface.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            surface.blit(self.__NORMAL_FONT.render(
                self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255,255,255)),
                (self.bar_x,self.bar_y1-self.__item_height*1.5)
            )
            self.bar_img1.set_pos(self.bar_x,self.bar_y1)
            self.bar_img1.set_percentage(self.soundVolume_background_music/100)
            self.bar_img1.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img1.percentage*self.bar_img1.width-self.button.get_width()/2,
                self.bar_y1-self.__item_height/2
                )
            )
            #音效
            surface.blit(self.__NORMAL_FONT.render(
                self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),True,(255, 255, 255)),
                (self.bar_x,self.bar_y2-self.__item_height*1.5)
            )
            self.bar_img2.set_pos(self.bar_x,self.bar_y2)
            self.bar_img2.set_percentage(self.soundVolume_sound_effects/100)
            self.bar_img2.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img2.percentage*self.bar_img2.width-self.button.get_width()/2,
                self.bar_y2-self.__item_height/2
                )
            )
            #环境声
            surface.blit(self.__NORMAL_FONT.render(
                self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),True,(255, 255, 255)),
                (self.bar_x,self.bar_y3-self.__item_height*1.5)
            )
            self.bar_img3.set_pos(self.bar_x,self.bar_y3)
            self.bar_img3.set_percentage(self.soundVolume_sound_environment/100)
            self.bar_img3.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img3.percentage*self.bar_img3.width-self.button.get_width()/2,
                self.bar_y3-self.__item_height/2
                )
            )
            #取消按钮
            self.__confirm_button.display(surface,self.pos)
            self.__cancel_button.display(surface,self.pos)
            #按键的判定按钮
            if pygame.mouse.get_pressed()[0]:
                #获取鼠标坐标
                mouse_x,mouse_y=pygame.mouse.get_pos()
                #判定划动条
                if 0 <= mouse_x-self.bar_x <= self.bar_width:
                    #如果碰到背景音乐的音量条
                    if -self.__item_height/2<mouse_y-self.bar_y1<self.__item_height*1.5:
                        self.soundVolume_background_music = round(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到音效的音量条
                    elif -self.__item_height/2<mouse_y-self.bar_y2<self.__item_height*1.5:
                        self.soundVolume_sound_effects = round(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到环境声的音量条
                    elif -self.__item_height/2<mouse_y-self.bar_y3<self.__item_height*1.5:
                        self.soundVolume_sound_environment = round(100*(mouse_x-self.bar_x)/self.bar_width)
                if self.__cancel_button.is_hover((mouse_x-self.x,mouse_y-self.y)):
                    self.__update_sound()
                    self.hidden = True
                elif self.__confirm_button.is_hover((mouse_x-self.x,mouse_y-self.y)):
                    set_setting("Sound","background_music",self.soundVolume_background_music)
                    set_setting("Sound","sound_effects",self.soundVolume_sound_effects)
                    set_setting("Sound","sound_environment",self.soundVolume_sound_environment)
                    save_setting()
                    pygame.mixer.music.set_volume(self.soundVolume_background_music/100.0)
                    self.hidden = True
                    self.need_update = True

#引擎本体的选项菜单
option_menu:object = None

#初始化引擎本体的选项菜单
def init_option_menu(x:int, y:int, width:int, height:int) -> None:
    global option_menu
    option_menu = OptionMenu(x,y,width,height)

#获取引擎本体的选项菜单的初始化信息
def get_option_menu_init() -> bool:
    global option_menu
    return option_menu is not None

def get_option_menu(): return option_menu
