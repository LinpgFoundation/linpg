from .console import *

# 进度条抽象，请勿直接初始化
class AbstractProgressBar(AbstractImageSurface):
    def __init__(self, img: Any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str):
        super().__init__(img, x, y, width, height, tag)
        self.__current_percentage: float = 0.0

    # 百分比
    @property
    def percentage(self) -> float:
        return self.__current_percentage

    def get_percentage(self) -> float:
        return self.__current_percentage

    def set_percentage(self, value: float) -> None:
        self.__current_percentage = round(keep_number_in_range(value, 0, 1), 5)


# 进度条简单形式的实现
class ProgressBar(AbstractProgressBar):
    def __init__(self, x: int_f, y: int_f, max_width: int, height: int, color: color_liked, tag: str = ""):
        super().__init__(None, x, y, max_width, height, tag)
        self.color: tuple[int, int, int, int] = Colors.get(color)

    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            Draw.rect(
                surface,
                self.color,
                (Coordinates.add(self.pos, offSet), (int(self.get_width() * self.percentage), self.get_height())),
            )


# 进度条Surface
class ProgressBarSurface(AbstractProgressBar):
    def __init__(
        self,
        imgOnTop: Optional[PoI],
        imgOnBottom: Optional[PoI],
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        mode: str = "horizontal",
        tag: str = "",
    ) -> None:
        if imgOnTop is not None:
            imgOnTop = RawImg.quickly_load(imgOnTop)
        super().__init__(imgOnTop, x, y, max_width, height, tag)
        self._img2: Optional[ImageSurface] = RawImg.quickly_load(imgOnBottom) if imgOnBottom is not None else None
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
    def copy(self) -> "ProgressBarSurface":
        return ProgressBarSurface(
            self.img.copy(),
            self._img2.copy() if self._img2 is not None else None,
            self.x,
            self.y,
            self.get_width(),
            self.get_height(),
            self.get_mode(),
        )

    def light_copy(self) -> "ProgressBarSurface":
        return ProgressBarSurface(self.img, self._img2, self.x, self.y, self.get_width(), self.get_height(), self.get_mode())

    # 展示
    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            pos = Coordinates.add(self.pos, offSet)
            if self._img2 is not None:
                surface.blit(RawImg.resize(self._img2, self.size), pos)
            if self.percentage > 0:
                imgOnTop = RawImg.resize(self.img, self.size)
                if self._mode:
                    surface.blit(imgOnTop.subsurface((0, 0, int(self.get_width() * self.percentage), self.get_height())), pos)
                else:
                    surface.blit(imgOnTop.subsurface((0, 0, self.get_width(), int(self.get_height() * self.percentage))), pos)


# 进度条形式的调整器
class ProgressBarAdjuster(ProgressBarSurface):
    def __init__(
        self,
        imgOnTop: Optional[PoI],
        imgOnBottom: Optional[PoI],
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
    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            super().display(surface, offSet)
            abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            x: int
            y: int
            if self._mode is True:
                x, y = Coordinates.add(
                    (
                        int(self.get_width() * self.percentage - self.__indicator.width / 2),
                        (self.get_height() - self.__indicator.height) // 2,
                    ),
                    abs_pos,
                )
                self.__indicator.set_pos(x, y)
                self.__indicator.draw(surface)
                value_font = Font.render(str(round(self.percentage * 100)), Colors.WHITE, self.get_height())
                surface.blit(
                    value_font,
                    Coordinates.add(
                        abs_pos,
                        (self.get_width() + self.__indicator.width * 0.7, (self.get_height() - value_font.get_height()) / 2),
                    ),
                )
            else:
                x, y = Coordinates.add(
                    (
                        (self.get_width() - self.__indicator.width) // 2,
                        int(self.get_height() * self.percentage - self.__indicator.height / 2),
                    ),
                    abs_pos,
                )

                self.__indicator.set_pos(x, y)
                self.__indicator.draw(surface)
                value_font = Font.render(str(round(self.percentage * 100)), Colors.WHITE, self.get_width())
                surface.blit(
                    value_font,
                    Coordinates.add(
                        abs_pos,
                        ((self.get_width() - value_font.get_width()) / 2, self.get_height() + self.__indicator.height * 0.7),
                    ),
                )
            if self.is_hovered(offSet):
                if Controller.mouse.get_pressed(0):
                    self.set_percentage(
                        (Controller.mouse.x - offSet[0] - self.x) / self.get_width()
                        if self._mode is True
                        else (Controller.mouse.y - offSet[1] - self.y) / self.get_height()
                    )
                elif Controller.get_event("scroll_down"):
                    self.set_percentage(min(round(self.percentage + 0.01, 2), 1.0))
                elif Controller.get_event("scroll_up"):
                    self.set_percentage(max(round(self.percentage - 0.01, 2), 0.0))


# 动态进度条Surface
class DynamicProgressBarSurface(ProgressBarSurface):
    def __init__(
        self,
        imgOnTop: Optional[PoI],
        imgOnBottom: Optional[PoI],
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        mode: str = "horizontal",
    ):
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode)
        self._percentage_to_be: float = 0.0
        self.__perecent_update_each_time: float = 0.0
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
        self._percentage_to_be = round(keep_number_in_range(value, 0, 1) * self.accuracy, 5)
        self.__perecent_update_each_time = round(
            (self._percentage_to_be - self.__real_current_percentage) / self.__total_update_intervals, 5
        )

    def copy(self) -> "DynamicProgressBarSurface":
        return DynamicProgressBarSurface(
            self.img.copy(),
            self._img2.copy() if self._img2 is not None else None,
            self.x,
            self.y,
            self.get_width(),
            self.get_height(),
            self.get_mode(),
        )

    def light_copy(self) -> "DynamicProgressBarSurface":
        return DynamicProgressBarSurface(
            self.img, self._img2, self.x, self.y, self.get_width(), self.get_height(), self.get_mode()
        )

    # 获取上方图片（子类可根据需求修改）
    def _get_img_on_top(self) -> ImageSurface:
        return self.img  # type: ignore

    # 展示
    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            _abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            # 画出底层图形
            if self._img2 is not None:
                surface.blit(RawImg.resize(self._img2, self.size), _abs_pos)
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
                img_on_top_t = RawImg.resize(self._get_img_on_top(), self.size)
                if self._mode:
                    if self.__real_current_percentage < self._percentage_to_be:
                        img2 = RawImg.crop(
                            img_on_top_t, size=(int(self.get_width() * self._percentage_to_be / self.accuracy), self.get_height())
                        )
                        img2.set_alpha(100)
                        surface.blit(img2, _abs_pos)
                        surface.blit(
                            img_on_top_t.subsurface((0, 0, int(self.get_width() * super().get_percentage()), self.get_height())),
                            _abs_pos,
                        )
                    else:
                        if self.__real_current_percentage > self._percentage_to_be:
                            img2 = RawImg.crop(
                                img_on_top_t, size=(int(self.get_width() * super().get_percentage()), self.get_height())
                            )
                            img2.set_alpha(100)
                            surface.blit(img2, _abs_pos)
                        surface.blit(
                            img_on_top_t.subsurface(
                                (0, 0, int(self.get_width() * self._percentage_to_be / self.accuracy), self.get_height())
                            ),
                            _abs_pos,
                        )
                else:
                    if self.__real_current_percentage < self._percentage_to_be:
                        img2 = RawImg.crop(
                            img_on_top_t, size=(self.get_width(), int(self.get_height() * self._percentage_to_be / self.accuracy))
                        )
                        img2.set_alpha(100)
                        surface.blit(img2, _abs_pos)
                        surface.blit(
                            img_on_top_t.subsurface((0, 0, self.get_width(), int(self.get_height() * super().get_percentage()))),
                            _abs_pos,
                        )
                    else:
                        if self.__real_current_percentage > self._percentage_to_be:
                            img2 = RawImg.crop(
                                img_on_top_t, size=(self.get_width(), int(self.get_height() * super().get_percentage()))
                            )
                            img2.set_alpha(100)
                            surface.blit(img2, _abs_pos)
                        surface.blit(
                            img_on_top_t.subsurface(
                                (0, 0, self.get_width(), int(self.get_height() * self._percentage_to_be / self.accuracy))
                            ),
                            _abs_pos,
                        )
