from .abstract import *

# 视觉小说系统模块
class DialogSystem(AbstractDialogSystem, PauseMenuModuleForGameSystem):

    __CHOICE_TEXT: str = str(Lang.get_texts("Dialog", "choice"))

    def __init__(self, basic_features_only: bool = False) -> None:
        AbstractDialogSystem.__init__(self)
        PauseMenuModuleForGameSystem.__init__(self)
        # 加载对话框系统
        self.__dialog_txt_system: DialogBox = DialogBox(self._FONT_SIZE)
        # UI按钮
        self.__buttons_container: Optional[GameObjectsDictContainer] = None
        # 加载ui
        if not basic_features_only:
            # UI按钮
            self.__buttons_container = UI.generate_container("dialog_buttons", {"button_size": self._FONT_SIZE * 2})
            # 暂停菜单
            self._enable_pause_menu()
        # 是否要显示历史对白页面
        self.__is_showing_history: bool = False
        self.__history_bg_surface: ImageSurface = Surface.colored(Display.get_size(), Colors.BLACK)
        self.__history_bg_surface.set_alpha(150)
        self.__history_text_surface: Optional[ImageSurface] = None
        self.__history_surface_local_y: int = 0
        # 展示历史界面-返回按钮
        self.history_back = (
            Button.load(
                "<!ui>back.png",
                Coordinates.convert((Display.get_width() * 0.04, Display.get_height() * 0.04)),
                Coordinates.convert((Display.get_width() * 0.03, Display.get_height() * 0.04)),
                150,
            )
            if not basic_features_only
            else None
        )
        # 初始化音量
        self._update_sound_volume()
        # 玩家做出的选项
        self.__dialog_options: dict = {}

    # 初始化关键参数
    def _initialize(  # type: ignore[override]
        self,
        chapterType: str,
        chapterId: int,
        part: str,
        projectName: Optional[str],
        dialogId: str = "head",
        dialog_options: dict = {},
    ) -> None:
        super()._initialize(chapterType, chapterId, part, projectName, dialogId)
        # 玩家做出的选项
        self.__dialog_options.clear()
        self.__dialog_options.update(dialog_options)

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return super()._get_data_need_to_save() | {"dialog_options": self.__dialog_options}

    # 获取对话框模块（按照父类要求实现）
    def _get_dialog_box(self) -> DialogBox:
        return self.__dialog_txt_system

    # 载入数据
    def _load_content(self) -> None:
        super()._load_content()
        # 重置对话框
        self.__dialog_txt_system.reset()

    # 读取章节
    def load(self, save_path: str) -> None:
        saveData = Config.load_file(save_path)
        self._initialize(
            saveData["chapter_type"],
            saveData["chapter_id"],
            saveData["type"],
            saveData["project_name"],
            saveData["dialog_id"],
            saveData["dialog_options"],
        )
        # 根据已有参数载入数据
        self._load_content()

    # 新建章节
    def new(self, chapterType: str, chapterId: int, part: str, projectName: Optional[str] = None) -> None:
        self._initialize(chapterType, chapterId, part, projectName)
        # 根据已有参数载入数据
        self._load_content()

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 如果dialog Id存在
        if dialog_id in self.dialog_content:
            super()._update_scene(dialog_id)
            # 自动保存
            if self.auto_save:
                self.save_progress()
        else:
            EXCEPTION.fatal("The dialog id {} does not exist!".format(dialog_id))

    # 更新音量
    def _update_sound_volume(self) -> None:
        self.set_bgm_volume(Media.volume.background_music / 100)
        self.__dialog_txt_system.set_sound_volume(Media.volume.effects / 100)

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

    def switch_part(self, part: str) -> None:
        self._part = part
        self._load_content()

    # 前往下一个对话
    def __go_to_next(self, surface: ImageSurface) -> None:
        if self._current_dialog_content["next_dialog_id"] is None:
            self.fade(surface)
            self.stop()
        elif (next_dialog_type := self.get_next_dialog_type()) is not None:
            # 默认转到下一个对话
            if next_dialog_type == "default":
                self._update_scene(self._current_dialog_content["next_dialog_id"]["target"])
            # 如果是多选项，则不用处理
            elif next_dialog_type == "option":
                pass
            # 如果是切换场景
            elif next_dialog_type == "changeScene":
                self.fade(surface)
                # 更新场景
                self._update_scene(self._current_dialog_content["next_dialog_id"]["target"])
                self.__dialog_txt_system.reset()
                self.fade(surface, "$in")
            # 如果是需要播放过程动画
            elif next_dialog_type == "cutscene":
                self.fade(surface)
                self.stop()
                self.play_cutscene(surface)
            # break被视为立刻退出，没有淡出动画
            elif next_dialog_type == "break":
                self.stop()
            # 非法type
            else:
                EXCEPTION.fatal('Type "{}" is not a valid type.'.format(next_dialog_type))

    def __check_button_event(self, surface: ImageSurface) -> bool:
        if self.__buttons_container is not None:
            if self.__buttons_container.is_hidden():
                self.__buttons_container.set_visible(True)
                self.__dialog_txt_system.set_visible(True)
            elif self.__buttons_container.item_being_hovered == "hide":
                self.__buttons_container.set_visible(False)
                self.__dialog_txt_system.set_visible(False)
            # 如果接来下没有文档了或者玩家按到了跳过按钮, 则准备淡出并停止播放
            elif self.__buttons_container.item_being_hovered == "skip":
                self.fade(surface)
                self.stop()
            elif self.__buttons_container.item_being_hovered == "is_auto":
                self.__dialog_txt_system.set_playing_automatically(False)
                self.__buttons_container.get("not_auto").set_visible(True)
                self.__buttons_container.get("is_auto").set_visible(False)
            elif self.__buttons_container.item_being_hovered == "not_auto":
                self.__dialog_txt_system.set_playing_automatically(True)
                self.__buttons_container.get("not_auto").set_visible(False)
                self.__buttons_container.get("is_auto").set_visible(True)
            elif self.__buttons_container.item_being_hovered == "history":
                self.__is_showing_history = True
            else:
                return False
            return True
        else:
            return False

    # 过场动画
    def play_cutscene(self, surface: ImageSurface, fade_out_in_ms: int = 3000) -> None:
        # 初始化部分参数
        is_skip: bool = False
        is_playing: bool = True
        # 初始化跳过按钮的参数
        skip_button: StaticImage = StaticImage(
            "<!ui>next.png",
            surface.get_width() * 23 // 25,
            surface.get_height() // 20,
            surface.get_width() * 11 // 200,
            surface.get_height() * 3 // 50,
        )
        # 进度条
        bar_height: int = surface.get_height() // 100
        white_progress_bar: ProgressBar = ProgressBar(
            bar_height, surface.get_height() - bar_height * 2, surface.get_width() - bar_height * 2, bar_height, "white"
        )
        # 生成黑色帘幕
        BLACK_CURTAIN: ImageSurface = Surface.colored(surface.get_size(), Colors.BLACK)
        BLACK_CURTAIN.set_alpha(0)
        # 创建视频文件
        VIDEO: VideoPlayer = VideoPlayer(
            os.path.join(Specification.get("FolderPath", "Movie"), self._current_dialog_content["next_dialog_id"]["target"])
        )
        VIDEO.pre_init()
        # 播放主循环
        while is_playing is True and VIDEO.is_playing() is True:
            VIDEO.draw(surface)
            skip_button.draw(surface)
            white_progress_bar.set_percentage(VIDEO.get_percentage_played())
            white_progress_bar.draw(surface)
            if skip_button.is_hovered() and Controller.mouse.get_pressed(0) and not is_skip:
                is_skip = True
                Music.fade_out(fade_out_in_ms)
            if is_skip is True:
                temp_alpha = BLACK_CURTAIN.get_alpha()
                if temp_alpha is not None and temp_alpha < 255:
                    BLACK_CURTAIN.set_alpha(temp_alpha + 5)
                else:
                    is_playing = False
                    VIDEO.stop()
                surface.blit(BLACK_CURTAIN, (0, 0))
            Display.flip()

    # 淡入或淡出
    def fade(self, surface: ImageSurface, stage: str = "$out") -> None:
        if stage == "$out":
            Media.fade_out(1000)
            for i in range(0, 255, 5):
                self._black_bg.set_alpha(i)
                self._black_bg.draw(surface)
                Display.flip()
        elif stage == "$in":
            for i in range(255, 0, -5):
                self.display_background_image(surface)
                self._black_bg.set_alpha(i)
                self._black_bg.draw(surface)
                Display.flip()
            # 重设black_bg的alpha值以便下一次使用
            self._black_bg.set_alpha(255)
        else:
            EXCEPTION.fatal('Stage input has to be either "in" or "out", not "{}"'.format(stage))

    def draw(self, surface: ImageSurface) -> None:
        super().draw(surface)
        # 按钮
        if self.__buttons_container is not None and not self.__is_showing_history:
            self.__buttons_container.draw(surface)
        # 按键判定
        if Controller.get_event("confirm"):
            if self.history_back is not None and self.history_back.is_hovered() and self.__is_showing_history is True:
                self.__is_showing_history = False
                self.__history_text_surface = None
            elif self.__is_showing_history is True or self.__check_button_event(surface) is True:
                pass
            # 如果所有行都没有播出，则播出所有行
            elif not self.__dialog_txt_system.is_all_played():
                self.__dialog_txt_system.play_all()
            # 如果玩家需要并做出了选择
            elif self._dialog_options_container.item_being_hovered >= 0:
                # 获取下一个对话的id
                _option: dict = self._current_dialog_content["next_dialog_id"]["target"][
                    self._dialog_options_container.item_being_hovered
                ]
                # 记录玩家选项
                self.__dialog_options[self._dialog_id] = {
                    "id": self._dialog_options_container.item_being_hovered,
                    "target": _option["id"],
                }
                # 更新场景
                self._update_scene(_option["id"])
            else:
                self.__go_to_next(surface)
        if Controller.get_event("previous") and self._current_dialog_content["last_dialog_id"] is not None:
            self._update_scene(self._current_dialog_content["last_dialog_id"])
        # 暂停菜单
        if Controller.get_event("back") and self.is_pause_menu_enabled():
            if self.__is_showing_history is True:
                self.__is_showing_history = False
            else:
                self._show_pause_menu(surface)

        if (
            self.__dialog_txt_system.is_all_played()
            and self.__dialog_txt_system.is_visible()
            and self.get_next_dialog_type() == "option"
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
                self.__history_text_surface = Surface.transparent(Display.get_size())
                dialogIdTemp: str = "head"
                local_y: int = self.__history_surface_local_y
                while True:
                    narratorTxt: Optional[str] = self.dialog_content[dialogIdTemp].get("narrator")
                    has_narrator: bool = narratorTxt is not None and len(narratorTxt) > 0
                    if has_narrator:
                        narratorTemp = self.__dialog_txt_system.FONT.render(narratorTxt + ":", Colors.WHITE)  # type: ignore
                        self.__history_text_surface.blit(
                            narratorTemp,
                            (Display.get_width() * 0.14 - narratorTemp.get_width(), Display.get_height() // 10 + local_y),
                        )
                    for i in range(len(self.dialog_content[dialogIdTemp]["contents"])):
                        txt: str = str(self.dialog_content[dialogIdTemp]["contents"][i])
                        if has_narrator:
                            if i == 0:
                                txt = '[ "' + txt
                            # 这里不用elif，以免当对话行数为一的情况
                            if i == len(self.dialog_content[dialogIdTemp]["contents"]) - 1:
                                txt += '" ]'
                        self.__history_text_surface.blit(
                            self.__dialog_txt_system.FONT.render(txt, Colors.WHITE),
                            (Display.get_width() * 0.15, Display.get_height() // 10 + local_y),
                        )
                        local_y += self.__dialog_txt_system.FONT.size * 3 // 2
                    if dialogIdTemp != self._dialog_id:
                        _next_dialog_type: str = str(self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"])
                        if _next_dialog_type == "default" or _next_dialog_type == "changeScene":
                            if (target_temp := self.dialog_content[dialogIdTemp]["next_dialog_id"]["target"]) is not None:
                                dialogIdTemp = str(target_temp)
                            else:
                                break
                        elif _next_dialog_type == "option":
                            narratorTemp = self.__dialog_txt_system.FONT.render(self.__CHOICE_TEXT + ":", (0, 191, 255))
                            self.__history_text_surface.blit(
                                narratorTemp,
                                (Display.get_width() * 0.14 - narratorTemp.get_width(), Display.get_height() // 10 + local_y),
                            )
                            self.__history_text_surface.blit(
                                self.__dialog_txt_system.FONT.render(
                                    str(
                                        self.dialog_content[dialogIdTemp]["next_dialog_id"]["target"][
                                            int(self.__dialog_options[dialogIdTemp]["id"])
                                        ]["text"]
                                    ),
                                    (0, 191, 255),
                                ),
                                (Display.get_width() * 0.15, Display.get_height() // 10 + local_y),
                            )
                            local_y += self.__dialog_txt_system.FONT.size * 3 // 2
                            if (
                                target_temp := self.__dialog_options[dialogIdTemp]["target"]
                            ) is not None and local_y < Display.get_height():
                                dialogIdTemp = str(target_temp)
                            else:
                                break
                        else:
                            break
                    else:
                        break
            surface.blit(self.__history_bg_surface, (0, 0))
            surface.blit(self.__history_text_surface, (0, 0))
            if self.history_back is not None:
                self.history_back.draw(surface)
                self.history_back.is_hovered()
        else:
            # 显示对话选项
            if self.__buttons_container is None or self.__buttons_container.is_visible():
                self._dialog_options_container.display(surface)
            # 当自动播放系统告知需要更新，如果对话被隐藏，则无视进入下一个对白的操作，反之则进入
            if (
                self.__buttons_container is not None
                and self.__buttons_container.is_visible()
                and self.__dialog_txt_system.is_update_needed()
            ):
                self.__go_to_next(surface)
