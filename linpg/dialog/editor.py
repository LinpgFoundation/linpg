from .dialog import *

# 对话制作器
class DialogEditor(AbstractDialogSystem):
    def __init__(self):
        super().__init__()
        # 存储视觉小说默认数据的参数
        self._dialog_data_default: dict = {}
        # 是否是父类
        self._is_default_dialog: bool = True
        # 默认内容
        self.please_enter_content: str = ""
        # 默认叙述者名
        self.please_enter_name: str = ""
        # 默认不播放音乐
        # self._is_muted = True

    # 加载数据
    def load(self, chapterType: str, chapterId: int, part: str, projectName: str = None) -> None:
        self._initialize(chapterType, chapterId, part, projectName)
        self.folder_for_save_file, self.name_for_save_file = os.path.split(self.get_dialog_file_location())
        # 加载对话框系统
        self._dialog_txt_system.dev_mode()
        # 将npc立绘系统设置为开发者模式
        self._npc_manager.dev_mode = True
        # 加载容器
        container_width = int(Display.get_width() * 0.2)
        self.UIContainerRightImage = IMG.load("<!ui>container.png", (container_width, Display.get_height()))
        # 右侧容器尺寸
        RightContainerRect: Rect = Rect(
            int(container_width * 0.075),
            int(Display.get_height() * 0.1),
            int(container_width * 0.85),
            int(Display.get_height() * 0.85),
        )
        # 背景图片编辑模块
        self.UIContainerRight_bg = SurfaceContainerWithScrollbar(
            None, RightContainerRect.x, RightContainerRect.y, RightContainerRect.width, RightContainerRect.height, "vertical"
        )
        self.UIContainerRight_bg.set_scroll_bar_pos("right")
        # 加载背景图片
        self.background_deselect = IMG.load("<!ui>deselect.png")
        self.UIContainerRight_bg.set("current_select", None)
        # 加载静态背景图片
        for imgPath in glob(os.path.join(self._background_image_folder_path, "*")):
            self.UIContainerRight_bg.set(os.path.basename(imgPath), IMG.load(imgPath, (container_width * 0.8, None)))
        # 加载动态背景图片
        if os.path.exists(ASSET.PATH_DICT["movie"]):
            for imgPath in glob(os.path.join(ASSET.PATH_DICT["movie"], "*")):
                self.UIContainerRight_bg.set(
                    os.path.basename(imgPath), IMG.resize(get_preview_of_video(imgPath), (container_width * 0.8, None))
                )
        # 加载透明图片
        self.UIContainerRight_bg.set(
            "<transparent>", get_texture_missing_surface((container_width * 0.8, container_width * 0.45))
        )
        self.UIContainerRight_bg.distance_between_item = int(Display.get_height() * 0.02)
        self.__current_select_bg_name = None
        self.__current_select_bg_copy = None
        # npc立绘编辑模块
        self.UIContainerRight_npc = SurfaceContainerWithScrollbar(
            None, RightContainerRect.x, RightContainerRect.y, RightContainerRect.width, RightContainerRect.height, "vertical"
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
            "<!ui>container_button.png",
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
        CONFIG = Lang.get_texts("DialogCreator")
        button_y: int = int(Display.get_height() * 0.03)
        font_size: int = int(button_width / 3)
        # 控制容器转换的按钮
        self.button_select_background = load_button_with_text_in_center(
            "<!ui>button.png", CONFIG["background"], "black", font_size, (0, button_y * 2), 150
        )
        self.button_select_npc = load_button_with_text_in_center(
            "<!ui>button.png", CONFIG["npc"], "black", font_size, (0, button_y * 2), 150
        )
        panding: int = int(
            (container_width - self.button_select_background.get_width() - self.button_select_npc.get_width()) / 3
        )
        self.button_select_background.set_left(panding)
        self.button_select_npc.set_left(self.button_select_background.get_right() + panding)
        button_size: tuple = (button_width, button_width)
        # 页面右上方的一排按钮
        custom_values: dict = {
            "button_size": button_width,
            "button_y": button_y,
            "mute_button_x": int(button_width * 8.5),
            "save_button_x": int(button_width * 7.25),
            "reload_button_x": int(button_width * 6),
            "add_and_next_button_x": int(button_width * 4.75),
            "previous_button_x": int(button_width * 3.5),
            "delete_button_x": int(button_width * 2.25),
            "back_button_x": button_width,
        }
        self.__buttons_ui_container = UI.generate("dialog_editor_buttons", custom_values)
        self.please_enter_content = CONFIG["please_enter_content"]
        self.please_enter_name = CONFIG["please_enter_name"]
        # 背景音乐
        self.dialog_bgm_select = DropDownSingleChoiceList(None, button_width * 11, button_y + font_size * 3, font_size)
        self.dialog_bgm_select.set("null", Lang.get_text("DialogCreator", "no_bgm"))
        for file_name in os.listdir(ASSET.PATH_DICT["music"]):
            self.dialog_bgm_select.set(file_name, file_name)
        # 从配置文件中加载数据
        self._load_content()
        # 移除按钮
        self.removeNpcButton = self._dialog_txt_system.FONT.render(CONFIG["remove_npc"], Color.BLACK)
        surfaceTmp = new_surface((self.removeNpcButton.get_width() * 1.2, self.removeNpcButton.get_height() * 1.2)).convert()
        surfaceTmp.fill(Color.WHITE)
        surfaceTmp.blit(self.removeNpcButton, (self.removeNpcButton.get_width() * 0.1, 0))
        self.removeNpcButton = surfaceTmp
        # 未保存离开时的警告
        self.__no_save_warning = UI.generate("leave_without_saving_warning")
        # 切换准备编辑的dialog部分
        self.dialog_key_select = DropDownSingleChoiceList(None, button_width * 11, button_y + font_size, font_size)
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
        if os.path.exists(path := self.get_dialog_file_location()):
            if "dialogs" in (data_t := Config.load(path)):
                try:
                    self._dialog_data = dict(data_t["dialogs"])
                except Exception:
                    EXCEPTION.warn("Cannot load dialogs due to invalid data type.")
                    self._dialog_data = {}
            else:
                self._dialog_data = {}
        else:
            self._dialog_data = {}
        # 如果不是默认主语言
        if (default_lang_of_dialog := self.get_default_lang()) != Setting.language:
            self._is_default_dialog = False
            # 读取原始数据
            self._dialog_data_default = dict(Config.load(self.get_dialog_file_location(default_lang_of_dialog), "dialogs"))
            # 如果当前dialogs是空的，则完全使用默认语言的数据
            if len(self._dialog_data) <= 0:
                self._dialog_data = deepcopy(self._dialog_data_default)
            # 如果当前dialogs不为空的，则填入未被填入的数据
            else:
                dialog_data_t = deepcopy(self._dialog_data_default)
                for part in self._dialog_data:
                    for key, value in self._dialog_data[part].items():
                        dialog_data_t[part][key].update(value)
                self._dialog_data = dialog_data_t
        # 如果是默认主语言，则不进行任何额外操作
        else:
            self._is_default_dialog = True
            self._dialog_data_default.clear()
        # 则尝试加载后仍然出现内容为空的情况
        if len(self._dialog_data) <= 0:
            self._part = "example_dialog"
            self._dialog_data[self._part] = {}
        # 更新场景
        self._update_scene(self._dialog_id)

    # 分离需要保存的数据
    def __slipt_the_stuff_need_save(self) -> dict:
        self._current_dialog_content["narrator"] = self._dialog_txt_system.narrator.get_text()
        self._current_dialog_content["content"] = self._dialog_txt_system.content.get_text()
        data_need_save: dict = deepcopy(self._dialog_data)
        if not self._is_default_dialog:
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

    # 更新UI
    def __update_ui(self) -> None:
        # 更新背景音乐选项菜单
        if (file_name := self._current_dialog_content["background_music"]) is not None:
            self.dialog_bgm_select.set_current_selected_item(file_name)
        else:
            self.dialog_bgm_select.set_current_selected_item("null")
        # 更新按钮
        if self.does_current_dialog_have_next_dialog() is True:
            self.__buttons_ui_container.get("add").hidden = True
            self.__buttons_ui_container.get("next").hidden = False
        else:
            self.__buttons_ui_container.get("add").hidden = False
            self.__buttons_ui_container.get("next").hidden = True

    # 更新场景
    def _update_scene(self, dialog_id: strint) -> None:
        # 确保当前版块有对话数据。如果当前版块为空，则加载默认模板
        if len(self.dialog_content) <= 0:
            self.dialog_content.update(Config.load_internal("template.json", "dialog_example"))
            for key in self.dialog_content:
                self.dialog_content[key]["content"].append(self.please_enter_content)
                self.dialog_content[key]["narrator"] = self.please_enter_name
            self._is_default_dialog = True
            self._dialog_data_default.clear()
        # 如果id存在，则加载对应数据
        if dialog_id in self.dialog_content:
            super()._update_scene(dialog_id)
            self.__update_ui()
        # 如果id不存在，则新增一个
        else:
            self.__add_dialog(dialog_id)

    # 添加新的对话
    def __add_dialog(self, dialogId: strint) -> None:
        self.dialog_content[dialogId] = {
            "background_img": self._current_dialog_content["background_img"],
            "background_music": self._current_dialog_content["background_music"],
            "characters_img": [],
            "content": [self.please_enter_content],
            "last_dialog_id": self._dialog_id,
            "narrator": self.please_enter_name,
            "next_dialog_id": None,
        }
        self._current_dialog_content["next_dialog_id"] = {"target": dialogId, "type": "default"}
        lastId = self.__get_last_id()
        if lastId is not None:
            self.dialog_content[dialogId]["narrator"] = self.dialog_content[lastId]["narrator"]
            self.dialog_content[dialogId]["characters_img"] = deepcopy(self.dialog_content[lastId]["characters_img"])
        # 检测是否自动保存
        if self.auto_save:
            self.save_progress()
        # 更新数据
        super()._update_scene(dialogId)
        self.__update_ui()

    # 获取上一个对话的ID
    def __get_last_id(self) -> strint:
        if "last_dialog_id" in self._current_dialog_content and self._current_dialog_content["last_dialog_id"] is not None:
            return self._current_dialog_content["last_dialog_id"]
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
    def __get_next_id(self, surface: ImageSurface) -> strint:
        if self.does_current_dialog_have_next_dialog() is True:
            theNext = self._current_dialog_content["next_dialog_id"]
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
        # 更新对话框数据
        if self._dialog_txt_system.narrator.need_save:
            self._current_dialog_content["narrator"] = self._dialog_txt_system.narrator.get_text()
        if self._dialog_txt_system.content.need_save:
            self._current_dialog_content["content"] = self._dialog_txt_system.content.get_text()
        # 展示按钮
        self.__buttons_ui_container.draw(surface)
        # 展示出当前可供使用的背景音乐
        self.dialog_bgm_select.draw(surface)
        if (
            current_bgm := self._current_dialog_content["background_music"]
        ) != self.dialog_bgm_select.get_current_selected_item():
            if self.dialog_bgm_select.get_current_selected_item() == "null" and current_bgm is None:
                pass
            else:
                if self.dialog_bgm_select.get_current_selected_item() == "null" and current_bgm is not None:
                    self._current_dialog_content["background_music"] = None
                else:
                    self._current_dialog_content["background_music"] = self.dialog_bgm_select.get(
                        self.dialog_bgm_select.get_current_selected_item()
                    )
                self._update_scene(self._dialog_id)
        # 展示出当前可供编辑的dialog部分
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
                    elif self.__buttons_ui_container.item_being_hovered == "back":
                        if self.__no_changes_were_made() is True:
                            self.stop()
                            break
                        else:
                            self.__no_save_warning.hidden = False
                    elif self.__buttons_ui_container.item_being_hovered == "previous":
                        lastId = self.__get_last_id()
                        if lastId is not None:
                            self._update_scene(lastId)
                        else:
                            EXCEPTION.inform("There is no last dialog id.")
                    elif self.__buttons_ui_container.item_being_hovered == "delete":
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
                            EXCEPTION.inform("There is no last dialog id.")
                    elif self.__buttons_ui_container.item_being_hovered == "next":
                        if (nextId := self.__get_next_id(surface)) is not None:
                            self._update_scene(nextId)
                        else:
                            EXCEPTION.inform("There is no next dialog id.")
                    elif self.__buttons_ui_container.item_being_hovered == "add":
                        nextId = 1
                        while nextId in self.dialog_content:
                            nextId += 1
                        self.__add_dialog(nextId)
                    elif self.__buttons_ui_container.item_being_hovered == "save":
                        self.save_progress()
                    elif self.__buttons_ui_container.item_being_hovered == "reload":
                        self._load_content()
                    elif self.__buttons_ui_container.item_being_hovered == "mute":
                        self._is_muted = not self._is_muted
                        if self._is_muted is True:
                            self.stop_bgm()
                    else:
                        leftClick = True
                # 鼠标右键
                elif event.button == 3:
                    # 移除角色立绘
                    if self._npc_manager.character_get_click is not None:
                        self._current_dialog_content["characters_img"].remove(self._npc_manager.character_get_click)
                        self._npc_manager.update(self._current_dialog_content["characters_img"])
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
                            self._current_dialog_content["background_img"] = imgName
                            self._update_background_image(imgName)
                        else:
                            self._current_dialog_content["background_img"] = None
                            self._update_background_image(None)
                elif not self.UIContainerRight_npc.hidden:
                    imgName = self.UIContainerRight_npc.item_being_hovered
                    if imgName is not None:
                        if self._current_dialog_content["characters_img"] is None:
                            self._current_dialog_content["characters_img"] = []
                        if len(self._current_dialog_content["characters_img"]) < 2:
                            self._current_dialog_content["characters_img"].append(imgName)
                            self._npc_manager.update(self._current_dialog_content["characters_img"])

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
