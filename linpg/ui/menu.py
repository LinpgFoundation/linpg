from .generator import *

# 内部菜单模块的抽象
class AbstractInternalMenu(HiddenableSurface):
    def __init__(self, menu_name: str) -> None:
        super().__init__(False)
        self._CONTENT: GameObjectsDictContainer = NULL_DICT_CONTAINER
        self._initialized: bool = False
        self._menu_name: str = menu_name

    # 初始化
    def initialize(self) -> None:
        self._CONTENT = UI.generate_container(self._menu_name)
        self._initialized = True

    # 菜单是否被触碰
    def is_hovered(self) -> bool:
        if self.is_visible() and self._CONTENT is not NULL_DICT_CONTAINER:
            return self._CONTENT.is_hovered()
        else:
            return False

    # 画出内容
    def draw(self, surface: ImageSurface) -> None:
        self._CONTENT.draw(surface)


# 设置UI
class DefaultOptionMenu(AbstractInternalMenu):
    def __init__(self) -> None:
        super().__init__("option_menu")
        self.need_update: dict = {}

    # 展示
    def draw(self, surface: ImageSurface) -> None:
        self.need_update = {"volume": False, "language": False}
        if self.is_visible():
            # 检查是否初始化
            if not self._initialized:
                self.initialize()
                lang_drop_down = self._CONTENT.get("lang_drop_down")
                for lang_choice in Lang.get_available_languages():
                    lang_drop_down.set(lang_choice, lang_choice)
                lang_drop_down.set_selected_item(Lang.current_language)
            else:
                lang_drop_down = self._CONTENT.get("lang_drop_down")
            # 更新百分比
            self._CONTENT.get("global_sound_volume").set_percentage(Setting.get("Sound", "global_value") / 100)
            self._CONTENT.get("background_music_sound_volume").set_percentage(Setting.get("Sound", "background_music") / 100)
            self._CONTENT.get("effects_sound_volume").set_percentage(Setting.get("Sound", "effects") / 100)
            self._CONTENT.get("environment_sound_volume").set_percentage(Setting.get("Sound", "environment") / 100)
            # 画出
            super().draw(surface)
            # 如果需要更新语言
            if lang_drop_down.get_selected_item() != Lang.current_language and lang_drop_down.get_selected_item() != "":
                # 更新语言并保存新的参数到本地
                Setting.set(
                    "Language",
                    value=Lang.get_language_id(lang_drop_down.get_selected_item()),
                )
                Setting.save()
                Lang.reload()
                self._initialized = False
                self.need_update["language"] = True
            # 按键的判定按钮
            if self._CONTENT.item_being_hovered is not None and not lang_drop_down.is_hovered():
                item_percentage_t: int = 0
                # 如果碰到全局音量条
                if self._CONTENT.item_being_hovered == "global_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("global_sound_volume").percentage * 100)
                    if item_percentage_t != int(Setting.get("Sound", "global_value")):
                        Setting.set("Sound", "global_value", value=item_percentage_t)
                        self.need_update["volume"] = True
                elif self._CONTENT.item_being_hovered == "background_music_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("background_music_sound_volume").percentage * 100)
                    if item_percentage_t != int(Setting.get("Sound", "background_music")):
                        Setting.set("Sound", "background_music", value=item_percentage_t)
                        Music.set_volume(Media.volume.background_music / 100.0)
                        self.need_update["volume"] = True
                # 如果碰到音效的音量条
                elif self._CONTENT.item_being_hovered == "effects_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("effects_sound_volume").percentage * 100)
                    if item_percentage_t != int(Setting.get("Sound", "effects")):
                        Setting.set("Sound", "effects", value=item_percentage_t)
                        self.need_update["volume"] = True
                # 如果碰到环境声的音量条
                elif self._CONTENT.item_being_hovered == "environment_sound_volume":
                    item_percentage_t = int(self._CONTENT.get("environment_sound_volume").percentage * 100)
                    if item_percentage_t != int(Setting.get("Sound", "environment")):
                        Setting.set("Sound", "environment", value=item_percentage_t)
                        self.need_update["volume"] = True
                # 保存新的参数
                if self.need_update["volume"] is True:
                    Setting.save()
                if Controller.mouse.get_pressed(0) and self._CONTENT.item_being_hovered == "back_button":
                    self.set_visible(False)


# 引擎本体的选项菜单
OptionMenu: DefaultOptionMenu = DefaultOptionMenu()

# 暂停菜单
class PauseMenu(AbstractInternalMenu):
    def __init__(self) -> None:
        super().__init__("pause_menu")
        self.__screenshot: Optional[ImageSurface] = None
        # 返回确认菜单
        self.__leave_warning: GameObjectsDictContainer = NULL_DICT_CONTAINER
        # 退出确认菜单
        self.__exit_warning: GameObjectsDictContainer = NULL_DICT_CONTAINER
        # 记录被按下的按钮
        self.__button_hovered: str = ""

    # 被点击的按钮
    def get_button_clicked(self) -> str:
        return self.__button_hovered

    def initialize(self) -> None:
        super().initialize()
        # 加载返回确认菜单
        self.__leave_warning = UI.generate_container("leave_without_saving_progress_warning")
        self.__leave_warning.set_visible(False)
        # 加载退出确认菜单
        self.__exit_warning = UI.generate_container("exit_without_saving_progress_warning")
        self.__exit_warning.set_visible(False)

    def hide(self) -> None:
        self.set_visible(False)
        self.__exit_warning.set_visible(False)
        self.__leave_warning.set_visible(False)
        self.__screenshot = None

    def draw(self, surface: ImageSurface) -> None:
        self.__button_hovered = ""
        if self.is_visible():
            if not self._initialized:
                self.initialize()
            # 展示原先的背景
            if self.__screenshot is None:
                self.__screenshot = IMG.add_darkness(surface, 10)
            # 画出原先的背景
            surface.blit(self.__screenshot, (0, 0))
            # 画出选项
            if self.__leave_warning.is_hidden() and self.__exit_warning.is_hidden():
                super().draw(surface)
            # 画出退出确认
            self.__leave_warning.draw(surface)
            self.__exit_warning.draw(surface)
            # 处理事件
            if Controller.get_event("back"):
                if self.__leave_warning.is_visible():
                    self.__leave_warning.set_visible(False)
                elif self.__exit_warning.is_visible():
                    self.__exit_warning.set_visible(False)
                else:
                    self.__button_hovered = "resume"
            elif Controller.get_event("confirm"):
                if self.__leave_warning.is_visible():
                    if self.__leave_warning.item_being_hovered == "confirm":
                        self.__button_hovered = "back_to_mainMenu"
                    elif self.__leave_warning.item_being_hovered == "cancel":
                        self.__leave_warning.set_visible(False)
                elif self.__exit_warning.is_visible():
                    if self.__exit_warning.item_being_hovered == "confirm":
                        Display.quit()
                    elif self.__exit_warning.item_being_hovered == "cancel":
                        self.__exit_warning.set_visible(False)
                elif self._CONTENT.item_being_hovered is not None:
                    if self._CONTENT.item_being_hovered == "back_to_mainMenu":
                        self.__leave_warning.set_visible(True)
                    elif self._CONTENT.item_being_hovered == "exit_to_desktop":
                        self.__exit_warning.set_visible(True)
                    else:
                        self.__button_hovered = self._CONTENT.item_being_hovered


# 暂停菜单处理模块
class PauseMenuModuleForGameSystem(AbstractInternalMenu):
    def __init__(self) -> None:
        # 暂停菜单
        self.__pause_menu: Optional[PauseMenu] = None

    # 保存进度（子类需实现）
    def save_progress(self) -> None:
        EXCEPTION.fatal("_get_data_need_to_save()", 1)

    # 淡入或淡出（子类需实现）
    def fade(self, surface: ImageSurface) -> None:
        EXCEPTION.fatal("fade()", 1)

    # 停止播放（子类需实现）
    def stop(self) -> None:
        EXCEPTION.fatal("stop()", 1)

    # 更新音量（子类需实现）
    def _update_sound_volume(self) -> None:
        EXCEPTION.fatal("_update_sound_volume()", 1)

    # 更新语言（子类需实现）
    def update_language(self) -> None:
        EXCEPTION.fatal("update_language()", 1)

    def _enable_pause_menu(self) -> None:
        self.__pause_menu = PauseMenu()

    def is_pause_menu_enabled(self) -> bool:
        return self.__pause_menu is not None

    def _initialize_pause_menu(self) -> None:
        if self.__pause_menu is not None:
            self.__pause_menu.initialize()

    def _show_pause_menu(self, surface: ImageSurface) -> None:
        if self.__pause_menu is not None:
            Media.pause()
            progress_saved_text = StaticImage(
                Font.render(Lang.get_text("Global", "progress_has_been_saved"), Colors.WHITE, int(Display.get_width() * 0.015)),
                0,
                0,
            )
            progress_saved_text.set_alpha(0)
            progress_saved_text.set_center(surface.get_width() / 2, surface.get_height() / 2)
            self.__pause_menu.set_visible(True)
            while self.__pause_menu.is_visible():
                Display.flip()
                if OptionMenu.is_hidden():
                    self.__pause_menu.draw(surface)
                    if self.__pause_menu.get_button_clicked() == "resume":
                        OptionMenu.set_visible(False)
                        self.__pause_menu.set_visible(False)
                    elif self.__pause_menu.get_button_clicked() == "save":
                        self.save_progress()
                        progress_saved_text.set_alpha(255)
                    elif self.__pause_menu.get_button_clicked() == "option_menu":
                        OptionMenu.set_visible(True)
                    elif self.__pause_menu.get_button_clicked() == "back_to_mainMenu":
                        try:
                            self.fade(surface)
                        except Exception:
                            Media.unload()
                        OptionMenu.set_visible(False)
                        progress_saved_text.set_alpha(0)
                        self.__pause_menu.set_visible(False)
                        GlobalValue.set("BackToMainMenu", True)
                        self.stop()
                else:
                    # 展示设置UI
                    OptionMenu.draw(surface)
                    # 更新音量
                    if OptionMenu.need_update["volume"] is True:
                        self._update_sound_volume()
                    # 更新语言
                    if OptionMenu.need_update["language"] is True:
                        self.update_language()
                # 显示进度已保存的文字
                progress_saved_text.draw(surface)
                progress_saved_text.subtract_alpha(5)
            del progress_saved_text
            self.__pause_menu.hide()
            Media.unpause()
