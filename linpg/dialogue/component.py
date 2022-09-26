from ..ui import *


# 对话模块Node
class DialogNode(Button):
    def __init__(self, key_name: str, font_size: int, next_keys: list[str], tag: str = ""):
        self.__key_name: str = key_name
        button_surface = ArtisticFont.render_description_box(self.__key_name, Colors.BLACK, font_size, font_size // 2, Colors.WHITE)
        super().__init__(button_surface, 0, 0, width=button_surface.get_width(), height=button_surface.get_height(), tag=tag)
        self.__next_keys: tuple[str, ...] = tuple(next_keys)
        self.has_been_displayed: bool = False

    # 下一个keys
    @property
    def next_keys(self) -> tuple[str, ...]:
        return self.__next_keys

    # 展示（注意，你无法在此输入off_set，你必须提前设置）
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if offSet != ORIGIN:
            EXCEPTION.fatal("You cannot set off set for DialogNode object!")
        super().display(_surface, offSet)


# 对话key向导窗口
class DialogNavigationWindow(AbstractFrame):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = ""):
        super().__init__(x, y, width, height, tag=tag)
        self.__nodes_map: dict[str, DialogNode] = {}
        self.__current_selected_key: str = "head"
        self.__font_size: int = 10
        self.__most_right: int = 0
        self.__most_top: int = 0
        self.__most_bottom: int = 0

    # 新增node
    def add_node(self, key: str, next_keys: list[str]) -> None:
        self.__nodes_map[key] = DialogNode(key, self.__font_size, next_keys)
        self._if_update_needed = True

    # 重新添加全部的key
    def read_all(self, dialogs_data: dict) -> None:
        self.__nodes_map.clear()
        for key in dialogs_data:
            next_keys: list[str] = []
            if dialogs_data[key]["next_dialog_id"] is not None and len(dialogs_data[key]["next_dialog_id"]) > 0:
                if dialogs_data[key]["next_dialog_id"]["type"] == "option":
                    for next_keys_options in dialogs_data[key]["next_dialog_id"]["target"]:
                        next_keys.append(next_keys_options["id"])
                elif isinstance(the_next_key := dialogs_data[key]["next_dialog_id"]["target"], (str, int)):
                    next_keys.append(str(the_next_key))
            self.add_node(key, next_keys)

    # 更新选中的key
    def update_selected(self, new_current_select: str) -> None:
        self.__current_selected_key = new_current_select
        self._if_update_needed = True

    # 获取当前选中的key
    def get_selected_key(self) -> str:
        return self.__current_selected_key

    def __update_node_pos(self, key: str = "head", offset_x: int = 0, offset_y: int = 0) -> int:
        key_node: DialogNode = self.__nodes_map[key]
        if not key_node.has_been_displayed:
            # 设置坐标并展示
            key_node.set_pos(offset_x, offset_y)
            key_node.has_been_displayed = True
            padding: int = 4 * self.__font_size
            if len(key_node.next_keys) > 1:
                offset_y = key_node.y - len(key_node.next_keys) * self.__font_size - padding
            for child_key in key_node.next_keys:
                offset_y = self.__update_node_pos(child_key, key_node.x + self.__font_size * 10, offset_y)
                offset_y += padding
            if self.__most_right < key_node.right:
                self.__most_right = key_node.right
            if self.__most_bottom < key_node.bottom:
                self.__most_bottom = key_node.bottom
            if self.__most_top > key_node.top:
                self.__most_top = key_node.top
        return offset_y

    def __draw_node(self, _surface: ImageSurface, key: str = "head") -> None:
        key_node: DialogNode = self.__nodes_map[key]
        if not key_node.has_been_displayed:
            # 设置坐标并展示
            key_node.display(_surface)
            key_node.has_been_displayed = True

            if self.__current_selected_key == key:
                Draw.rect(_surface, Colors.RED, key_node.get_rect(), 4)

            for child_key in key_node.next_keys:
                self.__draw_node(_surface, child_key)
                Draw.aaline(_surface, Colors.BLACK, key_node.right_center, self.__nodes_map[child_key].left_center, 3)

    def _update(self) -> None:
        if "head" in self.__nodes_map:
            for key in self.__nodes_map:
                self.__nodes_map[key].has_been_displayed = False
            self.__most_right = 0
            self.__most_bottom = 0
            self.__update_node_pos()
            for key in self.__nodes_map:
                self.__nodes_map[key].has_been_displayed = False
                self.__nodes_map[key].move_upward(self.__most_top)
            self._content_surface = Surfaces.transparent((self.__most_right, self.__most_bottom - self.__most_top))
            self.__draw_node(self._content_surface)
            self._if_update_needed = False
        else:
            EXCEPTION.fatal("Head is missing")

    def _any_content_container_event(self) -> bool:
        for key, value in self.__nodes_map.items():
            if Controller.mouse.is_in_rect(
                value.x + self.x - self.get_local_x(), value.y + self.y + self._bar_height - self.get_local_y(), value.get_width(), value.get_height()
            ):
                self.update_selected(key)
                return True
        return False


# 对话框模块基础框架
class AbstractDialogBox(HidableSurface, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        # 对胡框数据
        self._dialogue_box_max_height: int = Display.get_height() // 4
        self._dialogue_box_max_y: int = Display.get_height() * 65 // 100
        # 对胡框图片
        self._dialogue_box: StaticImage = StaticImage("<&ui>dialoguebox.png", Display.get_width() * 13 // 100, 0, Display.get_width() * 74 // 100)

    # 画出（子类需实现）
    def draw(self, _surface: ImageSurface) -> None:
        EXCEPTION.fatal("draw()", 1)

    # 更新内容（子类需实现）
    def update(self, narrator: str, contents: list) -> None:
        EXCEPTION.fatal("update()", 1)


# 对话开发模块
class EditableDialogBox(AbstractDialogBox):
    def __init__(self, fontSize: int):
        super().__init__()
        self.__contents: MultipleLinesInputBox = MultipleLinesInputBox(Display.get_width() * 2 / 10, Display.get_height() * 73 // 100, fontSize, Colors.WHITE)
        self.__narrator: SingleLineInputBox = SingleLineInputBox(Display.get_width() * 2 / 10, self._dialogue_box_max_y + fontSize, fontSize, Colors.WHITE)
        # 设置对话框高度和坐标
        self._dialogue_box.set_top(self._dialogue_box_max_y)
        self._dialogue_box.set_height(self._dialogue_box_max_height)

    # 是否内容相比上次有任何改变
    def any_changed_was_made(self) -> bool:
        return self.__narrator.need_save or self.__contents.need_save

    # 获取当前讲述人
    def get_narrator(self) -> str:
        return self.__narrator.get_text()

    # 获取当前内容
    def get_content(self) -> list:
        return self.__contents.get_text()

    # 更新内容
    def update(self, narrator: Optional[str], contents: Optional[list]) -> None:
        if narrator is None:
            self.__narrator.set_text()
        else:
            self.__narrator.set_text(narrator)
        if contents is None:
            self.__contents.set_text()
        else:
            self.__contents.set_text(contents)

    # 画出
    def draw(self, _surface: ImageSurface) -> None:
        if self.is_visible():
            # 画上对话框图片
            self._dialogue_box.draw(_surface)
            # 将文字画到屏幕上
            self.__narrator.draw(_surface)
            self.__contents.draw(_surface)


# 对话框和对话框内容
class DialogBox(AbstractDialogBox):

    # 翻页指示动态图标数据管理模块
    class __NextPageIndicatorIcon:
        def __init__(self) -> None:
            self.__status: bool = False
            self.__x_offset: int = 0
            self.__y_offset: int = 0

        def draw_to(self, _surface: ImageSurface, _x: int, _y: int, _width: int) -> None:
            # 更新坐标数值
            if not self.__status:
                self.__x_offset += 1
                self.__y_offset += 1
                if self.__x_offset >= _width:
                    self.__status = True
            else:
                self.__x_offset -= 1
                self.__y_offset -= 1
                if self.__x_offset <= 0:
                    self.__status = False
            final_y: int = _y + self.__y_offset // 4
            # 渲染
            Draw.polygon(
                _surface,
                Colors.WHITE,
                ((_x + self.__x_offset // 4, final_y), (_x + _width - self.__x_offset // 4, final_y), (_x + _width // 2, final_y + _width)),
            )

    def __init__(self, fontSize: int):
        super().__init__()
        self.FONT: FontGenerator = Font.create(fontSize)
        self.__contents: list = []
        self.__narrator: str = ""
        self.__text_index: int = 0
        self.__displayed_lines: int = 0
        self.__textPlayingSound: Optional[PG_Sound] = None
        if os.path.exists(_path := Specification.get_directory("sound", "ui", "dialog_words_playing.ogg")):
            self.__textPlayingSound = Sound.load(_path)
        self.__READING_SPEED: int = max(int(Setting.get("ReadingSpeed")), 1)
        # 翻页指示动态图标
        self.__next_page_indicator_icon = self.__NextPageIndicatorIcon()
        # 自动播放时参考的总阅读时间
        self.__read_time: int = 0
        # 总共的字数
        self.__total_letters: int = 0
        # 是否处于自动播放模式
        self.__auto_mode: bool = False
        # 是否处于淡出阶段
        self.__fade_out_stage: bool = False
        # 设置对话框高度和坐标
        self._dialogue_box.set_top(-1)
        self._dialogue_box.set_height(0)

    # 重置
    def reset(self) -> None:
        self.__fade_out_stage = False
        self._dialogue_box.set_height(0)
        self._dialogue_box.set_top(-1)

    # 是否所有内容均已展出
    def is_all_played(self) -> bool:
        # 如果self.__contents是空的，也就是说没有任何内容，那么应当视为所有内容都被播放了
        return len(self.__contents) == 0 or (
            self.__displayed_lines >= len(self.__contents) - 1 and self.__text_index >= len(self.__contents[self.__displayed_lines]) - 1
        )

    # 立刻播出所有内容
    def play_all(self) -> None:
        if not self.is_all_played():
            self.__displayed_lines = max(len(self.__contents) - 1, 0)
            self.__text_index = max(len(self.__contents[self.__displayed_lines]) - 1, 0)

    # 更新内容
    def update(self, narrator: Optional[str], contents: Optional[list], forceNotResizeDialogueBox: bool = False) -> None:
        self.stop_playing_text_sound()
        # 重设部分参数
        self.__text_index = 0
        self.__displayed_lines = 0
        self.__total_letters = 0
        self.__read_time = 0
        # 更新文字内容
        self.__contents = contents if contents is not None else []
        for text in self.__contents:
            self.__total_letters += len(text)
        # 更新讲述者名称
        if narrator is None:
            narrator = ""
        if self.__narrator != narrator and not forceNotResizeDialogueBox:
            self.__fade_out_stage = True
        self.__narrator = narrator

    # 获取文字播放时的音效的音量
    def get_sound_volume(self) -> float:
        if self.__textPlayingSound is not None:
            return self.__textPlayingSound.get_volume()
        else:
            return 0.0

    # 修改文字播放时的音效的音量
    def set_sound_volume(self, volume: number) -> None:
        if self.__textPlayingSound is not None:
            self.__textPlayingSound.set_volume(volume)

    # 是否开启自动播放模式
    def set_playing_automatically(self, value: bool) -> None:
        self.__auto_mode = value

    # 是否需要更新
    def is_update_needed(self) -> bool:
        return self.__auto_mode is True and self.__read_time >= self.__total_letters

    # 如果音效还在播放则停止播放文字音效
    @staticmethod
    def stop_playing_text_sound() -> None:
        if LINPG_RESERVED_SOUND_EFFECTS_CHANNEL is not None and LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.get_busy():
            LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.stop()

    def set_visible(self, visible: bool) -> None:
        super().set_visible(visible)
        # 如果声音在播放时模块被隐藏，则停止播放音效
        if self.is_hidden():
            self.stop_playing_text_sound()

    # 展示
    def draw(self, _surface: ImageSurface) -> None:
        if self.is_visible():
            # 渐入
            if not self.__fade_out_stage:
                # 如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
                if self._dialogue_box.y < 0:
                    self._dialogue_box.set_top(self._dialogue_box_max_y + self._dialogue_box_max_height / 2)
                # 画出对话框
                self._dialogue_box.draw(_surface)
                # 如果对话框图片还在放大阶段
                if self._dialogue_box.height < self._dialogue_box_max_height:
                    self._dialogue_box.set_height(
                        min(self._dialogue_box.height + self._dialogue_box_max_height / Display.get_delta_time() // 10, self._dialogue_box_max_height)
                    )
                    self._dialogue_box.move_upward(self._dialogue_box_max_height / Display.get_delta_time() // 20)
                # 如果已经放大好了，则将文字画到屏幕上
                else:
                    x: int = _surface.get_width() * 2 // 10
                    y: int = _surface.get_height() * 73 // 100
                    # 写上当前讲话人的名字
                    if len(self.__narrator) > 0:
                        _surface.blit(self.FONT.render(self.__narrator, Colors.WHITE), (x, self._dialogue_box.y + self.FONT.size))
                    # 对话框已播放的内容
                    for i in range(self.__displayed_lines):
                        _surface.blit(self.FONT.render(self.__contents[i], Colors.WHITE), (x, y + self.FONT.size * 3 * i // 2))
                    # 对话框正在播放的内容
                    _surface.blit(
                        self.FONT.render(self.__contents[self.__displayed_lines][: self.__text_index], Colors.WHITE),
                        (x, y + self.FONT.size * 3 * self.__displayed_lines // 2),
                    )
                    # 如果当前行的字符还没有完全播出
                    if self.__text_index < len(self.__contents[self.__displayed_lines]):
                        # 播放文字音效
                        if (
                            LINPG_RESERVED_SOUND_EFFECTS_CHANNEL is not None
                            and not LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.get_busy()
                            and self.__textPlayingSound is not None
                        ):
                            LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.play(self.__textPlayingSound)
                        self.__text_index += 1
                    # 当前行的所有字都播出后，播出下一行
                    elif self.__displayed_lines < len(self.__contents) - 1:
                        self.__text_index = 0
                        self.__displayed_lines += 1
                    # 当所有行都播出后
                    else:
                        self.stop_playing_text_sound()
                        if self.__auto_mode is True and self.__read_time < self.__total_letters:
                            self.__read_time += self.__READING_SPEED
                    # 画出翻页指示动态图标
                    _width: int = self.FONT.size * 2 // 3
                    self.__next_page_indicator_icon.draw_to(_surface, self._dialogue_box.right - _width * 4, self._dialogue_box.bottom - _width * 3, _width)
            # 淡出
            else:
                # 画出对话框图片
                self._dialogue_box.draw(_surface)
                height_t: int = self._dialogue_box.height - int(self._dialogue_box_max_height / Display.get_delta_time() / 10)
                if height_t > 0:
                    self._dialogue_box.set_height(height_t)
                    self._dialogue_box.move_downward(self._dialogue_box_max_height / Display.get_delta_time() // 20)
                else:
                    self.reset()
