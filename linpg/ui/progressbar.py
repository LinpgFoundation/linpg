from .console import *


# 进度条抽象，请勿直接初始化
class AbstractProgressBar(AbstractSurface, metaclass=ABCMeta):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, tag: str):
        super().__init__(x, y, width, height, tag)
        self.__current_percentage: float = 0.0

    # 百分比
    @property
    def percentage(self) -> float:
        return self.get_percentage()

    def get_percentage(self) -> float:
        return self.__current_percentage

    def set_percentage(self, value: float) -> None:
        self.__current_percentage = round(Numbers.keep_number_in_range(value, 0, 1), 5)


# 简单的分数百分比条的实现
class SimpleRectPointsBar(AbstractProgressBar):
    __FONT: Font = Font()

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
        super().__init__(x, y, max_width, height, tag)
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
        back_color: color_liked | None = None,
        outline_color: color_liked | None = None,
        font_color: color_liked | None = None,
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
            self.__FONT.update(int(self.get_height() * 0.6))
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
            _surface.blit(
                _text,
                (
                    bar_rect.x + (bar_rect.width - _text.get_width()) // 2,
                    bar_rect.y + (bar_rect.height - _text.get_height()) // 2,
                ),
            )


# 进度条形式的调整器
class Slider(AbstractProgressBar):
    def __init__(
        self,
        x: int_f,
        y: int_f,
        max_width: int,
        height: int,
        mode: Axis = Axis.HORIZONTAL,
        color: color_liked = Colors.WHITE,
        tag: str = "",
    ) -> None:
        super().__init__(x, y, max_width, height, tag)
        # 模式
        self.axis_mode: Axis = mode
        self.__color: tuple[int, int, int, int] = Colors.get(color)

    # 返回一个复制
    def copy(self) -> "Slider":
        return Slider(
            self.x,
            self.y,
            self.width,
            self.height,
            self.axis_mode,
            self.__color,
            self.tag,
        )

    def _draw_indicator(self, _surface: ImageSurface, x: int, y: int) -> None:
        if self.axis_mode is Axis.HORIZONTAL:
            x -= self.width // 20
            y -= self.height // 4
            Draw.rect(_surface, self.__color, (x, y, self.width // 10, self.height * 3 // 2))
        else:
            x -= self.width // 4
            y -= self.height // 20
            Draw.rect(_surface, self.__color, (x, y, self.width * 3 // 2, self.height // 10), 1)

    # 展示
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if not self.is_visible():
            return
        x, y = Coordinates.add(self.pos, offSet)
        _length: int = 0
        # draw rect filled
        if self.percentage > 0:
            if self.axis_mode is Axis.HORIZONTAL:
                _length = int(self.get_width() * self.percentage)
                Draw.rect(_surface, self.__color, (x, y, _length, self.get_height()))
            else:
                _length = int(self.get_height() * self.percentage)
                Draw.rect(_surface, self.__color, (x, y, self.get_width(), _length))
        # draw rect outline
        Draw.rect(_surface, self.__color, (x, y, self.get_width(), self.get_height()), 1)
        # draw other components
        if self.axis_mode is Axis.HORIZONTAL:
            self._draw_indicator(_surface, x + _length, y)
            value_font = Fonts.render(round(self.percentage * 100), Colors.WHITE, self.get_height())
            _surface.blit(value_font, (int(self.get_width() * 1.1) + x, (self.get_height() - value_font.get_height()) // 2 + y))
        else:
            self._draw_indicator(_surface, x, y + _length)
            value_font = Fonts.render(round(self.percentage * 100), Colors.WHITE, self.get_width())
            _surface.blit(value_font, ((self.get_width() - value_font.get_width()) // 2 + x, int(self.get_height() * 1.1) + y))
        # 处理事件
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
