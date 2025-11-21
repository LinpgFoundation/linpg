from ..ui import *


# 对话框模块基础框架
class AbstractDialogBox(Hidable, metaclass=ABCMeta):

    # is dialogue box pixelated
    IS_PIXELATED: bool = False

    def __init__(self) -> None:
        super().__init__()
        # 对胡框数据
        self._dialogue_box_max_height: int = Display.get_height() // 4
        self._dialogue_box_max_y: int = Display.get_height() * 65 // 100
        # 对胡框图片
        self._dialogue_box: StaticImage = StaticImage(
            Surfaces.colored((100, 100), Colors.GRAY),
            Display.get_width() * 13 // 100,
            0,
            Display.get_width() * 74 // 100,
            True,
            self.IS_PIXELATED,
        )

    def draw_dialogue_box(self, _surface: ImageSurface) -> None:
        self._dialogue_box.draw(_surface)

    # 画出（子类需实现）
    @abstractmethod
    def draw(self, _surface: ImageSurface) -> None:
        Exceptions.fatal("draw()", 1)

    # 更新内容（子类需实现）
    @abstractmethod
    def update(self, narrator: str, contents: list) -> None:
        Exceptions.fatal("update()", 1)


# 对话开发模块
class EditableDialogBox(AbstractDialogBox):
    def __init__(self, fontSize: int):
        super().__init__()
        self.__contents: MultipleLinesInputBox = MultipleLinesInputBox(
            Display.get_width() * 2 / 10, Display.get_height() * 73 // 100, fontSize, Colors.WHITE, fontSize * 8
        )
        self.__narrator: SingleLineInputBox = SingleLineInputBox(
            Display.get_width() * 2 / 10, self._dialogue_box_max_y + fontSize, fontSize, Colors.WHITE, fontSize * 4
        )
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
    def update(self, narrator: str | None, contents: list | None) -> None:
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
            self.__x_offset: float = 0
            self.__y_offset: float = 0

        def draw_to(self, _surface: ImageSurface, _x: int, _y: int, _width: int) -> None:
            # 更新坐标数值
            if not self.__status:
                self.__x_offset += Display.get_delta_time() / 30
                self.__y_offset += Display.get_delta_time() / 20
                if self.__y_offset >= _width / 2:
                    self.__status = True
            else:
                self.__x_offset -= Display.get_delta_time() / 30
                self.__y_offset -= Display.get_delta_time() / 20
                if self.__y_offset <= 0:
                    self.__status = False
            final_y: int = int(_y + self.__y_offset)
            # 渲染
            Draw.polygon(
                _surface,
                Colors.WHITE,
                (
                    (_x + int(self.__x_offset), final_y),
                    (_x + _width - int(self.__x_offset), final_y),
                    (_x + _width // 2, final_y + _width),
                ),
            )

    def __init__(self, fontSize: int):
        super().__init__()
        self.FONT: Font = Fonts.create(fontSize)
        self.__contents: list = []
        self.__narrator: str = ""
        self.__text_index: int = 0
        self.__next_text_index_count: int = 0
        self.__next_text_index_count_required: int = 10
        self.__displayed_lines: int = 0
        self.__textPlayingSound: Sound | None = None
        if os.path.exists(_path := Specifications.get_directory("sound", "ui", "dialog_words_playing.ogg")):
            self.__textPlayingSound = Sounds.load(_path)
        self.__READING_SPEED: int = max(Settings.get_int("ReadingSpeed"), 1)
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
            self.__displayed_lines >= len(self.__contents) - 1
            and self.__text_index >= len(self.__contents[self.__displayed_lines]) - 1
        )

    # 立刻播出所有内容
    def play_all(self) -> None:
        if not self.is_all_played():
            self.__displayed_lines = max(len(self.__contents) - 1, 0)
            self.__text_index = max(len(self.__contents[self.__displayed_lines]) - 1, 0)
            self.__next_text_index_count = self.__next_text_index_count_required

    # 更新内容
    def update(self, narrator: str | None, contents: list | None, forceNotResizeDialogueBox: bool = False) -> None:
        self.stop_playing_text_sound()
        # 重设部分参数
        self.__text_index = 0
        self.__next_text_index_count = 0
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
        return self.__auto_mode is True and self.__read_time >= self.__total_letters * 100

    # 如果音效还在播放则停止播放文字音效
    @staticmethod
    def stop_playing_text_sound() -> None:
        if (
            LINPG_RESERVED_CHANNELS.SOUND_EFFECTS_CHANNEL is not None
            and LINPG_RESERVED_CHANNELS.SOUND_EFFECTS_CHANNEL.get_busy()
        ):
            LINPG_RESERVED_CHANNELS.SOUND_EFFECTS_CHANNEL.stop()

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
                        min(
                            self._dialogue_box.height + self._dialogue_box_max_height * Display.get_delta_time() // 200,
                            self._dialogue_box_max_height,
                        )
                    )
                    self._dialogue_box.move_upward(self._dialogue_box_max_height * Display.get_delta_time() // 400)
                # 如果已经放大好了，则将文字画到屏幕上
                else:
                    self._dialogue_box.set_top(self._dialogue_box_max_y)
                    x: int = _surface.get_width() * 2 // 10
                    y: int = _surface.get_height() * 73 // 100
                    # 写上当前讲话人的名字
                    if len(self.__narrator) > 0:
                        _surface.blit(
                            self.FONT.render(self.__narrator, Colors.WHITE), (x, self._dialogue_box.y + self.FONT.size)
                        )
                    # 对话框已播放的内容
                    for i in range(self.__displayed_lines):
                        _surface.blit(self.FONT.render(self.__contents[i], Colors.WHITE), (x, y + self.FONT.size * 3 * i // 2))
                    # make sure self.__contents is not empty
                    if self.__displayed_lines < len(self.__contents):
                        # 对话框正在播放的内容
                        _surface.blit(
                            self.FONT.render(self.__contents[self.__displayed_lines][: self.__text_index], Colors.WHITE),
                            (x, y + self.FONT.size * 3 * self.__displayed_lines // 2),
                        )
                        # 如果当前行的字符还没有完全播出
                        if self.__text_index < len(self.__contents[self.__displayed_lines]):
                            # 播放文字音效
                            if (
                                LINPG_RESERVED_CHANNELS.SOUND_EFFECTS_CHANNEL is not None
                                and not LINPG_RESERVED_CHANNELS.SOUND_EFFECTS_CHANNEL.get_busy()
                                and self.__textPlayingSound is not None
                            ):
                                LINPG_RESERVED_CHANNELS.SOUND_EFFECTS_CHANNEL.play(self.__textPlayingSound)
                            if self.__next_text_index_count < self.__next_text_index_count_required:
                                self.__next_text_index_count += Display.get_delta_time()
                            else:
                                self.__text_index += 1
                                self.__next_text_index_count = 0
                        # 当前行的所有字都播出后，播出下一行
                        elif self.__displayed_lines < len(self.__contents) - 1:
                            self.__text_index = 0
                            self.__next_text_index_count = 0
                            self.__displayed_lines += 1
                        # 当所有行都播出后
                        else:
                            self.stop_playing_text_sound()
                            if self.__auto_mode is True and self.__read_time < self.__total_letters * 100:
                                self.__read_time += Display.get_delta_time() * self.__READING_SPEED
                    # 画出翻页指示动态图标
                    _width: int = self.FONT.size * 2 // 3
                    self.__next_page_indicator_icon.draw_to(
                        _surface, self._dialogue_box.right - _width * 4, self._dialogue_box.bottom - _width * 3, _width
                    )
            # 淡出
            else:
                # 画出对话框图片
                self._dialogue_box.draw(_surface)
                height_t: int = self._dialogue_box.height - int(self._dialogue_box_max_height * Display.get_delta_time() // 200)
                if height_t > 0:
                    self._dialogue_box.set_height(height_t)
                    self._dialogue_box.move_downward(self._dialogue_box_max_height * Display.get_delta_time() // 400)
                else:
                    self.reset()
