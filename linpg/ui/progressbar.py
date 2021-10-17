from .console import *

# 进度条抽象，请勿直接初始化
class AbstractProgressBar(AbstractImageSurface):
    def __init__(self, img: any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str):
        super().__init__(img, x, y, width, height, tag)
        self.__current_percentage: float = 0.0

    # 百分比
    @property
    def percentage(self) -> float:
        return self.__current_percentage

    def get_percentage(self) -> float:
        return self.__current_percentage

    def set_percentage(self, value: float) -> None:
        self.__current_percentage = keep_in_range(value, 0.0, 1.0)


# 进度条简单形式的实现
class ProgressBar(AbstractProgressBar):
    def __init__(self, x: int_f, y: int_f, max_width: int, height: int, color: color_liked, tag: str = ""):
        super().__init__(None, x, y, max_width, height, tag)
        self.color: tuple = Color.get(color)

    def display(self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN) -> None:
        if not self.hidden:
            draw_rect(
                surface,
                self.color,
                new_rect(Pos.add(self.pos, offSet), (int(self.get_width() * self.percentage), self.get_height())),
            )


# 进度条Surface
class ProgressBarSurface(AbstractProgressBar):
    def __init__(
        self,
        imgOnTop: PoI,
        imgOnBottom: PoI,
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        mode: str = "horizontal",
        tag: str = "",
    ) -> None:
        if imgOnTop is not None:
            imgOnTop = IMG.quickly_load(imgOnTop)
        super().__init__(imgOnTop, x, y, max_width, height, tag)
        self.img2 = IMG.quickly_load(imgOnBottom) if imgOnBottom is not None else None
        self._mode: bool = True
        self.set_mode(mode)

    # 模式
    @property
    def mode(self) -> str:
        return self.get_mode()

    def get_mode(self) -> str:
        return "horizontal" if self._mode else "vertical"

    def set_mode(self, mode: str) -> None:
        if mode == "horizontal":
            self._mode = True
        elif mode == "vertical":
            self._mode = False
        else:
            EXCEPTION.fatal("Mode '{}' is not supported!".format(mode))

    # 克隆
    def copy(self):
        return ProgressBarSurface(
            self.img.copy(), self.img2.copy(), self.x, self.y, self.get_width(), self.get_height(), self.get_mode()
        )

    def light_copy(self):
        return ProgressBarSurface(self.img, self.img2, self.x, self.y, self.get_width(), self.get_height(), self.get_mode())

    # 展示
    def display(self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN) -> None:
        if not self.hidden:
            pos = Pos.add(self.pos, offSet)
            surface.blit(IMG.resize(self.img2, self.size), pos)
            if self.percentage > 0:
                imgOnTop = IMG.resize(self.img, self.size)
                if self._mode:
                    surface.blit(
                        imgOnTop.subsurface((0, 0, int(self.get_width() * self.percentage), self.get_height())), pos
                    )
                else:
                    surface.blit(
                        imgOnTop.subsurface((0, 0, self.get_width(), int(self.get_height() * self.percentage))), pos
                    )


# 进度条形式的调整器
class ProgressBarAdjuster(ProgressBarSurface):
    def __init__(
        self,
        imgOnTop: PoI,
        imgOnBottom: PoI,
        indicator_img: PoI,
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        indicator_width: int,
        indicator_height: int,
        mode: str = "horizontal",
        tag: str = "",
    ) -> None:
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode=mode, tag=tag)
        self.__indicator: StaticImage = StaticImage(indicator_img, 0, 0, indicator_width, indicator_height)

    # 展示
    def display(self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN) -> None:
        if not self.hidden:
            super().display(surface, offSet)
            abs_pos: tuple[number] = Pos.add(self.pos, offSet)
            x: int
            y: int
            if self._mode:
                x, y = Pos.int(
                    Pos.add(
                        (
                            int(self.get_width() * self.percentage - self.__indicator.width / 2),
                            int((self.get_height() - self.__indicator.height) / 2),
                        ),
                        abs_pos,
                    )
                )
                self.__indicator.set_pos(x, y)
                self.__indicator.draw(surface)
                value_font = Font.render(str(round(self.percentage * 100)), Color.WHITE, self.get_height())
                surface.blit(
                    value_font,
                    Pos.int(
                        Pos.add(
                            abs_pos,
                            (
                                self.get_width() + self.__indicator.width * 0.7,
                                (self.get_height() - value_font.get_height()) / 2,
                            ),
                        )
                    ),
                )
            else:
                x, y = Pos.int(
                    Pos.add(
                        (
                            int((self.get_width() - self.__indicator.width) / 2),
                            int(self.get_height() * self.percentage - self.__indicator.height / 2),
                        ),
                        abs_pos,
                    )
                )
                self.__indicator.set_pos(x, y)
                self.__indicator.draw(surface)
                value_font = Font.render(str(round(self.percentage * 100)), Color.WHITE, self.get_width())
                surface.blit(
                    value_font,
                    Pos.int(
                        Pos.add(
                            abs_pos,
                            (
                                (self.get_width() - value_font.get_width()) / 2,
                                self.get_height() + self.__indicator.height * 0.7,
                            ),
                        )
                    ),
                )
            mouse_x: int
            mouse_y: int
            mouse_x, mouse_y = Pos.subtract(Controller.mouse.pos, offSet)
            if self.is_hover((mouse_x, mouse_y)):
                if Controller.mouse.get_pressed(0):
                    self.set_percentage(
                        (mouse_x - self.x) / self.get_width() if self._mode else (mouse_y - self.y) / self.get_height()
                    )
                elif Controller.get_event("scroll_down"):
                    self.set_percentage(min(round(self.percentage + 0.01, 2), 1.0))
                elif Controller.get_event("scroll_up"):
                    self.set_percentage(max(round(self.percentage - 0.01, 2), 0.0))


# 动态进度条Surface
class DynamicProgressBarSurface(ProgressBarSurface):
    def __init__(
        self,
        imgOnTop: PoI,
        imgOnBottom: PoI,
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        mode: str = "horizontal",
    ):
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode)
        self._percentage_to_be = 0
        self.__perecent_update_each_time = 0
        self.__total_update_intervals = 10

    # 数据准确度
    @property
    def accuracy(self) -> int:
        return self.__total_update_intervals * 100

    # 百分比
    @property
    def percentage(self) -> float:
        return self._percentage_to_be / self.accuracy

    @property
    def __real_current_percentage(self) -> number:
        return super().get_percentage() * self.accuracy

    def get_percentage(self) -> float:
        return self._percentage_to_be / self.accuracy

    def set_percentage(self, value: float) -> None:
        self._percentage_to_be = keep_in_range(value, 0.0, 1.0) * self.accuracy
        self.__perecent_update_each_time = (
            self._percentage_to_be - self.__real_current_percentage
        ) / self.__total_update_intervals

    def copy(self):
        return DynamicProgressBarSurface(
            self.img.copy(), self.img2.copy(), self.x, self.y, self.get_width(), self.get_height(), self.get_mode()
        )

    def light_copy(self):
        return DynamicProgressBarSurface(
            self.img, self.img2, self.x, self.y, self.get_width(), self.get_height(), self.get_mode()
        )

    # 展示
    def _draw_bar(self, surface: ImageSurface, imgOnTop: ImageSurface, imgOnBottom: ImageSurface, pos: tuple) -> None:
        # 画出底层图形
        surface.blit(IMG.resize(imgOnBottom, self.size), pos)
        # 检查并更新百分比
        if (
            self.__real_current_percentage < self._percentage_to_be
            and self.__perecent_update_each_time > 0
            or self.__real_current_percentage > self._percentage_to_be
            and self.__perecent_update_each_time < 0
        ):
            super().set_percentage(super().get_percentage() + self.__perecent_update_each_time / self.accuracy)
        elif self.__real_current_percentage != self._percentage_to_be:
            super().set_percentage(self._percentage_to_be / self.accuracy)
        # 画出图形
        if super().get_percentage() > 0:
            img_on_top_t = IMG.resize(imgOnTop, self.size)
            if self._mode:
                if self.__real_current_percentage < self._percentage_to_be:
                    img2 = IMG.crop(
                        img_on_top_t,
                        size=(int(self.get_width() * self._percentage_to_be / self.accuracy), self.get_height()),
                    )
                    img2.set_alpha(100)
                    surface.blit(img2, pos)
                    surface.blit(
                        img_on_top_t.subsurface((0, 0, int(self.get_width() * super().get_percentage()), self.get_height())),
                        pos,
                    )
                else:
                    if self.__real_current_percentage > self._percentage_to_be:
                        img2 = IMG.crop(
                            img_on_top_t, size=(int(self.get_width() * super().get_percentage()), self.get_height())
                        )
                        img2.set_alpha(100)
                        surface.blit(img2, pos)
                    surface.blit(
                        img_on_top_t.subsurface(
                            (0, 0, int(self.get_width() * self._percentage_to_be / self.accuracy), self.get_height())
                        ),
                        pos,
                    )
            else:
                if self.__real_current_percentage < self._percentage_to_be:
                    img2 = IMG.crop(
                        img_on_top_t,
                        size=(self.get_width(), int(self.get_height() * self._percentage_to_be / self.accuracy)),
                    )
                    img2.set_alpha(100)
                    surface.blit(img2, pos)
                    surface.blit(
                        img_on_top_t.subsurface((0, 0, self.get_width(), int(self.get_height() * super().get_percentage()))),
                        pos,
                    )
                else:
                    if self.__real_current_percentage > self._percentage_to_be:
                        img2 = IMG.crop(
                            img_on_top_t, size=(self.get_width(), int(self.get_height() * super().get_percentage()))
                        )
                        img2.set_alpha(100)
                        surface.blit(img2, pos)
                    surface.blit(
                        img_on_top_t.subsurface(
                            (0, 0, self.get_width(), int(self.get_height() * self._percentage_to_be / self.accuracy))
                        ),
                        pos,
                    )

    def display(self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN) -> None:
        if not self.hidden:
            self._draw_bar(surface, self.img, self.img2, Pos.add(self.pos, offSet))
