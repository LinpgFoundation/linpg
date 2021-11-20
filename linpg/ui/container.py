from .button import *

# 用于储存游戏对象的容器，类似html的div
class GameObjectsContainer(AbstractImageSurface):
    def __init__(self, bg_img: PoI, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(
            StaticImage(bg_img, 0, 0, width, height) if bg_img is not None else bg_img, x, y, width, height, tag
        )
        self._items_container: dict = {}
        self._item_being_hovered: str = None

    @property
    def item_being_hovered(self) -> str:
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
    def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
        self._item_being_hovered = None
        if self.is_visible():
            current_abs_pos: tuple = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.img is not None:
                self.img.display(surface, current_abs_pos)
            # 画出物品
            for key_of_game_object, game_object_t in self._items_container.items():
                game_object_t.display(surface, current_abs_pos)
                if isinstance(game_object_t, Button):
                    if game_object_t.has_been_hovered() is True:
                        self._item_being_hovered = key_of_game_object
                elif isinstance(game_object_t, GameObject):
                    if game_object_t.is_hovered(current_abs_pos):
                        self._item_being_hovered = key_of_game_object


# 下拉选项菜单
class DropDownSingleChoiceList(GameObjectsContainer):
    def __init__(
        self, bg_img: PoI, x: int_f, y: int_f, font_size: int, font_color: color_liked = "black", tag: str = ""
    ) -> None:
        # 方格高度
        self.__block_height: int = int(font_size * 1.5)
        # 是否折叠选项
        self.__fold_choice: bool = True
        super().__init__(bg_img, x, y, 0, 0, tag)
        self.__chosen_item_key: str = ""
        self.__DEFAULT_CONTENT: str = ""
        self.__font_color: tuple = None
        self.update_font_color(font_color)
        self.__FONT = Font.create(font_size)
        self.outline_thickness: int = 1

    # 重新计算宽度
    def __recalculate_width(self) -> None:
        self.set_width(0)
        for item in self._items_container.values():
            self.__update_width(item)

    # 根据物品判定是否需要更新宽度
    def __update_width(self, item: strint) -> None:
        if self.get_width() < (new_item_width := int(self.__FONT.estimate_text_width(item) + self.__FONT.size * 7)):
            self.set_width(new_item_width)

    # 更新font的尺寸
    def update_font_size(self, font_size: int) -> None:
        self.__FONT.update(font_size)
        self.__block_height = round(self.__FONT.size * 1.5)
        self.__recalculate_width()

    # 更新font的颜色
    def update_font_color(self, font_color: color_liked) -> None:
        self.__font_color = Color.get(font_color)

    # 新增一个物品
    def set(self, key: str, new_item: strint) -> None:
        super().set(key, new_item)
        self.__update_width(new_item)

    # 获取一个物品
    def get(self, key: str) -> strint:
        return super().get(key) if not self.is_empty() else self.__DEFAULT_CONTENT

    # 获取当前选中的物品
    def get_current_selected_item(self) -> str:
        return self.__chosen_item_key

    # 设置当前选中的物品
    def set_current_selected_item(self, key: str) -> None:
        self.__chosen_item_key = key

    # 获取高度
    def get_height(self) -> int:
        return (len(self._items_container) + 1) * self.__block_height if not self.__fold_choice else self.__block_height

    # 移除一个物品
    def pop(self, index: int) -> None:
        super().pop(index)
        self.__recalculate_width()

    # 清空物品栏
    def clear(self) -> None:
        super().clear()
        self.__recalculate_width()

    # 把物品画到surface上
    def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
        if self.is_visible():
            current_abs_pos: tuple = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.img is not None:
                self.img.display(surface, current_abs_pos)
            else:
                draw_rect(surface, Color.WHITE, (current_abs_pos, self.size))
            # 列出当前选中的选项
            current_pos: tuple = current_abs_pos
            font_surface: ImageSurface = self.__FONT.render_with_bounding(
                self.get_current_selected_item(), self.__font_color
            )
            surface.blit(
                font_surface,
                Coordinates.add(
                    current_pos, (self.__FONT.size * 3, int((self.__block_height - font_surface.get_height()) / 2))
                ),
            )
            rect_of_outline = new_rect(current_pos, (self.width, self.__block_height))
            draw_rect(surface, self.__font_color, rect_of_outline, self.outline_thickness)
            font_surface = IMG.flip(self.__FONT.render("^", self.__font_color), False, True)
            surface.blit(
                font_surface,
                Coordinates.add(
                    current_pos,
                    (
                        int(self.width - font_surface.get_width() * 1.5),
                        int((self.__block_height - font_surface.get_height()) / 2),
                    ),
                ),
            )
            if Controller.get_event("confirm"):
                if rect_of_outline.is_hovered():
                    self.__fold_choice = not self.__fold_choice
                elif not self.__fold_choice and not new_rect(current_abs_pos, self.size).is_hovered():
                    self.__fold_choice = True
            # 列出选择
            if not self.__fold_choice:
                index: int = 1
                for key_of_game_object, game_object_t in self._items_container.items():
                    current_pos = Coordinates.add(current_abs_pos, (0, index * self.__block_height))
                    font_surface = self.__FONT.render_with_bounding(game_object_t, self.__font_color)
                    surface.blit(
                        font_surface,
                        Coordinates.add(
                            current_pos, (self.__FONT.size * 3, int((self.__block_height - font_surface.get_height()) / 2))
                        ),
                    )
                    rect_of_outline = new_rect(current_pos, (self.width, self.__block_height))
                    draw_rect(surface, self.__font_color, rect_of_outline, self.outline_thickness)
                    if rect_of_outline.is_hovered() and Controller.mouse.get_pressed(0):
                        self.__chosen_item_key = key_of_game_object
                    draw_circle(
                        surface,
                        self.__font_color,
                        Coordinates.add(current_pos, (self.__FONT.size * 2, self.__block_height / 2)),
                        int(self.__block_height * 0.15),
                        self.outline_thickness if key_of_game_object != self.__chosen_item_key else 0,
                    )
                    index += 1
