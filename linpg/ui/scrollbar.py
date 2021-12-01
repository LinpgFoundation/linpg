from .dropdown import *

# 同一时刻会展示2个scrollbar的Surface
class AbstractScrollbarsSurface:
    def __init__(self) -> None:
        self._button_tickness: int = 20
        self._move_speed: int = 20
        self._bar_color: tuple[int] = Color.WHITE

    # 获取surface宽度（子类需要实现）
    def get_surface_width(self) -> int:
        EXCEPTION.fatal("get_surface_width()", 1)

    # 获取surface高度（子类需要实现）
    def get_surface_height(self) -> int:
        EXCEPTION.fatal("get_surface_height()", 1)

    # 获取scrollbar的颜色
    def get_bar_color(self) -> tuple[int]:
        return self._bar_color

    # 修改scrollbar的颜色
    def set_bar_color(self, color: color_liked) -> None:
        self._bar_color = Color.get(color)

    # 获取滚动条的Rect
    def _get_right_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Rect:
        return (
            Rect(
                int(self.right - self._button_tickness + off_set_x),
                int(self.y + off_set_y),
                self._button_tickness,
                self.get_height(),
            )
            if self.get_surface_height() > self.get_height()
            else NULL_RECT
        )

    def _get_bottom_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Rect:
        return (
            Rect(
                int(self.x + off_set_x),
                int(self.bottom - self._button_tickness + off_set_y),
                self.get_width(),
                self._button_tickness,
            )
            if self.get_surface_width() > self.get_width()
            else NULL_RECT
        )

    # 获取滚动条按钮的Rect
    def _get_right_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Rect:
        return (
            Rect(
                int(self.right - self._button_tickness + off_set_x),
                int(self.y - self.get_height() * self.local_y / self.get_surface_height() + off_set_y),
                self._button_tickness,
                int(self.get_height() * self.get_height() / self.get_surface_height()),
            )
            if self.get_surface_height() > self.get_height()
            else NULL_RECT
        )

    def _get_bottom_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Rect:
        return (
            Rect(
                int(self.x - self.get_width() * self.local_x / self.get_surface_width() + off_set_x),
                int(self.bottom - self._button_tickness + off_set_y),
                int(self.get_width() * self.get_width() / self.get_surface_width()),
                self._button_tickness,
            )
            if self.get_surface_width() > self.get_width()
            else NULL_RECT
        )

    def display_scrollbar(self, surface: ImageSurface, off_set: tuple = ORIGIN) -> None:
        # 获取滚轮条
        right_scroll_bar_rect: Rect = self._get_right_scroll_bar_rect(off_set[0], off_set[1])
        right_scroll_button_rect: Rect = self._get_right_scroll_button_rect(off_set[0], off_set[1])
        bottom_scroll_bar_rect: Rect = self._get_bottom_scroll_bar_rect(off_set[0], off_set[1])
        bottom_scroll_button_rect: Rect = self._get_bottom_scroll_button_rect(off_set[0], off_set[1])
        # 获取鼠标坐标
        if self.is_hovered(off_set):
            if Controller.mouse.get_pressed(0):
                if right_scroll_bar_rect.is_hovered():
                    if right_scroll_button_rect.is_hovered():
                        self.add_local_y(Controller.mouse.y_moved * (self.get_surface_height() / self.height))
                    else:
                        self.set_local_y(
                            (self.y - Controller.mouse.y + right_scroll_button_rect.height / 2)
                            / right_scroll_bar_rect.height
                            * self.get_surface_height()
                        )
                if bottom_scroll_bar_rect.is_hovered():
                    if bottom_scroll_button_rect.is_hovered():
                        self.add_local_x(Controller.mouse.x_moved * (self.get_surface_width() / self.width))
                    else:
                        self.set_local_x(
                            (self.x - Controller.mouse.x + bottom_scroll_button_rect.width / 2)
                            / bottom_scroll_bar_rect.width
                            * self.get_surface_width()
                        )
            if Controller.get_event("scroll_up"):
                if self._get_right_scroll_bar_rect(off_set[0], off_set[1]):
                    self.add_local_y(self._move_speed)
                if self._get_bottom_scroll_bar_rect(off_set[0], off_set[1]):
                    self.subtract_local_x(self._move_speed)
            if Controller.get_event("scroll_down"):
                if self._get_right_scroll_bar_rect(off_set[0], off_set[1]):
                    self.subtract_local_y(self._move_speed)
                if self._get_bottom_scroll_bar_rect(off_set[0], off_set[1]):
                    self.add_local_x(self._move_speed)
        # 防止local坐标越界
        if self.local_y > 0:
            self.set_local_y(0)
        elif self.get_surface_height() > self.get_height():
            if (local_y_max := self.get_height() - self.get_surface_height()) > self.local_y:
                self.set_local_y(local_y_max)
        if self.local_x > 0:
            self.set_local_x(0)
        elif self.get_surface_width() > self.get_width():
            if (local_x_max := self.get_width() - self.get_surface_width()) > self.local_x:
                self.set_local_x(local_x_max)
        # 画出滚动条
        if right_scroll_button_rect is not NULL_RECT:
            draw_rect(surface, self._bar_color, right_scroll_button_rect)
        if right_scroll_bar_rect is not NULL_RECT:
            draw_rect(surface, self._bar_color, right_scroll_bar_rect, 2)
        if bottom_scroll_button_rect is not NULL_RECT:
            draw_rect(surface, self._bar_color, bottom_scroll_button_rect)
        if bottom_scroll_bar_rect is not NULL_RECT:
            draw_rect(surface, self._bar_color, bottom_scroll_bar_rect, 2)


# 同一时刻只会拥有一个scrollbar的Surface
class AbstractSurfaceWithScrollbar(SurfaceWithLocalPos, AbstractScrollbarsSurface):
    def __init__(self) -> None:
        SurfaceWithLocalPos.__init__(self)
        AbstractScrollbarsSurface.__init__(self)
        self._mode: bool = False
        self.__scroll_bar_pos: bool = True
        self.__is_holding_scroll_button = False

    # 模式
    @property
    def mode(self) -> str:
        return "vertical" if not self._mode else "horizontal"

    def get_mode(self) -> str:
        return "vertical" if not self._mode else "horizontal"

    def set_mode(self, mode: str) -> None:
        if mode == "horizontal":
            self._mode = True
        elif mode == "vertical":
            self._mode = False
        else:
            EXCEPTION.fatal("Mode '{}' is not supported!".format(mode))

    def switch_mode(self) -> None:
        self._mode = not self._mode
        self.set_local_pos(0, 0)
        self.clear()

    # 滚动条位置
    @property
    def scroll_bar_pos(self) -> str:
        return self.get_scroll_bar_pos()

    def get_scroll_bar_pos(self) -> str:
        if not self._mode:
            return "right" if not self.__scroll_bar_pos else "left"
        else:
            return "bottom" if not self.__scroll_bar_pos else "top"

    def set_scroll_bar_pos(self, pos: str) -> None:
        if pos == "left":
            if not self._mode:
                self.__scroll_bar_pos = True
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the left during horizontal mode!")
        elif pos == "right":
            if not self._mode:
                self.__scroll_bar_pos = False
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the right during horizontal mode!")
        elif pos == "top":
            if self._mode is True:
                self.__scroll_bar_pos = True
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the top during vertical mode!")
        elif pos == "bottom":
            if self._mode is True:
                self.__scroll_bar_pos = False
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the bottom during vertical mode!")
        else:
            EXCEPTION.fatal(
                'Scroll bar position "{}" is not supported! Try sth like "right" or "bottom" instead.'.format(pos)
            )

    # 获取滚动条按钮的Rect
    def _get_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Rect:
        if not self._mode:
            if not self.__scroll_bar_pos:
                return self._get_right_scroll_button_rect(off_set_x, off_set_y)
            elif self.get_surface_height() > self.get_height():
                return Rect(
                    int(self.abs_x + off_set_x),
                    int(self.y - self.get_height() * self.local_y / self.get_surface_height() + off_set_y),
                    self._button_tickness,
                    int(self.get_height() * self.get_height() / self.get_surface_height()),
                )
        else:
            if not self.__scroll_bar_pos:
                return self._get_bottom_scroll_button_rect(off_set_x, off_set_y)
            elif self.get_surface_width() > self.get_width():
                return Rect(
                    int(self.x - self.get_width() * self.local_x / self.get_surface_width() + off_set_x),
                    int(self.abs_y + off_set_y),
                    int(self.get_width() * self.get_width() / self.get_surface_width()),
                    self._button_tickness,
                )
        return NULL_RECT

    # 获取滚动条的Rect
    def _get_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Rect:
        if not self._mode:
            if not self.__scroll_bar_pos:
                return self._get_right_scroll_bar_rect(off_set_x, off_set_y)
            elif self.get_surface_height() > self.get_height():
                return Rect(int(self.abs_x + off_set_x), int(self.y + off_set_y), self._button_tickness, self.get_height())
        else:
            if not self.__scroll_bar_pos:
                return self._get_bottom_scroll_bar_rect(off_set_x, off_set_y)
            elif self.get_surface_width() > self.get_width():
                return Rect(int(self.x + off_set_x), int(self.abs_y + off_set_y), self.get_width(), self._button_tickness)
        return NULL_RECT

    def display_scrollbar(self, surface: ImageSurface, off_set: tuple = ORIGIN) -> None:
        # 获取滚轮条
        scroll_bar_rect: Rect = self._get_scroll_bar_rect(off_set[0], off_set[1])
        scroll_button_rect: Rect = self._get_scroll_button_rect(off_set[0], off_set[1])
        # 获取鼠标坐标
        if self.is_hovered(off_set):
            # 查看与鼠标有关的事件
            if Controller.mouse.get_pressed(0):
                if scroll_bar_rect.is_hovered():
                    # 根据按钮位置调整本地坐标
                    if scroll_button_rect.is_hovered():
                        self.__is_holding_scroll_button = True
                    elif not self._mode:
                        self.set_local_y(
                            (self.y - Controller.mouse.y + scroll_button_rect.height / 2)
                            / scroll_bar_rect.height
                            * self.get_surface_height()
                        )
                    else:
                        self.set_local_x(
                            (self.x - Controller.mouse.x + scroll_button_rect.width / 2)
                            / scroll_bar_rect.width
                            * self.get_surface_width()
                        )
            else:
                self.__is_holding_scroll_button = False
            if Controller.get_event("scroll_up"):
                if not self._mode:
                    self.add_local_y(self._move_speed)
                else:
                    self.subtract_local_x(self._move_speed)
            if Controller.get_event("scroll_down"):
                if not self._mode:
                    self.subtract_local_y(self._move_speed)
                else:
                    self.add_local_x(self._move_speed)
        else:
            self.__is_holding_scroll_button = False
        # 需要调整本地坐标
        if self.__is_holding_scroll_button is True:
            if not self._mode:
                self.add_local_y(Controller.mouse.y_moved * (self.get_surface_height() / self.height))
            else:
                self.add_local_x(Controller.mouse.x_moved * (self.get_surface_width() / self.width))
        # 防止local坐标越界
        if not self._mode:
            if self.local_y > 0:
                self.set_local_y(0)
            elif (
                self.get_surface_height() > self.get_height()
                and (local_y_max := self.get_height() - self.get_surface_height()) > self.local_y
            ):
                self.set_local_y(local_y_max)
        elif self.local_x > 0:
            self.set_local_x(0)
        elif (
            self.get_surface_width() > self.get_width()
            and (local_x_max := self.get_width() - self.get_surface_width()) > self.local_x
        ):
            self.set_local_x(local_x_max)
        # 画出滚动条
        if scroll_button_rect is not NULL_RECT:
            draw_rect(surface, self._bar_color, scroll_button_rect)
        if scroll_bar_rect is not NULL_RECT:
            draw_rect(surface, self._bar_color, scroll_bar_rect, 2)
