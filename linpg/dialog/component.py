from .dialogbox import *

# 对话系统按钮UI模块
class DialogButtons(HiddenableSurface):
    def __init__(self) -> None:
        super().__init__()
        self.__button_hovered_index: int = 0
        self.__buttons_container: GameObjectsDictContainer = NULL_DICT_CONTAINER
        self.initialize()

    # 初始化
    def initialize(self) -> None:
        # 从设置中读取信息
        self.FONT = Font.create(Display.get_width() * 0.0175)
        # 取消隐藏按钮
        self.__buttons_container = UI.generate_container("dialog_buttons", {"button_size": self.FONT.size})
        # 自动播放模式
        self.autoMode: bool = False
        # 事件查询表
        self.__button_hovered_lookup_table: tuple[str, ...] = ("", "show", "hide", "skip", "auto", "history")

    @property
    def item_being_hovered(self) -> str:
        return self.__button_hovered_lookup_table[self.__button_hovered_index]

    def set_visible(self, visible: bool) -> None:
        super().set_visible(visible)
        if self.is_hidden():
            self.__buttons_container.get("hide").set_visible(False)
            self.__buttons_container.get("history").set_visible(False)
            self.__buttons_container.get("not_auto").set_visible(False)
            self.__buttons_container.get("is_auto").set_visible(False)
            self.__buttons_container.get("skip").set_visible(False)
            self.__buttons_container.get("show").set_visible(True)
        else:
            self.__buttons_container.get("hide").set_visible(True)
            self.__buttons_container.get("history").set_visible(True)
            self.__buttons_container.get("not_auto").set_visible(not self.autoMode)
            self.__buttons_container.get("is_auto").set_visible(self.autoMode)
            self.__buttons_container.get("skip").set_visible(True)
            self.__buttons_container.get("show").set_visible(False)

    def draw(self, surface: ImageSurface) -> None:
        self.__button_hovered_index = 0
        self.__buttons_container.draw(surface)
        if self.is_hidden():
            if self.__buttons_container.item_being_hovered == "show":
                self.__button_hovered_index = 1
        elif self.__buttons_container.item_being_hovered is not None:
            if self.__buttons_container.item_being_hovered == "hide":
                self.__button_hovered_index = 2
            elif self.__buttons_container.item_being_hovered == "history":
                self.__button_hovered_index = 5
            elif (
                self.__buttons_container.item_being_hovered == "not_auto"
                or self.__buttons_container.item_being_hovered == "is_auto"
            ):
                self.__button_hovered_index = 4
            elif self.__buttons_container.item_being_hovered == "skip":
                self.__button_hovered_index = 3

    def autoModeSwitch(self) -> None:
        self.autoMode = not self.autoMode
        self.__buttons_container.get("not_auto").set_visible(not self.autoMode)
        self.__buttons_container.get("is_auto").set_visible(self.autoMode)


class DialogNode(Button):
    def __init__(self, key_name: str, font_size: int, next_keys: list[str], tag: str = ""):
        self.__key_name: str = key_name
        button_surface = Font.render_description_box(self.__key_name, Colors.BLACK, font_size, font_size, Colors.WHITE)
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
            self._content_surface = new_transparent_surface((self.__most_right, self.__most_bottom - self.__most_top))
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
