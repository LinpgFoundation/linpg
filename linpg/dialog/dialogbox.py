from ..ui import *

# 对话框模块基础框架
class AbstractDialogBox(HiddenableSurface):
    def __init__(self) -> None:
        super().__init__()
        # 对胡框数据
        self._dialoguebox_max_height: int = int(Display.get_height() / 4)
        self._dialoguebox_max_y: int = int(Display.get_height() * 0.65)
        # 对胡框图片
        self._dialoguebox: StaticImage = StaticImage(
            "<!ui>dialoguebox.png", Display.get_width() * 0.13, 0, Display.get_width() * 0.74
        )

    # 画出（子类需实现）
    def draw(self, surface: ImageSurface) -> None:
        EXCEPTION.fatal("draw()", 1)

    # 更新内容（子类需实现）
    def update(self, narrator: str, contents: list) -> None:
        EXCEPTION.fatal("update()", 1)


# 对话开发模块
class DevDialogBox(AbstractDialogBox):
    def __init__(self, fontSize: int):
        super().__init__()
        self.__contents: MultipleLinesInputBox = MultipleLinesInputBox(
            Display.get_width() * 2 / 10, Display.get_height() * 0.73, fontSize, "white"
        )
        self.__narrator: SingleLineInputBox = SingleLineInputBox(
            Display.get_width() * 2 / 10, self._dialoguebox_max_y + fontSize, fontSize, "white"
        )
        # 设置对话框高度和坐标
        self._dialoguebox.set_top(self._dialoguebox_max_y)
        self._dialoguebox.set_height(self._dialoguebox_max_height)

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
    def draw(self, surface: ImageSurface) -> None:
        if self.is_visible():
            # 画上对话框图片
            self._dialoguebox.draw(surface)
            # 将文字画到屏幕上
            self.__narrator.draw(surface)
            self.__contents.draw(surface)


# 对话框和对话框内容
class DialogBox(AbstractDialogBox):
    def __init__(self, fontSize: int):
        super().__init__()
        self.FONT: FontGenerator = Font.create(fontSize)
        self.__contents: list = []
        self.__narrator: str = ""
        self.__text_index: int = 0
        self.__displayed_lines: int = 0
        self.__textPlayingSound: Optional[PG_Sound] = None
        try:
            self.__textPlayingSound = Sound.load(r"Assets/sound/ui/dialog_words_playing.ogg")
        except FileNotFoundError:
            self.__textPlayingSound = None
            EXCEPTION.inform(
                "Cannot find 'dialog_words_playing.ogg' in 'Assets/sound/ui'!\nAs a result, the text playing sound will be disabled."
            )
        self.__READING_SPEED: int = max(int(Setting.get("ReadingSpeed")), 1)
        # 鼠标图标
        self.__mouse_img = GifImage(
            (
                StaticImage("<!ui>mouse_none.png", 0, 0, self.FONT.size, self.FONT.size),
                StaticImage("<!ui>mouse.png", 0, 0, self.FONT.size, self.FONT.size),
            ),
            int(Display.get_width() * 0.82),
            int(Display.get_height() * 0.83),
            self.FONT.size,
            self.FONT.size,
            50,
        )
        self.__read_time: int = 0
        self.__total_letters: int = 0
        # 是否处于自动播放模式
        self.__auto_mode: bool = False
        # 是否处于淡出阶段
        self.__fade_out_stage: bool = False
        # 设置对话框高度和坐标
        self._dialoguebox.set_top(-1)
        self._dialoguebox.set_height(0)

    # 重置
    def reset(self) -> None:
        self.__fade_out_stage = False
        self._dialoguebox.set_height(0)
        self._dialoguebox.set_top(-1)

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

    # 更新内容
    def update(self, narrator: Optional[str], contents: Optional[list], forceNotResizeDialoguebox: bool = False) -> None:
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
        if self.__narrator != narrator and not forceNotResizeDialoguebox:
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
    def stop_playing_text_sound(self) -> None:
        if LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.get_busy():
            LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.stop()

    def set_visible(self, visible: bool) -> None:
        super().set_visible(visible)
        # 如果声音在播放时模块被隐藏，则停止播放音效
        if self.is_hidden():
            self.stop_playing_text_sound()

    # 展示
    def draw(self, surface: ImageSurface) -> None:
        if self.is_visible():
            # 渐入
            if not self.__fade_out_stage:
                # 如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
                if self._dialoguebox.y < 0:
                    self._dialoguebox.set_top(self._dialoguebox_max_y + self._dialoguebox_max_height / 2)
                # 画出对话框
                self._dialoguebox.draw(surface)
                # 如果对话框图片还在放大阶段
                if self._dialoguebox.height < self._dialoguebox_max_height:
                    self._dialoguebox.set_height(
                        min(
                            int(self._dialoguebox.height + self._dialoguebox_max_height * Display.sfpsp / 10),
                            self._dialoguebox_max_height,
                        )
                    )
                    self._dialoguebox.move_upward(self._dialoguebox_max_height * Display.sfpsp / 20)
                # 如果已经放大好了，则将文字画到屏幕上
                else:
                    x: int = int(surface.get_width() * 2 / 10)
                    y: int = int(surface.get_height() * 0.73)
                    # 写上当前讲话人的名字
                    if len(self.__narrator) > 0:
                        surface.blit(self.FONT.render(self.__narrator, Colors.WHITE), (x, self._dialoguebox.y + self.FONT.size))
                    # 对话框已播放的内容
                    for i in range(self.__displayed_lines):
                        surface.blit(
                            self.FONT.render(self.__contents[i], Colors.WHITE, with_bounding=True),
                            (x, y + self.FONT.size * 1.5 * i),
                        )
                    # 对话框正在播放的内容
                    surface.blit(
                        self.FONT.render(
                            self.__contents[self.__displayed_lines][: self.__text_index], Colors.WHITE, with_bounding=True
                        ),
                        (x, y + self.FONT.size * 1.5 * self.__displayed_lines),
                    )
                    # 如果当前行的字符还没有完全播出
                    if self.__text_index < len(self.__contents[self.__displayed_lines]):
                        # 播放文字音效
                        if not LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.get_busy() and self.__textPlayingSound is not None:
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
                    # 画出鼠标gif
                    self.__mouse_img.draw(surface)
            # 淡出
            else:
                # 画出对话框图片
                self._dialoguebox.draw(surface)
                height_t: int = int(self._dialoguebox.height - self._dialoguebox_max_height * Display.sfpsp / 10)
                if height_t > 0:
                    self._dialoguebox.set_height(height_t)
                    self._dialoguebox.move_downward(self._dialoguebox_max_height * Display.sfpsp / 20)
                else:
                    self.reset()
