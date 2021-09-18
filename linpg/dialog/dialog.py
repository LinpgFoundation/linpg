from .abstract import *

# 视觉小说系统模块
class DialogSystem(AbstractDialogSystem, PauseMenuModuleForGameSystem):
    def __init__(self, basic_features_only: bool = False) -> None:
        AbstractDialogSystem.__init__(self)
        PauseMenuModuleForGameSystem.__init__(self)
        if not basic_features_only:
            # UI按钮
            self._buttons_mananger = DialogButtons()
            # 暂停菜单
            self._enable_pause_menu()
        # 是否要显示历史对白页面
        self._is_showing_history: bool = False
        self._history_surface = None
        self._history_surface_local_y = 0
        # 展示历史界面-返回按钮
        self.history_back = (
            load_button(
                "<!ui>back.png",
                (Display.get_width() * 0.04, Display.get_height() * 0.04),
                (Display.get_width() * 0.03, Display.get_height() * 0.04),
                150,
            )
            if not basic_features_only
            else None
        )

    # 读取章节
    def load(self, save_path: str) -> None:
        saveData = Config.load(save_path)
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
    def new(self, chapterType: str, chapterId: int, part: str, projectName: str = None) -> None:
        self._initialize(chapterType, chapterId, part, projectName)
        # 根据已有参数载入数据
        self._load_content()

    # 更新场景
    def _update_scene(self, dialog_id: strint) -> None:
        # 如果dialog Id存在
        if dialog_id in self.dialog_content:
            super()._update_scene(dialog_id)
            # 自动保存
            if self.auto_save:
                self.save_progress()
        else:
            EXCEPTION.fatal("The dialog id {} does not exist!".format(dialog_id))

    def updated_language(self) -> None:
        super().updated_language()
        self._initialize_pause_menu()

    def continue_scene(self, dialog_id: strint) -> None:
        self._continue()
        self._update_scene(dialog_id)

    def switch_part(self, part: str) -> None:
        self._part = part
        self._load_content()

    def __check_button_event(self, surface: ImageSurface) -> bool:
        if self._buttons_mananger is not None and not self._is_showing_history:
            if self._buttons_mananger.item_being_hovered == "hide":
                self._buttons_mananger.hidden = not self._buttons_mananger.hidden
                self._dialog_txt_system.hidden = self._buttons_mananger.hidden
            # 如果接来下没有文档了或者玩家按到了跳过按钮, 则准备淡出并停止播放
            elif self._buttons_mananger.item_being_hovered == "skip":
                self.fade(surface)
                self.stop()
            elif self._buttons_mananger.item_being_hovered == "auto":
                self._buttons_mananger.autoModeSwitch()
                self._dialog_txt_system.autoMode = self._buttons_mananger.autoMode
            elif self._buttons_mananger.item_being_hovered == "history":
                self._is_showing_history = True
            else:
                return False
        else:
            return False
        return True

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
        if self._buttons_mananger is not None:
            self._buttons_mananger.draw(surface)
        # 按键判定
        leftClick: bool = False
        if Controller.get_event("confirm"):
            if self.history_back is not None and self.history_back.is_hover() and self._is_showing_history is True:
                self._is_showing_history = False
                self._history_surface = None
            elif self.__check_button_event(surface) is True:
                pass
            # 如果所有行都没有播出，则播出所有行
            elif not self._dialog_txt_system.is_all_played():
                self._dialog_txt_system.play_all()
            else:
                leftClick = True
        if Controller.get_event("scroll_up") and self._history_surface_local_y < 0:
            self._history_surface = None
            self._history_surface_local_y += Display.get_height() * 0.1
        if Controller.get_event("scroll_down"):
            self._history_surface = None
            self._history_surface_local_y -= Display.get_height() * 0.1
        if Controller.get_event("previous") and self._current_dialog_content["last_dialog_id"] is not None:
            self._update_scene(self._current_dialog_content["last_dialog_id"])
        # 暂停菜单
        if Controller.get_event("back") and self.is_pause_menu_enabled():
            if self._is_showing_history is True:
                self._is_showing_history = False
            else:
                self._show_pause_menu(surface)
        # 显示对话选项
        if (
            self._dialog_txt_system.is_all_played()
            and not self._dialog_txt_system.hidden
            and self._current_dialog_content["next_dialog_id"] is not None
            and self._current_dialog_content["next_dialog_id"]["type"] == "option"
        ):
            optionBox_y_base = (
                Display.get_height() * 3 / 4
                - (len(self._current_dialog_content["next_dialog_id"]["target"])) * 2 * Display.get_width() * 0.03
            ) / 4
            optionBox_height = int(Display.get_width() * 0.05)
            nextDialogId = None
            for i in range(len(self._current_dialog_content["next_dialog_id"]["target"])):
                option_txt = self._dialog_txt_system.FONT.render(
                    self._current_dialog_content["next_dialog_id"]["target"][i]["txt"], Color.WHITE
                )
                optionBox_width: int = int(option_txt.get_width() + Display.get_width() * 0.05)
                optionBox_x: int = int((Display.get_width() - optionBox_width) / 2)
                optionBox_y: int = int((i + 1) * 2 * Display.get_width() * 0.03 + optionBox_y_base)
                if (
                    0 < Controller.mouse.x - optionBox_x < optionBox_width
                    and 0 < Controller.mouse.y - optionBox_y < optionBox_height
                ):
                    self._option_box_selected_surface.set_size(optionBox_width, optionBox_height)
                    self._option_box_selected_surface.set_pos(optionBox_x, optionBox_y)
                    self._option_box_selected_surface.draw(surface)
                    display_in_center(
                        option_txt,
                        self._option_box_selected_surface,
                        self._option_box_selected_surface.x,
                        self._option_box_selected_surface.y,
                        surface,
                    )
                    # 保存选取的选项
                    if leftClick and not self._is_showing_history:
                        nextDialogId = self._current_dialog_content["next_dialog_id"]["target"][i]["id"]
                else:
                    self._option_box_surface.set_size(optionBox_width, optionBox_height)
                    self._option_box_surface.set_pos(optionBox_x, optionBox_y)
                    self._option_box_surface.draw(surface)
                    display_in_center(
                        option_txt, self._option_box_surface, self._option_box_surface.x, self._option_box_surface.y, surface
                    )
            if nextDialogId is not None:
                self._dialog_options[self._dialog_id] = {"id": i, "target": nextDialogId}
                # 更新场景
                self._update_scene(nextDialogId)
                leftClick = False
        # 展示历史
        if self._is_showing_history is True:
            if self._history_surface is None:
                self._history_surface = new_surface(Display.get_size()).convert()
                self._history_surface.fill(Color.BLACK)
                self._history_surface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = self._history_surface_local_y
                while dialogIdTemp is not None:
                    if self.dialog_content[dialogIdTemp]["narrator"] is not None:
                        narratorTemp = self._dialog_txt_system.FONT.render(
                            self.dialog_content[dialogIdTemp]["narrator"] + ":", Color.WHITE
                        )
                        self._history_surface.blit(
                            narratorTemp,
                            (Display.get_width() * 0.14 - narratorTemp.get_width(), Display.get_height() * 0.1 + local_y),
                        )
                    for i in range(len(self.dialog_content[dialogIdTemp]["content"])):
                        txt = self.dialog_content[dialogIdTemp]["content"][i]
                        if self.dialog_content[dialogIdTemp]["narrator"] is not None:
                            if i == 0:
                                txt = '[ "' + txt
                            elif i == len(self.dialog_content[dialogIdTemp]["content"]) - 1:
                                txt += '" ]'
                        self._history_surface.blit(
                            self._dialog_txt_system.FONT.render(txt, Color.WHITE),
                            (Display.get_width() * 0.15, Display.get_height() * 0.1 + local_y),
                        )
                        local_y += self._dialog_txt_system.FONT.size * 1.5
                    if dialogIdTemp != self._dialog_id:
                        if (
                            self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"] == "default"
                            or self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"] == "changeScene"
                        ):
                            dialogIdTemp = self.dialog_content[dialogIdTemp]["next_dialog_id"]["target"]
                        elif self.dialog_content[dialogIdTemp]["next_dialog_id"]["type"] == "option":
                            narratorTemp = self._dialog_txt_system.FONT.render(
                                self._buttons_mananger.choiceTxt + " - ", (0, 191, 255)
                            )
                            self._history_surface.blit(
                                narratorTemp,
                                (
                                    Display.get_width() * 0.15 - narratorTemp.get_width(),
                                    Display.get_height() * 0.1 + local_y,
                                ),
                            )
                            self._history_surface.blit(
                                self._dialog_txt_system.FONT.render(
                                    str(self._dialog_options[dialogIdTemp]["target"]), (0, 191, 255)
                                ),
                                (Display.get_width() * 0.15, Display.get_height() * 0.1 + local_y),
                            )
                            local_y += self._dialog_txt_system.FONT.size * 1.5
                            dialogIdTemp = self._dialog_options[dialogIdTemp]["target"]
                        else:
                            dialogIdTemp = None
                    else:
                        dialogIdTemp = None
            surface.blit(self._history_surface, (0, 0))
            if self.history_back is not None:
                self.history_back.draw(surface)
                self.history_back.is_hover()
        # 如果对话被隐藏，则无视进入下一个对白的操作
        elif self._buttons_mananger is not None and self._buttons_mananger.hidden is True:
            pass
        # 如果操作或自动播放系统告知需要更新
        elif self._dialog_txt_system.needUpdate() or leftClick:
            if self._current_dialog_content["next_dialog_id"] is None:
                self.fade(surface)
                self.stop()
            else:
                next_dialog_type: str = str(self._current_dialog_content["next_dialog_id"]["type"])
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
                    self._dialog_txt_system.reset()
                    self.fade(surface, "$in")
                # 如果是需要播放过程动画
                elif next_dialog_type == "cutscene":
                    self.fade(surface)
                    self.stop()
                    cutscene(
                        surface,
                        os.path.join(ASSET.PATH_DICT["movie"], self._current_dialog_content["next_dialog_id"]["target"]),
                    )
                # break被视为立刻退出，没有淡出动画
                elif next_dialog_type == "break":
                    self.stop()
                # 非法type
                else:
                    EXCEPTION.fatal('Type "{}" is not a valid type.'.format(next_dialog_type))
