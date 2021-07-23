from .button import *

# 用于储存游戏对象的容器，类似html的div
class GameObjectsContainer(AbstractImage):
    def __init__(
        self, bg_img: Union[str, ImageSurface, None], x: int_f, y: int_f, width: int, height: int, tag: str = ""
    ) -> None:
        super().__init__(
            StaticImage(bg_img, 0, 0, width, height) if bg_img is not None else bg_img, x, y, width, height, tag
        )
        self._items_container: dict = {}
        self._item_being_hovered: str = None

    @property
    def item_being_hovered(self) -> Union[str, None]:
        return self._item_being_hovered

    @property
    def item_num(self) -> int:
        return len(self._items_container)

    # 新增一个物品
    def set(self, key: str, new_item: any) -> None:
        self._items_container[key] = new_item

    # 获取一个物品
    def get(self, key: str) -> any:
        return self._items_container[key]

    # 交换2个key名下的图片
    def swap(self, key1: str, key2: str) -> None:
        temp_reference = self._items_container[key1]
        self._items_container[key1] = self._items_container[key2]
        self._items_container[key2] = temp_reference

    # 移除一个物品
    def remove(self, key: str) -> None:
        del self._items_container[key]

    # 清空物品栏
    def clear(self) -> None:
        self._items_container.clear()

    # 是否为空
    def is_empty(self) -> bool:
        return self.item_num <= 0

    # 是否包括
    def contain(self, key: str) -> bool:
        return key in self._items_container

    # 设置尺寸
    def set_width(self, value: int_f) -> None:
        super().set_width(value)
        if self.img is not None:
            self.img.set_width(value)

    def set_height(self, value: int_f) -> None:
        super().set_height(value)
        if self.img is not None:
            self.img.set_height(value)

    # 把物品画到surface上
    def display(self, surface: ImageSurface, offSet: tuple = Pos.ORIGIN) -> None:
        self._item_being_hovered = None
        if not self.hidden:
            current_abs_pos: tuple = Pos.add(self.pos, offSet)
            # 画出背景
            if self.img is not None:
                self.img.display(surface, current_abs_pos)
            # 画出物品
            for key_of_game_object, game_object_t in self._items_container.items():
                game_object_t.display(surface, current_abs_pos)
                if isinstance(game_object_t, Button) and game_object_t.has_been_hovered():
                    self._item_being_hovered = key_of_game_object
                elif isinstance(game_object_t, GameObject) and game_object_t.is_hover(
                    Pos.subtract(Controller.mouse.pos, current_abs_pos)
                ):
                    self._item_being_hovered = key_of_game_object


# 下拉选项菜单
class DropDownSingleChoiceList(GameObjectsContainer):
    def __init__(
        self,
        bg_img: Union[str, ImageSurface, None],
        x: int_f,
        y: int_f,
        font_size: int,
        font_color: color_liked = "black",
        tag: str = "",
    ) -> None:
        super().__init__(bg_img, x, y, 0, 0, tag)
        self.__chosen_item_key: str = ""
        self.__DEFAULT_CONTENT: str = ""
        self.__block_height: int = int(font_size * 1.5)
        self.__font_color: tuple = None
        self.update_font_color(font_color)
        self.__FONT = Font.create(font_size)
        self.__fold_choice: bool = True
        self.outline_thickness: int = 1

    # 重新计算宽度
    def _update_width(self) -> None:
        self.set_width(0)
        for item in self._items_container.values():
            if self.get_width() < (item_width := int(self.__FONT.estimate_text_width(item) * 1.5)):
                self.set_width(item_width)

    # 更新font的尺寸
    def update_font_size(self, font_size: int) -> None:
        self.__block_height: int = int(font_size * 1.5)
        self.__FONT.update(font_size)
        self._update_width()

    # 更新font的颜色
    def update_font_color(self, font_color: color_liked) -> None:
        self.__font_color = Color.get(font_color)

    # 新增一个物品
    def set(self, key: str, new_item: Union[str, int]) -> None:
        super().set(key, new_item)
        if self.get_width() < (new_item_width := int(self.__FONT.estimate_text_width(new_item) * 2)):
            self.set_width(new_item_width)

    # 获取一个物品
    def get(self, key: str) -> Union[str, int]:
        return super().get(key) if not self.is_empty() else self.__DEFAULT_CONTENT

    # 获取当前选中的物品
    def get_current_selected_item(self) -> Union[str, int]:
        return self.get(self.__chosen_item_key) if not self.is_empty() else self.__DEFAULT_CONTENT

    # 设置当前选中的物品
    def set_current_selected_item(self, key: str) -> None:
        self.__chosen_item_key = key

    # 获取高度
    def get_height(self) -> int:
        return (
            int((len(self._items_container) + 1) * self.__FONT.size * 1.5)
            if not self.__fold_choice
            else int(self.__FONT.size * 1.5)
        )

    # 移除一个物品
    def pop(self, index: int) -> None:
        super().pop(index)
        self._update_width()

    # 清空物品栏
    def clear(self) -> None:
        super().clear()
        self._update_width()

    # 把物品画到surface上
    def display(self, surface: ImageSurface, offSet: tuple = Pos.ORIGIN) -> None:
        if not self.hidden:
            current_abs_pos: tuple = Pos.add(self.pos, offSet)
            # 画出背景
            if self.img is not None:
                self.img.display(surface, current_abs_pos)
            else:
                draw_rect(surface, Color.WHITE, (current_abs_pos, self.size))
            # 列出当前选中的选项
            current_pos: tuple = current_abs_pos
            font_surface: ImageSurface = self.__FONT.render(self.get_current_selected_item(), self.__font_color)
            surface.blit(
                font_surface,
                Pos.add(current_pos, (int(self.width * 0.2), int((self.__block_height - font_surface.get_height()) / 2))),
            )
            rect_of_outline = new_rect(current_pos, (self.width, self.__block_height))
            draw_rect(surface, self.__font_color, rect_of_outline, self.outline_thickness)
            font_surface = IMG.flip(self.__FONT.render("^", self.__font_color), False, True)
            surface.blit(
                font_surface,
                Pos.add(
                    current_pos,
                    (
                        int(self.width - font_surface.get_width() * 1.5),
                        int((self.__block_height - font_surface.get_height()) / 2),
                    ),
                ),
            )
            if Controller.get_event("confirm"):
                if is_hover(rect_of_outline):
                    self.__fold_choice = not self.__fold_choice
                elif not self.__fold_choice and not is_hover(new_rect(current_abs_pos, self.size)):
                    self.__fold_choice = True
            # 列出选择
            if not self.__fold_choice:
                index: int = 0
                for key_of_game_object, game_object_t in self._items_container.items():
                    current_pos = Pos.add(current_abs_pos, (0, (index + 1) * self.__block_height))
                    font_surface = self.__FONT.render(game_object_t, self.__font_color)
                    surface.blit(
                        font_surface,
                        Pos.add(
                            current_pos, (int(self.width * 0.2), int((self.__block_height - font_surface.get_height()) / 2))
                        ),
                    )
                    rect_of_outline = new_rect(current_pos, (self.width, self.__block_height))
                    draw_rect(surface, self.__font_color, rect_of_outline, self.outline_thickness)
                    if is_hover(rect_of_outline) and Controller.mouse.get_pressed(0):
                        self.__chosen_item_key = key_of_game_object
                    draw_circle(
                        surface,
                        self.__font_color,
                        Pos.add(current_pos, (self.width * 0.1, self.__block_height / 2)),
                        3,
                        self.outline_thickness if key_of_game_object != self.__chosen_item_key else 0,
                    )
                    index += 1


# 带有滚动条的Surface容器
class SurfaceContainerWithScrollbar(GameObjectsContainer):
    def __init__(
        self,
        img: Union[str, ImageSurface, None],
        x: int_f,
        y: int_f,
        width: int,
        height: int,
        mode: str = "horizontal",
        tag: str = "",
    ) -> None:
        super().__init__(IMG.load(img, (width, height)) if img is not None else img, x, y, width, height, tag)
        self.panding: int = 0
        self.distance_between_item: int = 20
        self.move_speed: int = 20
        self.button_tickness = 20
        self.__total_width: int = 0
        self.__total_height: int = 0
        self.__is_holding_scroll_button: bool = False
        self.__mouse_x_last = 0
        self.__mouse_y_last = 0
        self.__mode: bool = False
        self.set_mode(mode)
        self.__scroll_bar_pos: bool = True
        self.__item_per_line: int = 1

    # 模式
    @property
    def mode(self) -> str:
        return self.get_mode()

    def get_mode(self) -> str:
        return "vertical" if not self.__mode else "horizontal"

    def set_mode(self, mode: str) -> None:
        if mode == "horizontal":
            self.__mode = True
        elif mode == "vertical":
            self.__mode = False
        else:
            EXCEPTION.fatal("Mode '{}' is not supported!".format(mode))

    def switch_mode(self) -> None:
        self.__mode = not self.__mode
        self.set_local_pos(0, 0)
        self.clear()

    # 滚动条位置
    @property
    def scroll_bar_pos(self) -> str:
        return self.get_scroll_bar_pos()

    def get_scroll_bar_pos(self) -> str:
        if not self.__mode:
            return "right" if not self.__scroll_bar_pos else "left"
        else:
            return "bottom" if not self.__scroll_bar_pos else "top"

    def set_scroll_bar_pos(self, pos: str) -> None:
        if pos == "left":
            if not self.__mode:
                self.__scroll_bar_pos = True
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the left during horizontal mode!")
        elif pos == "right":
            if not self.__mode:
                self.__scroll_bar_pos = False
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the right during horizontal mode!")
        elif pos == "top":
            if self.__mode is True:
                self.__scroll_bar_pos = True
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the top during vertical mode!")
        elif pos == "bottom":
            if self.__mode is True:
                self.__scroll_bar_pos = False
            else:
                EXCEPTION.fatal("You cannot put the scroll bar on the bottom during vertical mode!")
        else:
            EXCEPTION.fatal(
                'Scroll bar position "{}" is not supported! Try sth like "right" or "bottom" instead.'.format(pos)
            )

    # 获取滚动条按钮的Rect
    def __get_scroll_button_rect(self, off_set_x: number, off_set_y: number) -> Union[Rect, None]:
        if not self.__mode:
            if self.__total_height > self._height:
                return (
                    Rect(
                        int(self.x + self._local_x + off_set_x),
                        int(self.y - self._height * self._local_y / self.__total_height + off_set_y),
                        self.button_tickness,
                        int(self._height * self._height / self.__total_height),
                    )
                    if self.__scroll_bar_pos is True
                    else Rect(
                        int(self.x + self._local_x + self._width - self.button_tickness + off_set_x),
                        int(self.y - self._height * self._local_y / self.__total_height + off_set_y),
                        self.button_tickness,
                        int(self._height * self._height / self.__total_height),
                    )
                )
        else:
            if self.__total_width > self._width:
                return (
                    Rect(
                        int(self.x - self._width * self._local_x / self.__total_width + off_set_x),
                        int(self.y + self._local_y + off_set_y),
                        int(self._width * self._width / self.__total_width),
                        self.button_tickness,
                    )
                    if self.__scroll_bar_pos is True
                    else Rect(
                        int(self.x - self._width * self._local_x / self.__total_width + off_set_x),
                        int(self.y + self._local_y + self._height - self.button_tickness + off_set_y),
                        int(self._width * self._width / self.__total_width),
                        self.button_tickness,
                    )
                )
        return None

    # 获取滚动条的Rect
    def __get_scroll_bar_rect(self, off_set_x: number, off_set_y: number) -> Union[Rect, None]:
        if not self.__mode:
            if self.__total_height > self._height:
                return (
                    Rect(
                        int(self.x + self._local_x + off_set_x),
                        int(self.y + off_set_y),
                        self.button_tickness,
                        self._height,
                    )
                    if self.__scroll_bar_pos is True
                    else Rect(
                        int(self.x + self._local_x + self._width - self.button_tickness + off_set_x),
                        int(self.y + off_set_y),
                        self.button_tickness,
                        self._height,
                    )
                )
        else:
            if self.__total_width > self._width:
                return (
                    Rect(
                        int(self.x + off_set_x),
                        int(self.y + self._local_y + off_set_y),
                        self._width,
                        self.button_tickness,
                    )
                    if self.__scroll_bar_pos is True
                    else Rect(
                        int(self.x + off_set_x),
                        int(self.y + self._local_y + self._height - self.button_tickness + off_set_y),
                        self._width,
                        self.button_tickness,
                    )
                )
        return None

    # 每一行放多少个物品
    @property
    def item_per_line(self) -> int:
        return self.__item_per_line

    def get_item_per_line(self) -> int:
        return self.__item_per_line

    def set_item_per_line(self, value: int) -> None:
        self.__item_per_line = int(value)

    # 把素材画到屏幕上
    def display(self, surface: ImageSurface, off_set: tuple = Pos.ORIGIN) -> None:
        self._item_being_hovered = None
        if not self.hidden:
            """画出"""
            # 如果有背景图片，则画出
            if self.img is not None:
                surface.blit(self.img, Pos.add(self.pos, off_set))
            # 计算出基础坐标
            current_x: int = int(self.x + self._local_x + off_set[0])
            current_y: int = int(self.y + self._local_y + off_set[1])
            if not self.__mode:
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
            for key, item in self._items_container.items():
                if item is not None:
                    if not self.__mode:
                        abs_local_y = int(current_y - self.y)
                        if 0 <= abs_local_y < self._height:
                            new_height = self._height - abs_local_y
                            if new_height > item.get_height():
                                new_height = item.get_height()
                            new_width = item.get_width()
                            if new_width > self._width:
                                new_width = self._width
                            subsurface_rect = Rect(0, 0, new_width, new_height)
                            surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y))
                            if is_hover(subsurface_rect, off_set_x=current_x, off_set_y=current_y):
                                self._item_being_hovered = key
                        elif -(item.get_height()) <= abs_local_y < 0:
                            crop_height = -abs_local_y
                            new_height = item.get_height() - crop_height
                            if new_height > self._height:
                                new_height = self._height
                            new_width = item.get_width()
                            if new_width > self._width:
                                new_width = self._width
                            subsurface_rect = Rect(0, crop_height, new_width, new_height)
                            surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y + crop_height))
                            if is_hover(subsurface_rect, off_set_x=current_x, off_set_y=current_y):
                                self._item_being_hovered = key
                        # 换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line - 1:
                            current_y += self.distance_between_item + item.get_height()
                            current_x = int(self.x + self._local_x + off_set[0] + self.panding)
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_x += self.distance_between_item + item.get_width()
                            item_has_been_dawn_on_this_line += 1
                    else:
                        abs_local_x = int(current_x - self.x)
                        if 0 <= abs_local_x < self._width:
                            new_width = self._width - abs_local_x
                            if new_width > item.get_width():
                                new_width = item.get_width()
                            new_height = item.get_height()
                            if new_height > self._height:
                                new_height = self._height
                            subsurface_rect = Rect(0, 0, new_width, new_height)
                            surface.blit(
                                get_img_subsurface(item, subsurface_rect),
                                (current_x, current_y),
                            )
                            if is_hover(subsurface_rect, off_set_x=current_x, off_set_y=current_y):
                                self._item_being_hovered = key
                        elif -(item.get_width()) <= abs_local_x < 0:
                            crop_width = -abs_local_x
                            new_width = item.get_width() - crop_width
                            if new_width > self._width:
                                new_width = self._width
                            new_height = item.get_height()
                            if new_height > self._height:
                                new_height = self._height
                            subsurface_rect = Rect(crop_width, 0, new_width, new_height)
                            surface.blit(get_img_subsurface(item, subsurface_rect), (current_x + crop_width, current_y))
                            if is_hover(subsurface_rect, off_set_x=current_x, off_set_y=current_y):
                                self._item_being_hovered = key
                        # 换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line - 1:
                            current_x += self.distance_between_item + item.get_width()
                            current_y = int(self.y + self._local_y + off_set[1] + self.panding)
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_y += self.distance_between_item + item.get_height()
                            item_has_been_dawn_on_this_line += 1
            # 处理总长宽
            if not self.__mode:
                self.__total_height = int(current_y - self.y - self._local_y - off_set[1])
                if item_has_been_dawn_on_this_line > 0:
                    self.__total_height += item.get_height()
                self.__total_width = self._width
            else:
                self.__total_width = int(current_x - self.x - self._local_x - off_set[0])
                if item_has_been_dawn_on_this_line > 0:
                    self.__total_width += item.get_width()
                self.__total_height = self._height
            """处理事件"""
            # 获取鼠标坐标
            if self.is_hover(Pos.subtract(Controller.mouse.pos, off_set)):
                if (
                    not self.__mode
                    and self.__total_height > self._height
                    or self.__mode is True
                    and self.__total_width > self._width
                ):
                    # 查看与鼠标有关的事件
                    for event in Controller.events:
                        if event.type == MOUSE_BUTTON_DOWN:
                            if event.button == 1:
                                scroll_bar_rect = self.__get_scroll_bar_rect(off_set[0], off_set[1])
                                if scroll_bar_rect is not None and is_hover(scroll_bar_rect):
                                    scroll_button_rect = self.__get_scroll_button_rect(off_set[0], off_set[1])
                                    if is_hover(scroll_button_rect):
                                        if not self.__is_holding_scroll_button:
                                            self.__is_holding_scroll_button = True
                                            self.__mouse_x_last, self.__mouse_y_last = Controller.mouse.pos
                                    else:
                                        self.__is_holding_scroll_button = True
                                        self.__mouse_x_last, self.__mouse_y_last = Controller.mouse.pos
                                        if not self.__mode:
                                            self._local_y = int(
                                                (self.y - Controller.mouse.y + scroll_button_rect.height / 2)
                                                / scroll_bar_rect.height
                                                * self.__total_height
                                            )
                                        else:
                                            self._local_x = int(
                                                (self.x - Controller.mouse.x + scroll_button_rect.width / 2)
                                                / scroll_bar_rect.width
                                                * self.__total_width
                                            )
                            elif event.button == 4:
                                if not self.__mode:
                                    self._local_y += self.move_speed
                                else:
                                    self._local_x -= self.move_speed
                            elif event.button == 5:
                                if not self.__mode:
                                    self._local_y -= self.move_speed
                                else:
                                    self._local_x += self.move_speed
                        elif event.type == MOUSE_BUTTON_UP and event.button == 1:
                            self.__is_holding_scroll_button = False
                else:
                    self.__is_holding_scroll_button = False
            else:
                self.__is_holding_scroll_button = False
            # 调整本地坐标
            if self.__is_holding_scroll_button is True:
                if not self.__mode:
                    self._local_y += (self.__mouse_y_last - Controller.mouse.y) * (self.__total_height / self.height)
                    self.__mouse_y_last = Controller.mouse.y
                else:
                    self._local_x += (self.__mouse_x_last - Controller.mouse.x) * (self.__total_width / self.width)
                    self.__mouse_x_last = Controller.mouse.x
            # 防止local坐标越界
            if not self.__mode:
                if self._local_y > 0:
                    self._local_y = 0
                elif self.__total_height > self._height:
                    if (local_y_max := self._height - self.__total_height) > self._local_y:
                        self._local_y = local_y_max
            else:
                if self._local_x > 0:
                    self._local_x = 0
                elif self.__total_width > self._width:
                    if (local_x_max := self._width - self.__total_width) > self._local_x:
                        self._local_x = local_x_max
            # 画出滚动条
            if (scroll_button_rect := self.__get_scroll_button_rect(off_set[0], off_set[1])) is not None:
                draw_rect(surface, Color.WHITE, scroll_button_rect)
            if (scroll_bar_rect := self.__get_scroll_bar_rect(off_set[0], off_set[1])) is not None:
                draw_rect(surface, Color.WHITE, scroll_bar_rect, 2)
