# cython: language_level=3
from .generator import *

#暂停菜单
class PauseMenu:
    def __init__(self) -> None:
        self.__CONTENT = None
        self.__initialized:bool = False
        self.screenshot = None
        self.hidden:bool = True
    def initialize(self) -> None:
        self.__CONTENT = UI.generate_deault("pause_menu")
        self.__initialized = True
    def draw(self, surface:ImageSurface) -> None:
        if not self.hidden:
            if not self.__initialized:
                self.initialize()
            #展示原先的背景
            if self.screenshot is None: self.screenshot = IMG.add_darkness(surface, 10)
            #画出原先的背景
            surface.blit(self.screenshot,(0,0))
            #画出UI
            self.__CONTENT.draw(surface)
    #被点击的按钮
    def get_button_clicked(self) -> str:
        if not self.hidden:
            if Controller.get_event("back"):
                return "resume"
            elif Controller.get_event("confirm") and self.__CONTENT.item_being_hovered is not None:
                return self.__CONTENT.item_being_hovered
        return ""

#设置UI
class OptionMenuInterface:
    def __init__(self):
        self.__CONTENT = None
        self.__initialized:bool = False
        self.need_update:bool = {}
        self.hidden:bool = True
    def is_hover(self) -> bool: return self.__CONTENT.is_hover()
    def draw(self, surface:ImageSurface) -> None:
        self.need_update = {
            "volume": False,
            "language": False
            }
        if not self.hidden:
            #检查是否初始化
            if not self.__initialized:
                self.__CONTENT = UI.generate_deault("option_menu")
                lang_drop_down = self.__CONTENT.get("lang_drop_down")
                for lang_choice in Lang.get_available_languages():
                    lang_drop_down.set(lang_choice, lang_choice)
                    lang_drop_down.set_current_selected_item(Lang.get_current_language())
                self.__initialized = True
            else:
                lang_drop_down = self.__CONTENT.get("lang_drop_down")
            #更新百分比
            self.__CONTENT.get("global_sound_volume").set_percentage(Setting.get("Sound", "global_value")/100)
            self.__CONTENT.get("background_music_sound_volume").set_percentage(Setting.get("Sound", "background_music")/100)
            self.__CONTENT.get("effects_sound_volume").set_percentage(Setting.get("Sound", "effects")/100)
            self.__CONTENT.get("environment_sound_volume").set_percentage(Setting.get("Sound", "environment")/100)
            #画出
            self.__CONTENT.draw(surface)
            #如果需要更新语言
            if lang_drop_down.get_current_selected_item() != Lang.get_current_language():
                #更新语言并保存新的参数到本地
                Setting.set_and_save("Language", value=Lang.get_language_id(lang_drop_down.get_current_selected_item()))
                Lang.reload()
                self.__initialized = False
                self.need_update["language"] = True
            #按键的判定按钮
            if self.__CONTENT.item_being_hovered is not None and not lang_drop_down.is_hover():
                #如果碰到全局音量条
                if self.__CONTENT.item_being_hovered == "global_sound_volume":
                    item_percentage_t = int(self.__CONTENT.get("global_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "global_value"):
                        Setting.set("Sound", "global_value", item_percentage_t)
                        self.need_update["volume"] = True
                elif self.__CONTENT.item_being_hovered == "background_music_sound_volume":
                    item_percentage_t = int(self.__CONTENT.get("background_music_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "background_music"):
                        Setting.set("Sound", "background_music", item_percentage_t)
                        Music.set_volume(Media.volume.background_music/100.0)
                        self.need_update["volume"] = True
                #如果碰到音效的音量条
                elif self.__CONTENT.item_being_hovered == "effects_sound_volume":
                    item_percentage_t = int(self.__CONTENT.get("effects_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "effects"):
                        Setting.set("Sound", "effects", item_percentage_t)
                        self.need_update["volume"] = True
                #如果碰到环境声的音量条
                elif self.__CONTENT.item_being_hovered == "environment_sound_volume":
                    item_percentage_t = int(self.__CONTENT.get("environment_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "environment"):
                        Setting.set("Sound", "environment", item_percentage_t)
                        self.need_update["volume"] = True
                #保存新的参数
                if self.need_update["volume"] is True: Setting.save()
                if Controller.mouse.get_pressed(0) and self.__CONTENT.item_being_hovered == "back_button": self.hidden = True

#引擎本体的选项菜单
OptionMenu:OptionMenuInterface = OptionMenuInterface()
