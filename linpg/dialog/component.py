from .dialogbox import *

# 对话模块Node
class DialogNode(Button):
    def __init__(self, key_name: str, font_size: int, next_keys: list[str], tag: str = ""):
        self.__key_name: str = key_name
        button_surface = Font.render_description_box(self.__key_name, Colors.BLACK, font_size, font_size // 2, Colors.WHITE)
        super().__init__(button_surface, 0, 0, width=button_surface.get_width(), height=button_surface.get_height(), tag=tag)
        self.__next_keys: tuple[str, ...] = tuple(next_keys)
        self.has_been_displayed: bool = False

    # 下一个keys
    @property
    def next_keys(self) -> tuple[str, ...]:
        return self.__next_keys

    # 展示（注意，你无法在此输入off_set，你必须提前设置）
    def display(self, surface: ImageSurface) -> None:  # type: ignore[override]
        return super().display(surface)


# 对话key向导窗口
class DialogNavigationWindow(AbstractFrame):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = ""):
        super().__init__(x, y, width, height, tag=tag)
        self.__nodes_map: dict[str, DialogNode] = {}
        self.__current_selected_key: str = "head"
        self.__font_size: int = 10
        self.__most_right: int = 0
        self.__most_top: int = 0
        self.__most_bottom: int = 0

    # 新增node
    def add_node(self, key: str, next_keys: list[str]) -> None:
        self.__nodes_map[key] = DialogNode(key, self.__font_size, next_keys)
        self._if_update_needed = True

    # 重新添加全部的key
    def readd_all(self, dialogs_data: dict) -> None:
        self.__nodes_map.clear()
        for key in dialogs_data:
            next_keys: list[str] = []
            if dialogs_data[key]["next_dialog_id"] is not None:
                if dialogs_data[key]["next_dialog_id"]["type"] == "option":
                    for next_keys_options in dialogs_data[key]["next_dialog_id"]["target"]:
                        next_keys.append(next_keys_options["id"])
                elif isinstance(the_next_key := dialogs_data[key]["next_dialog_id"]["target"], (str, int)):
                    next_keys.append(str(the_next_key))
            self.add_node(key, next_keys)

    # 更新选中的key
    def update_selected(self, new_current_select: str) -> None:
        self.__current_selected_key = new_current_select
        self._if_update_needed = True

    # 获取当前选中的key
    def get_selected_key(self) -> str:
        return self.__current_selected_key

    def __update_node_pos(self, key: str = "head", offset_x: int = 0, offset_y: int = 0) -> int:
        key_node: DialogNode = self.__nodes_map[key]
        if not key_node.has_been_displayed:
            # 设置坐标并展示
            key_node.set_pos(offset_x, offset_y)
            key_node.has_been_displayed = True
            panding: int = 4 * self.__font_size
            if len(key_node.next_keys) > 1:
                offset_y = key_node.y - len(key_node.next_keys) * self.__font_size - panding
            for child_key in key_node.next_keys:
                offset_y = self.__update_node_pos(child_key, key_node.x + self.__font_size * 10, offset_y)
                offset_y += panding
            if self.__most_right < key_node.right:
                self.__most_right = key_node.right
            if self.__most_bottom < key_node.bottom:
                self.__most_bottom = key_node.bottom
            if self.__most_top > key_node.top:
                self.__most_top = key_node.top
        return offset_y

    def __draw_node(self, surface: ImageSurface, key: str = "head") -> None:
        key_node: DialogNode = self.__nodes_map[key]
        if not key_node.has_been_displayed:
            # 设置坐标并展示
            key_node.display(surface)
            key_node.has_been_displayed = True

            if self.__current_selected_key == key:
                Draw.rect(surface, Colors.RED, key_node.get_rect(), 4)

            for child_key in key_node.next_keys:
                self.__draw_node(surface, child_key)
                Draw.aaline(surface, Colors.BLACK, key_node.right_center, self.__nodes_map[child_key].left_center, 3)

    def _update(self) -> None:
        if "head" in self.__nodes_map:
            for key in self.__nodes_map:
                self.__nodes_map[key].has_been_displayed = False
            self.__most_right = 0
            self.__most_bottom = 0
            self.__update_node_pos()
            for key in self.__nodes_map:
                self.__nodes_map[key].has_been_displayed = False
                self.__nodes_map[key].y -= self.__most_top
            self._content_surface = Surface.transparent((self.__most_right, self.__most_bottom - self.__most_top))
            self.__draw_node(self._content_surface)
            self._if_update_needed = False
        else:
            EXCEPTION.fatal("Head is missing")

    def _any_content_container_event(self) -> bool:
        for key in self.__nodes_map:
            if convert_rect(
                (
                    Coordinates.subtract(
                        Coordinates.add(self.__nodes_map[key].pos, (self.x, self.content_container_y)), self.local_pos
                    ),
                    self.__nodes_map[key].get_size(),
                )
            ).is_hovered():
                self.update_selected(key)
                return True
        return False
