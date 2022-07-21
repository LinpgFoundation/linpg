from .dropdown import *

# 同一时刻会展示2个scrollbar的Surface
class AbstractScrollbarsSurface(SurfaceWithLocalPos):
    def __init__(self) -> None:
        super().__init__()
        self._button_tickness: int = 20
        self._move_speed: int = 20
        self._bar_color: tuple[int, int, int, int] = Colors.WHITE

    # 获取surface宽度（子类需要实现）
    def get_surface_width(self) -> int:
        EXCEPTION.fatal("get_surface_width()", 1)

    # 获取surface高度（子类需要实现）
    def get_surface_height(self) -> int:
        EXCEPTION.fatal("get_surface_height()", 1)

    # 获取x坐标（子类需实现）
    def get_left(self) -> int:
        EXCEPTION.fatal("get_left()", 1)

    # 获取y坐标（子类需实现）
    def get_top(self) -> int:
        EXCEPTION.fatal("get_top()", 1)

    # 获取x+width坐标（子类需实现）
    def get_right(self) -> int:
        EXCEPTION.fatal("get_right()", 1)

    # 获取y+height坐标（子类需实现）
    def get_bottom(self) -> int:
        EXCEPTION.fatal("get_bottom()", 1)

    # 获取宽度（子类需实现）
    def get_width(self) -> int:
        EXCEPTION.fatal("get_width()", 1)

    # 获取高度（子类需实现）
    def get_height(self) -> int:
        EXCEPTION.fatal("get_height()", 1)

    # 是否被鼠标触碰（子类需实现）
    def is_hovered(self, off_set: Optional[tuple[int, int]] = None) -> bool:
        EXCEPTION.fatal("is_hovered()", 1)

    # 获取scrollbar的颜色
    def get_bar_color(self) -> tuple[int, int, int, int]:
        return self._bar_color

    # 修改scrollbar的颜色
    def set_bar_color(self, color: color_liked) -> None:
        self._bar_color = Colors.get(color)

    # 获取滚动条的Rect
    def _get_right_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Optional[Rectangle]:
        return (
            Rectangle(
                self.get_right() - self._button_tickness + int(off_set_x),
                self.get_top() + int(off_set_y),
                self._button_tickness,
                self.get_height(),
            )
            if self.get_surface_height() > self.get_height()
            else None
        )

    def _get_bottom_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Optional[Rectangle]:
        return (
            Rectangle(
                self.get_left() + int(off_set_x),
                self.get_bottom() - self._button_tickness + int(off_set_y),
                self.get_width(),
                self._button_tickness,
            )
            if self.get_surface_width() > self.get_width()
            else None
        )

    # 获取滚动条按钮的Rect
    def _get_right_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Optional[Rectangle]:
        return (
            Rectangle(
                self.get_right() - self._button_tickness + int(off_set_x),
                int(self.get_top() - self.get_height() * self.local_y / self.get_surface_height() + off_set_y),
                self._button_tickness,
                self.get_height() * self.get_height() // self.get_surface_height(),
            )
            if self.get_surface_height() > self.get_height()
            else None
        )

    def _get_bottom_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Optional[Rectangle]:
        return (
            Rectangle(
                int(self.get_left() - self.get_width() * self.local_x / self.get_surface_width() + off_set_x),
                self.get_bottom() - self._button_tickness + int(off_set_y),
                self.get_width() * self.get_width() // self.get_surface_width(),
                self._button_tickness,
            )
            if self.get_surface_width() > self.get_width()
            else None
        )

    def display_scrollbar(self, _surface: ImageSurface, off_set: tuple[int, int] = ORIGIN) -> None:
        # 获取滚轮条
        right_scroll_bar_rect: Optional[Rectangle] = self._get_right_scroll_bar_rect(off_set[0], off_set[1])
        right_scroll_button_rect: Optional[Rectangle] = self._get_right_scroll_button_rect(off_set[0], off_set[1])
        bottom_scroll_bar_rect: Optional[Rectangle] = self._get_bottom_scroll_bar_rect(off_set[0], off_set[1])
        bottom_scroll_button_rect: Optional[Rectangle] = self._get_bottom_scroll_button_rect(off_set[0], off_set[1])
        # 获取鼠标坐标
        if self.is_hovered(off_set):
            if Controller.mouse.get_pressed(0):
                if (
                    right_scroll_bar_rect is not None
                    and right_scroll_button_rect is not None
                    and right_scroll_bar_rect.is_hovered()
                ):
                    if right_scroll_button_rect.is_hovered():
                        self.add_local_y(Controller.mouse.y_moved * (self.get_surface_height() / self.get_height()))
                    else:
                        self.set_local_y(
                            (self.get_top() - Controller.mouse.y + right_scroll_button_rect.height / 2)
                            / right_scroll_bar_rect.height
                            * self.get_surface_height()
                        )
                if (
                    bottom_scroll_bar_rect is not None
                    and bottom_scroll_button_rect is not None
                    and bottom_scroll_bar_rect.is_hovered()
                ):
                    if bottom_scroll_button_rect.is_hovered():
                        self.add_local_x(Controller.mouse.x_moved * (self.get_surface_width() / self.get_width()))
                    else:
                        self.set_local_x(
                            (self.get_left() - Controller.mouse.x + bottom_scroll_button_rect.width / 2)
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
        if right_scroll_button_rect is not None:
            Draw.rect(_surface, self._bar_color, right_scroll_button_rect.get_rect())
        if right_scroll_bar_rect is not None:
            Draw.rect(_surface, self._bar_color, right_scroll_bar_rect.get_rect(), 2)
        if bottom_scroll_button_rect is not None:
            Draw.rect(_surface, self._bar_color, bottom_scroll_button_rect.get_rect())
        if bottom_scroll_bar_rect is not None:
            Draw.rect(_surface, self._bar_color, bottom_scroll_bar_rect.get_rect(), 2)


# 同一时刻只会拥有一个scrollbar的Surface
class AbstractSurfaceWithScrollbar(AbstractScrollbarsSurface):
    def __init__(self) -> None:
        super().__init__()
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
            EXCEPTION.fatal('Scroll bar position "{}" is not supported! Try sth like "right" or "bottom" instead.'.format(pos))

    # 获取滚动条按钮的Rect
    def _get_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Optional[Rectangle]:
        if not self._mode:
            if not self.__scroll_bar_pos:
                return self._get_right_scroll_button_rect(off_set_x, off_set_y)
            elif self.get_surface_height() > self.get_height():
                return Rectangle(
                    self.abs_x + int(off_set_x),
                    int(self.get_top() - self.get_height() * self.local_y / self.get_surface_height() + off_set_y),
                    self._button_tickness,
                    self.get_height() * self.get_height() // self.get_surface_height(),
                )
        else:
            if not self.__scroll_bar_pos:
                return self._get_bottom_scroll_button_rect(off_set_x, off_set_y)
            elif self.get_surface_width() > self.get_width():
                return Rectangle(
                    int(self.get_left() - self.get_width() * self.local_x / self.get_surface_width() + off_set_x),
                    self.abs_y + int(off_set_y),
                    self.get_width() * self.get_width() // self.get_surface_width(),
                    self._button_tickness,
                )
        return None

    # 获取滚动条的Rect
    def _get_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Optional[Rectangle]:
        if not self._mode:
            if not self.__scroll_bar_pos:
                return self._get_right_scroll_bar_rect(off_set_x, off_set_y)
            elif self.get_surface_height() > self.get_height():
                return Rectangle(
                    self.abs_x + int(off_set_x), self.get_top() + int(off_set_y), self._button_tickness, self.get_height()
                )
        else:
            if not self.__scroll_bar_pos:
                return self._get_bottom_scroll_bar_rect(off_set_x, off_set_y)
            elif self.get_surface_width() > self.get_width():
                return Rectangle(
                    self.get_left() + int(off_set_x), self.abs_y + int(off_set_y), self.get_width(), self._button_tickness
                )
        return None

    def display_scrollbar(self, _surface: ImageSurface, off_set: tuple[int, int] = ORIGIN) -> None:
        # 获取滚轮条
        scroll_bar_rect: Optional[Rectangle] = self._get_scroll_bar_rect(off_set[0], off_set[1])
        scroll_button_rect: Optional[Rectangle] = self._get_scroll_button_rect(off_set[0], off_set[1])
        # 获取鼠标坐标
        if self.is_hovered(off_set):
            # 查看与鼠标有关的事件
            if scroll_bar_rect is not None and scroll_button_rect is not None and Controller.mouse.get_pressed(0):
                if scroll_bar_rect.is_hovered():
                    # 根据按钮位置调整本地坐标
                    if scroll_button_rect.is_hovered():
                        self.__is_holding_scroll_button = True
                    elif not self._mode:
                        self.set_local_y(
                            (self.get_top() - Controller.mouse.y + scroll_button_rect.height / 2)
                            / scroll_bar_rect.height
                            * self.get_surface_height()
                        )
                    else:
                        self.set_local_x(
                            (self.get_left() - Controller.mouse.x + scroll_button_rect.width / 2)
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
                self.add_local_y(Controller.mouse.y_moved * (self.get_surface_height() / self.get_height()))
            else:
                self.add_local_x(Controller.mouse.x_moved * (self.get_surface_width() / self.get_width()))
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
        if scroll_button_rect is not None:
            Draw.rect(_surface, self._bar_color, scroll_button_rect.get_rect())
        if scroll_bar_rect is not None:
            Draw.rect(_surface, self._bar_color, scroll_bar_rect.get_rect(), 2)


# 带有滚动条的Surface容器
class SurfaceContainerWithScrollbar(GameObjectsDictContainer, AbstractSurfaceWithScrollbar):
    def __init__(
        self, img: Optional[PoI], x: int_f, y: int_f, width: int, height: int, mode: str = "horizontal", tag: str = ""
    ) -> None:
        GameObjectsDictContainer.__init__(self, img, x, y, width, height, tag)
        AbstractSurfaceWithScrollbar.__init__(self)
        self.__surface_width: int = 0
        self.__surface_height: int = 0
        self.panding: int = 0
        self.distance_between_item: int = 20
        self.set_mode(mode)
        self.__item_per_line: int = 1

    def get_surface_width(self) -> int:
        return self.__surface_width

    def get_surface_height(self) -> int:
        return self.__surface_height

    # 每一行放多少个物品
    @property
    def item_per_line(self) -> int:
        return self.__item_per_line

    def get_item_per_line(self) -> int:
        return self.__item_per_line

    def set_item_per_line(self, value: int) -> None:
        self.__item_per_line = value

    def switch_mode(self) -> None:
        super().switch_mode()
        self.clear()

    # 把素材画到屏幕上
    def display(self, _surface: ImageSurface, off_set: tuple[int, int] = ORIGIN) -> None:
        self._item_being_hovered = None
        if self.is_visible():
            # 如果有背景图片，则画出
            if self.img is not None:
                _surface.blit(self.img, Coordinates.add(self.pos, off_set))
            # 计算出基础坐标
            current_x: int = self.abs_x + off_set[0]
            current_y: int = self.abs_y + off_set[1]
            if not self._mode:
                current_x += self.panding
            else:
                current_y += self.panding
            # 定义部分用到的变量
            abs_local_y: int
            crop_height: int
            new_height: int
            abs_local_x: int
            crop_width: int
            new_width: int
            item_has_been_dawn_on_this_line: int = 0
            # 画出物品栏里的图片
            for key, item in self._get_container().items():
                if item is not None:
                    if not self._mode:
                        abs_local_y = current_y - self.y
                        if 0 <= abs_local_y < self.get_height():
                            new_height = self.get_height() - abs_local_y
                            if new_height > item.get_height():
                                new_height = item.get_height()
                            new_width = item.get_width()
                            if new_width > self.get_width():
                                new_width = self.get_width()
                            subsurface_rect = Rectangle(0, 0, new_width, new_height)
                            _surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y))
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = str(key)
                        elif -(item.get_height()) <= abs_local_y < 0:
                            crop_height = -abs_local_y
                            new_height = item.get_height() - crop_height
                            if new_height > self.get_height():
                                new_height = self.get_height()
                            new_width = item.get_width()
                            if new_width > self.get_width():
                                new_width = self.get_width()
                            subsurface_rect = Rectangle(0, crop_height, new_width, new_height)
                            _surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y + crop_height))
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = str(key)
                        # 换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line - 1:
                            current_y += self.distance_between_item + item.get_height()
                            current_x = self.abs_x + off_set[0] + self.panding
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_x += self.distance_between_item + item.get_width()
                            item_has_been_dawn_on_this_line += 1
                    else:
                        abs_local_x = current_x - self.x
                        if 0 <= abs_local_x < self.get_width():
                            new_width = self.get_width() - abs_local_x
                            if new_width > item.get_width():
                                new_width = item.get_width()
                            new_height = item.get_height()
                            if new_height > self.get_height():
                                new_height = self.get_height()
                            subsurface_rect = Rectangle(0, 0, new_width, new_height)
                            _surface.blit(
                                get_img_subsurface(item, subsurface_rect),
                                (current_x, current_y),
                            )
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = str(key)
                        elif -(item.get_width()) <= abs_local_x < 0:
                            crop_width = -abs_local_x
                            new_width = item.get_width() - crop_width
                            if new_width > self.get_width():
                                new_width = self.get_width()
                            new_height = item.get_height()
                            if new_height > self.get_height():
                                new_height = self.get_height()
                            subsurface_rect = Rectangle(crop_width, 0, new_width, new_height)
                            _surface.blit(get_img_subsurface(item, subsurface_rect), (current_x + crop_width, current_y))
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = str(key)
                        # 换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line - 1:
                            current_x += self.distance_between_item + item.get_width()
                            current_y = self.abs_y + off_set[1] + self.panding
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_y += self.distance_between_item + item.get_height()
                            item_has_been_dawn_on_this_line += 1
            # 处理总长宽
            if not self._mode:
                self.__surface_height = current_y - self.abs_y - off_set[1]
                if item_has_been_dawn_on_this_line > 0:
                    self.__surface_height += item.get_height()
                self.__surface_width = self.get_width()
            else:
                self.__surface_width = current_x - self.abs_x - off_set[0]
                if item_has_been_dawn_on_this_line > 0:
                    self.__surface_width += item.get_width()
                self.__surface_height = self.get_height()
            self.display_scrollbar(_surface, off_set)
