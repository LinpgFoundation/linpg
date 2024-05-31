from .abstract import *


# 视觉小说系统模块
class VisualNovelPlayer(AbstractVisualNovelPlayer, PauseMenuModuleForGameSystem):
    __CHOICE_TEXT: str = str(Lang.get_texts("Dialog", "choice"))

    def __init__(self) -> None:
        AbstractVisualNovelPlayer.__init__(self)
        PauseMenuModuleForGameSystem.__init__(self)
        # 加载对话框系统
        self.__dialog_txt_system: DialogBox = DialogBox(self._FONT_SIZE)
        # UI按钮
        self.__buttons_container: GameObjectsDictContainer | None = None
        # 是否要显示历史对白页面
        self.__is_showing_history: bool = False
        self.__history_bg_surface: ImageSurface = Surfaces.colored(Display.get_size(), Colors.BLACK)
        self.__history_bg_surface.set_alpha(150)
        self.__history_text_surface: ImageSurface | None = None
        self.__history_surface_local_y: int = 0
        # 展示历史界面-返回按钮
        self.__history_back: Button | None = None
        # 是否取消背景渲染
        self.__disable_background_image_rendering: bool = False
        # 初始化音量
        self._update_sound_volume()
        # 玩家做出的选项
        self.__dialog_options: Final[dict] = {}
        # 是否正在淡出的flag
        self.__is_fading_out: bool = True
        # 是否已经完成最后一个Node
        self.__has_reached_the_end: bool = False

    # 禁用基本功能
    def disable_basic_features(self) -> None:
        self.__disable_background_image_rendering = True
        self.__history_back = None
        self.__buttons_container = None
        self._disable_pause_menu()

    # 启用基本功能
    def enable_basic_features(self) -> None:
        self.__disable_background_image_rendering = False
        self.__history_back = Button.load(
            "<&ui>back.png",
            Coordinates.convert((Display.get_width() * 0.04, Display.get_height() * 0.04)),
            Coordinates.convert((Display.get_width() * 0.03, Display.get_height() * 0.04)),
            150,
        )
        # UI按钮
        self.__buttons_container = UI.generate_container("dialog_buttons", {"button_size": self._FONT_SIZE * 2})
        # 暂停菜单
        self._enable_pause_menu()

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return super()._get_data_need_to_save() | {"dialog_options": self.__dialog_options}

    # 获取对话框模块（按照父类要求实现）
    def _get_dialog_box(self) -> DialogBox:
        return self.__dialog_txt_system

    # 是否已经完成最后一个Node
    def _has_reached_the_end(self) -> bool:
        return self.__has_reached_the_end

    # 载入数据
    def _load_content(self) -> None:
        super()._load_content()
        # 将npc立绘系统设置为普通模式
        VisualNovelCharacterImageManager.dev_mode = False
        # 重置对话框
        self.__dialog_txt_system.reset()
        # 重置播放完成的flag
        self.__has_reached_the_end = False

    # 读取存档
    def load_progress(self, _data: dict) -> None:
        super().load_progress(_data)
        # 载入玩家之前做出的选项
        self.__dialog_options.clear()
        self.__dialog_options.update(_data.get("dialog_options", {}))

    # 新读取章节
    def new(self, chapterType: str, chapterId: int, section: str, projectName: str | None = None, dialogId: str = "head") -> None:
        super().new(chapterType, chapterId, section, projectName, dialogId)
        # 初始化重要ui组件
        if not self.__disable_background_image_rendering:
            self.enable_basic_features()

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 如果dialog Id存在
        if self._content.contains_dialogue(self._content.section, dialog_id):
            super()._update_scene(dialog_id)
        else:
            EXCEPTION.fatal(f"The dialog id {dialog_id} does not exist!")

    # 更新音量
    def _update_sound_volume(self) -> None:
        self.set_bgm_volume(Volume.get_background_music() / 100)
        self.__dialog_txt_system.set_sound_volume(Volume.get_effects() / 100)

    # 更新语言
    def update_language(self) -> None:
        super().update_language()
        if self.__buttons_container is not None:
            self.__buttons_container = UI.generate_container("dialog_buttons", {"button_size": self._FONT_SIZE * 2})
            self.__buttons_container.set_visible(self.__dialog_txt_system.is_visible())
        self.__CHOICE_TEXT = str(Lang.get_texts("Dialog", "choice"))
        self._initialize_pause_menu()

    def continue_scene(self, dialog_id: str) -> None:
        self._continue()
        self._update_scene(dialog_id)

    # 前往下一个对话
    def __go_to_next(self, _surface: ImageSurface) -> None:
        self.__is_fading_out = True
        if not self._content.current.has_next():
            self._fade(_surface)
            self.__has_reached_the_end = True
            self.stop()
        else:
            match self._content.current.next.get_type():
                # 默认转到下一个对话
                case "default":
                    self._update_scene(self._content.current.next.get_target())
                # 如果是多选项，则不用处理
                case "option":
                    pass
                # 如果是切换场景
                case "scene":
                    self._fade(_surface)
                    # 更新场景
                    self._update_scene(str(self._content.current.next.get_target()))
                    self.__dialog_txt_system.reset()
                    self.__is_fading_out = False
                    self._fade(_surface)
                # 如果是需要播放过程动画
                case "cutscene":
                    self._fade(_surface)
                    self.stop()
                    self.play_cutscene(_surface)
                # break被视为立刻退出，没有淡出动画
                case "break":
                    self.stop()
                # 非法type
                case _:
                    EXCEPTION.fatal(f'Current dialog "{self._content.current.id}" has a valid next type.')

    def __check_button_event(self, _surface: ImageSurface) -> bool:
        if self.__buttons_container is not None:
            if self.__buttons_container.is_hidden():
                self.__buttons_container.set_visible(True)
                self.__dialog_txt_system.set_visible(True)
            else:
                match self.__buttons_container.item_being_hovered:
                    case "hide":
                        self.__buttons_container.set_visible(False)
                        self.__dialog_txt_system.set_visible(False)
                    # 如果接来下没有文档了或者玩家按到了跳过按钮, 则准备淡出并停止播放
                    case "skip":
                        self.__is_fading_out = True
                        self._fade(_surface)
                        self.__has_reached_the_end = True
                        self.stop()
                    case "is_auto":
                        self.__dialog_txt_system.set_playing_automatically(False)
                        self.__buttons_container.get("not_auto").set_visible(True)
                        self.__buttons_container.get("is_auto").set_visible(False)
                    case "not_auto":
                        self.__dialog_txt_system.set_playing_automatically(True)
                        self.__buttons_container.get("not_auto").set_visible(False)
                        self.__buttons_container.get("is_auto").set_visible(True)
                    case "history":
                        self.__is_showing_history = True
                    case _:
                        return False
            return True
        return False

    # 过场动画
    def play_cutscene(self, _surface: ImageSurface, fade_out_in_ms: int = 3000) -> None:
        # 初始化部分参数
        is_skip: bool = False
        is_playing: bool = True
        # 初始化跳过按钮的参数
        skip_button: StaticImage = StaticImage(
            "<&ui>next.png", _surface.get_width() * 23 // 25, _surface.get_height() // 20, _surface.get_width() * 11 // 200, _surface.get_height() * 3 // 50
        )
        # 进度条
        bar_height: int = _surface.get_height() // 100
        white_progress_bar: ProgressBar = ProgressBar(
            bar_height, _surface.get_height() - bar_height * 2, _surface.get_width() - bar_height * 2, bar_height, Colors.WHITE
        )
        # 生成黑色帘幕
        BLACK_CURTAIN: ImageSurface = Surfaces.colored(_surface.get_size(), Colors.BLACK)
        BLACK_CURTAIN.set_alpha(0)
        # 创建视频文件
        VIDEO: VideoPlayer = VideoPlayer(Specification.get_directory("movie", self._content.current.next.get_target()))
        VIDEO.pre_init()
        # 播放主循环
        while is_playing is True and VIDEO.is_playing() is True:
            VIDEO.draw(_surface)
            skip_button.draw(_surface)
            white_progress_bar.set_percentage(VIDEO.get_percentage_played())
            white_progress_bar.draw(_surface)
            if skip_button.is_hovered() and Controller.mouse.get_pressed(0) and not is_skip:
                is_skip = True
                Music.fade_out(fade_out_in_ms)
            if is_skip is True:
                temp_alpha = BLACK_CURTAIN.get_alpha()
                if temp_alpha is not None and temp_alpha < 255:
                    BLACK_CURTAIN.set_alpha(temp_alpha + Display.get_delta_time())
                else:
                    is_playing = False
                    VIDEO.stop()
                _surface.blit(BLACK_CURTAIN, ORIGIN)
            Display.flip()

    # 淡入或淡出
    def _fade(self, _surface: ImageSurface) -> None:
        if not self.__disable_background_image_rendering:
            _alpha: int = 0
            _alpha_max: Final[int] = 1275
            if self.__is_fading_out is True:
                Media.fade_out(1000)
                while _alpha <= _alpha_max:
                    self._black_bg.set_alpha(_alpha // 20)
                    self._black_bg.draw(_surface)
                    _alpha += Display.get_delta_time()
                    Display.flip()
            else:
                _alpha = _alpha_max
                while _alpha >= 0:
                    self.display_background_image(_surface)
                    self._black_bg.set_alpha(_alpha // 5)
                    self._black_bg.draw(_surface)
                    _alpha -= Display.get_delta_time() * 2
                    Display.flip()
                # 重设black_bg的alpha值以便下一次使用
                self._black_bg.set_alpha(255)

    # 重写父类的display_background_image方法使其在背景被disable后不会继续渲染背景图片
    def display_background_image(self, _surface: ImageSurface) -> None:
        if not self.__disable_background_image_rendering:
            super().display_background_image(_surface)

    def draw(self, _surface: ImageSurface) -> None:
        super().draw(_surface)
        # 按钮
        if self.__buttons_container is not None and not self.__is_showing_history:
            self.__buttons_container.draw(_surface)
        # 按键判定
        if Controller.get_event("confirm"):
            if self.__history_back is not None and self.__history_back.is_hovered() and self.__is_showing_history is True:
                self.__is_showing_history = False
                self.__history_text_surface = None
            elif self.__is_showing_history is True or self.__check_button_event(_surface) is True:
                pass
            # 如果所有行都没有播出，则播出所有行
            elif not self.__dialog_txt_system.is_all_played():
                self.__dialog_txt_system.play_all()
            # 如果玩家需要并做出了选择
            elif self._dialog_options_container.item_being_hovered >= 0:
                # 获取下一个对话的id
                _option: dict = self._content.current.next.get_targets()[self._dialog_options_container.item_being_hovered]
                # 记录玩家选项
                self.__dialog_options[self._content.get_current_dialogue_id()] = {
                    "id": self._dialog_options_container.item_being_hovered,
                    "target": _option["id"],
                }
                # 更新场景
                self._update_scene(_option["id"])
            else:
                self.__go_to_next(_surface)
        if Controller.get_event("previous") and self._content.previous is not None:
            self._update_scene(self._content.previous.id)
        # 暂停菜单
        if (Controller.get_event("back") or Controller.get_event("hard_confirm")) and self._is_pause_menu_enabled():
            if self.__is_showing_history is True:
                self.__is_showing_history = False
                self.__history_text_surface = None
            else:
                self._show_pause_menu(_surface)

        if (
            self.__dialog_txt_system.is_all_played()
            and self.__dialog_txt_system.is_visible()
            and self._content.current.next.get_type() == "option"
            and self._dialog_options_container.is_hidden()
        ):
            self._get_dialog_options_container_ready()
        # 展示历史
        if self.__is_showing_history is True:
            if Controller.get_event("scroll_up") and self.__history_surface_local_y < 0:
                self.__history_text_surface = None
                self.__history_surface_local_y += Display.get_height() // 10
            if Controller.get_event("scroll_down"):
                self.__history_text_surface = None
                self.__history_surface_local_y -= Display.get_height() // 10
            if self.__history_text_surface is None:
                self.__history_text_surface = Surfaces.transparent(Display.get_size())
                dialogIdTemp: str = "head"
                local_y: int = self.__history_surface_local_y
                while True:
                    dialogContent: pyvns.Dialogue = self._content.get_dialogue(self._content.section, dialogIdTemp)
                    has_narrator: bool = len(dialogContent.narrator) > 0
                    if has_narrator:
                        narratorTemp: ImageSurface = self.__dialog_txt_system.FONT.render(dialogContent.narrator + ":", Colors.WHITE)
                        self.__history_text_surface.blit(
                            narratorTemp, (Display.get_width() * 0.14 - narratorTemp.get_width(), Display.get_height() // 10 + local_y)
                        )
                    for i, _text in enumerate(dialogContent.contents):
                        if has_narrator:
                            if i == 0:
                                _text = '[ "' + _text
                            # 这里不用elif，以免当对话行数为一的情况
                            if i == len(dialogContent.contents) - 1:
                                _text += '" ]'
                        self.__history_text_surface.blit(
                            self.__dialog_txt_system.FONT.render(_text, Colors.WHITE), (Display.get_width() * 0.15, Display.get_height() // 10 + local_y)
                        )
                        local_y += self.__dialog_txt_system.FONT.size * 3 // 2
                    if dialogIdTemp != self._content.get_current_dialogue_id():
                        match dialogContent.next.get_type():
                            case "default" | "scene":
                                if dialogContent.has_next():
                                    dialogIdTemp = dialogContent.next.get_target()
                                else:
                                    break
                            case "option":
                                narratorTemp = self.__dialog_txt_system.FONT.render(self.__CHOICE_TEXT + ":", (0, 191, 255))
                                self.__history_text_surface.blit(
                                    narratorTemp, (Display.get_width() * 0.14 - narratorTemp.get_width(), Display.get_height() // 10 + local_y)
                                )
                                self.__history_text_surface.blit(
                                    self.__dialog_txt_system.FONT.render(
                                        str(dialogContent.next.get_targets()[int(self.__dialog_options[dialogIdTemp]["id"])]["text"]),
                                        (0, 191, 255),
                                    ),
                                    (Display.get_width() * 0.15, Display.get_height() // 10 + local_y),
                                )
                                local_y += self.__dialog_txt_system.FONT.size * 3 // 2
                                if (target_temp := self.__dialog_options[dialogIdTemp]["target"]) is not None and local_y < Display.get_height():
                                    dialogIdTemp = str(target_temp)
                                else:
                                    break
                            case _:
                                break
                    else:
                        break
            _surface.blit(self.__history_bg_surface, ORIGIN)
            _surface.blit(self.__history_text_surface, ORIGIN)
            if self.__history_back is not None:
                self.__history_back.draw(_surface)
                self.__history_back.is_hovered()
        else:
            # 显示对话选项
            if self.__buttons_container is None or self.__buttons_container.is_visible():
                self._dialog_options_container.display(_surface)
            # 当自动播放系统告知需要更新，如果对话被隐藏，则无视进入下一个对白的操作，反之则进入
            if self.__buttons_container is not None and self.__buttons_container.is_visible() and self.__dialog_txt_system.is_update_needed():
                self.__go_to_next(_surface)
