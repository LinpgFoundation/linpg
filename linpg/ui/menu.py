from .generator import *


# 内部菜单模块的抽象
class AbstractInternalMenu(Hidable, metaclass=ABCMeta):
    def __init__(self, menu_name: str) -> None:
        super().__init__(False)
        self._CONTENT: GameObjectsDictContainer | None = None
        self._initialized: bool = False
        self._menu_name: str = menu_name

    # 初始化
    def initialize(self) -> None:
        self._CONTENT = UI.generate_container(self._menu_name)
        self._initialized = True

    # 菜单是否被触碰
    def is_hovered(self) -> bool:
        return self._CONTENT.is_hovered() if self.is_visible() and self._CONTENT is not None else False

    # 画出内容
    def draw(self, _surface: ImageSurface) -> None:
        if self.is_visible() and self._CONTENT is not None:
            self._CONTENT.draw(_surface)


# 警告确认窗口
class ConfirmationWarningWindow(AbstractInternalMenu):
    @property
    def item_being_hovered(self) -> str | None:
        return self._CONTENT.item_being_hovered if self._CONTENT is not None else None


# 设置UI
class OptionMenu(AbstractInternalMenu):
    def __init__(self) -> None:
        super().__init__("option_menu")
        self.need_update: dict[str, bool] = {}

    # 初始化
    def initialize(self) -> None:
        super().initialize()
        if self._CONTENT is None:
            EXCEPTION.fatal("The ui has not been correctly initialized.")
        lang_drop_down: DropDownList = self._CONTENT.get("lang_drop_down")
        for lang_choice in Lang.get_available_languages():
            lang_drop_down.set(lang_choice, lang_choice)
        lang_drop_down.set_selected_item(Lang.get_current_language())

    # 确保初始化
    def __ensure_initialization(self) -> None:
        if not self._initialized:
            self.initialize()

    # 宽
    def get_width(self) -> int:
        self.__ensure_initialization()
        return self._CONTENT.get_width() if self._CONTENT is not None else 0

    # 高
    def get_height(self) -> int:
        self.__ensure_initialization()
        return self._CONTENT.get_height() if self._CONTENT is not None else 0

    # 更新背景（非专业人员勿碰）
    def update_background(self, newImg: Any) -> None:
        self.__ensure_initialization()
        if self._CONTENT is not None:
            self._CONTENT.update_background(newImg)

    # 展示
    def draw(self, _surface: ImageSurface) -> None:
        self.need_update.clear()
        if self.is_visible():
            # 检查是否初始化
            self.__ensure_initialization()
            if self._CONTENT is None:
                EXCEPTION.fatal("The ui has not been correctly initialized.")
            lang_drop_down: DropDownList = self._CONTENT.get("lang_drop_down")
            # 更新百分比
            self._CONTENT.get("global_sound_volume").set_percentage(Setting.get("Sound", "global_value") / 100)
            self._CONTENT.get("background_music_sound_volume").set_percentage(Setting.get("Sound", "background_music") / 100)
            self._CONTENT.get("effects_sound_volume").set_percentage(Setting.get("Sound", "effects") / 100)
            self._CONTENT.get("environment_sound_volume").set_percentage(Setting.get("Sound", "environment") / 100)
            # 如果背景没有被初始化或自定义，则渲染默认背景风格
            if not self._CONTENT.is_background_init():
                _surface.blit(Filters.box_blur(_surface.subsurface(self._CONTENT.get_rect()), 30), self._CONTENT.get_pos())
                # 外圈
                Draw.rect(_surface, Colors.WHITE, self._CONTENT.get_rect(), _surface.get_height() // 300, 20)
                # 内圈
                _padding: int = _surface.get_height() // 100
                Draw.rect(
                    _surface,
                    Colors.WHITE,
                    Rectangles.apply(self._CONTENT.get_rect(), (_padding, _padding, _padding * -2, _padding * -2)).get_rect(),
                    _surface.get_height() // 300,
                    20,
                )
            # 画出
            super().draw(_surface)
            # 如果需要更新语言
            if lang_drop_down.get_selected_item() != Lang.get_current_language() and lang_drop_down.get_selected_item() != "":
                # 更新语言并保存新的参数到本地
                Setting.set("Language", value=Lang.get_language_id(lang_drop_down.get_selected_item()))
                Setting.save()
                Lang.reload()
                self._initialized = False
                self.need_update["language"] = True
            # 按键的判定按钮
            if self._CONTENT.item_being_hovered is not None and not lang_drop_down.is_hovered():
                item_percentage_t: int
                match self._CONTENT.item_being_hovered:
                    # 如果碰到全局音量条
                    case "global_sound_volume":
                        item_percentage_t = int(self._CONTENT.get("global_sound_volume").percentage * 100)
                        if item_percentage_t != int(Setting.get("Sound", "global_value")):
                            Setting.set("Sound", "global_value", value=item_percentage_t)
                            self.need_update["volume"] = True
                    # 如果碰到背景音乐音量条
                    case "background_music_sound_volume":
                        item_percentage_t = int(self._CONTENT.get("background_music_sound_volume").percentage * 100)
                        if item_percentage_t != int(Setting.get("Sound", "background_music")):
                            Setting.set("Sound", "background_music", value=item_percentage_t)
                            Music.set_volume(Volume.get_background_music() / 100.0)
                            self.need_update["volume"] = True
                    # 如果碰到音效的音量条
                    case "effects_sound_volume":
                        item_percentage_t = int(self._CONTENT.get("effects_sound_volume").percentage * 100)
                        if item_percentage_t != int(Setting.get("Sound", "effects")):
                            Setting.set("Sound", "effects", value=item_percentage_t)
                            self.need_update["volume"] = True
                    # 如果碰到环境声的音量条
                    case "environment_sound_volume":
                        item_percentage_t = int(self._CONTENT.get("environment_sound_volume").percentage * 100)
                        if item_percentage_t != int(Setting.get("Sound", "environment")):
                            Setting.set("Sound", "environment", value=item_percentage_t)
                            self.need_update["volume"] = True
                    # 返回
                    case "confirm":
                        if Controller.get_event("confirm") is True:
                            self.set_visible(False)
                # 保存新的参数
                if self.need_update.get("volume") is True:
                    Setting.save()
            # 关闭菜单
            if Controller.get_event("back") is True:
                self.set_visible(False)


# 暂停菜单
class PauseMenu(AbstractInternalMenu):
    def __init__(self) -> None:
        super().__init__("pause_menu")
        # 返回确认菜单
        self.__leave_warning: ConfirmationWarningWindow = ConfirmationWarningWindow("leave_without_saving_progress_warning")
        # 退出确认菜单
        self.__exit_warning: ConfirmationWarningWindow = ConfirmationWarningWindow("exit_without_saving_progress_warning")
        # 记录被按下的按钮
        self.__button_hovered: str = ""
        self.split_point: int = -1

    # 被点击的按钮
    def get_button_clicked(self) -> str:
        return self.__button_hovered

    def initialize(self) -> None:
        super().initialize()
        # 加载返回确认菜单
        self.__leave_warning.initialize()
        self.__leave_warning.set_visible(False)
        # 加载退出确认菜单
        self.__exit_warning.initialize()
        self.__exit_warning.set_visible(False)

    def set_visible(self, visible: bool) -> None:
        super().set_visible(visible)
        if self.is_hidden():
            self.__exit_warning.set_visible(False)
            self.__leave_warning.set_visible(False)

    def draw(self, _surface: ImageSurface) -> None:
        self.__button_hovered = ""
        if self.is_visible():
            if not self._initialized:
                self.initialize()
            # 画出分割线
            if self.__leave_warning.is_hidden() and self.__exit_warning.is_hidden():
                if self.split_point < 0:
                    self.split_point = int(_surface.get_width() * 0.3)
                Draw.line(_surface, Colors.WHITE, (self.split_point, 0), (self.split_point, _surface.get_height()), 5)
            # 画出选项
            if self.__leave_warning.is_hidden() and self.__exit_warning.is_hidden():
                super().draw(_surface)
            # 画出退出确认
            self.__leave_warning.draw(_surface)
            self.__exit_warning.draw(_surface)
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
                    match self.__leave_warning.item_being_hovered:
                        case "confirm":
                            self.__button_hovered = "back_to_mainMenu"
                        case "cancel":
                            self.__leave_warning.set_visible(False)
                elif self.__exit_warning.is_visible():
                    match self.__exit_warning.item_being_hovered:
                        case "confirm":
                            from sys import exit

                            exit()
                        case "cancel":
                            self.__exit_warning.set_visible(False)
                elif self._CONTENT is not None and self._CONTENT.item_being_hovered is not None:
                    match self._CONTENT.item_being_hovered:
                        case "back_to_mainMenu":
                            self.__leave_warning.set_visible(True)
                        case "exit_to_desktop":
                            self.__exit_warning.set_visible(True)
                        case _:
                            self.__button_hovered = self._CONTENT.item_being_hovered


# 选取存档的菜单
class SaveOrLoadSelectedProgressMenu(Hidable):
    def __init__(self) -> None:
        super().__init__(False)
        # 行
        self.row: int = 3
        # 列
        self.colum: int = 3
        # 当前选中存档的id
        self.__slotId: int = -1
        # 存档数据
        self.__saves: dict[int, Saves.Progress] = {}
        # 当前页码
        self.__page_id: int = 1
        # 最高页码
        self.__max_pages: int = 10

    # 是否显示
    def set_visible(self, visible: bool) -> None:
        super().set_visible(visible)
        if self.is_visible() is True:
            self.__saves = Saves.get_progresses()

    def get_selected_slot(self) -> int:
        return self.__slotId

    def get_selected_save(self) -> Saves.Progress | None:
        return self.__saves.get(self.__slotId)

    # 渲染切换页面的两侧按钮
    def __process_page_switching(self, _surface: ImageSurface) -> None:
        # 初始化参数
        triangle_size: int = _surface.get_height() // 50
        padding: int = _surface.get_width() // 200
        center_y: int = _surface.get_height() // 2
        button_rect: Rectangle = Rectangle(padding, center_y - triangle_size - padding, triangle_size + padding * 2, padding * 2 + triangle_size * 2)
        _color: tuple[int, int, int, int] = Colors.WHITE
        # 渲染并处理左侧按钮
        if self.__page_id > 1:
            if button_rect.is_hovered():
                _color = Colors.YELLOW
            button_rect.draw_outline(_surface, _color)
            Draw.polygon(
                _surface,
                _color,
                (
                    (padding * 2, center_y),
                    (padding * 2 + triangle_size, center_y - triangle_size),
                    (padding * 2 + triangle_size, center_y + triangle_size),
                ),
            )
            if Controller.get_event("confirm") and button_rect.is_hovered():
                self.__page_id -= 1
        # 渲染并处理右侧按钮
        if self.__page_id < self.__max_pages:
            button_rect.set_pos(_surface.get_width() - triangle_size - padding * 3, center_y - triangle_size - padding)
            _color = Colors.WHITE if not button_rect.is_hovered() else Colors.YELLOW
            button_rect.draw_outline(_surface, _color)
            Draw.polygon(
                _surface,
                _color,
                (
                    (_surface.get_width() - padding * 2, center_y),
                    (_surface.get_width() - triangle_size - padding * 2, center_y - triangle_size),
                    (_surface.get_width() - triangle_size - padding * 2, center_y + triangle_size),
                ),
            )
            if Controller.get_event("confirm") and button_rect.is_hovered():
                self.__page_id += 1

    def draw(self, _surface: ImageSurface) -> None:
        self.__slotId = -1
        if self.is_visible() is True:
            if Controller.get_event("back") or Controller.get_event("hard_confirm"):
                self.set_visible(False)
            else:
                rect_width: int = _surface.get_width() // (self.colum + 1)
                colum_padding: int = rect_width // (self.colum + 1)
                rect_height: int = _surface.get_height() // (self.row + 1)
                row_padding: int = rect_height // (self.row + 1)
                _rect: Rectangle = Rectangle(0, 0, rect_width, rect_height)
                self.__process_page_switching(_surface)
                # 渲染页码
                pageIdText: ImageSurface = Font.render(f"- {self.__page_id} -", Colors.WHITE, row_padding // 2)
                _surface.blit(
                    pageIdText,
                    ((_surface.get_width() - pageIdText.get_width()) // 2, _surface.get_height() - row_padding + (row_padding - pageIdText.get_height()) // 2),
                )
                # 渲染存档信息
                for _y in range(self.row):
                    for _x in range(self.colum):
                        _rect.set_pos(colum_padding + (colum_padding + rect_width) * _x, row_padding + (row_padding + rect_height) * _y)
                        _slotId: int = (self.__page_id - 1) * self.colum * self.colum + _y * self.colum + _x
                        _rect.draw_outline(_surface, Colors.GRAY, 0)
                        _file: Saves.Progress | None = self.__saves.get(_slotId)
                        if _file is not None:
                            _img_height: int = int(_rect.get_height() * 0.8)
                            _surface.blit(Images.smoothly_resize_and_crop_to_fit(_file.screenshot, (_rect.get_width(), _img_height)), _rect.get_pos())
                            _createdAt: ImageSurface = Font.render(
                                f"{_file.createdAt} - Chapter {_file.data.get('chapter_id')}", Colors.WHITE, (_rect.get_height() - _img_height) // 2
                            )
                            _surface.blit(
                                _createdAt,
                                (
                                    _rect.x + (_rect.get_width() - _createdAt.get_width()) // 2,
                                    _rect.y + _img_height + (_rect.get_height() - _img_height - _createdAt.get_height()) // 2,
                                ),
                            )
                        if not _rect.is_hovered():
                            _rect.draw_outline(_surface, Colors.WHITE, 4)
                        else:
                            _rect.draw_outline(_surface, Colors.YELLOW, 4)
                            if Controller.get_event("confirm"):
                                self.__slotId = _slotId


# 暂停菜单处理模块
class PauseMenuModuleForGameSystem(AbstractInternalMenu):
    # 引擎本体的选项菜单
    OPTION_MENU: OptionMenu = OptionMenu()

    def __init__(self) -> None:
        super().__init__("")
        # 暂停菜单
        self.__pause_menu: PauseMenu | None = None
        # 存档选择
        self.__select_progress_menu: SaveOrLoadSelectedProgressMenu = SaveOrLoadSelectedProgressMenu()
        # 是保存进程还是读取存档
        self.__save_or_load: bool = False

    # 获取需要保存的数据（子类必须实现）
    @abstractmethod
    def _get_data_need_to_save(self) -> dict:
        EXCEPTION.fatal("_get_data_need_to_save()", 1)

    # 加载进度（子类需实现）
    @abstractmethod
    def load_progress(self, _data: dict) -> None:
        EXCEPTION.fatal("load_progress()", 1)

    # 淡入或淡出（建议子类重写）
    def _fade(self, _surface: ImageSurface) -> None:
        Media.unload()

    # 停止播放（子类需实现）
    @abstractmethod
    def stop(self) -> None:
        EXCEPTION.fatal("stop()", 1)

    # 更新音量（子类需实现）
    @abstractmethod
    def _update_sound_volume(self) -> None:
        EXCEPTION.fatal("_update_sound_volume()", 1)

    # 更新语言（子类需实现）
    @abstractmethod
    def update_language(self) -> None:
        EXCEPTION.fatal("update_language()", 1)

    # 启用暂停菜单
    def _enable_pause_menu(self) -> None:
        self.__pause_menu = PauseMenu()

    # 禁用暂停菜单
    def _disable_pause_menu(self) -> None:
        self.__pause_menu = None

    # 暂停菜单是否启用
    def _is_pause_menu_enabled(self) -> bool:
        return self.__pause_menu is not None

    # 初始化暂停菜单
    def _initialize_pause_menu(self) -> None:
        if self.__pause_menu is not None:
            self.__pause_menu.initialize()

    # 关闭菜单（并确保所有相关子菜单正常关闭）
    def __close_menus(self) -> None:
        self.OPTION_MENU.set_visible(False)
        if self.__pause_menu is not None:
            self.__pause_menu.set_visible(False)
        self.__select_progress_menu.set_visible(False)

    # 渲染暂停页面
    def _show_pause_menu(self, _surface: ImageSurface) -> None:
        if self.__pause_menu is not None:
            # 暂停背景音乐
            Media.pause()
            # 用于存档的截图
            _screenshot: ImageSurface = _surface.copy()
            # 用于背景的毛玻璃效果图
            _background: ImageSurface = Filters.gaussian_blur(_screenshot)
            # 启用菜单
            self.__pause_menu.set_visible(True)
            # 主循环
            while self.__pause_menu.is_visible():
                Display.flip()
                _surface.blit(_background, ORIGIN)
                # 存档选择系统
                if self.__select_progress_menu.is_visible():
                    self.__select_progress_menu.draw(_surface)
                    if self.__select_progress_menu.get_selected_slot() >= 0:
                        # 新建存档
                        if self.__save_or_load is True:
                            Saves.save(self._get_data_need_to_save(), _screenshot, self.__select_progress_menu.get_selected_slot())
                            self.__select_progress_menu.set_visible(True)
                        # 读取存档
                        else:
                            _save: Saves.Progress | None = self.__select_progress_menu.get_selected_save()
                            if _save is not None:
                                self.__close_menus()
                                self.load_progress(_save.data)
                # 设置选项菜单
                elif self.OPTION_MENU.is_visible():
                    self.OPTION_MENU.draw(_surface)
                    # 更新音量
                    if self.OPTION_MENU.need_update.get("volume") is True:
                        self._update_sound_volume()
                    # 更新语言
                    if self.OPTION_MENU.need_update.get("language") is True:
                        self.update_language()
                # 暂停选项菜单
                else:
                    self.__pause_menu.draw(_surface)
                    match self.__pause_menu.get_button_clicked():
                        case "resume":
                            self.__close_menus()
                        case "save":
                            self.__select_progress_menu.set_visible(True)
                            self.__save_or_load = True
                        case "load":
                            self.__select_progress_menu.set_visible(True)
                            self.__save_or_load = False
                        case "option_menu":
                            self.OPTION_MENU.set_visible(True)
                        case "back_to_mainMenu":
                            self.__close_menus()
                            self._fade(_surface)
                            self.stop()
            # 继续播放背景音乐
            Media.unpause()
