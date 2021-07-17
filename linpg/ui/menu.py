# cython: language_level=3
from .generator import *

#内部菜单模块的抽象
class AbstractInternalMenu:
    def __init__(self, menu_name:str) -> None:
        self._CONTENT = None
        self._initialized:bool = False
        self._menu_name:str = menu_name
        self.hidden:bool = True
    #初始化
    def initialize(self) -> None:
        self._CONTENT = UI.generate_deault(self._menu_name)
        self._initialized = True
    #菜单是否被触碰
    def is_hover(self) -> bool:
        if not self.hidden and self._CONTENT is not None:
            return self._CONTENT.is_hover()
        else:
            return False
    #画出内容
    def draw(self, surface:ImageSurface) -> None:
        self._CONTENT.draw(surface)

#暂停菜单
class PauseMenu(AbstractInternalMenu):
    def __init__(self) -> None:
        super().__init__("pause_menu")
        self.screenshot = None
    #被点击的按钮
    def get_button_clicked(self) -> str:
        if not self.hidden:
            if Controller.get_event("back"):
                return "resume"
            elif Controller.get_event("confirm") and self._CONTENT.item_being_hovered is not None:
                return self._CONTENT.item_being_hovered
        return ""
    def draw(self, surface:ImageSurface) -> None:
        if not self.hidden:
            if not self._initialized:
                self.initialize()
            #展示原先的背景
            if self.screenshot is None: self.screenshot = IMG.add_darkness(surface, 10)
            #画出原先的背景
            surface.blit(self.screenshot,(0,0))
            #画出UI
            super().draw(surface)

#设置UI
class DefaultOptionMenu(AbstractInternalMenu):
    def __init__(self) -> None:
        super().__init__("option_menu")
        self.need_update:dict = {}
    def draw(self, surface:ImageSurface) -> None:
        self.need_update = {
            "volume": False,
            "language": False
            }
        if not self.hidden:
            #检查是否初始化
            if not self._initialized:
                self.initialize()
                lang_drop_down = self._CONTENT.get("lang_drop_down")
                for lang_choice in Lang.get_available_languages():
                    lang_drop_down.set(lang_choice, lang_choice)
                    lang_drop_down.set_current_selected_item(Lang.current_language)
            else:
                lang_drop_down = self._CONTENT.get("lang_drop_down")
            #更新百分比
            self._CONTENT.get("global_sound_volume").set_percentage(Setting.get("Sound", "global_value")/100)
            self._CONTENT.get("background_music_sound_volume").set_percentage(Setting.get("Sound", "background_music")/100)
            self._CONTENT.get("effects_sound_volume").set_percentage(Setting.get("Sound", "effects")/100)
            self._CONTENT.get("environment_sound_volume").set_percentage(Setting.get("Sound", "environment")/100)
            #画出
            super().draw(surface)
            #如果需要更新语言
            if lang_drop_down.get_current_selected_item() != Lang.current_language:
                #更新语言并保存新的参数到本地
                Setting.set("Language", value=Lang.get_language_id(lang_drop_down.get_current_selected_item()))
                Setting.save()
                Lang.reload()
                self._initialized = False
                self.need_update["language"] = True
            #按键的判定按钮
            if self._CONTENT.item_being_hovered is not None and not lang_drop_down.is_hover():
                item_percentage_t: int = 0
                #如果碰到全局音量条
                if self._CONTENT.item_being_hovered == "global_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("global_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "global_value"):
                        Setting.set("Sound", "global_value", value=item_percentage_t)
                        self.need_update["volume"] = True
                elif self._CONTENT.item_being_hovered == "background_music_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("background_music_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "background_music"):
                        Setting.set("Sound", "background_music", value=item_percentage_t)
                        Music.set_volume(Media.volume.background_music/100.0)
                        self.need_update["volume"] = True
                #如果碰到音效的音量条
                elif self._CONTENT.item_being_hovered == "effects_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("effects_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "effects"):
                        Setting.set("Sound", "effects", value=item_percentage_t)
                        self.need_update["volume"] = True
                #如果碰到环境声的音量条
                elif self._CONTENT.item_being_hovered == "environment_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("environment_sound_volume").percentage*100)
                    if item_percentage_t != Setting.get("Sound", "environment"):
                        Setting.set("Sound", "environment", value=item_percentage_t)
                        self.need_update["volume"] = True
                #保存新的参数
                if self.need_update["volume"] is True: Setting.save()
                if Controller.mouse.get_pressed(0) and self._CONTENT.item_being_hovered == "back_button": self.hidden = True

#引擎本体的选项菜单
OptionMenu: DefaultOptionMenu = DefaultOptionMenu()
