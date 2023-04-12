from .dialog import *


# 对话制作器
class DialogEditor(AbstractVisualNovelSystem):
    # deselect选中的背景
    __BACKGROUND_DESELECT_IMAGE: Final[StaticImage] = StaticImage.new_place_holder()
    __IS_BACKGROUND_DESELECT_IMAGE_INIT: bool = False

    def __init__(self) -> None:
        super().__init__()
        # 导航窗口
        self.__dialog_navigation_window: DialogNavigationWindow = DialogNavigationWindow(
            Display.get_width() // 10, Display.get_height() // 5, Display.get_width() // 10, Display.get_height() // 10
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
        # 背景音乐选择 DropDown ui
        self.__dialog_bgm_select: DropDownList = DropDownList(None, 0, 0, 1)
        # 背景图片编辑模块
        self.__UIContainerRight_bg: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(None, 0, 0, 0, 0, Axis.VERTICAL)
        # npc立绘编辑模块
        self.__UIContainerRight_npc: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(None, 0, 0, 0, 0, Axis.VERTICAL)
        # 控制容器转换的按钮
        self.__button_select_background: Button = Button.load("<&ui>button.png", (0, 0), (0, 0), 150)
        self.__button_select_npc: Button = Button.load("<&ui>button.png", (0, 0), (0, 0), 150)
        # 未保存数据时警告的窗口
        self.__no_save_warning: GameObjectsDictContainer = UI.generate_container("leave_without_saving_warning")
        # 当前选择的背景的名称
        self.__current_select_bg_name: Optional[str] = None
        # 当前选择的背景的复制品
        self.__current_select_bg_copy: Optional[ImageSurface] = None
        # 用于选择小说脚本的key的下拉菜单
        self.__dialog_section_selection: DropDownList = DropDownList(None, 0, 0, 1)
        # 检测并初始化deselect选中的背景
        if not self.__IS_BACKGROUND_DESELECT_IMAGE_INIT:
            self.__BACKGROUND_DESELECT_IMAGE.update_image("<&ui>deselect.png")
        # 默认不播放音乐
        # self._is_muted = True

    # 获取对话框模块（按照父类要求实现）
    def _get_dialog_box(self) -> EditableDialogBox:
        return self.__dialog_txt_system

    # 加载数据
    def new(self, chapterType: str, chapterId: int, section: str, projectName: Optional[str] = None, dialogId: str = "head") -> None:
        # 加载容器
        container_width: int = Display.get_width() // 5
        self.__UIContainerRightImage = Images.load("<&ui>container.png", (container_width, Display.get_height()))
        # 右侧容器尺寸
        RightContainerRect: Rectangle = Rectangle(
            container_width * 3 // 40, Display.get_height() // 10, container_width * 17 // 20, Display.get_height() * 17 // 20
        )
        # 重置背景图片编辑模块
        self.__UIContainerRight_bg.clear()
        self.__UIContainerRight_bg.move_to(RightContainerRect.get_pos())
        self.__UIContainerRight_bg.set_size(RightContainerRect.width, RightContainerRect.height)
        self.__UIContainerRight_bg.set_scroll_bar_pos("right")
        # 加载背景图片
        self.__UIContainerRight_bg.set("current_select", None)
        # 加载静态背景图片
        for imgPath in glob(Specification.get_directory("background_image", "*")):
            self.__UIContainerRight_bg.set(os.path.basename(imgPath), Images.load(imgPath, (container_width * 4 // 5, None)))
        # 加载动态背景图片
        if os.path.exists(Specification.get_directory("movie")):
            for imgPath in glob(Specification.get_directory("movie", "*")):
                self.__UIContainerRight_bg.set(os.path.basename(imgPath), Images.resize(Videos.get_thumbnail(imgPath), (container_width * 4 // 5, None)))
        self.__UIContainerRight_bg.distance_between_item = Display.get_height() // 50
        self.__current_select_bg_name = None
        self.__current_select_bg_copy = None
        # 重置npc立绘编辑模块
        self.__UIContainerRight_npc.clear()
        self.__UIContainerRight_npc.move_to(RightContainerRect.get_pos())
        self.__UIContainerRight_npc.set_size(RightContainerRect.width, RightContainerRect.height)
        self.__UIContainerRight_npc.set_scroll_bar_pos("right")
        # 加载npc立绘
        for imgPath in glob(Specification.get_directory("character_image", "*")):
            self.__UIContainerRight_npc.set(os.path.basename(imgPath), Images.load(imgPath, (container_width * 4 // 5, None)))
        self.__UIContainerRight_npc.set_visible(False)
        self.__UIContainerRight_npc.distance_between_item = 0
        # 容器按钮
        button_width: int = Display.get_width() // 25
        self.__UIContainerRightButton = MovableStaticImage(
            "<&ui>container_button.png",
            Display.get_width() - button_width,
            Display.get_height() * 2 // 5,
            Display.get_width() - button_width - container_width,
            Display.get_height() * 2 // 5,
            container_width // 10,
            0,
            button_width,
            Display.get_height() // 5,
        )
        self.__UIContainerRightButton.rotate(90)
        # UI按钮
        CONFIG = Lang.get_texts("Editor")
        button_y: int = Display.get_height() * 3 // 100
        font_size: int = button_width // 3
        # 重置控制容器转换的按钮
        self.__button_select_background.set_pos(0, button_y * 3 // 2)
        self.__button_select_background.set_text(ButtonComponent.text(str(CONFIG["background"]), font_size * 2 / 3, alpha_when_not_hover=150))
        self.__button_select_background.set_auto_resize(True)
        self.__button_select_npc.set_pos(0, button_y * 3 // 2)
        self.__button_select_npc.set_text(ButtonComponent.text(str(CONFIG["npc"]), font_size * 2 // 3, alpha_when_not_hover=150))
        self.__button_select_npc.set_auto_resize(True)
        padding: int = (container_width - self.__button_select_background.get_width() - self.__button_select_npc.get_width()) // 3
        self.__button_select_background.set_left(padding)
        self.__button_select_npc.set_left(self.__button_select_background.get_right() + padding)
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
        # 更新可选择的背景音乐
        self.__dialog_bgm_select.clear()
        self.__dialog_bgm_select.set_pos(button_width * 11, button_y + font_size * 3)
        self.__dialog_bgm_select.update_font_size(font_size)
        self.__dialog_bgm_select.set("null", Lang.get_text("Editor", "no_bgm"))
        for file_name in os.listdir(Specification.get_directory("music")):
            self.__dialog_bgm_select.set(file_name, file_name)
        # 移除按钮
        self.__remove_npc_button = ArtisticFont.render_description_box(CONFIG["remove_npc"], Colors.BLACK, self._FONT_SIZE, self._FONT_SIZE // 5, Colors.WHITE)
        # 初始化用于选择小说脚本的key的下拉菜单
        self.__dialog_section_selection.clear()
        self.__dialog_section_selection.set_pos(button_width * 11, button_y + font_size)
        self.__dialog_section_selection.update_font_size(font_size)

        # 初始化数据
        super().new(chapterType, chapterId, section, projectName, dialogId)

        # 将脚本的不同部分的key载入到ui中
        for key in self._content.get():
            self.__dialog_section_selection.set(key, key)
        self.__dialog_section_selection.set_selected_item(self._content.get_section())

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        original_data: dict = Config.try_load_file_if_exists(self.get_data_file_path())
        original_data["dialogs"] = self.__split_the_stuff_need_save()
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
            current_select_bg: ImageSurface = self.__UIContainerRight_bg.get("current_select")
            self.__current_select_bg_copy = current_select_bg.copy()
            self.__BACKGROUND_DESELECT_IMAGE.set_size(current_select_bg.get_width(), current_select_bg.get_height())
            self.__BACKGROUND_DESELECT_IMAGE.draw(current_select_bg)
        else:
            if self.__current_select_bg_name is not None:
                self.__UIContainerRight_bg.set(self.__current_select_bg_name, self.__current_select_bg_copy)
            self.__UIContainerRight_bg.set("current_select", None)
            self.__current_select_bg_name = None
            self.__current_select_bg_copy = None

    # 读取章节信息
    def _load_content(self) -> None:
        # 将npc立绘系统设置为开发者模式
        VisualNovelCharacterImageManager.dev_mode = True
        # 加载内容数据
        self._content.clear()
        if os.path.exists(path := self.get_data_file_path()) and "dialogs" in (data_t := Config.load_file(path)):
            _dialogs: Optional[dict] = data_t.get("dialogs")
            if _dialogs is not None:
                self._content.update(_dialogs)
            else:
                EXCEPTION.warn("Cannot load dialogs due to invalid data type.")
        # 如果不是默认主语言
        if (default_lang_of_dialog := self.get_default_lang()) != Setting.get_language():
            self._is_default_dialog = False
            # 读取原始数据
            self._dialog_data_default = dict(Config.load(self.get_dialog_file_location(default_lang_of_dialog), "dialogs"))
            # 如果当前dialogs是空的，则完全使用默认语言的数据
            if self._content.is_empty():
                self._content.update(copy.deepcopy(self._dialog_data_default))
            # 如果当前dialogs不为空的，则填入未被填入的数据
            else:
                dialog_data_t = copy.deepcopy(self._dialog_data_default)
                for section, value in self._content.get().items():
                    for node_id, Node in value.items():
                        if node_id not in dialog_data_t[section]:
                            dialog_data_t[section][node_id] = Node
                        else:
                            dialog_data_t[section][node_id].update(Node)
                self._content.clear()
                self._content.update(dialog_data_t)
        # 如果是默认主语言，则不进行任何额外操作
        else:
            self._is_default_dialog = True
            self._dialog_data_default.clear()
        # 则尝试加载后仍然出现内容为空的情况
        if self._content.is_empty():
            self._content.set_section("example_dialog")
            self._content.set_section_content({})
        # 检测是否有非str的key name
        for section in self._content.get():
            if isinstance(section, str):
                if self.__if_try_to_fix_issues is True:
                    # 如果有，则尝试转换
                    while True:
                        index: int = 0
                        old_key: Optional[str] = None
                        key: str = ""
                        for key, value in self._content.get_section_content(section).items():
                            if value["next_dialog_id"] is not None and "target" in value["next_dialog_id"]:
                                if isinstance(value["next_dialog_id"]["target"], list):
                                    for index in range(len(value["next_dialog_id"]["target"])):
                                        if not isinstance(value["next_dialog_id"]["target"][index]["id"], str):
                                            old_key = copy.deepcopy(value["next_dialog_id"]["target"][index]["id"])
                                            break
                                    if old_key is not None:
                                        break
                                elif not isinstance(value["next_dialog_id"]["target"], str):
                                    old_key = copy.deepcopy(value["next_dialog_id"]["target"])
                                    break
                        if old_key is not None:
                            new_key: str
                            try:
                                new_key = self.generate_a_new_recommended_key(int(old_key))
                            except Exception:
                                new_key = self.generate_a_new_recommended_key()
                            if not isinstance(self._content.get_dialog(section, key)["next_dialog_id"]["target"], list):
                                self._content.get_dialog(section, key)["next_dialog_id"]["target"] = new_key
                            else:
                                self._content.get_dialog(section, key)["next_dialog_id"]["target"][index]["id"] = new_key
                            self._content.get_dialog(section, new_key).clear()
                            self._content.get_dialog(section, new_key).update(self._content.get_dialog(section, old_key))
                            self._content.remove_dialog(section, old_key)
                        else:
                            break
                else:
                    for key in self._content.get_section_content(section):
                        if not isinstance(key, str):
                            EXCEPTION.fatal(f"Key name has to be a string, not {key}")
            else:
                EXCEPTION.fatal(f"Part name has to be a string, not {section}!")
        # 更新场景
        self._update_scene(self._content.get_id())
        # 如果有不同，应该立即保存
        if not self.__no_changes_were_made():
            self._save()

    # 分离需要保存的数据
    def __split_the_stuff_need_save(self) -> dict[str, dict[str, dict]]:
        self._content.current.narrator = self.__dialog_txt_system.get_narrator()
        self._content.current.contents = self.__dialog_txt_system.get_content()
        self._content.save_current_changes()
        data_need_save: dict[str, dict[str, dict]] = copy.deepcopy(self._content.get())
        if not self._is_default_dialog and self.__compress_when_saving is True:
            # 移除掉相似的内容
            for section in self._dialog_data_default:
                for dialogId, defaultDialogData in self._dialog_data_default[section].items():
                    if dialogId in data_need_save[section]:
                        for dataType in defaultDialogData:
                            if data_need_save[section][dialogId][dataType] == defaultDialogData[dataType]:
                                del data_need_save[section][dialogId][dataType]
                        if len(data_need_save[section][dialogId]) == 0:
                            del data_need_save[section][dialogId]
        return data_need_save

    # 检查是否有任何改动
    def __no_changes_were_made(self) -> bool:
        return (
            os.path.exists((dialog_file_location_t := self.get_data_file_path()))
            and Config.load(dialog_file_location_t, "dialogs") == self.__split_the_stuff_need_save()
        )

    # 更新UI
    def __update_ui(self) -> None:
        # 更新背景音乐选项菜单
        self.__dialog_bgm_select.set_selected_item(self._content.current.background_music if self._content.current.background_music is not None else "null")
        # 更新按钮
        if self.__buttons_ui_container is not None:
            if self._content.current.has_next() is True:
                self.__buttons_ui_container.get("add").set_visible(False)
                self.__buttons_ui_container.get("next").set_visible(True)
            else:
                self.__buttons_ui_container.get("add").set_visible(True)
                self.__buttons_ui_container.get("next").set_visible(False)
        else:
            EXCEPTION.fatal("The ui has not been correctly initialized.")
        # 更新dialog navigation窗口
        self.__dialog_navigation_window.read_all(self._content.get_section_content())
        self.__dialog_navigation_window.update_selected(self._content.get_id())

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 确保当前版块有对话数据。如果当前版块为空，则加载默认模板
        if len(self._content.get_section_content()) <= 0:
            self._content.get_section_content()["head"] = {"contents": [self.__please_enter_content], "narrator": self.__please_enter_name}
            self._is_default_dialog = True
            self._dialog_data_default.clear()
        # 如果id存在，则加载对应数据
        if dialog_id in self._content.get_section_content():
            super()._update_scene(dialog_id)
            self.__update_ui()
        # 如果id不存在，则新增一个
        elif dialog_id != "head":
            self.__add_dialog(str(dialog_id))
        else:
            EXCEPTION.fatal("You have to setup a head.")

    # 添加新的对话
    def __add_dialog(self, dialogId: str) -> None:
        self._content.get_section_content()[dialogId] = {
            "background_image": self._content.current.background_image,
            "background_music": self._content.current.background_music,
            "character_images": [],
            "contents": [self.__please_enter_content],
            "last_dialog_id": self._content.get_id(),
            "narrator": self.__please_enter_name,
            "next_dialog_id": None,
        }
        self._content.current.next["target"] = dialogId
        self._content.current.next["type"] = "default"
        self._content.save_current_changes()
        _lastId: str = self.__get_last_id()
        if _lastId != "<NULL>":
            self._content.get_dialog(_id=dialogId)["narrator"] = self._content.get_dialog(_id=_lastId)["narrator"]
            self._content.get_dialog(_id=dialogId)["character_images"] = copy.deepcopy(self._content.get_dialog(_id=_lastId)["character_images"])
        # 更新数据
        super()._update_scene(dialogId)
        self.__update_ui()

    # 连接2个dialog node
    def __make_connection(self, key1: Optional[str], key2: Optional[str], addNode: bool = False) -> None:
        if key1 is not None:
            seniorNodePointer = self._content.get_dialog(_id=key1)["next_dialog_id"]
            if not addNode:
                match seniorNodePointer["type"]:
                    case "default" | "changeScene":
                        seniorNodePointer["target"] = key2
                    case "option":
                        for optionChoice in seniorNodePointer["target"]:
                            if optionChoice["id"] == self._content.get_id():
                                optionChoice["id"] = key2
                                break
                    case _:
                        # 如果当前next_dialog_id的类型不支持的话，报错
                        EXCEPTION.fatal(f"Cannot recognize next_dialog_id type: {seniorNodePointer['type']}, please fix it")
                # 修改下一个对白配置文件中的"last_dialog_id"的参数
                if key2 is not None:
                    if self._content.get_dialog(_id=key2).get("last_dialog_id") is not None:
                        self._content.get_dialog(_id=key2)["last_dialog_id"] = key1
                else:
                    self._content.get_dialog(_id=key1)["next_dialog_id"] = None
        else:
            EXCEPTION.warn(f'Fail to make a connection between "{key1}" and "{key2}".')

    # 获取上一个对话的ID
    def __get_last_id(self) -> str:
        if self._content.get_id() == "head":
            return "<NULL>"
        elif self._content.last is not None:
            return self._content.last.id
        else:
            for key, dialog_data in self._content.get_section_content().items():
                if dialog_data["next_dialog_id"] is not None:
                    match dialog_data["next_dialog_id"]["type"]:
                        case "default" | "changeScene":
                            if dialog_data["next_dialog_id"]["target"] == self._content.get_id():
                                return str(key)
                        case "option":
                            for optionChoice in dialog_data["next_dialog_id"]["target"]:
                                if optionChoice["id"] == self._content.get_id():
                                    return str(key)
            return "<NULL>"

    # 获取下一个对话的ID
    def __try_get_next_id(self, _surface: ImageSurface) -> str:
        if self._content.current.has_next() is True:
            if not self._content.current.has_multiple_next():
                return str(self._content.current.next["target"])
            elif self._content.current.next.get("type") == "option":
                if len(self._content.current.next["target"]) > 1:
                    self._get_dialog_options_container_ready()
                    screenshot = _surface.copy()
                    while True:
                        _surface.blit(screenshot, (0, 0))
                        # 显示对话选项
                        self._dialog_options_container.display(_surface)
                        # 等待玩家选择一个选项
                        if Controller.get_event("confirm") and self._dialog_options_container.item_being_hovered >= 0:
                            # 获取下一个对话的id
                            return str(self._content.current.next["target"][self._dialog_options_container.item_being_hovered]["id"])
                        elif Controller.get_event("back"):
                            self._dialog_options_container.clear()
                            self._dialog_options_container.set_visible(False)
                            break
                        Display.flip()
                elif len(self._content.current.next["target"]) == 1:
                    return str(self._content.current.next["target"][0]["id"])
        return "<NULL>"

    def draw(self, _surface: ImageSurface) -> None:
        super().draw(_surface)
        # 更新对话框数据
        if self.__dialog_txt_system.any_changed_was_made():
            self._content.current.narrator = self.__dialog_txt_system.get_narrator()
            self._content.current.contents = self.__dialog_txt_system.get_content()
            self._content.save_current_changes()
        # 确保按钮初始化
        if self.__buttons_ui_container is None:
            EXCEPTION.fatal("The ui has not been correctly initialized.")
        # 展示按钮
        self.__buttons_ui_container.draw(_surface)
        # 展示出当前可供使用的背景音乐
        self.__dialog_bgm_select.draw(_surface)
        isCurrentBgmSelectedNull: bool = self.__dialog_bgm_select.get_selected_item() == "null"
        if self._content.current.background_music != self.__dialog_bgm_select.get_selected_item() and not (
            self._content.current.background_music is None and isCurrentBgmSelectedNull is True
        ):
            self._content.current.background_music = (
                None if isCurrentBgmSelectedNull else str(self.__dialog_bgm_select.get(self.__dialog_bgm_select.get_selected_item()))
            )
            self._content.save_current_changes()
            self._update_scene(self._content.get_id())
        # 展示出当前可供编辑的dialog部分
        self.__dialog_section_selection.draw(_surface)
        # 切换当前正在浏览编辑的dialog部分
        if self.__dialog_section_selection.get_selected_item() != self._content.get_section():
            self._content.set_section(self.__dialog_section_selection.get_selected_item())
            self._update_scene(self._content.get_id() if self._content.get_id() in self._content.get_section_content() else "head")
        # 处理输入事件
        confirm_event_tag: bool = False
        lastId: str
        if not self.__dialog_navigation_window.is_hovered():
            if Controller.get_event("confirm"):
                if self.__UIContainerRightButton.is_hovered():
                    self.__UIContainerRightButton.switch()
                    self.__UIContainerRightButton.flip()
                else:
                    match self.__buttons_ui_container.item_being_hovered:
                        # 退出
                        case "back":
                            if self.__no_changes_were_made() is True:
                                self.stop()
                            else:
                                self.__no_save_warning.set_visible(True)
                        # 前一对话
                        case "previous":
                            lastId = self.__get_last_id()
                            if lastId == "<NULL>":
                                EXCEPTION.inform("There is no last dialog id.")
                            else:
                                self._update_scene(lastId)
                        # 删除当前对话
                        case "delete":
                            if self._content.get_id() != "head":
                                lastId = self.__get_last_id()
                                nextId: str = self.__try_get_next_id(_surface)
                                self._content.remove_section()
                                if lastId != "<NULL>":
                                    if nextId != "<NULL>":
                                        self.__make_connection(lastId, nextId)
                                    else:
                                        self._content.get_dialog(_id=lastId)["next_dialog_id"] = None
                                    self._update_scene(lastId)
                                elif nextId != "<NULL>":
                                    self._content.get_dialog(_id=nextId)["last_dialog_id"] = None
                                    self._update_scene(nextId)
                                else:
                                    EXCEPTION.inform("Cannot delete this dialog because there is no valid last and next id; you need to delete it manually.")
                            else:
                                EXCEPTION.inform("Cannot delete head; you need to delete it manually.")
                        # 下一对话
                        case "next":
                            if (nextId := self.__try_get_next_id(_surface)) != "<NULL>":
                                self._update_scene(str(nextId))
                            else:
                                EXCEPTION.inform("There is no next dialog id.")
                        # 新增
                        case "add":
                            self.__add_dialog(self.generate_a_new_recommended_key())
                        # 保存进度
                        case "save":
                            self._save()
                        # 重新加载进度
                        case "reload":
                            self._load_content()
                        # 停止播放背景音乐
                        case "mute":
                            self._is_muted = not self._is_muted
                            if self._is_muted is True:
                                self.stop_bgm()
                        case _:
                            confirm_event_tag = True
            # 移除角色立绘
            elif Controller.get_event("delete") and VisualNovelCharacterImageManager.character_get_click is not None:
                self._content.current.character_images.remove(VisualNovelCharacterImageManager.character_get_click)
                self._content.save_current_changes()
                self._update_scene(self._content.get_id())
        # 显示移除角色的提示
        if VisualNovelCharacterImageManager.character_get_click is not None:
            _surface.blit(self.__remove_npc_button, Controller.mouse.get_pos())
        # 画上右侧菜单的按钮
        self.__UIContainerRightButton.draw(_surface)
        # 画上右侧菜单
        if self.__UIContainerRightButton.right < Display.get_width():
            _surface.blit(self.__UIContainerRightImage, (self.__UIContainerRightButton.right, 0))
            self.__UIContainerRight_bg.display(_surface, (self.__UIContainerRightButton.right, 0))
            self.__UIContainerRight_npc.display(_surface, (self.__UIContainerRightButton.right, 0))
            # self.__UIContainerRight_bg.draw_outline(_surface,(self.__UIContainerRightButton.right,0))
            # self.__UIContainerRight_npc.draw_outline(_surface,(self.__UIContainerRightButton.right,0))
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
            self.__button_select_background.display(_surface, (self.__UIContainerRightButton.right, 0))
            self.__button_select_npc.display(_surface, (self.__UIContainerRightButton.right, 0))
            # 检测是否有物品被选中需要更新
            if confirm_event_tag is True:
                if self.__UIContainerRight_bg.is_visible():
                    if (imgName := self.__UIContainerRight_bg.item_being_hovered) is not None:
                        self._content.current.background_image = imgName if imgName != "current_select" else None
                        self._content.save_current_changes()
                        self._update_background_image(self._content.current.background_image)
                elif self.__UIContainerRight_npc.is_visible() and self.__UIContainerRight_npc.item_being_hovered is not None:
                    self._content.current.character_images.append(self.__UIContainerRight_npc.item_being_hovered)
                    self._content.save_current_changes()
                    VisualNovelCharacterImageManager.update(self._content.current.character_images)

        # 展示dialog navigation窗口
        self.__dialog_navigation_window.present_on(_surface)
        # 如果dialog navigation窗口和当前选中的key不一致，则以dialog navigation窗口为基准进行更新
        if self.__dialog_navigation_window.get_selected_key() != self._content.get_id():
            self._update_scene(self.__dialog_navigation_window.get_selected_key())

        # 未保存离开时的警告
        self.__no_save_warning.draw(_surface)
        if Controller.get_event("confirm"):
            match self.__no_save_warning.item_being_hovered:
                # 保存并离开
                case "save":
                    self._save()
                    self.stop()
                # 取消
                case "cancel":
                    self.__no_save_warning.set_visible(False)
                # 不保存并离开
                case "dont_save":
                    self.stop()
