from ..ui import *

# ui路径
DIALOG_UI_PATH: str = os.path.join("Assets", "image", "UI")

# 对话框和对话框内容
class DialogBox:
    def __init__(self, fontSize: int_f):
        # 编辑器模式
        self.__dev_mode: bool = False
        # 对胡框数据
        self.dialoguebox_max_height: int = int(Display.get_height() / 4)
        self.dialoguebox_max_y: int = int(Display.get_height() * 0.65)
        # 对胡框图片
        self.dialoguebox: StaticImage = StaticImage(
            os.path.join(DIALOG_UI_PATH, "dialoguebox.png"), int(Display.get_width() * 0.13), 0, Display.get_width() * 0.74
        )
        self.FONT: int = Font.create(fontSize)
        self.content = []
        self.narrator = None
        self.textIndex = None
        self.displayedLine = None
        try:
            self.__textPlayingSound = Sound.load(r"Assets/sound/ui/dialog_words_playing.ogg")
        except FileNotFoundError:
            self.__textPlayingSound = None
            EXCEPTION.warn(
                "Cannot find 'dialog_words_playing.ogg' in 'Assets/sound/ui'!\nAs a result, the text playing sound will be disabled."
            )
        self.READINGSPEED = Setting.get("ReadingSpeed")
        # 鼠标图标
        self.mouseImg = GifImage(
            numpy.asarray(
                (
                    StaticImage(os.path.join(DIALOG_UI_PATH, "mouse_none.png"), 0, 0, self.FONT.size, self.FONT.size),
                    StaticImage(os.path.join(DIALOG_UI_PATH, "mouse.png"), 0, 0, self.FONT.size, self.FONT.size),
                )
            ),
            int(Display.get_width() * 0.82),
            int(Display.get_height() * 0.83),
            self.FONT.size,
            self.FONT.size,
            50,
        )
        self.hidden: bool = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
        self.reset()

    # 编辑器模式
    def dev_mode(self) -> None:
        self.__dev_mode = not self.__dev_mode
        if not self.__dev_mode:
            self.content = []
            self.narrator = None
        else:
            self.content = MultipleLinesInputBox(
                Display.get_width() * 0.2, Display.get_height() * 0.73, self.FONT.size, "white"
            )
            self.narrator = SingleLineInputBox(
                Display.get_width() * 0.2, self.dialoguebox_max_y + self.FONT.size, self.FONT.size, "white"
            )

    # 是否所有内容均已展出
    def is_all_played(self) -> bool:
        # 如果self.content是空的，也就是说没有任何内容，那么应当视为所有内容都被播放了
        if len(self.content) == 0 or self.__dev_mode is True:
            return True
        else:
            return (
                self.displayedLine >= len(self.content) - 1 and self.textIndex >= len(self.content[self.displayedLine]) - 1
            )

    # 立刻播出所有内容
    def play_all(self) -> None:
        if not self.is_all_played():
            self.displayedLine = len(self.content) - 1
            self.textIndex = len(self.content[self.displayedLine]) - 1

    # 更新内容
    def update(self, narrator: str, content: list, forceNotResizeDialoguebox: bool = False) -> None:
        if not self.__dev_mode:
            self.stop_playing_text_sound()
            self.totalLetters = 0
            self.readTime = 0
            for i in range(len(self.content)):
                self.totalLetters += len(self.content[i])
            if self.narrator != narrator and not forceNotResizeDialoguebox:
                self.__fade_out_stage = True
            self.textIndex = 0
            self.displayedLine = 0
            self.narrator = narrator
            self.content = content
        else:
            self.narrator.set_text(narrator)
            self.content.set_text(content)

    def reset(self) -> None:
        self.__fade_out_stage = False
        self.dialoguebox_height = 0
        self.dialoguebox_y = None
        self.__txt_alpha = 255

    # 获取文字播放时的音效的音量
    def get_sound_volume(self) -> float:
        if self.__textPlayingSound is not None:
            return self.__textPlayingSound.get_volume()
        else:
            return 0.0

    # 修改文字播放时的音效的音量
    def set_sound_volume(self, volume: number) -> None:
        if self.__textPlayingSound is not None:
            self.__textPlayingSound.set_volume(volume / 100.0)

    # 是否需要更新
    def needUpdate(self) -> bool:
        return True if self.autoMode and self.readTime >= self.totalLetters else False

    # 如果音效还在播放则停止播放文字音效
    def stop_playing_text_sound(self) -> None:
        if Media.get_busy() and self.__textPlayingSound is not None:
            self.__textPlayingSound.stop()

    # 将文字画到屏幕上
    def __draw_text(self, surface: ImageSurface) -> None:
        if not self.__dev_mode:
            x: int = int(surface.get_width() * 0.2)
            y: int = int(surface.get_height() * 0.73)
            # 写上当前讲话人的名字
            if self.narrator is not None:
                surface.blit(self.FONT.render(self.narrator, Color.WHITE), (x, self.dialoguebox_y + self.FONT.size))
            # 对话框已播放的内容
            for i in range(self.displayedLine):
                surface.blit(self.FONT.render(self.content[i], Color.WHITE), (x, y + self.FONT.size * 1.5 * i))
            # 对话框正在播放的内容
            surface.blit(
                self.FONT.render(self.content[self.displayedLine][: self.textIndex], Color.WHITE),
                (x, y + self.FONT.size * 1.5 * self.displayedLine),
            )
            # 如果当前行的字符还没有完全播出
            if self.textIndex < len(self.content[self.displayedLine]):
                if not Media.get_busy() and self.__textPlayingSound is not None:
                    self.__textPlayingSound.play()
                self.textIndex += 1
            # 当前行的所有字都播出后，播出下一行
            elif self.displayedLine < len(self.content) - 1:
                if not Media.get_busy() and self.__textPlayingSound is not None:
                    self.__textPlayingSound.play()
                self.textIndex = 1
                self.displayedLine += 1
            # 当所有行都播出后
            else:
                self.stop_playing_text_sound()
                if self.autoMode and self.readTime < self.totalLetters:
                    self.readTime += self.READINGSPEED
            # 画出鼠标gif
            self.mouseImg.draw(surface)
        else:
            self.narrator.draw(surface)
            self.content.draw(surface)

    # 画上对话框图片
    def __draw_dialogbox(self, surface: ImageSurface) -> None:
        if not self.__dev_mode:
            self.dialoguebox.set_top(int(self.dialoguebox_y))
            self.dialoguebox.set_height(self.dialoguebox_height)
        else:
            self.dialoguebox.set_top(self.dialoguebox_max_y)
            self.dialoguebox.set_height(self.dialoguebox_max_height)
        self.dialoguebox.draw(surface)

    # 展示
    def draw(self, surface: ImageSurface) -> None:
        if not self.hidden:
            # 渐入
            if not self.__fade_out_stage:
                # 如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
                if self.dialoguebox_y is None:
                    self.dialoguebox_y = self.dialoguebox_max_y + self.dialoguebox_max_height / 2
                # 画出对话框
                self.__draw_dialogbox(surface)
                # 如果对话框图片还在放大阶段
                if self.dialoguebox_height < self.dialoguebox_max_height:
                    self.dialoguebox_height = min(
                        int(self.dialoguebox_height + self.dialoguebox_max_height * Display.sfpsp / 10),
                        self.dialoguebox_max_height,
                    )
                    self.dialoguebox_y -= int(self.dialoguebox_max_height * Display.sfpsp / 20)
                # 如果已经放大好了
                else:
                    self.__draw_text(surface)
            # 淡出
            else:
                # 画出对话框图片
                if self.dialoguebox_y is not None:
                    # 画出对话框
                    self.__draw_dialogbox(surface)
                if self.dialoguebox_height > 0:
                    self.dialoguebox_height = max(
                        int(self.dialoguebox_height - self.dialoguebox_max_height * Display.sfpsp / 10), 0
                    )
                    self.dialoguebox_y += int(self.dialoguebox_max_height * Display.sfpsp / 20)
                else:
                    self.reset()
