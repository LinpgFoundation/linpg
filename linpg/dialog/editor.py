from .dialog import *

# 对话制作器
class DialogEditor(AbstractDialogSystem):
    def load(self, chapterType: str, chapterId: int, part: str, projectName: str = None):
        self._initialize(chapterType, chapterId, part, projectName)
        self.folder_for_save_file, self.name_for_save_file = os.path.split(self.get_dialog_file_location())
        # 加载对话框系统
        self._dialog_txt_system.dev_mode()
        # 将自身和npc立绘系统设置为开发者模式
        self.dev_mode = True
        self._npc_manager.dev_mode = True
        # 加载容器
        container_width = int(Display.get_width() * 0.2)
        self.UIContainerRightImage = IMG.load(
            os.path.join(DIALOG_UI_PATH, "container.png"), (container_width, Display.get_height())
        )
        # 背景容器
        self.UIContainerRight_bg = SurfaceContainerWithScrollbar(
            None,
            int(container_width * 0.075),
            int(Display.get_height() * 0.1),
            int(container_width * 0.85),
            int(Display.get_height() * 0.85),
            "vertical",
        )
        self.UIContainerRight_bg.set_scroll_bar_pos("right")
        # 加载背景图片
        self.background_deselect = IMG.load(os.path.join(DIALOG_UI_PATH, "deselect.png"))
        self.UIContainerRight_bg.set("current_select", None)
        for imgPath in glob(os.path.join(self._background_image_folder_path, "*")):
            self.UIContainerRight_bg.set(os.path.basename(imgPath), IMG.load(imgPath, (container_width * 0.8, None)))
        self.UIContainerRight_bg.set(
            "<transparent>", get_texture_missing_surface((container_width * 0.8, container_width * 0.45))
        )
        self.UIContainerRight_bg.distance_between_item = int(Display.get_height() * 0.02)
        self.__current_select_bg_name = None
        self.__current_select_bg_copy = None
        # npc立绘容器
        self.UIContainerRight_npc = SurfaceContainerWithScrollbar(
            None,
            int(container_width * 0.075),
            int(Display.get_height() * 0.1),
            int(container_width * 0.85),
            int(Display.get_height() * 0.85),
            "vertical",
        )
        self.UIContainerRight_npc.set_scroll_bar_pos("right")
        # 加载npc立绘
        for imgPath in glob(os.path.join(self._npc_manager.image_folder_path, "*")):
            self.UIContainerRight_npc.set(os.path.basename(imgPath), IMG.load(imgPath, (container_width * 0.8, None)))
        self.UIContainerRight_npc.hidden = True
        self.UIContainerRight_npc.distance_between_item = 0
        # 容器按钮
        button_width: int = int(Display.get_width() * 0.04)
        self.UIContainerRightButton = MovableImage(
            os.path.join(DIALOG_UI_PATH, "container_button.png"),
            int(Display.get_width() - button_width),
            int(Display.get_height() * 0.4),
            int(Display.get_width() - button_width - container_width),
            int(Display.get_height() * 0.4),
            int(container_width / 10),
            0,
            button_width,
            int(Display.get_height() * 0.2),
        )
        self.UIContainerRightButton.rotate(90)
        # UI按钮
        CONFIG = Lang.get_text("DialogCreator")
        button_y: int = int(Display.get_height() * 0.03)
        font_size: int = int(button_width / 3)
        # 控制容器转换的按钮
        self.button_select_background = load_button_with_text_in_center(
            os.path.join(DIALOG_UI_PATH, "menu.png"), CONFIG["background"], "black", font_size, (0, button_y * 2), 150
        )
        self.button_select_npc = load_button_with_text_in_center(
            os.path.join(DIALOG_UI_PATH, "menu.png"), CONFIG["npc"], "black", font_size, (0, button_y * 2), 150
        )
        panding: int = int(
            (container_width - self.button_select_background.get_width() - self.button_select_npc.get_width()) / 3
        )
        self.button_select_background.set_left(panding)
        self.button_select_npc.set_left(self.button_select_background.get_right() + panding)
        button_size: tuple = (button_width, button_width)
        # 页面右上方的一排按钮
        self.buttonsUI = {
            "save": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "save.png"),
                Lang.get_text("Global", "save"),
                (button_width * 7.25, button_y),
                button_size,
                150,
            ),
            "reload": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "reload.png"),
                Lang.get_text("Global", "reload_file"),
                (button_width * 6, button_y),
                button_size,
                150,
            ),
            "add": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "add.png"), CONFIG["add"], (button_width * 4.75, button_y), button_size, 150
            ),
            "next": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "dialog_skip.png"),
                CONFIG["next"],
                (button_width * 4.75, button_y),
                button_size,
                150,
            ),
            "previous": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "previous.png"),
                CONFIG["previous"],
                (button_width * 3.5, button_y),
                button_size,
                150,
            ),
            "delete": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "delete.png"),
                CONFIG["delete"],
                (button_width * 2.25, button_y),
                button_size,
                150,
            ),
            "back": load_button_with_des(
                os.path.join(DIALOG_UI_PATH, "back.png"),
                Lang.get_text("Global", "back_to_main_menu"),
                (button_width, button_y),
                button_size,
                150,
            ),
        }
        self.please_enter_content = CONFIG["please_enter_content"]
        self.please_enter_name = CONFIG["please_enter_name"]
        # 从配置文件中加载数据
        self._load_content()
        # 移除按钮
        self.removeNpcButton = self._dialog_txt_system.FONT.render(CONFIG["removeNpc"], Color.BLACK)
        surfaceTmp = new_surface((self.removeNpcButton.get_width() * 1.2, self.removeNpcButton.get_height() * 1.2)).convert()
        surfaceTmp.fill(Color.WHITE)
        surfaceTmp.blit(self.removeNpcButton, (self.removeNpcButton.get_width() * 0.1, 0))
        self.removeNpcButton = surfaceTmp
        # 未保存离开时的警告
        self.__no_save_warning = UI.generate_deault("leave_without_saving_warning")
        # 切换准备编辑的dialog部分
        self.dialog_key_select = DropDownSingleChoiceList(None, button_width * 9, button_y + font_size, font_size)
        for key in self._dialog_data:
            self.dialog_key_select.set(key, key)
        self.dialog_key_select.set_current_selected_item(self._part)

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        original_data: dict = (
            Config.load(self.get_dialog_file_location()) if os.path.exists(self.get_dialog_file_location()) else {}
        )
        original_data["dialogs"] = self.__slipt_the_stuff_need_save()
        return original_data

    # 更新背景选项栏
    def _update_background_image(self, image_name: str) -> None:
        super()._update_background_image(image_name)
        if image_name is not None:
            if self.__current_select_bg_name is not None:
                self.UIContainerRight_bg.set("current_select", self.__current_select_bg_copy)
                self.UIContainerRight_bg.swap("current_select", self.__current_select_bg_name)
            self.UIContainerRight_bg.swap("current_select", image_name)
            self.__current_select_bg_name = image_name
            current_select_bg = self.UIContainerRight_bg.get("current_select")
            self.__current_select_bg_copy = current_select_bg.copy()
            current_select_bg.blit(IMG.smoothly_resize(self.background_deselect, current_select_bg.get_size()), (0, 0))
        else:
            self.UIContainerRight_bg.set(self.__current_select_bg_name, self.__current_select_bg_copy)
            self.UIContainerRight_bg.set("current_select", None)
            self.__current_select_bg_name = None
            self.__current_select_bg_copy = None

    # 读取章节信息
    def _load_content(self) -> None:
        self._dialog_data = (
            Config.load(self.get_dialog_file_location(), "dialogs")
            if os.path.exists(self.get_dialog_file_location())
            else {}
        )
        # 获取默认语言
        default_lang_of_dialog: str = self.get_default_lang()
        # 如果dialogs字典是空的
        if len(list(self._dialog_data.keys())) <= 0:
            # 如果不是默认主语言，则尝试加载主语言
            if default_lang_of_dialog != Setting.language:
                self.is_default = False
                # 读取原始数据
                self._dialog_data_default = Config.load(self.get_dialog_file_location(default_lang_of_dialog), "dialogs")
                self._dialog_data = deepcopy(self._dialog_data_default)
        else:
            # 如果不是默认主语言
            if default_lang_of_dialog != Setting.language:
                self.is_default = False
                # 读取原始数据
                self._dialog_data_default = Config.load(self.get_dialog_file_location(default_lang_of_dialog), "dialogs")
                # 填入未被填入的数据
                for part in self._dialog_data_default:
                    for key, DIALOG_DATA_TEMP in self._dialog_data_default[part].items():
                        if key in self._dialog_data[part]:
                            for key2, dataNeedReplace in DIALOG_DATA_TEMP.items():
                                if key2 not in self._dialog_data[part][key]:
                                    self._dialog_data[part][key][key2] = deepcopy(dataNeedReplace)
                        else:
                            self._dialog_data[part][key] = deepcopy(DIALOG_DATA_TEMP)
            else:
                self.is_default = True
                self._dialog_data_default = None
        # 则尝试加载后仍然出现内容为空的情况
        if len(list(self._dialog_data.keys())) <= 0:
            self._part = "example_dialog"
            self._dialog_data[self._part] = {}
        if len(list(self._dialog_data[self._part].keys())) <= 0:
            self._dialog_data[self._part]["head"] = {
                "background_img": None,
                "background_music": None,
                "characters_img": [],
                "content": [self.please_enter_content],
                "last_dialog_id": None,
                "narrator": self.please_enter_name,
                "next_dialog_id": None,
            }
            self.is_default = True
            self._dialog_data_default = None
        # 更新场景
        self._update_scene(self._dialog_id)

    # 分离需要保存的数据
    def __slipt_the_stuff_need_save(self) -> dict:
        self.current_dialog_content["narrator"] = self._dialog_txt_system.narrator.get_text()
        self.current_dialog_content["content"] = self._dialog_txt_system.content.get_text()
        data_need_save: dict = deepcopy(self._dialog_data)
        if not self.is_default:
            # 移除掉相似的内容
            for part in self._dialog_data_default:
                for dialogId, defaultDialogData in self._dialog_data_default[part].items():
                    if dialogId in data_need_save[part]:
                        for dataType in defaultDialogData:
                            if data_need_save[part][dialogId][dataType] == defaultDialogData[dataType]:
                                del data_need_save[part][dialogId][dataType]
                        if len(data_need_save[part][dialogId]) == 0:
                            del data_need_save[part][dialogId]
        return data_need_save

    # 检查是否有任何改动
    def __no_changes_were_made(self) -> bool:
        if os.path.exists((dialog_file_location_t := self.get_dialog_file_location())):
            return Config.load(dialog_file_location_t, "dialogs") == self.__slipt_the_stuff_need_save()
        else:
            return False

    # 更新场景
    def _update_scene(self, theNextDialogId: Union[str, int]) -> None:
        if theNextDialogId in self.dialog_content:
            super()._update_scene(theNextDialogId)
        else:
            self.__add_dialog(theNextDialogId)

    # 添加新的对话
    def __add_dialog(self, dialogId: Union[str, int]) -> None:
        self.dialog_content[dialogId] = {
            "background_img": self.dialog_content[self._dialog_id]["background_img"],
            "background_music": self.dialog_content[self._dialog_id]["background_music"],
            "characters_img": [],
            "content": [self.please_enter_content],
            "last_dialog_id": self._dialog_id,
            "narrator": self.please_enter_name,
            "next_dialog_id": None,
        }
        self.dialog_content[self._dialog_id]["next_dialog_id"] = {"target": dialogId, "type": "default"}
        lastId = self.__get_last_id()
        if lastId is not None:
            self.dialog_content[dialogId]["narrator"] = self.dialog_content[lastId]["narrator"]
            self.dialog_content[dialogId]["characters_img"] = deepcopy(self.dialog_content[lastId]["characters_img"])
        # 检测是否自动保存
        if not self.auto_save:
            self._update_scene(dialogId)
        else:
            self.save_progress()

    # 获取上一个对话的ID
    def __get_last_id(self) -> Union[str, int, None]:
        if (
            "last_dialog_id" in self.dialog_content[self._dialog_id]
            and self.dialog_content[self._dialog_id]["last_dialog_id"] is not None
        ):
            return self.dialog_content[self._dialog_id]["last_dialog_id"]
        elif self._dialog_id == "head":
            return None
        else:
            for key, dialog_data in self.dialog_content.items():
                if dialog_data["next_dialog_id"] is not None:
                    if (
                        dialog_data["next_dialog_id"]["type"] == "default"
                        and dialog_data["next_dialog_id"]["target"] == self._dialog_id
                    ):
                        return key
                    elif (
                        dialog_data["next_dialog_id"]["type"] == "changeScene"
                        and dialog_data["next_dialog_id"]["target"] == self._dialog_id
                    ):
                        return key
                    elif dialog_data["next_dialog_id"]["type"] == "option":
                        for optionChoice in dialog_data["next_dialog_id"]["target"]:
                            if optionChoice["id"] == self._dialog_id:
                                return key
            return None

    # 获取下一个对话的ID
    def __get_next_id(self, surface: ImageSurface) -> Union[str, int, None]:
        if (
            "next_dialog_id" in self.dialog_content[self._dialog_id]
            and (theNext := self.dialog_content[self._dialog_id]["next_dialog_id"]) is not None
        ):
            if theNext["type"] == "default" or theNext["type"] == "changeScene":
                return theNext["target"]
            elif theNext["type"] == "option":
                optionBox_y_base = (
                    surface.get_height() * 3 / 4 - (len(theNext["target"])) * 2 * surface.get_width() * 0.03
                ) / 4
                option_button_height = surface.get_width() * 0.05
                screenshot = surface.copy()
                # 等待玩家选择一个选项
                while True:
                    surface.blit(screenshot, (0, 0))
                    for i in range(len(theNext["target"])):
                        button = theNext["target"][i]
                        option_txt = self._dialog_txt_system.FONT.render(button["txt"], Color.WHITE)
                        option_button_width = int(option_txt.get_width() + surface.get_width() * 0.05)
                        option_button_x = int((surface.get_width() - option_button_width) / 2)
                        option_button_y = int((i + 1) * 2 * surface.get_width() * 0.03 + optionBox_y_base)
                        if (
                            0 < Controller.mouse.x - option_button_x < option_button_width
                            and 0 < Controller.mouse.y - option_button_y < option_button_height
                        ):
                            self._option_box_selected_surface.set_size(option_button_width, option_button_height)
                            self._option_box_selected_surface.set_pos(option_button_x, option_button_y)
                            self._option_box_selected_surface.draw(surface)
                            display_in_center(
                                option_txt,
                                self._option_box_selected_surface,
                                self._option_box_selected_surface.x,
                                self._option_box_selected_surface.y,
                                surface,
                            )
                            if Controller.get_event("confirm"):
                                return button["id"]
                        else:
                            self._option_box_surface.set_size(option_button_width, option_button_height)
                            self._option_box_surface.set_pos(option_button_x, option_button_y)
                            self._option_box_surface.draw(surface)
                            display_in_center(
                                option_txt,
                                self._option_box_surface,
                                self._option_box_surface.x,
                                self._option_box_surface.y,
                                surface,
                            )
                    Display.flip()
        return None

    def draw(self, surface: ImageSurface) -> None:
        super().draw(surface)
        # 获取当前dialog数据
        currentDialogContent = self.get_current_dialog_content()
        # 更新对话框数据
        if self._dialog_txt_system.narrator.need_save:
            currentDialogContent["narrator"] = self._dialog_txt_system.narrator.get_text()
        if self._dialog_txt_system.content.need_save:
            currentDialogContent["content"] = self._dialog_txt_system.content.get_text()
        # 初始化数值
        buttonHovered = None
        theNextDialogId = currentDialogContent["next_dialog_id"]
        # 展示按钮
        for button in self.buttonsUI:
            if button == "next" and theNextDialogId is None or button == "next" and len(theNextDialogId) < 2:
                if self.buttonsUI["add"].is_hover():
                    buttonHovered = "add"
                self.buttonsUI["add"].draw(surface)
            elif button != "add":
                if self.buttonsUI[button].is_hover():
                    buttonHovered = button
                self.buttonsUI[button].draw(surface)
        # 展示出当前可供编辑的dialog章节
        self.dialog_key_select.draw(surface)
        # 切换当前正在浏览编辑的dialog部分
        if self.dialog_key_select.get_current_selected_item() != self._part:
            self._part = self.dialog_key_select.get_current_selected_item()
            try:
                self._update_scene(self._dialog_id)
            except Exception:
                self._update_scene("head")
        # 处理输入事件
        leftClick: bool = False
        for event in Controller.events:
            if event.type == MOUSE_BUTTON_DOWN:
                if event.button == 1:
                    if self.UIContainerRightButton.is_hover():
                        self.UIContainerRightButton.switch()
                        self.UIContainerRightButton.flip()
                    # 退出
                    elif buttonHovered == "back":
                        if self.__no_changes_were_made() is True:
                            self.stop()
                            break
                        else:
                            self.__no_save_warning.hidden = False
                    elif buttonHovered == "previous":
                        lastId = self.__get_last_id()
                        if lastId is not None:
                            self._update_scene(lastId)
                        else:
                            EXCEPTION.warn("There is no last dialog id.")
                    elif buttonHovered == "delete":
                        lastId = self.__get_last_id()
                        nextId = self.__get_next_id(surface)
                        if lastId is not None:
                            if (
                                self.dialog_content[lastId]["next_dialog_id"]["type"] == "default"
                                or self.dialog_content[lastId]["next_dialog_id"]["type"] == "changeScene"
                            ):
                                self.dialog_content[lastId]["next_dialog_id"]["target"] = nextId
                            elif self.dialog_content[lastId]["next_dialog_id"]["type"] == "option":
                                for optionChoice in self.dialog_content[lastId]["next_dialog_id"]["target"]:
                                    if optionChoice["id"] == self._dialog_id:
                                        optionChoice["id"] = nextId
                                        break
                            else:
                                # 如果当前next_dialog_id的类型不支持的话，报错
                                EXCEPTION.fatal(
                                    "Cannot recognize next_dialog_id type: {}, please fix it".format(
                                        self.dialog_content[lastId]["next_dialog_id"]["type"]
                                    )
                                )
                            # 修改下一个对白配置文件中的"last_dialog_id"的参数
                            if nextId is not None:
                                if (
                                    "last_dialog_id" in self.dialog_content[nextId]
                                    and self.dialog_content[nextId]["last_dialog_id"] is not None
                                ):
                                    self.dialog_content[nextId]["last_dialog_id"] = lastId
                            else:
                                self.dialog_content[lastId]["next_dialog_id"] = None
                            needDeleteId = self._dialog_id
                            self._update_scene(lastId)
                            del self.dialog_content[needDeleteId]
                        else:
                            EXCEPTION.warn("There is no last dialog id.")
                    elif buttonHovered == "next":
                        nextId = self.__get_next_id(surface)
                        if nextId is not None:
                            self._update_scene(nextId)
                        else:
                            EXCEPTION.warn("There is no next dialog id.")
                    elif buttonHovered == "add":
                        nextId = 1
                        while nextId in self.dialog_content:
                            nextId += 1
                        self.__add_dialog(nextId)
                    elif buttonHovered == "save":
                        self.save_progress()
                    elif buttonHovered == "reload":
                        self._load_content()
                    else:
                        leftClick = True
                # 鼠标右键
                elif event.button == 3:
                    # 移除角色立绘
                    if self._npc_manager.character_get_click is not None:
                        currentDialogContent["characters_img"].remove(self._npc_manager.character_get_click)
                        self._npc_manager.update(currentDialogContent["characters_img"])
                        self._npc_manager.character_get_click = None
        # 显示移除角色的提示
        if self._npc_manager.character_get_click is not None:
            surface.blit(self.removeNpcButton, Controller.mouse.pos)
        # 画上右侧菜单的按钮
        self.UIContainerRightButton.draw(surface)
        # 画上右侧菜单
        if self.UIContainerRightButton.right < Display.get_width():
            surface.blit(self.UIContainerRightImage, (self.UIContainerRightButton.right, 0))
            self.UIContainerRight_bg.display(surface, (self.UIContainerRightButton.right, 0))
            self.UIContainerRight_npc.display(surface, (self.UIContainerRightButton.right, 0))
            # self.UIContainerRight_bg.draw_outline(surface,(self.UIContainerRightButton.right,0))
            # self.UIContainerRight_npc.draw_outline(surface,(self.UIContainerRightButton.right,0))
            # 检测按钮
            if is_hover(self.button_select_background, off_set_x=self.UIContainerRightButton.right) and leftClick is True:
                self.UIContainerRight_bg.hidden = False
                self.UIContainerRight_npc.hidden = True
                leftClick = False
            if is_hover(self.button_select_npc, off_set_x=self.UIContainerRightButton.right) and leftClick is True:
                self.UIContainerRight_bg.hidden = True
                self.UIContainerRight_npc.hidden = False
                leftClick = False
            # 画出按钮
            self.button_select_background.display(surface, (self.UIContainerRightButton.right, 0))
            self.button_select_npc.display(surface, (self.UIContainerRightButton.right, 0))
            # 检测是否有物品被选中需要更新
            if leftClick is True:
                if not self.UIContainerRight_bg.hidden:
                    imgName = self.UIContainerRight_bg.item_being_hovered
                    if imgName is not None:
                        if imgName != "current_select":
                            currentDialogContent["background_img"] = imgName
                            self._update_background_image(imgName)
                        else:
                            currentDialogContent["background_img"] = None
                            self._update_background_image(None)
                elif not self.UIContainerRight_npc.hidden:
                    imgName = self.UIContainerRight_npc.item_being_hovered
                    if imgName is not None:
                        if currentDialogContent["characters_img"] is None:
                            currentDialogContent["characters_img"] = []
                        if len(currentDialogContent["characters_img"]) < 2:
                            currentDialogContent["characters_img"].append(imgName)
                            self._npc_manager.update(currentDialogContent["characters_img"])

        # 未保存离开时的警告
        self.__no_save_warning.draw(surface)
        if leftClick is True and self.__no_save_warning.item_being_hovered != "":
            # 保存并离开
            if self.__no_save_warning.item_being_hovered == "save":
                self.save_progress()
                self.stop()
            # 取消
            elif self.__no_save_warning.item_being_hovered == "cancel":
                self.__no_save_warning.hidden = True
            # 不保存并离开
            elif self.__no_save_warning.item_being_hovered == "dont_save":
                self.stop()
