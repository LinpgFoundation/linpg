from .dropdown import *


# 同一时刻会展示2个scrollbar的Surface
class AbstractScrollBarsSurface(SurfaceWithLocalPos, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        self._button_thickness: int = 20
        self._move_speed: int = 20
        self._bar_color: tuple[int, int, int, int] = Colors.WHITE

    # 获取surface宽度（子类需要实现）
    @abstractmethod
    def get_surface_width(self) -> int:
        Exceptions.fatal("get_surface_width()", 1)

    # 获取surface高度（子类需要实现）
    @abstractmethod
    def get_surface_height(self) -> int:
        Exceptions.fatal("get_surface_height()", 1)

    # 获取x坐标（子类需实现）
    @abstractmethod
    def get_left(self) -> int:
        Exceptions.fatal("get_left()", 1)

    # 获取y坐标（子类需实现）
    @abstractmethod
    def get_top(self) -> int:
        Exceptions.fatal("get_top()", 1)

    # 获取x+width坐标（子类需实现）
    @abstractmethod
    def get_right(self) -> int:
        Exceptions.fatal("get_right()", 1)

    # 获取y+height坐标（子类需实现）
    @abstractmethod
    def get_bottom(self) -> int:
        Exceptions.fatal("get_bottom()", 1)

    # 获取宽度（子类需实现）
    @abstractmethod
    def get_width(self) -> int:
        Exceptions.fatal("get_width()", 1)

    # 获取高度（子类需实现）
    @abstractmethod
    def get_height(self) -> int:
        Exceptions.fatal("get_height()", 1)

    # 是否被鼠标触碰（子类需实现）
    @abstractmethod
    def is_hovered(self, off_set: tuple[int, int] | None = None) -> bool:
        Exceptions.fatal("is_hovered()", 1)

    # 获取scrollbar的颜色
    def get_bar_color(self) -> tuple[int, int, int, int]:
        return self._bar_color

    # 修改scrollbar的颜色
    def set_bar_color(self, color: color_liked) -> None:
        self._bar_color = Colors.get(color)

    # 获取滚动条的Rect
    def _get_right_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Rectangle | None:
        return (
            Rectangle(
                self.get_right() - self._button_thickness + int(off_set_x),
                self.get_top() + int(off_set_y),
                self._button_thickness,
                self.get_height(),
            )
            if self.get_surface_height() > self.get_height()
            else None
        )

    def _get_bottom_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Rectangle | None:
        return (
            Rectangle(
                self.get_left() + int(off_set_x),
                self.get_bottom() - self._button_thickness + int(off_set_y),
                self.get_width(),
                self._button_thickness,
            )
            if self.get_surface_width() > self.get_width()
            else None
        )

    # 获取滚动条按钮的Rect
    def _get_right_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Rectangle | None:
        return (
            Rectangle(
                self.get_right() - self._button_thickness + int(off_set_x),
                int(self.get_top() - self.get_height() * self.local_y / self.get_surface_height() + off_set_y),
                self._button_thickness,
                self.get_height() * self.get_height() // self.get_surface_height(),
            )
            if self.get_surface_height() > self.get_height()
            else None
        )

    def _get_bottom_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Rectangle | None:
        return (
            Rectangle(
                int(self.get_left() - self.get_width() * self.local_x / self.get_surface_width() + off_set_x),
                self.get_bottom() - self._button_thickness + int(off_set_y),
                self.get_width() * self.get_width() // self.get_surface_width(),
                self._button_thickness,
            )
            if self.get_surface_width() > self.get_width()
            else None
        )

    def display_scrollbar(self, _surface: ImageSurface, off_set: tuple[int, int] = ORIGIN) -> None:
        # 获取滚轮条
        right_scroll_bar_rect: Rectangle | None = self._get_right_scroll_bar_rect(off_set[0], off_set[1])
        right_scroll_button_rect: Rectangle | None = self._get_right_scroll_button_rect(off_set[0], off_set[1])
        bottom_scroll_bar_rect: Rectangle | None = self._get_bottom_scroll_bar_rect(off_set[0], off_set[1])
        bottom_scroll_button_rect: Rectangle | None = self._get_bottom_scroll_button_rect(off_set[0], off_set[1])
        # 获取鼠标坐标
        if Controller.mouse.get_pressed(0):
            if (
                right_scroll_bar_rect is not None
                and right_scroll_button_rect is not None
                and right_scroll_bar_rect.is_hovered()
            ):
                if right_scroll_button_rect.is_hovered():
                    self.add_local_y(Controller.mouse.get_y_moved() * (self.get_surface_height() / self.get_height()))
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
                    self.add_local_x(Controller.mouse.get_x_moved() * (self.get_surface_width() / self.get_width()))
                else:
                    self.set_local_x(
                        (self.get_left() - Controller.mouse.x + bottom_scroll_button_rect.width / 2)
                        / bottom_scroll_bar_rect.width
                        * self.get_surface_width()
                    )
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
class AbstractSurfaceWithScrollBar(AbstractScrollBarsSurface, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        self.axis_mode: Axis = Axis.VERTICAL
        self.__scroll_bar_pos: bool = True
        self.__is_holding_scroll_button = False

    def switch_mode(self) -> None:
        self.axis_mode = Axis.VERTICAL if self.axis_mode is not Axis.VERTICAL else Axis.HORIZONTAL
        self.set_local_pos(0, 0)

    # 滚动条位置
    @property
    def scroll_bar_pos(self) -> str:
        return self.get_scroll_bar_pos()

    def get_scroll_bar_pos(self) -> str:
        if self.axis_mode is Axis.VERTICAL:
            return "right" if not self.__scroll_bar_pos else "left"
        else:
            return "bottom" if not self.__scroll_bar_pos else "top"

    def set_scroll_bar_pos(self, pos: str) -> None:
        match pos:
            case "left":
                if self.axis_mode is Axis.VERTICAL:
                    self.__scroll_bar_pos = True
                else:
                    Exceptions.fatal("You cannot put the scroll bar on the left during horizontal mode!")
            case "right":
                if self.axis_mode is Axis.VERTICAL:
                    self.__scroll_bar_pos = False
                else:
                    Exceptions.fatal("You cannot put the scroll bar on the right during horizontal mode!")
            case "top":
                if self.axis_mode is Axis.HORIZONTAL:
                    self.__scroll_bar_pos = True
                else:
                    Exceptions.fatal("You cannot put the scroll bar on the top during vertical mode!")
            case "bottom":
                if self.axis_mode is Axis.HORIZONTAL:
                    self.__scroll_bar_pos = False
                else:
                    Exceptions.fatal("You cannot put the scroll bar on the bottom during vertical mode!")
            case _:
                Exceptions.fatal(f'Scroll bar position "{pos}" is not supported! Try sth like "right" or "bottom" instead.')

    # 获取滚动条按钮的Rect
    def _get_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Rectangle | None:
        if self.axis_mode is Axis.VERTICAL:
            if not self.__scroll_bar_pos:
                return self._get_right_scroll_button_rect(off_set_x, off_set_y)
            elif self.get_surface_height() > self.get_height():
                return Rectangle(
                    self.abs_x + int(off_set_x),
                    int(self.get_top() - self.get_height() * self.local_y / self.get_surface_height() + off_set_y),
                    self._button_thickness,
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
                    self._button_thickness,
                )
        return None

    # 获取滚动条的Rect
    def _get_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Rectangle | None:
        if self.axis_mode is Axis.VERTICAL:
            if not self.__scroll_bar_pos:
                return self._get_right_scroll_bar_rect(off_set_x, off_set_y)
            elif self.get_surface_height() > self.get_height():
                return Rectangle(
                    self.abs_x + int(off_set_x), self.get_top() + int(off_set_y), self._button_thickness, self.get_height()
                )
        else:
            if not self.__scroll_bar_pos:
                return self._get_bottom_scroll_bar_rect(off_set_x, off_set_y)
            elif self.get_surface_width() > self.get_width():
                return Rectangle(
                    self.get_left() + int(off_set_x), self.abs_y + int(off_set_y), self.get_width(), self._button_thickness
                )
        return None

    def display_scrollbar(self, _surface: ImageSurface, off_set: tuple[int, int] = ORIGIN) -> None:
        # 获取滚轮条
        scroll_bar_rect: Rectangle | None = self._get_scroll_bar_rect(off_set[0], off_set[1])
        scroll_button_rect: Rectangle | None = self._get_scroll_button_rect(off_set[0], off_set[1])
        if scroll_bar_rect is not None and scroll_button_rect is not None:
            # 如果没有按下的事件，则重置holding_scroll_button的flag
            if not Controller.mouse.get_pressed(0):
                self.__is_holding_scroll_button = False
            # 如果有按下的事件
            if self.is_hovered(off_set):
                if (
                    Controller.mouse.get_pressed(0) is True
                    and not self.__is_holding_scroll_button
                    and scroll_bar_rect.is_hovered()
                ):
                    # 根据按钮位置调整本地坐标
                    if scroll_button_rect.is_hovered():
                        self.__is_holding_scroll_button = True
                    elif self.axis_mode is Axis.VERTICAL:
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
                if Controller.get_event("scroll_up"):
                    if self.axis_mode is Axis.VERTICAL:
                        self.add_local_y(self._move_speed)
                    else:
                        self.subtract_local_x(self._move_speed)
                if Controller.get_event("scroll_down"):
                    if self.axis_mode is Axis.VERTICAL:
                        self.subtract_local_y(self._move_speed)
                    else:
                        self.add_local_x(self._move_speed)
        # 需要调整本地坐标
        if self.__is_holding_scroll_button is True:
            if self.axis_mode is Axis.VERTICAL:
                self.add_local_y(Controller.mouse.get_y_moved() * self.get_surface_height() / self.get_height())
            else:
                self.add_local_x(Controller.mouse.get_x_moved() * self.get_surface_width() / self.get_width())
        # 防止local坐标越界
        if self.axis_mode is Axis.VERTICAL:
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
class SurfaceContainerWithScrollBar(GameObjectsDictContainer, AbstractSurfaceWithScrollBar):
    def __init__(
        self, img: PoI | None, x: int_f, y: int_f, width: int, height: int, mode: Axis = Axis.HORIZONTAL, tag: str = ""
    ) -> None:
        GameObjectsDictContainer.__init__(self, img, x, y, width, height, tag)
        AbstractSurfaceWithScrollBar.__init__(self)
        self.__surface_width: int = 0
        self.__surface_height: int = 0
        self.padding: int = 0
        self.distance_between_item: int = 20
        self.axis_mode = mode
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
            if Surfaces.is_not_null(self._get_image_reference()):
                _surface.blit(self._get_image_reference(), Coordinates.add(self.pos, off_set))
            # 计算出基础坐标
            current_x: int = self.abs_x + off_set[0]
            current_y: int = self.abs_y + off_set[1]
            if self.axis_mode is Axis.VERTICAL:
                current_x += self.padding
            else:
                current_y += self.padding
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
                    if self.axis_mode is Axis.VERTICAL:
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
                            current_x = self.abs_x + off_set[0] + self.padding
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
                            _surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y))
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
                            current_y = self.abs_y + off_set[1] + self.padding
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_y += self.distance_between_item + item.get_height()
                            item_has_been_dawn_on_this_line += 1
            # 处理总长宽
            if self.axis_mode is Axis.VERTICAL:
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
