# cython: language_level=3
from .container import *

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
            if controller.get_event("back"):
                return "break"
            elif controller.get_event("confirm"):
                #判定按钮
                if self.button_resume.is_hover():
                    return "break"
                elif self.button_save.is_hover():
                    return "save"
                elif self.button_setting.is_hover():
                    return "option_menu"
                elif self.button_back.is_hover():
                    global_value.set("BackToMainMenu",True)
                    return "back_to_mainMenu"
        return ""

#设置UI
class OptionMenu(AbstractImage):
    def __init__(self, x:int, y:int, width:int, height:int, tag:str=""):
        self.__ui_image_folder_path:str = "Assets/image/UI"
        #加载设置菜单的背景图片
        baseImgPath:str = os.path.join(self.__ui_image_folder_path,"setting_baseImg.png")
        if os.path.exists(baseImgPath):
            baseImg = smoothly_resize_img(load_img(baseImgPath), (width,height))
        else:
            baseImg = new_surface((width,height)).convert()
            baseImg.fill((255,255,255))
            draw_rect(baseImg, Color.GRAY, Rect(width*0.05, height*0.05, width*0.9, height*0.9))
        super().__init__(baseImg, x, y, width, height, tag)
        #默认隐藏
        self.hidden = True
        #物品尺寸
        self.__item_height:int = int(self.height*0.05)
        #划动条的宽度
        self.bar_width:int = int(self.width*0.6)
        self.button = load_img(os.path.join(self.__ui_image_folder_path,"setting_bar_circle.png"),(self.__item_height,self.__item_height*2))
        self.bar_img1 = DynamicProgressBarSurface(
            os.path.join(self.__ui_image_folder_path,"setting_bar_full.png"),
            os.path.join(self.__ui_image_folder_path,"setting_bar_empty.png"),
            0,0,self.bar_width,self.__item_height)
        self.bar_img2 = self.bar_img1.light_copy()
        self.bar_img3 = self.bar_img2.light_copy()
        self.bar_x = int(self.x+(width-self.bar_width)/2)
        edge_panding = height*0.05
        self.bar_y0 = self.y + self.__item_height*4
        self.bar_y1 = self.y + self.__item_height*8
        self.bar_y2 = self.y + self.__item_height*12
        self.bar_y3 = self.y + self.__item_height*16
        #音量数值
        self.soundVolume_background_music = keep_in_range(Setting.get("Sound","background_music"),0,100)
        self.soundVolume_sound_effects = keep_in_range(Setting.get("Sound","sound_effects"),0,100)
        self.soundVolume_sound_environment = keep_in_range(Setting.get("Sound","sound_environment"),0,100)
        #字体渲染器
        self.__NORMAL_FONT = create_font(self.__item_height)
        #设置UI中的文字
        langTxt = Lang.get_text("OptionMenu")
        self.settingTitleTxt = TextSurface(render_font(langTxt["setting"],"white",self.__item_height*1.5),0,edge_panding)
        self.settingTitleTxt.set_centerx(width/2)
        #语言
        self.current_lang = TextSurface(render_font("{}: ".format(langTxt["language"]), "white", self.__item_height),self.bar_x, self.bar_y0)
        self.language_choice = DropDownSingleChoiceList(None, self.bar_x, self.bar_y0, self.__item_height)
        for lang_choice in Lang.get_available_languages():
            self.language_choice.append(lang_choice)
        self.language_choice.set_current_selected_item(Lang.get_current_language())
        #背景音乐
        self.backgroundMusicTxt:str = langTxt["background_music"]
        #音效
        self.soundEffectsTxt:str = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt:str = langTxt["sound_environment"]
        #返回
        self.__back_button = load_dynamic_text(Lang.get_text("Global","back"),"white",(0,0),self.__item_height)
        self.__back_button.set_bottom(height-edge_panding)
        self.__back_button.set_centerx(self.width/2)
        self.need_update:dict = {}
    #更新语言
    def __update_lang(self, lang:str) -> None:
        #更新语言并保存新的参数到本地
        Setting.set_and_save("Language", value=Lang.get_language_id(lang))
        Lang.reload()
        #设置UI中的文字
        langTxt = Lang.get_text("OptionMenu")
        self.settingTitleTxt.font_surface = render_font(langTxt["setting"],"white",self.__item_height*1.5)
        #语言
        self.current_lang = TextSurface(render_font("{}: ".format(langTxt["language"]), "white", self.__item_height),self.bar_x, self.bar_y0)
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["sound_environment"]
        #返回
        self.__back_button = load_dynamic_text(Lang.get_text("Global","back"), "white", self.__back_button.pos, self.__item_height)
    def draw(self, surface:ImageSurface) -> None:
        self.need_update = {
            "volume": False,
            "language": False
            }
        if not self.hidden:
            #底部图
            surface.blit(self.img,(self.x,self.y))
            self.settingTitleTxt.display(surface,self.pos)
            #背景音乐
            surface.blit(self.__NORMAL_FONT.render(
                self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255,255,255)),
                (self.bar_x,self.bar_y1-self.__item_height*1.6)
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
                (self.bar_x,self.bar_y2-self.__item_height*1.6)
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
                (self.bar_x,self.bar_y3-self.__item_height*1.6)
            )
            self.bar_img3.set_pos(self.bar_x,self.bar_y3)
            self.bar_img3.set_percentage(self.soundVolume_sound_environment/100)
            self.bar_img3.draw(surface)
            surface.blit(self.button,(
                self.bar_x+self.bar_img3.percentage*self.bar_img3.width-self.button.get_width()/2,
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
            if controller.mouse_get_press(0):
                #获取鼠标坐标
                mouse_x,mouse_y=controller.get_mouse_pos()
                #判定划动条
                if 0 <= mouse_x-self.bar_x <= self.bar_width and not self.language_choice.is_hover():
                    #如果碰到背景音乐的音量条
                    if -self.__item_height/2<mouse_y-self.bar_y1<self.__item_height*1.5:
                        self.soundVolume_background_music = round(100*(mouse_x-self.bar_x)/self.bar_width)
                        Setting.set("Sound","background_music",self.soundVolume_background_music)
                        set_music_volume(self.soundVolume_background_music/100.0)
                        self.need_update["volume"] = True
                    #如果碰到音效的音量条
                    elif -self.__item_height/2<mouse_y-self.bar_y2<self.__item_height*1.5:
                        self.soundVolume_sound_effects = round(100*(mouse_x-self.bar_x)/self.bar_width)
                        Setting.set("Sound","sound_effects",self.soundVolume_sound_effects)
                        self.need_update["volume"] = True
                    #如果碰到环境声的音量条
                    elif -self.__item_height/2<mouse_y-self.bar_y3<self.__item_height*1.5:
                        self.soundVolume_sound_environment = round(100*(mouse_x-self.bar_x)/self.bar_width)
                        Setting.set("Sound","sound_environment",self.soundVolume_sound_environment)
                        self.need_update["volume"] = True
                    #保存新的参数
                    if self.need_update["volume"] is True: Setting.save()
                    #判定返回按钮 
                    if self.__back_button.has_been_hovered():
                        self.hidden = True

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
