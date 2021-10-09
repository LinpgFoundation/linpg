from .dialogbox import *

# 对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        self.__button_hovered: int = 0
        self.hidden: bool = False
        self.initialize()

    # 初始化
    def initialize(self) -> None:
        # 从设置中读取信息
        self.FONT = Font.create(Display.get_width() * 0.0175)
        # 从语言文件中读取按钮文字
        dialog_txt: dict = Lang.get_texts("Dialog")
        # 生成跳过按钮
        tempButtonIcon = IMG.load("<!ui>next.png", (self.FONT.size, self.FONT.size))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"], Color.WHITE)
        temp_w = tempButtonTxt.get_width() + self.FONT.size * 1.5
        self.choiceTxt = dialog_txt["choice"]
        self.skipButton = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.skipButtonHovered = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.icon_y = (tempButtonTxt.get_height() - tempButtonIcon.get_height()) / 2
        self.skipButtonHovered.blit(tempButtonIcon, (tempButtonTxt.get_width() + self.FONT.size * 0.5, self.icon_y))
        self.skipButtonHovered.blit(tempButtonTxt, (0, 0))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"], Color.GRAY)
        tempButtonIcon = IMG.add_darkness(tempButtonIcon, 100)
        self.skipButton.blit(tempButtonIcon, (tempButtonTxt.get_width() + self.FONT.size * 0.5, self.icon_y))
        self.skipButton.blit(tempButtonTxt, (0, 0))
        self.skipButton = StaticImage(self.skipButton, Display.get_width() * 0.9, Display.get_height() * 0.05)
        self.skipButtonHovered = StaticImage(self.skipButtonHovered, Display.get_width() * 0.9, Display.get_height() * 0.05)
        # 生成自动播放按钮
        self.autoIconHovered = IMG.load("<!ui>auto.png", (self.FONT.size, self.FONT.size))
        self.autoIcon = IMG.add_darkness(self.autoIconHovered, 100)
        self.autoIconDegree = 0
        self.autoIconDegreeChange = (2 ** 0.5 - 1) * self.FONT.size / 45
        self.autoMode: bool = False
        tempButtonTxt = self.FONT.render(dialog_txt["auto"], Color.GRAY)
        temp_w = tempButtonTxt.get_width() + self.FONT.size * 1.5
        self.autoButton = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.autoButtonHovered = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.autoButton.blit(tempButtonTxt, (0, 0))
        self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"], Color.WHITE), (0, 0))
        self.autoButton = DynamicImage(self.autoButton, Display.get_width() * 0.8, Display.get_height() * 0.05)
        self.autoButton.tag = int(self.autoButton.x + self.autoButton.img.get_width() - self.FONT.size)
        self.autoButtonHovered = DynamicImage(self.autoButtonHovered, Display.get_width() * 0.8, Display.get_height() * 0.05)
        self.autoButtonHovered.tag = int(self.autoButtonHovered.x + self.autoButtonHovered.img.get_width() - self.FONT.size)
        # 隐藏按钮
        self.hideButton = load_button(
            "<!ui>hide.png", (Display.get_width() * 0.05, Display.get_height() * 0.05), (self.FONT.size, self.FONT.size), 150
        )
        # 取消隐藏按钮
        self.showButton = load_button(
            "<!ui>show.png", (Display.get_width() * 0.05, Display.get_height() * 0.05), (self.FONT.size, self.FONT.size), 150
        )
        # 历史回溯按钮
        self.historyButton = load_button(
            "<!ui>history.png",
            (Display.get_width() * 0.1, Display.get_height() * 0.05),
            (self.FONT.size, self.FONT.size),
            150,
        )

    @property
    def item_being_hovered(self) -> str:
        if self.__button_hovered == 1:
            return "hide"
        elif self.__button_hovered == 2:
            return "skip"
        elif self.__button_hovered == 3:
            return "auto"
        elif self.__button_hovered == 4:
            return "history"
        else:
            return ""

    def draw(self, surface: ImageSurface) -> None:
        self.__button_hovered = 0
        if self.hidden is True:
            self.showButton.draw(surface)
            if self.showButton.is_hover():
                self.__button_hovered = 1
        else:
            self.hideButton.draw(surface)
            self.historyButton.draw(surface)
            if self.skipButton.is_hover():
                self.skipButtonHovered.draw(surface)
                self.__button_hovered = 2
            else:
                self.skipButton.draw(surface)
            if self.autoButton.is_hover():
                self.autoButtonHovered.draw(surface)
                if self.autoMode:
                    rotatedIcon = IMG.rotate(self.autoIconHovered, self.autoIconDegree)
                    surface.blit(
                        rotatedIcon,
                        (
                            self.autoButtonHovered.tag + self.autoIconHovered.get_width() / 2 - rotatedIcon.get_width() / 2,
                            self.autoButtonHovered.y
                            + self.icon_y
                            + self.autoIconHovered.get_height() / 2
                            - rotatedIcon.get_height() / 2,
                        ),
                    )
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    surface.blit(self.autoIconHovered, (self.autoButtonHovered.tag, self.autoButtonHovered.y + self.icon_y))
                self.__button_hovered = 3
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(surface)
                    rotatedIcon = IMG.rotate(self.autoIconHovered, self.autoIconDegree)
                    surface.blit(
                        rotatedIcon,
                        (
                            self.autoButtonHovered.tag + self.autoIconHovered.get_width() / 2 - rotatedIcon.get_width() / 2,
                            self.autoButtonHovered.y
                            + self.icon_y
                            + self.autoIconHovered.get_height() / 2
                            - rotatedIcon.get_height() / 2,
                        ),
                    )
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    self.autoButton.draw(surface)
                    surface.blit(self.autoIcon, (self.autoButton.tag, self.autoButton.y + self.icon_y))
            if self.hideButton.is_hover():
                self.__button_hovered = 1
            elif self.historyButton.is_hover():
                self.__button_hovered = 4

    def autoModeSwitch(self) -> None:
        if not self.autoMode:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0


# 过场动画
def cutscene(surface: ImageSurface, videoPath: str, fade_out_in_ms: int = 3000) -> None:
    # 初始化部分参数
    is_skip: bool = False
    is_playing: bool = True
    # 初始化跳过按钮的参数
    skip_button: StaticImage = StaticImage(
        "<!ui>next.png",
        int(surface.get_width() * 0.92),
        int(surface.get_height() * 0.05),
        int(surface.get_width() * 0.055),
        int(surface.get_height() * 0.06),
    )
    # 进度条
    bar_height: int = 10
    white_progress_bar: ProgressBar = ProgressBar(
        bar_height, surface.get_height() - bar_height * 2, surface.get_width() - bar_height * 2, bar_height, "white"
    )
    # 生成黑色帘幕
    BLACK_CURTAIN: ImageSurface = new_surface(surface.get_size()).convert()
    BLACK_CURTAIN.fill(Color.BLACK)
    BLACK_CURTAIN.set_alpha(0)
    # 创建视频文件
    VIDEO: VideoPlayer = VideoPlayer(videoPath)
    VIDEO.pre_init()
    # 播放主循环
    while is_playing is True and VIDEO.is_playing() is True:
        VIDEO.draw(surface)
        skip_button.draw(surface)
        white_progress_bar.set_percentage(VIDEO.get_percentage_played())
        white_progress_bar.draw(surface)
        if skip_button.is_hover() and Controller.mouse.get_pressed(0) and not is_skip:
            is_skip = True
            Music.fade_out(fade_out_in_ms)
        if is_skip is True:
            temp_alpha: int = BLACK_CURTAIN.get_alpha()
            if temp_alpha < 255:
                BLACK_CURTAIN.set_alpha(temp_alpha + 5)
            else:
                is_playing = False
                VIDEO.stop()
            surface.blit(BLACK_CURTAIN, (0, 0))
        Display.flip()


class DialogNavigator(AbstractSurfaceWindow):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, bar_height: int_f, tag: str = ""):
        super().__init__(x, y, width, height, bar_height, tag=tag)

    def _present_content(self, surface: ImageSurface) -> None:
        pass
