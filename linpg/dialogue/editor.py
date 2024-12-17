from .dialog import *


# 对话制作器
class VisualNovelEditor(AbstractVisualNovelPlayer):
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
        # 存放并管理编辑器上方所有按钮的容器
        self.__buttons_ui_container: GameObjectsDictContainer | None = None
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
        self.__current_select_bg_name: str = ""
        # 当前选择的背景的复制品
        self.__current_select_bg_copy: ImageSurface | None = None
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
    def new(self, chapterType: str, chapterId: int, section: str, projectName: str | None = None, dialogId: str = "head") -> None:
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
        self.__current_select_bg_name = ""
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
        button_y: int = Display.get_height() * 3 // 100
        font_size: int = button_width // 3
        # 重置控制容器转换的按钮
        self.__button_select_background.set_pos(0, button_y * 3 // 2)
        self.__button_select_background.set_text(ButtonComponent.text(Lang.get_text("Editor", "background"), font_size * 2 / 3, alpha_when_not_hover=150))
        self.__button_select_background.set_auto_resize(True)
        self.__button_select_npc.set_pos(0, button_y * 3 // 2)
        self.__button_select_npc.set_text(ButtonComponent.text(Lang.get_text("Editor", "npc"), font_size * 2 // 3, alpha_when_not_hover=150))
        self.__button_select_npc.set_auto_resize(True)
        padding: int = (container_width - self.__button_select_background.get_width() - self.__button_select_npc.get_width()) // 3
        self.__button_select_background.set_left(padding)
        self.__button_select_npc.set_left(self.__button_select_background.get_right() + padding)
        # 页面右上方的一排按钮
        custom_values: dict[str, int] = {
            "button_size": button_width,
            "button_y": button_y,
            "mute_button_x": button_width * 85 // 10,
            "save_button_x": button_width * 725 // 100,
            "reload_button_x": button_width * 6,
            "add_and_next_button_x": button_width * 475 // 100,
            "previous_button_x": button_width * 35 // 10,
            "delete_button_x": button_width * 225 // 100,
            "back_button_x": button_width,
        }
        self.__buttons_ui_container = UI.generate_container("dialog_editor_buttons", custom_values)
        # 更新可选择的背景音乐
        self.__dialog_bgm_select.clear()
        self.__dialog_bgm_select.set_pos(button_width * 11, button_y + font_size * 3)
        self.__dialog_bgm_select.update_font_size(font_size)
        self.__dialog_bgm_select.set("", Lang.get_text("Editor", "no_bgm"))
        for file_name in os.listdir(Specification.get_directory("music")):
            self.__dialog_bgm_select.set(file_name, file_name)
        # 移除按钮
        self.__delete_npc_prompt = ArtisticFont.render_description_box(
            Lang.get_text("Editor", "delete_npc"), Colors.BLACK, self._FONT_SIZE, self._FONT_SIZE // 5, Colors.WHITE
        )
        # 初始化用于选择小说脚本的key的下拉菜单
        self.__dialog_section_selection.clear()
        self.__dialog_section_selection.set_pos(button_width * 11, button_y + font_size)
        self.__dialog_section_selection.update_font_size(font_size)

        # 初始化数据
        super().new(chapterType, chapterId, section, projectName, dialogId)

        # 将脚本的不同部分的key载入到ui中
        for key in self._content.get_sections():
            self.__dialog_section_selection.set(key, key)
        self.__dialog_section_selection.set_selected_item(self._content.get_section())

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        original_data: dict = Config.try_load_file_if_exists(self.get_data_file_path())
        # remove "dialogs" as "dialogs" keyword is deprecated
        if "dialogs" in original_data:
            original_data.pop("dialogs")
        # save data
        original_data["dialogues"] = self.__get_the_stuff_need_save()
        return original_data

    # 更新背景选项栏
    def _update_background_image(self, image_name: str) -> None:
        super()._update_background_image(image_name)
        if len(image_name) > 0:
            if len(self.__current_select_bg_name) > 0:
                self.__UIContainerRight_bg.set("current_select", self.__current_select_bg_copy)
                self.__UIContainerRight_bg.swap("current_select", self.__current_select_bg_name)
            self.__UIContainerRight_bg.swap("current_select", image_name)
            self.__current_select_bg_name = image_name
            current_select_bg: ImageSurface = self.__UIContainerRight_bg.get("current_select")
            self.__current_select_bg_copy = current_select_bg.copy()
            self.__BACKGROUND_DESELECT_IMAGE.set_size(current_select_bg.get_width(), current_select_bg.get_height())
            self.__BACKGROUND_DESELECT_IMAGE.draw(current_select_bg)
        else:
            if len(self.__current_select_bg_name) > 0:
                self.__UIContainerRight_bg.set(self.__current_select_bg_name, self.__current_select_bg_copy)
            self.__UIContainerRight_bg.set("current_select", None)
            self.__current_select_bg_name = ""
            self.__current_select_bg_copy = None

    # 加载默认模板
    def _load_template(self) -> None:
        self._content.set_section("dialog_example")
        self._content.set_current_section_dialogues({"head": self._get_template()})

    # get template
    @staticmethod
    def _get_template() -> pyvns.dialogue_data_t:
        return {"contents": [Lang.get_text("Editor", "please_enter_content")], "narrator": Lang.get_text("Editor", "please_enter_name")}

    # 读取章节信息
    def _load_content(self) -> None:
        # 将npc立绘系统设置为开发者模式
        VisualNovelCharacterImageManager.dev_mode = True
        # 加载内容数据
        self._content.clear()
        dialogs_data: dict = Config.try_load_file_if_exists(self.get_data_file_path())
        if "dialogues" in dialogs_data:
            self._content.update(dialogs_data["dialogues"])
        elif "dialogs" in dialogs_data:
            self._content.update(dialogs_data["dialogs"])
        else:
            # 则尝试加载后仍然出现内容为空的情况
            EXCEPTION.inform("No valid dialog content found.")
            # 则加载默认模板
            self._load_template()
        # 更新场景
        self._update_scene(self._content.get_current_dialogue_id())

    # 分离需要保存的数据
    def __get_the_stuff_need_save(self) -> dict[str, dict[str, dict]]:
        self._content.current.narrator = self.__dialog_txt_system.get_narrator()
        self._content.current.contents = self.__dialog_txt_system.get_content()
        return self._content.to_dict()

    # 更新UI
    def __update_ui(self) -> None:
        # 更新背景音乐选项菜单
        self.__dialog_bgm_select.set_selected_item(self._content.current.background_music)
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
        self.__dialog_navigation_window.read_all(self._content.get_current_section_dialogues())
        self.__dialog_navigation_window.update_selected(self._content.get_current_dialogue_id())

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 确保当前版块有对话数据。如果当前版块为空，则加载默认模板
        if len(self._content.get_current_section_dialogues()) <= 0:
            self._content.set_current_section_dialogues(self._get_template())
        # 如果id存在，则加载对应数据
        if dialog_id in self._content.get_current_section_dialogues():
            super()._update_scene(dialog_id)
            self.__update_ui()
        # 如果id不存在，则新增一个
        elif dialog_id != "head":
            self.__add_dialog(str(dialog_id))
        else:
            EXCEPTION.fatal("You have to setup a head.")

    # 添加新的对话
    def __add_dialog(self, dialogId: str) -> None:
        # update current dialogue id
        self._content.current.set_next("default", dialogId)
        # add new dialogue data to dialogue
        new_dialogue: pyvns.dialogue_data_t = self._content.current.to_dict() | self._get_template()
        new_dialogue["previous"] = self._content.get_current_dialogue_id()
        new_dialogue.pop("next")
        if len(self._content.current.narrator) > 0:
            new_dialogue["narrator"] = self._content.current.narrator
        self._content.set_dialogue(self._content.get_section(), dialogId, new_dialogue)
        # 更新数据
        super()._update_scene(dialogId)
        self.__update_ui()

    # 获取上一个对话的ID
    def __get_last_id(self) -> str:
        if self._content.get_current_dialogue_id() == "head":
            return ""
        elif len(self._content.get_current().previous) > 0:
            return self._content.get_current().previous
        else:
            for key, dialog_tmp in self._content.get_current_section_dialogues().items():
                if dialog_tmp.has_next():
                    if dialog_tmp.next.has_single_target():
                        if dialog_tmp.next.get_target() == self._content.get_current_dialogue_id():
                            return str(key)
                    else:
                        for optionChoice in dialog_tmp.next.get_targets():
                            if optionChoice["id"] == self._content.get_current_dialogue_id():
                                return str(key)
            return ""

    # 生产一个新的推荐id
    def __generate_a_new_recommended_key(self, index: int = 1) -> str:
        while True:
            newId: str = f"~0{index}" if index <= 9 else f"~{index}"
            if newId in self._content.get_current_section_dialogues():
                index += 1
            else:
                return newId

    # 获取下一个对话的ID
    def __try_get_next_id(self, _surface: ImageSurface) -> str:
        if self._content.current.has_next() is True:
            if self._content.current.next.has_single_target():
                return self._content.current.next.get_target()
            # for next with more than one targets
            if len(self._content.current.next.get_targets()) > 1:
                self._get_dialog_options_container_ready()
                screenshot = _surface.copy()
                while True:
                    _surface.blit(screenshot, (0, 0))
                    # 显示对话选项
                    self._dialog_options_container.display(_surface)
                    # 等待玩家选择一个选项
                    if Controller.get_event("confirm") and self._dialog_options_container.item_being_hovered >= 0:
                        # 获取下一个对话的id
                        return str(self._content.current.next.get_targets()[self._dialog_options_container.item_being_hovered]["id"])
                    elif Controller.get_event("back"):
                        self._dialog_options_container.clear()
                        self._dialog_options_container.set_visible(False)
                        break
                    Display.flip()
            elif len(self._content.current.next.get_targets()) == 1:
                return str(self._content.current.next.get_targets()[0]["id"])
        return ""

    def draw(self, _surface: ImageSurface) -> None:
        super().draw(_surface)
        # 更新对话框数据
        if self.__dialog_txt_system.any_changed_was_made():
            self._content.current.narrator = self.__dialog_txt_system.get_narrator()
            self._content.current.contents = self.__dialog_txt_system.get_content()
        # 确保按钮初始化
        if self.__buttons_ui_container is None:
            EXCEPTION.fatal("The ui has not been correctly initialized.")
        # 展示按钮
        self.__buttons_ui_container.draw(_surface)
        # 展示出当前可供使用的背景音乐
        self.__dialog_bgm_select.draw(_surface)
        if self._content.current.background_music != self.__dialog_bgm_select.get_selected_item():
            self._content.current.background_music = self.__dialog_bgm_select.get_selected_item()
            self._update_scene(self._content.get_current_dialogue_id())
        # 展示出当前可供编辑的dialog部分
        self.__dialog_section_selection.draw(_surface)
        # 切换当前正在浏览编辑的dialog部分
        if self.__dialog_section_selection.get_selected_item() != self._content.get_section():
            self._content.set_section(self.__dialog_section_selection.get_selected_item())
            self._update_scene("head")
        # 处理输入事件
        confirm_event_tag: bool = False
        lastId: str
        if not self.__dialog_navigation_window.is_hovered():
            if Controller.get_event("confirm"):
                if self.__UIContainerRightButton.is_hovered():
                    self.__UIContainerRightButton.switch()
                    self.__UIContainerRightButton.flip()
                else:
                    # 退出
                    if self.__buttons_ui_container.item_being_hovered == "back":
                        # if no change were made
                        if Config.try_load_file_if_exists(self.get_data_file_path()).get("dialogues") == self.__get_the_stuff_need_save() is True:
                            self.stop()
                        else:
                            self.__no_save_warning.set_visible(True)
                    # 前一对话
                    elif self.__buttons_ui_container.item_being_hovered == "previous":
                        lastId = self.__get_last_id()
                        if len(lastId) == 0:
                            EXCEPTION.inform("There is no last dialog id.")
                        else:
                            self._update_scene(lastId)
                    # 删除当前对话
                    elif self.__buttons_ui_container.item_being_hovered == "delete":
                        if self._content.get_current_dialogue_id() != "head" or (
                            self._content.current.has_next() and self._content.current.next.has_single_target()
                        ):
                            self._content.remove_current_dialogue()
                            self._update_scene(self._content.get_current_dialogue_id())
                    # 下一对话
                    elif self.__buttons_ui_container.item_being_hovered == "next":
                        if len(nextId := self.__try_get_next_id(_surface)) >= 0:
                            self._update_scene(str(nextId))
                        else:
                            EXCEPTION.inform("There is no next dialog id.")
                    # 新增
                    elif self.__buttons_ui_container.item_being_hovered == "add":
                        self.__add_dialog(self.__generate_a_new_recommended_key())
                    # 保存进度
                    elif self.__buttons_ui_container.item_being_hovered == "save":
                        self._save()
                    # 重新加载进度
                    elif self.__buttons_ui_container.item_being_hovered == "reload":
                        self.update_language()
                    # 停止播放背景音乐
                    elif self.__buttons_ui_container.item_being_hovered == "mute":
                        self._is_muted = not self._is_muted
                        if self._is_muted is True:
                            self.stop_bgm()
                    else:
                        confirm_event_tag = True
            # 移除角色立绘
            elif (Controller.get_event("delete") or Controller.get_event("hard_confirm")) and VisualNovelCharacterImageManager.character_get_click is not None:
                character_images = self._content.current.character_images
                # adding check to avoid removing during fade out stage
                if VisualNovelCharacterImageManager.character_get_click in character_images:
                    character_images.remove(VisualNovelCharacterImageManager.character_get_click)
                self._content.current.character_images = character_images
                self._update_scene(self._content.get_current_dialogue_id())
        # 显示移除角色的提示
        if VisualNovelCharacterImageManager.character_get_click is not None:
            _surface.blit(self.__delete_npc_prompt, Controller.mouse.get_pos())
        # 画上右侧菜单的按钮
        self.__UIContainerRightButton.draw(_surface)
        # 画上右侧菜单
        if self.__UIContainerRightButton.right < Display.get_width():
            _surface.blit(self.__UIContainerRightImage, (self.__UIContainerRightButton.right, 0))
            self.__UIContainerRight_bg.display(_surface, (self.__UIContainerRightButton.right, 0))
            self.__UIContainerRight_npc.display(_surface, (self.__UIContainerRightButton.right, 0))
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
                        self._content.current.background_image = imgName if imgName != "current_select" else ""
                        self._update_background_image(self._content.current.background_image)
                elif self.__UIContainerRight_npc.is_visible() and self.__UIContainerRight_npc.item_being_hovered is not None:
                    character_images = self._content.current.character_images
                    character_images.append(self.__UIContainerRight_npc.item_being_hovered)
                    self._content.current.character_images = character_images
                    VisualNovelCharacterImageManager.update(self._content.current.character_images)

        # 展示dialog navigation窗口
        self.__dialog_navigation_window.present_on(_surface)
        # 如果dialog navigation窗口和当前选中的key不一致，则以dialog navigation窗口为基准进行更新
        if self.__dialog_navigation_window.get_selected_key() != self._content.get_current_dialogue_id():
            self._update_scene(self.__dialog_navigation_window.get_selected_key())

        # 未保存离开时的警告
        self.__no_save_warning.draw(_surface)
        if Controller.get_event("confirm"):
            # 保存并离开
            if self.__no_save_warning.item_being_hovered == "save":
                self._save()
                self.stop()
            # 取消
            elif self.__no_save_warning.item_being_hovered == "cancel":
                self.__no_save_warning.set_visible(False)
            # 不保存并离开
            elif self.__no_save_warning.item_being_hovered == "dont_save":
                self.stop()
