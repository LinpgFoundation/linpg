from ..ui import *


# 对话框模块基础框架
class AbstractDialogBox(Hidable, metaclass=ABCMeta):

    # padding scale in percentage of surface size
    PADDING_TOP: int = 2
    PADDING_LEFT: int = 2

    # margin scale in percentage of surface size
    MARGIN_TOP: int = 75
    MARGIN_BOTTOM: int = 5
    MARGIN_RIGHT: int = 5
    MARGIN_LEFT: int = 5

    IMAGE: StaticImage | None = None

    # get dialog box image
    def _get_image(self) -> StaticImage:
        # ensure image is initialized
        if self.IMAGE is None:
            self.IMAGE = StaticImage(Surfaces.colored((100, 100), Colors.GRAY), 0, 0)
        return self.IMAGE

    # 画出
    def draw(self, _surface: ImageSurface) -> None:
        if self.is_hidden():
            return
        self._draw(_surface)

    # 画出内容（子类可重写）
    def _draw(self, _surface: ImageSurface) -> None:
        self._get_image().draw(_surface)

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
            Display.get_width() * 2 / 10, self.__contents.get_bottom() + fontSize, fontSize, Colors.WHITE, fontSize * 4
        )

    # 是否内容相比上次有任何改变
    def any_changed_was_made(self) -> bool:
        return self.__narrator.need_save or self.__contents.need_save

    # 获取当前讲述人
    def get_narrator(self) -> str:
        return self.__narrator.get_text()

    # 获取当前内容
    def get_content(self) -> list[str]:
        return self.__contents.get_text()

    # 更新内容
    def update(self, narrator: str | None, contents: list[str] | None) -> None:
        if narrator is None:
            self.__narrator.set_text()
        else:
            self.__narrator.set_text(narrator)
        if contents is None:
            self.__contents.set_text()
        else:
            self.__contents.set_text(contents)

    # 画出
    def _draw(self, _surface: ImageSurface) -> None:
        super()._draw(_surface)
        # 将文字画到屏幕上
        self.__narrator.draw(_surface)
        self.__contents.draw(_surface)


# 对话框和对话框内容
class DialogBox(AbstractDialogBox):

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
        self.__next_page_indicator_icon = NextPageIndicatorIcon()
        # 自动播放时参考的总阅读时间
        self.__read_time: int = 0
        # 总共的字数
        self.__total_letters: int = 0
        # 是否处于自动播放模式
        self.__auto_mode: bool = False
        # 设置对话框高度和坐标
        self._get_image().set_top(-1)
        self._get_image().set_height(0)

    # 是否所有内容均已展出
    def is_all_played(self) -> bool:
        return (
            self.__displayed_lines >= len(self.__contents)
            or self.__displayed_lines == len(self.__contents) - 1
            and self.__text_index >= len(self.__contents[self.__displayed_lines]) - 1
        )

    # 立刻播出所有内容
    def play_all(self) -> None:
        if self.is_all_played():
            return
        self.__displayed_lines = max(len(self.__contents) - 1, 0)
        self.__text_index = max(len(self.__contents[self.__displayed_lines]) - 1, 0)
        self.__next_text_index_count = self.__next_text_index_count_required

    # 更新内容
    def update(self, narrator: str | None, contents: list | None) -> None:
        self.stop_playing_text_sound()
        # 重设部分参数
        self.__text_index = 0
        self.__next_text_index_count = 0
        self.__displayed_lines = 0
        self.__total_letters = 0
        self.__read_time = 0
        # 更新文字内容
        self.__contents = [] if contents is None else contents
        for text in self.__contents:
            self.__total_letters += len(text)
        # 更新讲述者名称
        self.__narrator = "" if narrator is None else narrator

    # 获取文字播放时的音效的音量
    def get_sound_volume(self) -> float:
        if self.__textPlayingSound is not None:
            return self.__textPlayingSound.get_volume()
        else:
            return 0.0

    # 修改文字播放时的音效的音量
    def set_sound_volume(self, volume: number) -> None:
        if self.__textPlayingSound is None:
            return
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
        if self.is_visible():
            return
        self.stop_playing_text_sound()

    # 展示
    def _draw(self, _surface: ImageSurface) -> None:
        # 画出对话框
        margin_top: int = _surface.height * self.MARGIN_TOP // 100
        margin_left: int = _surface.width * self.MARGIN_LEFT // 100
        self._get_image().set_size(
            _surface.width - margin_left - _surface.width * self.MARGIN_RIGHT // 100,
            _surface.height - margin_top - _surface.height * self.MARGIN_BOTTOM // 100,
        )
        self._get_image().set_left(margin_left)
        self._get_image().set_top(margin_top)
        super()._draw(_surface)
        # 将文字画到屏幕上
        x: int = self._get_image().left + _surface.width * self.PADDING_LEFT // 100
        y: int = self._get_image().top + _surface.height * self.PADDING_TOP // 100
        # 写上当前讲话人的名字
        if len(self.__narrator) > 0:
            _surface.blit(self.FONT.render(self.__narrator, Colors.WHITE), (x, y))
        # 调整y坐标以开始写对话内容
        y += self.FONT.size * 2
        # 对话框已播放的内容
        for i in range(self.__displayed_lines):
            _surface.blit(self.FONT.render(self.__contents[i], Colors.WHITE), (x, y + self.FONT.size * i * 2))
        # make sure self.__contents is not empty
        if self.__displayed_lines < len(self.__contents):
            # 对话框正在播放的内容
            _surface.blit(
                self.FONT.render(self.__contents[self.__displayed_lines][: self.__text_index], Colors.WHITE),
                (x, y + self.FONT.size * self.__displayed_lines * 2),
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
            elif self.__displayed_lines < len(self.__contents):
                self.__text_index = 0
                self.__next_text_index_count = 0
                self.__displayed_lines += 1
            # 当所有行都播出后
            else:
                self.stop_playing_text_sound()
                if self.__auto_mode is True and self.__read_time < self.__total_letters * 100:
                    self.__read_time += Display.get_delta_time() * self.__READING_SPEED
        else:
            # 画出翻页指示动态图标
            _width: int = self.FONT.size * 2 // 3
            self.__next_page_indicator_icon.draw_to(
                _surface, self._get_image().right - _width * 4, self._get_image().bottom - _width * 3, _width
            )
