from .console import *


# 进度条抽象，请勿直接初始化
class AbstractProgressBar(AbstractImageSurface, metaclass=ABCMeta):
    def __init__(self, img: Any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str):
        super().__init__(img, x, y, width, height, tag)
        self.__current_percentage: float = 0.0

    # 百分比
    @property
    def percentage(self) -> float:
        return self.get_percentage()

    def get_percentage(self) -> float:
        return self.__current_percentage

    def set_percentage(self, value: float) -> None:
        self.__current_percentage = round(Numbers.keep_number_in_range(value, 0, 1), 5)


# 进度条简单形式的实现
class ProgressBar(AbstractProgressBar):
    def __init__(self, x: int_f, y: int_f, max_width: int, height: int, color: color_liked, tag: str = ""):
        super().__init__(None, x, y, max_width, height, tag)
        self.__color: tuple[int, int, int, int] = Colors.get(color)

    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            Draw.rect(_surface, self.__color, (Coordinates.add(self.pos, offSet), (int(self.get_width() * self.percentage), self.get_height())))


# 简单的分数百分比条的实现
class SimpleRectPointsBar(AbstractProgressBar):
    __FONT: FontGenerator = FontGenerator()

    def __init__(
        self,
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        front_color: color_liked,
        back_color: color_liked,
        outline_color: color_liked,
        font_color: color_liked,
        tag: str = "",
    ):
        super().__init__(None, x, y, max_width, height, tag)
        self.__back_color: tuple[int, int, int, int] = Colors.get(back_color)
        self.__front_color: tuple[int, int, int, int] = Colors.get(front_color)
        self.__outline_color: tuple[int, int, int, int] = Colors.get(outline_color)
        self.__font_color: tuple[int, int, int, int] = Colors.get(font_color)
        self.__current_point: int = 0
        self.__max_point: int = 1

    # 重写百分比的计算方式
    def get_percentage(self) -> float:
        return self.__current_point / self.__max_point

    # 设置当前值
    def set_current_point(self, value: int) -> None:
        self.__current_point = Numbers.keep_int_in_range(value, 0, self.__max_point)

    # 设置最大值
    def set_max_point(self, value: int) -> None:
        self.__max_point = max(value, 1)

    # 设置颜色
    def set_color(
        self,
        front_color: color_liked,
        back_color: Optional[color_liked] = None,
        outline_color: Optional[color_liked] = None,
        font_color: Optional[color_liked] = None,
    ) -> None:
        self.__front_color = Colors.get(front_color)
        if back_color is not None:
            self.__back_color = Colors.get(back_color)
        if outline_color is not None:
            self.__outline_color = Colors.get(outline_color)
        if font_color is not None:
            self.__font_color = Colors.get(font_color)

    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            # 更新文字模块
            self.__FONT.check_for_update(int(self.get_height() * 0.6))
            # 根据当前值计算条长度
            _width: int = int(self.get_width() * self.__current_point / self.__max_point)
            # 原先的绝对x
            original_x: int = self.pos[0] + offSet[0]
            # 生成一个rect用于渲染
            bar_rect = Rectangle(self.pos[0] + offSet[0], self.pos[1] + offSet[1], _width, self.get_height())
            # 渲染多个矩形
            bar_rect.draw_outline(_surface, self.__front_color, 0)
            bar_rect.move_right(_width - 1)
            bar_rect.set_width(self.get_width() - _width)
            bar_rect.draw_outline(_surface, self.__back_color, 0)
            bar_rect.set_width(self.get_width() + 1)
            bar_rect.set_left(original_x - 1)
            bar_rect.draw_outline(_surface, self.__outline_color)
            # 渲染数值文字并画出
            _text: ImageSurface = self.__FONT.render(f"{self.__current_point} / {self.__max_point}", self.__font_color)
            _surface.blit(_text, (bar_rect.x + (bar_rect.width - _text.get_width()) // 2, bar_rect.y + (bar_rect.height - _text.get_height()) // 2))


# 进度条Surface
class ProgressBarSurface(AbstractProgressBar):
    def __init__(
        self, imgOnTop: Optional[PoI], imgOnBottom: Optional[PoI], x: int_f, y: int_f, max_width: int, height: int, mode: Axis = Axis.HORIZONTAL, tag: str = ""
    ) -> None:
        if imgOnTop is not None:
            imgOnTop = Images.quickly_load(imgOnTop)
        super().__init__(imgOnTop, x, y, max_width, height, tag)
        self._img2: Optional[ImageSurface] = Images.quickly_load(imgOnBottom) if imgOnBottom is not None else None
        # 模式
        self.axis_mode: Axis = mode

    # 克隆
    def copy(self) -> "ProgressBarSurface":
        return ProgressBarSurface(
            self.get_image_copy(), self._img2.copy() if self._img2 is not None else None, self.x, self.y, self.get_width(), self.get_height(), self.axis_mode
        )

    def light_copy(self) -> "ProgressBarSurface":
        return ProgressBarSurface(self._get_image_reference(), self._img2, self.x, self.y, self.get_width(), self.get_height(), self.axis_mode)

    # 展示
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            pos = Coordinates.add(self.pos, offSet)
            if self._img2 is not None:
                _surface.blit(Images.resize(self._img2, self.size), pos)
            if self.percentage > 0:
                imgOnTop = Images.resize(self._get_image_reference(), self.size)
                if self.axis_mode is Axis.HORIZONTAL:
                    _surface.blit(imgOnTop.subsurface(0, 0, int(self.get_width() * self.percentage), self.get_height()), pos)
                else:
                    _surface.blit(imgOnTop.subsurface(0, 0, self.get_width(), int(self.get_height() * self.percentage)), pos)


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
        mode: Axis = Axis.HORIZONTAL,
        tag: str = "",
    ) -> None:
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode=mode, tag=tag)
        self.__indicator: StaticImage = StaticImage(indicator_img, 0, 0, indicator_width, indicator_height)

    # 展示
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            super().display(_surface, offSet)
            abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            x: int
            y: int
            if self.axis_mode is Axis.HORIZONTAL:
                x, y = Coordinates.add(
                    (int(self.get_width() * self.percentage - self.__indicator.width / 2), (self.get_height() - self.__indicator.height) // 2), abs_pos
                )
                self.__indicator.set_pos(x, y)
                self.__indicator.draw(_surface)
                value_font = Font.render(str(round(self.percentage * 100)), Colors.WHITE, self.get_height())
                _surface.blit(
                    value_font,
                    Coordinates.add(abs_pos, (self.get_width() + self.__indicator.width * 7 // 10, (self.get_height() - value_font.get_height()) / 2)),
                )
            else:
                x, y = Coordinates.add(
                    ((self.get_width() - self.__indicator.width) // 2, int(self.get_height() * self.percentage - self.__indicator.height / 2)), abs_pos
                )

                self.__indicator.set_pos(x, y)
                self.__indicator.draw(_surface)
                value_font = Font.render(str(round(self.percentage * 100)), Colors.WHITE, self.get_width())
                _surface.blit(
                    value_font,
                    Coordinates.add(abs_pos, ((self.get_width() - value_font.get_width()) / 2, self.get_height() + self.__indicator.height * 7 // 10)),
                )
            if self.is_hovered(offSet):
                if Controller.mouse.get_pressed(0):
                    self.set_percentage(
                        (Controller.mouse.x - offSet[0] - self.x) / self.get_width()
                        if self.axis_mode is Axis.HORIZONTAL
                        else (Controller.mouse.y - offSet[1] - self.y) / self.get_height()
                    )
                elif Controller.get_event("scroll_down"):
                    self.set_percentage(min(round(self.percentage + 0.01, 2), 1.0))
                elif Controller.get_event("scroll_up"):
                    self.set_percentage(max(round(self.percentage - 0.01, 2), 0.0))


# 动态进度条Surface
class DynamicProgressBarSurface(ProgressBarSurface):
    def __init__(self, imgOnTop: Optional[PoI], imgOnBottom: Optional[PoI], x: int_f, y: int_f, max_width: int, height: int, mode: Axis = Axis.HORIZONTAL):
        super().__init__(imgOnTop, imgOnBottom, x, y, max_width, height, mode)
        self._percentage_to_be: float = 0.0
        self.__percent_update_each_time: float = 0.0
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
        self._percentage_to_be = round(Numbers.keep_number_in_range(value, 0, 1) * self.accuracy, 5)
        self.__percent_update_each_time = round((self._percentage_to_be - self.__real_current_percentage) / self.__total_update_intervals, 5)

    def copy(self) -> "DynamicProgressBarSurface":
        return DynamicProgressBarSurface(
            self.get_image_copy(), self._img2.copy() if self._img2 is not None else None, self.x, self.y, self.get_width(), self.get_height(), self.axis_mode
        )

    def light_copy(self) -> "DynamicProgressBarSurface":
        return DynamicProgressBarSurface(self._get_image_reference(), self._img2, self.x, self.y, self.get_width(), self.get_height(), self.axis_mode)

    # 获取上方图片（子类可根据需求修改）
    def _get_img_on_top(self) -> ImageSurface:
        return self._get_image_reference()  # type: ignore

    # 展示
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            _abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            # 画出底层图形
            if self._img2 is not None:
                _surface.blit(Images.resize(self._img2, self.size), _abs_pos)
            # 检查并更新百分比
            if (
                self.__real_current_percentage < self._percentage_to_be
                and self.__percent_update_each_time > 0
                or self.__real_current_percentage > self._percentage_to_be
                and self.__percent_update_each_time < 0
            ):
                super().set_percentage(super().get_percentage() + self.__percent_update_each_time / self.accuracy)
            elif self.__real_current_percentage != self._percentage_to_be:
                super().set_percentage(self._percentage_to_be / self.accuracy)
            # 画出图形
            if super().get_percentage() > 0:
                img_on_top_t = Images.resize(self._get_img_on_top(), self.size)
                if self.axis_mode is Axis.HORIZONTAL:
                    if self.__real_current_percentage < self._percentage_to_be:
                        img2 = img_on_top_t.subsurface((0, 0, int(self.get_width() * self._percentage_to_be / self.accuracy), self.get_height()))
                        img2.set_alpha(100)
                        _surface.blit(img2, _abs_pos)
                        _surface.blit(img_on_top_t.subsurface(0, 0, int(self.get_width() * super().get_percentage()), self.get_height()), _abs_pos)
                    else:
                        if self.__real_current_percentage > self._percentage_to_be:
                            img2 = img_on_top_t.subsurface((0, 0, int(self.get_width() * super().get_percentage()), self.get_height()))
                            img2.set_alpha(100)
                            _surface.blit(img2, _abs_pos)
                        _surface.blit(
                            img_on_top_t.subsurface((0, 0, int(self.get_width() * self._percentage_to_be / self.accuracy), self.get_height())), _abs_pos
                        )
                else:
                    if self.__real_current_percentage < self._percentage_to_be:
                        img2 = img_on_top_t.subsurface((0, 0, self.get_width(), int(self.get_height() * self._percentage_to_be / self.accuracy)))
                        img2.set_alpha(100)
                        _surface.blit(img2, _abs_pos)
                        _surface.blit(img_on_top_t.subsurface(0, 0, self.get_width(), int(self.get_height() * super().get_percentage())), _abs_pos)
                    else:
                        if self.__real_current_percentage > self._percentage_to_be:
                            img2 = img_on_top_t.subsurface((0, 0, self.get_width(), int(self.get_height() * super().get_percentage())))
                            img2.set_alpha(100)
                            _surface.blit(img2, _abs_pos)
                        _surface.blit(
                            img_on_top_t.subsurface((0, 0, self.get_width(), int(self.get_height() * self._percentage_to_be / self.accuracy))), _abs_pos
                        )
