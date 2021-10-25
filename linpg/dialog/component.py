from .dialogbox import *

# 对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        self.__button_hovered: int = 0
        self.hidden: bool = False
        self.__buttons_container = None
        self.initialize()

    # 初始化
    def initialize(self) -> None:
        # 从设置中读取信息
        self.FONT = Font.create(Display.get_width() * 0.0175)
        # 从语言文件中读取按钮文字
        dialog_txt: dict = Lang.get_texts("Dialog")
        # 生成跳过按钮
        tempButtonIcon = IMG.load("<!ui>next.png", (self.FONT.size, self.FONT.size))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"], Color.WHITE)
        temp_w = tempButtonTxt.get_width() + self.FONT.size * 1.5
        self.choiceTxt = dialog_txt["choice"]
        self.skipButton = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.skipButtonHovered = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.icon_y = (tempButtonTxt.get_height() - tempButtonIcon.get_height()) / 2
        self.skipButtonHovered.blit(tempButtonIcon, (tempButtonTxt.get_width() + self.FONT.size * 0.5, self.icon_y))
        self.skipButtonHovered.blit(tempButtonTxt, (0, 0))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"], Color.GRAY)
        tempButtonIcon = IMG.add_darkness(tempButtonIcon, 100)
        self.skipButton.blit(tempButtonIcon, (tempButtonTxt.get_width() + self.FONT.size * 0.5, self.icon_y))
        self.skipButton.blit(tempButtonTxt, (0, 0))
        self.skipButton = StaticImage(self.skipButton, Display.get_width() * 0.9, Display.get_height() * 0.05)
        self.skipButtonHovered = StaticImage(self.skipButtonHovered, Display.get_width() * 0.9, Display.get_height() * 0.05)
        # 生成自动播放按钮
        self.autoIconHovered = IMG.load("<!ui>auto.png", (self.FONT.size, self.FONT.size))
        self.autoIcon = IMG.add_darkness(self.autoIconHovered, 100)
        self.autoIconDegree = 0
        self.autoIconDegreeChange = (2 ** 0.5 - 1) * self.FONT.size / 45
        self.autoMode: bool = False
        tempButtonTxt = self.FONT.render(dialog_txt["auto"], Color.GRAY)
        temp_w = tempButtonTxt.get_width() + self.FONT.size * 1.5
        self.autoButton = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.autoButtonHovered = new_transparent_surface((temp_w, tempButtonTxt.get_height()))
        self.autoButton.blit(tempButtonTxt, (0, 0))
        self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"], Color.WHITE), (0, 0))
        self.autoButton = DynamicImage(self.autoButton, Display.get_width() * 0.8, Display.get_height() * 0.05)
        self.autoButton.tag = int(self.autoButton.x + self.autoButton.img.get_width() - self.FONT.size)
        self.autoButtonHovered = DynamicImage(self.autoButtonHovered, Display.get_width() * 0.8, Display.get_height() * 0.05)
        self.autoButtonHovered.tag = int(self.autoButtonHovered.x + self.autoButtonHovered.img.get_width() - self.FONT.size)
        # 取消隐藏按钮
        self.showButton = load_button(
            "<!ui>show.png", (Display.get_width() * 0.05, Display.get_height() * 0.05), (self.FONT.size, self.FONT.size), 150
        )
        self.__buttons_container = UI.generate("dialog_buttons", {"button_size": self.FONT.size})

    @property
    def item_being_hovered(self) -> str:
        if self.__button_hovered == 1:
            return "hide"
        elif self.__button_hovered == 2:
            return "skip"
        elif self.__button_hovered == 3:
            return "auto"
        elif self.__button_hovered == 4:
            return "history"
        else:
            return ""

    def draw(self, surface: ImageSurface) -> None:
        self.__button_hovered = 0
        if self.hidden is True:
            self.showButton.draw(surface)
            if self.showButton.is_hover():
                self.__button_hovered = 1
        else:
            self.__buttons_container.draw(surface)
            if self.skipButton.is_hover():
                self.skipButtonHovered.draw(surface)
                self.__button_hovered = 2
            else:
                self.skipButton.draw(surface)
            if self.autoButton.is_hover():
                self.autoButtonHovered.draw(surface)
                if self.autoMode:
                    rotatedIcon = IMG.rotate(self.autoIconHovered, self.autoIconDegree)
                    surface.blit(
                        rotatedIcon,
                        (
                            self.autoButtonHovered.tag + self.autoIconHovered.get_width() / 2 - rotatedIcon.get_width() / 2,
                            self.autoButtonHovered.y
                            + self.icon_y
                            + self.autoIconHovered.get_height() / 2
                            - rotatedIcon.get_height() / 2,
                        ),
                    )
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    surface.blit(self.autoIconHovered, (self.autoButtonHovered.tag, self.autoButtonHovered.y + self.icon_y))
                self.__button_hovered = 3
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(surface)
                    rotatedIcon = IMG.rotate(self.autoIconHovered, self.autoIconDegree)
                    surface.blit(
                        rotatedIcon,
                        (
                            self.autoButtonHovered.tag + self.autoIconHovered.get_width() / 2 - rotatedIcon.get_width() / 2,
                            self.autoButtonHovered.y
                            + self.icon_y
                            + self.autoIconHovered.get_height() / 2
                            - rotatedIcon.get_height() / 2,
                        ),
                    )
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    self.autoButton.draw(surface)
                    surface.blit(self.autoIcon, (self.autoButton.tag, self.autoButton.y + self.icon_y))
            if self.__buttons_container.item_being_hovered == "hide":
                self.__button_hovered = 1
            elif self.__buttons_container.item_being_hovered == "history":
                self.__button_hovered = 4

    def autoModeSwitch(self) -> None:
        if not self.autoMode:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0


class DialogNode(Button):
    def __init__(self, key_name: str, font_size: int, next_keys: list[str], tag: str = ""):
        self.__key_name: str = key_name
        button_surface = Font.render_description_box(self.__key_name, Color.BLACK, font_size, font_size, Color.WHITE)
        super().__init__(button_surface, 0, 0, width=button_surface.get_width(), height=button_surface.get_height(), tag=tag)
        self.__next_keys: tuple[str] = tuple(next_keys)
        self.has_been_displayed: bool = False

    # 下一个keys
    @property
    def next_keys(self) -> tuple[str]:
        return self.__next_keys

    # 展示（注意，你无法在此输入off_set，你必须提前设置）
    def display(self, surface: ImageSurface) -> None:
        return super().display(surface)


class DialogNavigatorWindow(AbstractSurfaceWindow):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = ""):
        super().__init__(x, y, width, height, tag=tag)
        self.__node_maps: dict[str, DialogNode] = {}
        self.__current_selected_key: str = "head"
        self.__font_size: int = 10
        self.__most_right: int = 0
        self.__most_top: int = 0
        self.__most_bottom: int = 0

    def add_node(self, key: str, next_keys: list[str]) -> None:
        self.__node_maps[key] = DialogNode(key, self.__font_size, next_keys)
        self._if_update_needed = True

    def add_all(self, dialogs_data: dict):
        for key in dialogs_data:
            next_keys: list[str] = []
            if dialogs_data[key]["next_dialog_id"]["type"] == "option":
                for next_keys_options in dialogs_data[key]["next_dialog_id"]["target"]:
                    next_keys.append(next_keys_options["id"])
            else:
                next_keys: list[str].append(dialogs_data[key]["next_dialog_id"]["target"])
            self.add_node(dialogs_data[key], next_keys)

    def update_selected(self, new_current_select: str) -> None:
        self.__current_selected_key = new_current_select
        self._if_update_needed = True

    def __update_node_pos(self, key: str = "head", offset_x: int = 0, offset_y: int = 0) -> None:
        key_node: DialogNode = self.__node_maps[key]
        if not key_node.has_been_displayed:
            # 设置坐标并展示
            key_node.set_pos(offset_x, offset_y)
            key_node.has_been_displayed = True
            panding: int = 4 * self.__font_size
            if len(key_node.next_keys) > 1:
                offset_y = key_node.y - len(key_node.next_keys) * self.__font_size - panding
            for child_key in key_node.next_keys:
                offset_y += panding
                offset_y = self.__update_node_pos(child_key, key_node.x + self.__font_size * 10, offset_y)
            if self.__most_right < key_node.right:
                self.__most_right = key_node.right
            if self.__most_bottom < key_node.bottom:
                self.__most_bottom = key_node.bottom
            if self.__most_top > key_node.top:
                self.__most_top = key_node.top
        return offset_y

    def __draw_node(self, surface: ImageSurface, key: str = "head") -> int:
        key_node: DialogNode = self.__node_maps[key]
        if not key_node.has_been_displayed:
            # 设置坐标并展示
            key_node.display(surface)
            key_node.has_been_displayed = True

            if Controller.mouse.get_pressed(0) is True and is_hover(convert_rect(key_node.get_rect())):
                self.update_selected(key)

            if self.__current_selected_key == key:
                draw_rect(surface, Color.RED, key_node.get_rect(), 4)

            for child_key in key_node.next_keys:
                self.__draw_node(surface, child_key)
                pygame.draw.aaline(surface, Color.BLACK, key_node.right_center, self.__node_maps[child_key].left_center, 3)

    def _update(self) -> None:
        if "head" in self.__node_maps:
            for key in self.__node_maps:
                self.__node_maps[key].has_been_displayed = False
            self.__most_right = 0
            self.__most_bottom = 0
            self.__update_node_pos()
            for key in self.__node_maps:
                self.__node_maps[key].has_been_displayed = False
                self.__node_maps[key].y -= self.__most_top
            self._content_surface = new_transparent_surface((self.__most_right, self.__most_bottom - self.__most_top))
            self.__draw_node(self._content_surface)

            self._if_update_needed = False
        else:
            EXCEPTION.fatal("Head is missing")

    def _process_content_surface_events(self) -> bool:
        return False
