# cython: language_level=3
from .progressbar import *

#暂停菜单
class PauseMenu:
    def __init__(self) -> None:
        self.black_bg = None
        self.button_resume = None
        self.button_save = None
        self.button_setting = None
        self.button_back = None
        self.screenshot = None
        self.hidden:bool = True
    def initialize(self, surface:ImageSurface) -> None:
        surfaceTmp = new_surface(Display.get_size()).convert()
        surfaceTmp.fill(Color.BLACK)
        self.black_bg = StaticImage(surfaceTmp, 0, 0)
        self.black_bg.set_alpha(50)
        #按钮-继续
        self.button_resume = load_dynamic_text(
            Lang.get_text("Global","resume"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.4),surface.get_width()/38
        )
        #按钮-保存游戏
        self.button_save = load_dynamic_text(
            Lang.get_text("Global","save_current_progress"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.5),surface.get_width()/38
        )
        #按钮-设置
        self.button_setting = load_dynamic_text(
            Lang.get_text("OptionMenu","option_menu"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.6),surface.get_width()/38
        )
        #按钮-返回
        self.button_back = load_dynamic_text(
            Lang.get_text("Global","back"),
            "white",
            (surface.get_width()*0.1,surface.get_height()*0.7),surface.get_width()/38
        )
    def draw(self, surface:ImageSurface) -> None:
        if not self.hidden:
            #展示原先的背景
            if self.screenshot is None: self.screenshot = surface.copy()
            #画出原先的背景
            surface.blit(self.screenshot,(0,0))
            #如果背景层还没有初始化
            if self.black_bg is None: self.initialize(surface)
            #展示暂停菜单的背景层
            self.black_bg.draw(surface)
            #展示按钮
            self.button_resume.draw(surface)
            self.button_save.draw(surface)
            self.button_setting.draw(surface)
            self.button_back.draw(surface)
    #被点击的按钮
    @property
    def button_clicked(self) -> str: return self.get_button_clicked()
    def get_button_clicked(self) -> str:
        if not self.hidden:
            #判定按键
            if Controller.get_event("back"):
                return "break"
            elif Controller.get_event("confirm"):
                #判定按钮
                if self.button_resume.is_hover():
                    return "break"
                elif self.button_save.is_hover():
                    return "save"
                elif self.button_setting.is_hover():
                    return "option_menu"
                elif self.button_back.is_hover():
                    GlobalValue.set("BackToMainMenu",True)
                    return "back_to_mainMenu"
        return ""

#设置UI
class OptionMenuInterface(AbstractImage):
    def __init__(self):
        width = int(Display.get_width()*0.5)
        height = int(Display.get_height()*0.75)
        x = int((Display.get_width()-width)/2)
        y = int((Display.get_height()-height)/2)
        self.__ui_image_folder_path:str = "Assets/image/UI"
        super().__init__(None, x, y, width, height, "")
        #默认隐藏
        self.hidden = True
        #物品尺寸
        self.__item_height:int = int(self.height*0.05)
        #划动条的宽度
        self.bar_width:int = int(self.width*0.6)
        self.button = None
        self.__bar_input = None
        self.bar_x = int(self.x+(width-self.bar_width)/2)
        edge_panding = height*0.05
        self.bar_y0 = self.y + self.__item_height*4
        self.bar_y1 = self.y + self.__item_height*8
        self.bar_y2 = self.y + self.__item_height*12
        self.bar_y3 = self.y + self.__item_height*16
        #字体渲染器
        self.__NORMAL_FONT = Font.create(self.__item_height)
        self.settingTitleTxt = None
        #语言
        self.current_lang = None
        self.language_choice = None
        #设置UI中的文字
        langTxt = Lang.get_text("OptionMenu")
        #背景音乐
        self.backgroundMusicTxt:str = langTxt["background_music"]
        #音效
        self.soundEffectsTxt:str = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt:str = langTxt["environmental_sound"]
        #返回
        self.__back_button = None
        self.need_update:dict = {}
    def __init(self) -> None:
        if self.__bar_input is None:
            #加载设置菜单的背景图片
            baseImgPath:str = os.path.join(self.__ui_image_folder_path,"setting_baseImg.png")
            if os.path.exists(baseImgPath):
                baseImg = smoothly_resize_img(load_img(baseImgPath), self.size)
            else:
                baseImg = new_surface(self.size).convert()
                baseImg.fill(Color.WHITE)
                draw_rect(baseImg, Color.GRAY, Rect(self.width*0.05, self.height*0.05, self.width*0.9, self.height*0.9))
            self.img = baseImg
            self.button = load_img(os.path.join(self.__ui_image_folder_path,"setting_bar_circle.png"),(self.__item_height,self.__item_height*2))
            self.__bar_input = DynamicProgressBarSurface(
                os.path.join(self.__ui_image_folder_path,"setting_bar_full.png"),
                os.path.join(self.__ui_image_folder_path,"setting_bar_empty.png"),
                0, 0, self.bar_width, self.__item_height
                )
            self.settingTitleTxt = TextSurface(Font.render(Lang.get_text("OptionMenu","setting"),"white",self.__item_height*1.5),0,self.height*0.05)
            self.settingTitleTxt.set_centerx(self.width/2)
            self.current_lang = TextSurface(Font.render("{}: ".format(Lang.get_text("OptionMenu","language")), "white", self.__item_height),self.bar_x, self.bar_y0)
            self.language_choice = DropDownSingleChoiceList(None, self.bar_x, self.bar_y0, self.__item_height)
            for lang_choice in Lang.get_available_languages():
                self.language_choice.append(lang_choice)
            self.language_choice.set_current_selected_item(Lang.get_current_language())
            self.__back_button = load_dynamic_text(Lang.get_text("Global","back"),"white",(0,0),self.__item_height)
            self.__back_button.set_bottom(self.height-self.height*0.05)
            self.__back_button.set_centerx(self.width/2)
    #更新语言
    def __update_lang(self, lang:str) -> None:
        #更新语言并保存新的参数到本地
        Setting.set_and_save("Language", value=Lang.get_language_id(lang))
        Lang.reload()
        #设置UI中的文字
        langTxt = Lang.get_text("OptionMenu")
        self.settingTitleTxt.font_surface = Font.render(langTxt["setting"],"white",self.__item_height*1.5)
        #语言
        self.current_lang = TextSurface(Font.render("{}: ".format(langTxt["language"]), "white", self.__item_height),self.bar_x, self.bar_y0)
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["environmental_sound"]
        #返回
        self.__back_button = load_dynamic_text(Lang.get_text("Global","back"), "white", self.__back_button.pos, self.__item_height)
    def draw(self, surface:ImageSurface) -> None:
        self.need_update = {
            "volume": False,
            "language": False
            }
        if not self.hidden:
            self.__init()
            #底部图
            surface.blit(self.img,(self.x,self.y))
            self.settingTitleTxt.display(surface,self.pos)
            #背景音乐
            surface.blit(
                self.__NORMAL_FONT.render(self.backgroundMusicTxt+": "+str(Media.volume.background_music), Color.WHITE),
                (self.bar_x,self.bar_y1-self.__item_height*1.6)
            )
            self.__bar_input.set_pos(self.bar_x,self.bar_y1)
            self.__bar_input.set_percentage(Media.volume.background_music/100)
            self.__bar_input.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.__bar_input.percentage*self.__bar_input.width-self.button.get_width()/2,
                self.bar_y1-self.__item_height/2
                )
            )
            #音效
            surface.blit(
                self.__NORMAL_FONT.render(self.soundEffectsTxt+": "+str(Media.volume.effects), Color.WHITE),
                (self.bar_x,self.bar_y2-self.__item_height*1.6)
            )
            self.__bar_input.set_pos(self.bar_x,self.bar_y2)
            self.__bar_input.set_percentage(Media.volume.effects/100)
            self.__bar_input.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.__bar_input.percentage*self.__bar_input.width-self.button.get_width()/2,
                self.bar_y2-self.__item_height/2
                )
            )
            #环境声
            surface.blit(
                self.__NORMAL_FONT.render(self.soundEnvironmentTxt+": "+str(Media.volume.environment), Color.WHITE),
                (self.bar_x,self.bar_y3-self.__item_height*1.6)
            )
            self.__bar_input.set_pos(self.bar_x,self.bar_y3)
            self.__bar_input.set_percentage(Media.volume.environment/100)
            self.__bar_input.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.__bar_input.percentage*self.__bar_input.width-self.button.get_width()/2,
                self.bar_y3-self.__item_height/2
                )
            )
            #返回按钮
            self.__back_button.display(surface, self.pos)
            #语言
            self.current_lang.draw(surface)
            self.language_choice.display(surface, (self.current_lang.get_width(),0))
            #如果需要，则更新语言
            if self.language_choice.get_current_selected_item() != Lang.get_current_language():
                self.__update_lang(self.language_choice.get_current_selected_item())
                self.need_update["language"] = True
            #按键的判定按钮
            if Controller.mouse.get_pressed(0) and 0 <= Controller.mouse.x-self.bar_x <= self.bar_width and not self.language_choice.is_hover():
                    #如果碰到背景音乐的音量条
                    if -self.__item_height/2<Controller.mouse.y-self.bar_y1<self.__item_height*1.5:
                        Setting.set("Sound", "background_music", round(100*(Controller.mouse.x-self.bar_x)/self.bar_width))
                        Music.set_volume(Media.volume.background_music/100.0)
                        self.need_update["volume"] = True
                    #如果碰到音效的音量条
                    elif -self.__item_height/2<Controller.mouse.y-self.bar_y2<self.__item_height*1.5:
                        Setting.set("Sound", "effects", round(100*(Controller.mouse.x-self.bar_x)/self.bar_width))
                        self.need_update["volume"] = True
                    #如果碰到环境声的音量条
                    elif -self.__item_height/2<Controller.mouse.y-self.bar_y3<self.__item_height*1.5:
                        Setting.set("Sound", "environment", round(100*(Controller.mouse.x-self.bar_x)/self.bar_width))
                        self.need_update["volume"] = True
                    #保存新的参数
                    if self.need_update["volume"] is True: Setting.save()
                    #判定返回按钮 
                    if self.__back_button.has_been_hovered():
                        self.hidden = True

#引擎本体的选项菜单
OptionMenu:OptionMenuInterface = OptionMenuInterface()
