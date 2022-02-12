from .converter import *

# 对话制作器
class DialogEditor(DialogConverter):
    def __init__(self) -> None:
        super().__init__()
        # 导航窗口
        self.__dialog_navigation_window: DialogNavigationWindow = DialogNavigationWindow(
            0, Display.get_height() / 10, Display.get_width() / 10, Display.get_height() / 10
        )
        # 加载对话框系统
        self.__dialog_txt_system: EditableDialogBox = EditableDialogBox(self._FONT_SIZE)
        # 存储视觉小说默认数据的参数
        self._dialog_data_default: dict = {}
        # 是否是父类
        self._is_default_dialog: bool = True
        # 默认内容
        self.__please_enter_content: str = ""
        # 默认叙述者名
        self.__please_enter_name: str = ""
        # 是否尝试修复错位
        self.__if_try_to_fix_issues: bool = False
        # 压缩模式
        self.__compress_when_saving: bool = True
        # 存放并管理编辑器上方所有按钮的容器
        self.__buttons_ui_container: Optional[GameObjectsDictContainer] = None
        # 未保存数据时警告的窗口
        self.__no_save_warning: GameObjectsDictContainer = UI.generate_container("leave_without_saving_warning")
        # 当前选择的背景的名称
        self.__current_select_bg_name: Optional[str] = None
        # 默认不播放音乐
        # self._is_muted = True

    # 获取对话框模块（按照父类要求实现）
    def _get_dialog_box(self) -> EditableDialogBox:
        return self.__dialog_txt_system

    # 加载数据
    def load(self, chapterType: str, chapterId: int, part: str, projectName: str = None) -> None:
        self._initialize(chapterType, chapterId, part, projectName)
        self.folder_for_save_file, self.name_for_save_file = os.path.split(self.get_dialog_file_location())
        # 将npc立绘系统设置为开发者模式
        self._npc_manager.dev_mode = True
        # 加载容器
        container_width = int(Display.get_width() * 2 / 10)
        self.__UIContainerRightImage = IMG.load("<!ui>container.png", (container_width, Display.get_height()))
        # 右侧容器尺寸
        RightContainerRect: Rectangle = Rectangle(
            int(container_width * 0.075),
            int(Display.get_height() * 0.1),
            int(container_width * 0.85),
            int(Display.get_height() * 0.85),
        )
        # 背景图片编辑模块
        self.__UIContainerRight_bg = SurfaceContainerWithScrollbar(
            None, RightContainerRect.x, RightContainerRect.y, RightContainerRect.width, RightContainerRect.height, "vertical"
        )
        self.__UIContainerRight_bg.set_scroll_bar_pos("right")
        # 加载背景图片
        self.background_deselect = IMG.load("<!ui>deselect.png")
        self.__UIContainerRight_bg.set("current_select", None)
        # 加载静态背景图片
        for imgPath in glob(os.path.join(self._background_image_folder_path, "*")):
            self.__UIContainerRight_bg.set(os.path.basename(imgPath), IMG.load(imgPath, (container_width * 0.8, None)))
        # 加载动态背景图片
        if os.path.exists(ASSET.PATH_DICT["movie"]):
            for imgPath in glob(os.path.join(ASSET.PATH_DICT["movie"], "*")):
                self.__UIContainerRight_bg.set(
                    os.path.basename(imgPath), IMG.resize(get_preview_of_video(imgPath), (container_width * 0.8, None))
                )
        # 加载透明图片
        self.__UIContainerRight_bg.set(
            "<transparent>", get_texture_missing_surface((int(container_width * 0.8), int(container_width * 0.45)))
        )
        self.__UIContainerRight_bg.distance_between_item = int(Display.get_height() * 0.02)
        self.__current_select_bg_name = None
        self.__current_select_bg_copy = None
        # npc立绘编辑模块
        self.__UIContainerRight_npc = SurfaceContainerWithScrollbar(
            None, RightContainerRect.x, RightContainerRect.y, RightContainerRect.width, RightContainerRect.height, "vertical"
        )
        self.__UIContainerRight_npc.set_scroll_bar_pos("right")
        # 加载npc立绘
        for imgPath in glob(os.path.join(self._npc_manager.image_folder_path, "*")):
            self.__UIContainerRight_npc.set(os.path.basename(imgPath), IMG.load(imgPath, (container_width * 0.8, None)))
        self.__UIContainerRight_npc.set_visible(False)
        self.__UIContainerRight_npc.distance_between_item = 0
        # 容器按钮
        button_width: int = int(Display.get_width() * 0.04)
        self.__UIContainerRightButton = MovableImage(
            "<!ui>container_button.png",
            int(Display.get_width() - button_width),
            int(Display.get_height() * 0.4),
            int(Display.get_width() - button_width - container_width),
            int(Display.get_height() * 0.4),
            int(container_width / 10),
            0,
            button_width,
            int(Display.get_height() * 2 / 10),
        )
        self.__UIContainerRightButton.rotate(90)
        # UI按钮
        CONFIG = Lang.get_texts("DialogCreator")
        button_y: int = int(Display.get_height() * 3 / 100)
        font_size: int = int(button_width / 3)
        # 控制容器转换的按钮
        self.__button_select_background = Button.load("<!ui>button.png", (0, int(button_y * 3 / 2)), (0, 0), 150)
        self.__button_select_background.set_text(
            ButtonComponent.text(str(CONFIG["background"]), font_size * 2 / 3, alpha_when_not_hover=150)
        )
        self.__button_select_background.set_auto_resize(True)
        self.__button_select_npc = Button.load("<!ui>button.png", (0, int(button_y * 3 / 2)), (0, 0), 150)
        self.__button_select_npc.set_text(ButtonComponent.text(str(CONFIG["npc"]), font_size * 2 / 3, alpha_when_not_hover=150))
        self.__button_select_npc.set_auto_resize(True)
        panding: int = int(
            (container_width - self.__button_select_background.get_width() - self.__button_select_npc.get_width()) / 3
        )
        self.__button_select_background.set_left(panding)
        self.__button_select_npc.set_left(self.__button_select_background.get_right() + panding)
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
        self.__buttons_ui_container = UI.generate_container("dialog_editor_buttons", custom_values)
        self.__please_enter_content = str(CONFIG["please_enter_content"])
        self.__please_enter_name = str(CONFIG["please_enter_name"])
        # 背景音乐
        self.dialog_bgm_select = DropDownList(None, button_width * 11, button_y + font_size * 3, font_size)
        self.dialog_bgm_select.set("null", Lang.get_text("DialogCreator", "no_bgm"))
        for file_name in os.listdir(ASSET.PATH_DICT["music"]):
            self.dialog_bgm_select.set(file_name, file_name)
        # 从配置文件中加载数据
        self._load_content()
        # 移除按钮
        self.__remove_npc_button = Font.render_description_box(
            CONFIG["remove_npc"], Colors.BLACK, self._FONT_SIZE, int(self._FONT_SIZE / 5), Colors.WHITE
        )
        # 切换准备编辑的dialog部分
        self.dialog_key_select = DropDownList(None, button_width * 11, button_y + font_size, font_size)
        for key in self._dialog_data:
            self.dialog_key_select.set(key, key)
        self.dialog_key_select.set_selected_item(self._part)

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        original_data: dict = (
            Config.load_file(self.get_dialog_file_location()) if os.path.exists(self.get_dialog_file_location()) else {}
        )
        original_data["dialogs"] = self.__slipt_the_stuff_need_save()
        return original_data

    # 更新背景选项栏
    def _update_background_image(self, image_name: Optional[str]) -> None:
        super()._update_background_image(image_name)
        if image_name is not None:
            if self.__current_select_bg_name is not None:
                self.__UIContainerRight_bg.set("current_select", self.__current_select_bg_copy)
                self.__UIContainerRight_bg.swap("current_select", self.__current_select_bg_name)
            self.__UIContainerRight_bg.swap("current_select", image_name)
            self.__current_select_bg_name = image_name
            current_select_bg = self.__UIContainerRight_bg.get("current_select")
            self.__current_select_bg_copy = current_select_bg.copy()
            current_select_bg.blit(IMG.smoothly_resize(self.background_deselect, current_select_bg.get_size()), (0, 0))
        else:
            if self.__current_select_bg_name is not None:
                self.__UIContainerRight_bg.set(self.__current_select_bg_name, self.__current_select_bg_copy)
            self.__UIContainerRight_bg.set("current_select", None)
            self.__current_select_bg_name = None
            self.__current_select_bg_copy = None

    # 读取章节信息
    def _load_content(self) -> None:
        if os.path.exists(path := self.get_dialog_file_location()):
            if "dialogs" in (data_t := Config.load_file(path)):
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
                    for node_id, Node in self._dialog_data[part].items():
                        if node_id not in dialog_data_t[part]:
                            dialog_data_t[part][node_id] = Node
                        else:
                            dialog_data_t[part][node_id].update(Node)
                self._dialog_data = dialog_data_t
        # 如果是默认主语言，则不进行任何额外操作
        else:
            self._is_default_dialog = True
            self._dialog_data_default.clear()
        # 则尝试加载后仍然出现内容为空的情况
        if len(self._dialog_data) <= 0:
            self._part = "example_dialog"
            self._dialog_data[self._part] = {}
        # 检测是否有非str的key name
        for part in self._dialog_data:
            if isinstance(part, str):
                if self.__if_try_to_fix_issues is True:
                    # 如果有，则尝试转换
                    self._check_and_fix_non_str_key(part)
                else:
                    for key in self._dialog_data[part]:
                        if not isinstance(key, str):
                            EXCEPTION.fatal("Key name has to be a string, not {}".format(key))
            else:
                EXCEPTION.fatal("Part name has to be a string, not {}!".format(part))
        # 更新场景
        self._update_scene(self._dialog_id)

    # 分离需要保存的数据
    def __slipt_the_stuff_need_save(self) -> dict:
        self._current_dialog_content["narrator"] = self.__dialog_txt_system.get_narrator()
        self._current_dialog_content["contents"] = self.__dialog_txt_system.get_content()
        data_need_save: dict = deepcopy(self._dialog_data)
        if not self._is_default_dialog and self.__compress_when_saving is True:
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
            return bool(Config.load(dialog_file_location_t, "dialogs") == self.__slipt_the_stuff_need_save())
        else:
            return False

    # 更新UI
    def __update_ui(self) -> None:
        # 更新背景音乐选项菜单
        if (file_name := self._current_dialog_content["background_music"]) is not None:
            self.dialog_bgm_select.set_selected_item(file_name)
        else:
            self.dialog_bgm_select.set_selected_item("null")
        # 更新按钮
        assert self.__buttons_ui_container is not None
        if self.does_current_dialog_have_next_dialog() is True:
            self.__buttons_ui_container.get("add").set_visible(False)
            self.__buttons_ui_container.get("next").set_visible(True)
        else:
            self.__buttons_ui_container.get("add").set_visible(True)
            self.__buttons_ui_container.get("next").set_visible(False)
        # 更新dialog navigation窗口
        self.__dialog_navigation_window.readd_all(self.dialog_content)
        self.__dialog_navigation_window.update_selected(self._dialog_id)

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 确保当前版块有对话数据。如果当前版块为空，则加载默认模板
        if len(self.dialog_content) <= 0:
            self.dialog_content.update(Template.get("dialog_example"))
            for key in self.dialog_content:
                self.dialog_content[key]["contents"].append(self.__please_enter_content)
                self.dialog_content[key]["narrator"] = self.__please_enter_name
            self._is_default_dialog = True
            self._dialog_data_default.clear()
        # 如果id存在，则加载对应数据
        if dialog_id in self.dialog_content:
            super()._update_scene(dialog_id)
            self.__update_ui()
        # 如果id不存在，则新增一个
        elif dialog_id != "head":
            self.__add_dialog(str(dialog_id))
        else:
            EXCEPTION.fatal("You have to setup a head.")

    # 添加新的对话
    def __add_dialog(self, dialogId: str) -> None:
        self.dialog_content[dialogId] = {
            "background_image": self._current_dialog_content["background_image"],
            "background_music": self._current_dialog_content["background_music"],
            "character_images": [],
            "contents": [self.__please_enter_content],
            "last_dialog_id": self._dialog_id,
            "narrator": self.__please_enter_name,
            "next_dialog_id": None,
        }
        self._current_dialog_content["next_dialog_id"] = {"target": dialogId, "type": "default"}
        lastId = self.__get_last_id()
        if lastId != "<!null>":
            self.dialog_content[dialogId]["narrator"] = self.dialog_content[lastId]["narrator"]
            self.dialog_content[dialogId]["character_images"] = deepcopy(self.dialog_content[lastId]["character_images"])
        # 检测是否自动保存
        if self.auto_save:
            self.save_progress()
        # 更新数据
        super()._update_scene(dialogId)
        self.__update_ui()

    # 连接2个dialog node
    def __make_connection(self, key1: Optional[str], key2: Optional[str], addNode: bool = False) -> None:
        if key1 is not None:
            seniorNodePointer = self.dialog_content[key1]["next_dialog_id"]
            if not addNode:
                if seniorNodePointer["type"] == "default" or seniorNodePointer["type"] == "changeScene":
                    seniorNodePointer["target"] = key2
                elif seniorNodePointer["type"] == "option":
                    for optionChoice in seniorNodePointer["target"]:
                        if optionChoice["id"] == self._dialog_id:
                            optionChoice["id"] = key2
                            break
                else:
                    # 如果当前next_dialog_id的类型不支持的话，报错
                    EXCEPTION.fatal("Cannot recognize next_dialog_id type: {}, please fix it".format(seniorNodePointer["type"]))
                # 修改下一个对白配置文件中的"last_dialog_id"的参数
                if key2 is not None:
                    if "last_dialog_id" in self.dialog_content[key2] and self.dialog_content[key2]["last_dialog_id"] is not None:
                        self.dialog_content[key2]["last_dialog_id"] = key1
                else:
                    self.dialog_content[key1]["next_dialog_id"] = None
        else:
            EXCEPTION.warn('Fail to make a connection between "{0}" and "{1}".'.format(key1, key2))

    # 获取上一个对话的ID
    def __get_last_id(self, child_node: str = None) -> str:
        if child_node is None:
            child_node = self._dialog_id
        if "last_dialog_id" in self._current_dialog_content and self._current_dialog_content["last_dialog_id"] is not None:
            return str(self._current_dialog_content["last_dialog_id"])
        elif child_node == "head":
            return "<!null>"
        else:
            for key, dialog_data in self.dialog_content.items():
                if dialog_data["next_dialog_id"] is not None:
                    if (
                        dialog_data["next_dialog_id"]["type"] == "default"
                        or dialog_data["next_dialog_id"]["type"] == "changeScene"
                    ) and dialog_data["next_dialog_id"]["target"] == child_node:
                        return str(key)
                    elif dialog_data["next_dialog_id"]["type"] == "option":
                        for optionChoice in dialog_data["next_dialog_id"]["target"]:
                            if optionChoice["id"] == child_node:
                                return str(key)
            return "<!null>"

    # 获取下一个对话的ID
    def __try_get_next_id(self, surface: ImageSurface) -> str:
        if self.does_current_dialog_have_next_dialog() is True:
            theNext = self._current_dialog_content["next_dialog_id"]
            if theNext["type"] == "default" or theNext["type"] == "changeScene":
                return str(theNext["target"])
            elif theNext["type"] == "option":
                if len(theNext["target"]) > 1:
                    self._get_dialog_options_container_ready()
                    screenshot = surface.copy()
                    while True:
                        surface.blit(screenshot, (0, 0))
                        # 显示对话选项
                        self._dialog_options_container.display(surface)
                        # 等待玩家选择一个选项
                        if Controller.get_event("confirm") and self._dialog_options_container.item_being_hovered >= 0:
                            # 获取下一个对话的id
                            return str(
                                self._current_dialog_content["next_dialog_id"]["target"][
                                    self._dialog_options_container.item_being_hovered
                                ]["id"]
                            )
                        elif Controller.get_event("back"):
                            self._dialog_options_container.clear()
                            self._dialog_options_container.set_visible(False)
                            break
                        Display.flip()
                elif len(theNext["target"]) == 1:
                    return str(self._current_dialog_content["next_dialog_id"]["target"][0]["id"])
        return "<!null>"

    def draw(self, surface: ImageSurface) -> None:
        super().draw(surface)
        # 更新对话框数据
        if self.__dialog_txt_system.any_changed_was_made():
            self._current_dialog_content["narrator"] = self.__dialog_txt_system.get_narrator()
            self._current_dialog_content["contents"] = self.__dialog_txt_system.get_content()
        # 确保按钮初始化
        assert self.__buttons_ui_container is not None
        # 展示按钮
        self.__buttons_ui_container.draw(surface)
        # 展示出当前可供使用的背景音乐
        self.dialog_bgm_select.draw(surface)
        if (current_bgm := self._current_dialog_content["background_music"]) != self.dialog_bgm_select.get_selected_item():
            if self.dialog_bgm_select.get_selected_item() == "null" and current_bgm is None:
                pass
            else:
                if self.dialog_bgm_select.get_selected_item() == "null" and current_bgm is not None:
                    self._current_dialog_content["background_music"] = None
                else:
                    self._current_dialog_content["background_music"] = self.dialog_bgm_select.get(
                        self.dialog_bgm_select.get_selected_item()
                    )
                self._update_scene(self._dialog_id)
        # 展示出当前可供编辑的dialog部分
        self.dialog_key_select.draw(surface)
        # 切换当前正在浏览编辑的dialog部分
        if self.dialog_key_select.get_selected_item() != self._part:
            self._part = self.dialog_key_select.get_selected_item()
            if self._dialog_id in self.dialog_content:
                self._update_scene(self._dialog_id)
            else:
                self._update_scene("head")
        # 处理输入事件
        confirm_event_tag: bool = False
        lastId: str
        if not self.__dialog_navigation_window.is_hovered():
            if Controller.get_event("confirm"):
                if self.__UIContainerRightButton.is_hovered():
                    self.__UIContainerRightButton.switch()
                    self.__UIContainerRightButton.flip()
                # 退出
                elif self.__buttons_ui_container.item_being_hovered == "back":
                    if self.__no_changes_were_made() is True:
                        self.stop()
                    else:
                        self.__no_save_warning.set_visible(True)
                elif self.__buttons_ui_container.item_being_hovered == "previous":
                    lastId = self.__get_last_id()
                    if lastId != "<!null>":
                        self._update_scene(str(lastId))
                    else:
                        EXCEPTION.inform("There is no last dialog id.")
                elif self.__buttons_ui_container.item_being_hovered == "delete":
                    lastId = self.__get_last_id()
                    nextId: str = self.__try_get_next_id(surface)
                    needDeleteId: str = ""
                    if lastId != "<!null>":
                        if nextId != "<!null>":
                            self.__make_connection(lastId, nextId)
                        needDeleteId = self._dialog_id
                        self._update_scene(str(lastId))
                        del self.dialog_content[needDeleteId]
                    elif nextId != "<!null>":
                        needDeleteId = self._dialog_id
                        self._update_scene(str(nextId))
                        del self.dialog_content[needDeleteId]
                    else:
                        EXCEPTION.inform(
                            "Cannot delete this dialog because there is no valid last and next id. You need to delete it manually"
                        )
                elif self.__buttons_ui_container.item_being_hovered == "next":
                    if (nextId := self.__try_get_next_id(surface)) != "<!null>":
                        self._update_scene(str(nextId))
                    else:
                        EXCEPTION.inform("There is no next dialog id.")
                elif self.__buttons_ui_container.item_being_hovered == "add":
                    self.__add_dialog(self.generate_a_new_recommended_key())
                elif self.__buttons_ui_container.item_being_hovered == "save":
                    self.save_progress()
                elif self.__buttons_ui_container.item_being_hovered == "reload":
                    self._load_content()
                elif self.__buttons_ui_container.item_being_hovered == "mute":
                    self._is_muted = not self._is_muted
                    if self._is_muted is True:
                        self.stop_bgm()
                else:
                    confirm_event_tag = True
            # 移除角色立绘
            elif Controller.get_event("delete") and self._npc_manager.character_get_click is not None:
                self._current_dialog_content["character_images"].remove(self._npc_manager.character_get_click)
                self._npc_manager.update(self._current_dialog_content["character_images"])
                self._npc_manager.character_get_click = None
        # 显示移除角色的提示
        if self._npc_manager.character_get_click is not None:
            surface.blit(self.__remove_npc_button, Controller.mouse.pos)
        # 画上右侧菜单的按钮
        self.__UIContainerRightButton.draw(surface)
        # 画上右侧菜单
        if self.__UIContainerRightButton.right < Display.get_width():
            surface.blit(self.__UIContainerRightImage, (self.__UIContainerRightButton.right, 0))
            self.__UIContainerRight_bg.display(surface, (self.__UIContainerRightButton.right, 0))
            self.__UIContainerRight_npc.display(surface, (self.__UIContainerRightButton.right, 0))
            # self.__UIContainerRight_bg.draw_outline(surface,(self.__UIContainerRightButton.right,0))
            # self.__UIContainerRight_npc.draw_outline(surface,(self.__UIContainerRightButton.right,0))
            # 检测按钮
            if self.__button_select_background.is_hovered((self.__UIContainerRightButton.right, 0)) and confirm_event_tag is True:
                self.__UIContainerRight_bg.set_visible(True)
                self.__UIContainerRight_npc.set_visible(False)
                confirm_event_tag = False
            if self.__button_select_npc.is_hovered((self.__UIContainerRightButton.right, 0)) and confirm_event_tag is True:
                self.__UIContainerRight_bg.set_visible(False)
                self.__UIContainerRight_npc.set_visible(True)
                confirm_event_tag = False
            # 画出按钮
            self.__button_select_background.display(surface, (self.__UIContainerRightButton.right, 0))
            self.__button_select_npc.display(surface, (self.__UIContainerRightButton.right, 0))
            # 检测是否有物品被选中需要更新
            if confirm_event_tag is True:
                if self.__UIContainerRight_bg.is_visible():
                    imgName = self.__UIContainerRight_bg.item_being_hovered
                    if imgName is not None:
                        if imgName != "current_select":
                            self._current_dialog_content["background_image"] = imgName
                            self._update_background_image(imgName)
                        else:
                            self._current_dialog_content["background_image"] = None
                            self._update_background_image(None)
                elif self.__UIContainerRight_npc.is_visible():
                    imgName = self.__UIContainerRight_npc.item_being_hovered
                    if imgName is not None:
                        if self._current_dialog_content["character_images"] is None:
                            self._current_dialog_content["character_images"] = []
                        if len(self._current_dialog_content["character_images"]) < 2:  # type: ignore
                            self._current_dialog_content["character_images"].append(imgName)  # type: ignore
                            self._npc_manager.update(self._current_dialog_content["character_images"])  # type: ignore

        # 展示dialog navigation窗口
        self.__dialog_navigation_window.present_on(surface)
        # 如果dialog navigation窗口和当前选中的key不一致，则以dialog navigation窗口为基准进行更新
        if self.__dialog_navigation_window.get_selected_key() != self._dialog_id:
            self._update_scene(self.__dialog_navigation_window.get_selected_key())

        # 未保存离开时的警告
        self.__no_save_warning.draw(surface)
        if Controller.get_event("confirm") and self.__no_save_warning.item_being_hovered != "":
            # 保存并离开
            if self.__no_save_warning.item_being_hovered == "save":
                self.save_progress()
                self.stop()
            # 取消
            elif self.__no_save_warning.item_being_hovered == "cancel":
                self.__no_save_warning.set_visible(False)
            # 不保存并离开
            elif self.__no_save_warning.item_being_hovered == "dont_save":
                self.stop()
