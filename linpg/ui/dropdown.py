from .container import *

# 下拉选项菜单
class DropDownList(GameObjectsDictContainer):
    def __init__(
        self, bg_img: Optional[PoI], x: int_f, y: int_f, font_size: int, font_color: color_liked = "black", tag: str = ""
    ) -> None:
        # 方格高度
        self.__block_height: int = font_size * 3 // 2
        # 是否折叠选项
        self.__fold_choice: bool = True
        super().__init__(bg_img, x, y, 0, 0, tag)
        self.__chosen_item_key: str = ""
        self.__DEFAULT_CONTENT: str = ""
        # 字体颜色
        self.__font_color: tuple[int, int, int, int] = Colors.get(font_color)
        # 字体
        self.__FONT = Font.create(font_size)
        # 边缘粗细
        self.outline_thickness: int = 1

    # 重新计算宽度
    def __recalculate_width(self) -> None:
        self.set_width(0)
        for item in self._get_container().values():
            self.__update_width(item)

    # 根据物品判定是否需要更新宽度
    def __update_width(self, item: strint) -> None:
        _new_width: int = self.__FONT.estimate_text_width(item) + self.__FONT.size * 7
        if self.get_width() < _new_width:
            self.set_width(_new_width)

    # 更新font的尺寸
    def update_font_size(self, font_size: int) -> None:
        self.__FONT.update(font_size)
        self.__block_height = round(self.__FONT.size * 3 / 2)
        self.__recalculate_width()

    # 更新font的颜色
    def update_font_color(self, font_color: color_liked) -> None:
        self.__font_color = Colors.get(font_color)

    # 新增一个物品
    def set(self, key: str, new_item: strint) -> None:  # type: ignore[override]
        super().set(key, new_item)
        self.__update_width(new_item)

    # 获取一个物品
    def get(self, key: str) -> strint:
        return super().get(key) if not self.is_empty() else self.__DEFAULT_CONTENT

    # 获取当前选中的物品
    def get_selected_item(self) -> str:
        return self.__chosen_item_key

    # 设置当前选中的物品
    def set_selected_item(self, key: str) -> None:
        self.__chosen_item_key = key

    # 获取高度
    def get_height(self) -> int:
        return (len(self._get_container()) + 1) * self.__block_height if not self.__fold_choice else self.__block_height

    # 移除一个物品
    def remove(self, key: str) -> None:
        super().remove(key)
        self.__recalculate_width()

    # 清空物品栏
    def clear(self) -> None:
        super().clear()
        self.__recalculate_width()

    # 把物品画到surface上
    def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
        if self.is_visible():
            current_abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.img is not None and self.img is not Surfaces.NULL:
                self.img.display(surface, current_abs_pos)
            else:
                Draw.rect(surface, Colors.WHITE, (current_abs_pos, self.size))
            # 列出当前选中的选项
            current_pos: tuple = current_abs_pos
            font_surface: ImageSurface = self.__FONT.render(self.get_selected_item(), self.__font_color, with_bounding=True)
            surface.blit(
                font_surface,
                Coordinates.add(current_pos, (self.__FONT.size * 3, (self.__block_height - font_surface.get_height()) // 2)),
            )
            rect_of_outline = Rectangle(current_pos[0], current_pos[1], self.width, self.__block_height)
            Draw.rect(surface, self.__font_color, rect_of_outline.get_rect(), self.outline_thickness)
            font_surface = RawImg.flip(self.__FONT.render("^", self.__font_color), False, True)
            surface.blit(
                font_surface,
                Coordinates.add(
                    current_pos,
                    (
                        self.width - font_surface.get_width() * 3 // 2,
                        (self.__block_height - font_surface.get_height()) // 2,
                    ),
                ),
            )
            if Controller.get_event("confirm"):
                if rect_of_outline.is_hovered():
                    self.__fold_choice = not self.__fold_choice
                elif not self.__fold_choice and not Controller.mouse.is_in_rect(
                    current_abs_pos[0], current_abs_pos[1], self.get_width(), self.get_height()
                ):
                    self.__fold_choice = True
            # 列出选择
            if not self.__fold_choice:
                index: int = 1
                for key_of_game_object, game_object_t in self._get_container().items():
                    current_pos = Coordinates.add(current_abs_pos, (0, index * self.__block_height))
                    font_surface = self.__FONT.render(game_object_t, self.__font_color, with_bounding=True)
                    surface.blit(
                        font_surface,
                        Coordinates.add(
                            current_pos, (self.__FONT.size * 3, (self.__block_height - font_surface.get_height()) // 2)
                        ),
                    )
                    rect_of_outline = Rectangle(current_pos[0], current_pos[1], self.width, self.__block_height)
                    Draw.rect(surface, self.__font_color, rect_of_outline.get_rect(), self.outline_thickness)
                    if rect_of_outline.is_hovered() and Controller.get_event("confirm"):
                        self.__chosen_item_key = key_of_game_object
                    Draw.circle(
                        surface,
                        self.__font_color,
                        Coordinates.add(current_pos, (self.__FONT.size * 2, self.__block_height / 2)),
                        self.__block_height * 3 // 20,
                        self.outline_thickness if key_of_game_object != self.__chosen_item_key else 0,
                    )
                    index += 1
