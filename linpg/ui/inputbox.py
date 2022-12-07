import time

from .scrollbar import *

# 用于表示移除字符的位置的Enum
class _RemoveCharLocation(enum.IntEnum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    ALL = enum.auto()


# 输入框Abstract，请勿实体化
class AbstractInputBox(GameObject2d, metaclass=ABCMeta):
    def __init__(self, x: int_f, y: int_f, font_size: int, txt_color: color_liked, default_width: int) -> None:
        super().__init__(x, y)
        self._FONT: FontGenerator = Font.create(font_size)
        self._default_width: int = default_width
        self._default_height: int = self._FONT.size * 3 // 2
        self._input_box: Rectangle = Rectangle(x, y, default_width, self._default_height)
        self._color: tuple[int, int, int, int] = Colors.get("lightskyblue")
        self._text_color: tuple[int, int, int, int] = Colors.get(txt_color)
        self._active: bool = False
        self._holder: ImageSurface = self._FONT.render("|", self._text_color)
        self._holder_index: int = 0
        self.need_save: bool = False

    def get_width(self) -> int:
        return self._input_box.width

    def get_height(self) -> int:
        return self._input_box.height

    def get_fontsize(self) -> int:
        return self._FONT.size

    def set_fontsize(self, font_size: int) -> None:
        self._FONT.update(font_size)

    def set_pos(self, x: int_f, y: int_f) -> None:
        super().set_pos(x, y)
        self._input_box = Rectangle(x, y, self._default_width, self._FONT.size * 3 // 2)


# 单行输入框
class SingleLineInputBox(AbstractInputBox):
    def __init__(self, x: int_f, y: int_f, font_size: int, txt_color: color_liked, default_width: int = 150) -> None:
        super().__init__(x, y, font_size, txt_color, default_width)
        self._text: str = ""
        self._left_ctrl_pressing: bool = False
        self._padding: int = (self._input_box.height - self._holder.get_height()) // 2

    def get_text(self) -> str:
        self.need_save = False
        return self._text

    def set_text(self, new_txt: str = "") -> None:
        self._text = new_txt
        self._holder_index = len(self._text)
        self._reset_inputbox_width()

    def _add_chars(self, chars: str) -> None:
        if len(chars) > 0:
            self._text = self._text[: self._holder_index] + chars + self._text[self._holder_index :]
            self._holder_index += len(chars)
            self._reset_inputbox_width()
        elif Debug.get_developer_mode():
            EXCEPTION.inform("The value of event.unicode is empty!")

    def _remove_char(self, action: _RemoveCharLocation) -> None:
        if action is _RemoveCharLocation.LEFT:
            if self._holder_index > 0:
                self._text = self._text[: self._holder_index - 1] + self._text[self._holder_index :]
                self._holder_index -= 1
        elif action is _RemoveCharLocation.RIGHT:
            if self._holder_index < len(self._text):
                self._text = self._text[: self._holder_index] + self._text[self._holder_index + 1 :]
        elif action is _RemoveCharLocation.ALL:
            self.set_text()
        else:
            EXCEPTION.fatal("Action has to be either 'ahead' or 'behind'!")
        self._reset_inputbox_width()

    def _reset_holder_index(self, mouse_x: int) -> None:
        last_width: int = 0
        local_x: int = mouse_x - self.x
        new_width: int = 0
        i: int = 0
        for i in range(len(self._text)):
            new_width = self._FONT.estimate_text_width(self._text[:i]) + self._FONT.size // 4
            if new_width > local_x:
                break
            else:
                last_width = new_width
        if (new_width - local_x) < (local_x - last_width):
            self._holder_index = i
        else:
            self._holder_index = i - 1

    def _reset_inputbox_width(self) -> None:
        if self._text is not None and len(self._text) > 0:
            self._input_box.set_width(max(self._default_width, self._FONT.estimate_text_width(self._text) + self._FONT.size * 3 // 5))
        else:
            self._input_box.set_width(self._default_width)

    def _check_key_down(self, event: PG_Event) -> bool:
        match event.key:
            case Keys.BACKSPACE:
                self._remove_char(_RemoveCharLocation.LEFT)
                return True
            case Keys.DELETE:
                self._remove_char(_RemoveCharLocation.RIGHT)
                return True
            case Keys.ARROW_LEFT:
                if self._holder_index > 0:
                    self._holder_index -= 1
                    return True
            case Keys.ARROW_RIGHT:
                if self._holder_index < len(self._text):
                    self._holder_index += 1
                    return True
            case _:
                if (event.unicode == "v" and Keys.get_pressed("v") and Keys.get_pressed(Keys.LEFT_CTRL)) or (
                    event.key == Keys.LEFT_CTRL and Keys.get_pressed("v") and Keys.get_pressed(Keys.LEFT_CTRL)
                ):
                    self._add_chars(Keys.get_clipboard())
                    return True
        return False

    # 画出文字内容
    def _draw_content(self, _surface: ImageSurface, with_holder: bool = True) -> None:
        if self._text is not None and len(self._text) > 0:
            font_t = self._FONT.render(self._text, self._text_color)
            _surface.blit(font_t, (self.x + self._padding, self.y + (self._input_box.height - font_t.get_height()) // 2))
        if with_holder is True:
            if int(time.time() % 2) == 0 or len(Controller.get_events()) > 0:
                _surface.blit(self._holder, (self.x + self._padding + self._FONT.estimate_text_width(self._text[: self._holder_index]), self.y + self._padding))

    # 画出内容
    def draw(self, _surface: ImageSurface) -> None:
        for event in Controller.get_events():
            if event.type == Keys.DOWN and self._active is True:
                if self._check_key_down(event):
                    pass
                elif event.key == Keys.ESCAPE:
                    self._active = False
                    self.need_save = True
                else:
                    self._add_chars(event.unicode)
            elif event.type == MOUSE_BUTTON_DOWN and event.button == 1 and self._active is True:
                if self.x <= Controller.mouse.x <= self.x + self._input_box.width and self.y <= Controller.mouse.y <= self.y + self._input_box.height:
                    self._reset_holder_index(Controller.mouse.x)
                else:
                    self._active = False
                    self.need_save = True
            elif (
                event.type == MOUSE_BUTTON_DOWN
                and event.button == 1
                and 0 <= Controller.mouse.x - self.x <= self._input_box.width
                and 0 <= Controller.mouse.y - self.y <= self._input_box.height
            ):
                self._active = True
                self._reset_holder_index(Controller.mouse.x)
        # 画出输入框
        if self._active:
            Draw.rect(_surface, self._color, self._input_box.get_rect(), 2)
        self._draw_content(_surface, self._active)


# 多行输入框
class MultipleLinesInputBox(AbstractInputBox):
    def __init__(self, x: int_f, y: int_f, font_size: int, txt_color: color_liked, default_width: int = 150) -> None:
        super().__init__(x, y, font_size, txt_color, default_width)
        self._text: list[str] = [""]
        self.__lineId: int = 0
        self.__show_PySimpleGUI_input_box: Button = Button.load("<&ui>back.png", (0, 0), (self._FONT.size, self._FONT.size))
        self.__PySimpleGUIWindow: Optional[PySimpleGUI.Window] = None

    def get_text(self) -> list:
        self.need_save = False
        return [] if (len(self._text) == 0 or self._text == [""]) else self._text

    def get_raw_text(self) -> str:
        text: str = ""
        for each_line in self._text:
            text += each_line + "\n"
        text.removesuffix("\n")
        return text

    def set_text(self, new_txt: list = []) -> None:
        if len(new_txt) > 0:
            self._text = new_txt
        else:
            self._text = [""]
        # 防止数值越界
        if self.__lineId > (line_limit := len(self._text) - 1):
            self.__lineId = line_limit
        if self._holder_index > (index_limit := len(self._text[self.__lineId])):
            self._holder_index = index_limit
        # 重置尺寸
        self._reset_inputbox_size()

    def set_fontsize(self, font_size: int) -> None:
        super().set_fontsize(font_size)
        self._reset_inputbox_size()

    def _reset_inputbox_width(self) -> None:
        width: int = self._default_width
        if self._text is not None and len(self._text) > 0:
            for txtTmp in self._text:
                new_width: int = self._FONT.estimate_text_width(txtTmp) + self._FONT.size // 2
                if new_width > width:
                    width = new_width
        self._input_box.set_width(width)

    def _reset_inputbox_height(self) -> None:
        self._input_box.set_height(self._default_height * len(self._text))

    def _reset_inputbox_size(self) -> None:
        self._reset_inputbox_width()
        self._reset_inputbox_height()

    def _add_chars(self, chars: str) -> None:
        if len(chars) > 0:
            if "\n" not in chars:
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index] + chars + self._text[self.__lineId][self._holder_index :]
                self._holder_index += len(chars)
                self._reset_inputbox_width()
            else:
                theStringAfterHolderIndex = self._text[self.__lineId][self._holder_index :]
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index]
                for i in range(len(chars) - 1):
                    if chars[i] != "\n":
                        self._text[self.__lineId] += chars[i]
                        self._holder_index += 1
                    else:
                        self.__lineId += 1
                        self._text.insert(self.__lineId, "")
                        self._holder_index = 0
                self._text[self.__lineId] += theStringAfterHolderIndex
                self._reset_inputbox_size()
        else:
            EXCEPTION.inform("The value of event.unicode is empty!")

    # 删除对应字符
    def _remove_char(self, action: _RemoveCharLocation) -> None:
        if action is _RemoveCharLocation.LEFT:
            if self._holder_index > 0:
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index - 1] + self._text[self.__lineId][self._holder_index :]
                self._holder_index -= 1
            elif self.__lineId > 0:
                # 如果当前行有内容
                if len(self._text[self.__lineId]) > 0:
                    self._holder_index = len(self._text[self.__lineId - 1])
                    self._text[self.__lineId - 1] += self._text[self.__lineId]
                    self._text.pop(self.__lineId)
                    self.__lineId -= 1
                else:
                    self._text.pop(self.__lineId)
                    self.__lineId -= 1
                    self._holder_index = len(self._text[self.__lineId])
        elif action is _RemoveCharLocation.RIGHT:
            if self._holder_index < len(self._text[self.__lineId]):
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index] + self._text[self.__lineId][self._holder_index + 1 :]
            elif self.__lineId < len(self._text) - 1:
                # 如果下一行有内容
                if len(self._text[self.__lineId + 1]) > 0:
                    self._text[self.__lineId] += self._text[self.__lineId + 1]
                self._text.pop(self.__lineId + 1)
        elif action is _RemoveCharLocation.ALL:
            self.set_text()
        else:
            EXCEPTION.fatal("Action has to be either 'ahead' or 'behind'!")
        self._reset_inputbox_size()

    def _reset_holder_index(self, mouse_x: int, mouse_y: int) -> None:
        self.__lineId = round((mouse_y - self.y) / self._FONT.size) - 1
        if self.__lineId < 0:
            self.__lineId = 0
        elif self.__lineId >= len(self._text):
            self.__lineId = len(self._text) - 1
        last_width: int = 0
        local_x: int = mouse_x - self.x
        new_width: int = 0
        i: int = 0
        for i in range(len(self._text[self.__lineId])):
            new_width = self._FONT.estimate_text_width(self._text[self.__lineId][:i]) + self._FONT.size // 4
            if new_width > local_x:
                break
            else:
                last_width = new_width
        if (new_width - local_x) < (local_x - last_width):
            self._holder_index = i
        else:
            self._holder_index = i - 1

    def draw(self, _surface: ImageSurface) -> None:
        for event in Controller.get_events():
            if self._active:
                if event.type == Keys.DOWN:
                    match event.key:
                        case Keys.BACKSPACE:
                            self._remove_char(_RemoveCharLocation.LEFT)
                        case Keys.DELETE:
                            self._remove_char(_RemoveCharLocation.RIGHT)
                        case Keys.ARROW_LEFT:
                            if self._holder_index > 0:
                                self._holder_index -= 1
                        case Keys.ARROW_RIGHT:
                            if self._holder_index < len(self._text[self.__lineId]):
                                self._holder_index += 1
                        case Keys.ARROW_UP:
                            if self.__lineId > 0:
                                self.__lineId -= 1
                                if self._holder_index > len(self._text[self.__lineId]) - 1:
                                    self._holder_index = len(self._text[self.__lineId]) - 1
                        case Keys.ARROW_DOWN:
                            if self.__lineId < len(self._text) - 1:
                                self.__lineId += 1
                                if self._holder_index > len(self._text[self.__lineId]) - 1:
                                    self._holder_index = len(self._text[self.__lineId]) - 1
                        # ESC，关闭
                        case Keys.ESCAPE:
                            self._active = False
                            self.need_save = True
                        case Keys.RETURN:
                            # 如果“|”位于最后
                            if self._holder_index == len(self._text[self.__lineId]):
                                self._text.insert(self.__lineId + 1, "")
                            else:
                                self._text.insert(self.__lineId + 1, self._text[self.__lineId][self._holder_index :])
                                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index]
                            self.__lineId += 1
                            self._holder_index = 0
                            self._reset_inputbox_size()
                        case _:
                            if (
                                event.unicode == "v"
                                and Keys.get_pressed("v")
                                and Keys.get_pressed(Keys.LEFT_CTRL)
                                or event.key == Keys.LEFT_CTRL
                                and Keys.get_pressed("v")
                                and Keys.get_pressed(Keys.LEFT_CTRL)
                            ):
                                self._add_chars(Keys.get_clipboard())
                            else:
                                self._add_chars(event.unicode)
                elif event.type == MOUSE_BUTTON_DOWN and event.button == 1:
                    if self.x <= Controller.mouse.x <= self.x + self._input_box.width and self.y <= Controller.mouse.y <= self.y + self._input_box.height:
                        self._reset_holder_index(Controller.mouse.x, Controller.mouse.y)
                    else:
                        self._active = False
                        self.need_save = True
            elif (
                event.type == MOUSE_BUTTON_DOWN
                and event.button == 1
                and self.x <= Controller.mouse.x <= self.x + self._input_box.width
                and self.y <= Controller.mouse.y <= self.y + self._input_box.height
            ):
                self._active = True
                self._reset_holder_index(Controller.mouse.x, Controller.mouse.y)
        if self._text is not None:
            for i in range(len(self._text)):
                # 画出文字
                _surface.blit(self._FONT.render(self._text[i], self._text_color), (self.x + self._FONT.size // 4, self.y + i * self._default_height))
        if self._active:
            # 画出输入框
            Draw.rect(_surface, self._color, self._input_box.get_rect(), 2)
            # 画出 “|” 符号
            if int(time.time() % 2) == 0 or len(Controller.get_events()) > 0:
                _surface.blit(
                    self._holder,
                    (
                        self.x + self._FONT.size // 10 + self._FONT.estimate_text_width(self._text[self.__lineId][: self._holder_index]),
                        self.y + self.__lineId * self._default_height,
                    ),
                )
            # 展示基于PySimpleGUI的外部输入框
            self.__show_PySimpleGUI_input_box.set_right(self._input_box.right)
            self.__show_PySimpleGUI_input_box.set_bottom(self._input_box.bottom)
            self.__show_PySimpleGUI_input_box.draw(_surface)
            if self.__PySimpleGUIWindow is not None:
                external_input_event, external_input_values = self.__PySimpleGUIWindow.read()
                if external_input_event == PySimpleGUI.WIN_CLOSED:
                    self.__PySimpleGUIWindow.close()
                    self.__PySimpleGUIWindow = None
                else:
                    in_text: Optional[str] = external_input_values.get("CONTENT")
                    if in_text is not None:
                        self._remove_char(_RemoveCharLocation.ALL)
                        self._add_chars(in_text)
            elif self.__show_PySimpleGUI_input_box.is_hovered() and Controller.get_event("confirm"):
                self.__PySimpleGUIWindow = PySimpleGUI.Window(
                    "external input",
                    [
                        [
                            PySimpleGUI.Multiline(
                                default_text=self.get_raw_text(), key="CONTENT", expand_x=True, expand_y=True, auto_size_text=True, enable_events=True
                            )
                        ],
                        [PySimpleGUI.CloseButton(Lang.get_text("Global", "confirm"))],
                    ],
                    size=(Display.get_width() // 5, Display.get_height() // 5),
                    keep_on_top=True,
                    resizable=True,
                    auto_size_buttons=True,
                    auto_size_text=True,
                )
