import time

_SPEECH_RECOGNITION_ENABLED: bool = False

try:
    import speech_recognition as sr  # type: ignore

    _SPEECH_RECOGNITION_ENABLED = True
except ImportError:
    _SPEECH_RECOGNITION_ENABLED = False

from .scrollbar import *


# 输入框Abstract，请勿实体化
class AbstractInputBox(GameObject2d, metaclass=ABCMeta):
    def __init__(self, x: int_f, y: int_f, font_size: int, txt_color: color_liked, default_width: int) -> None:
        super().__init__(x, y)
        self._FONT: FontGenerator = Font.create(font_size)
        self._default_width: int = default_width
        self._default_height: int = self._FONT.size * 3 // 2
        self._input_box: Rectangle = Rectangle(x, y, default_width, self._default_height)
        self._color: tuple[int, int, int, int] = Colors.LIGHT_SKY_BLUE
        self._text_color: tuple[int, int, int, int] = Colors.get(txt_color)
        self._active: bool = False
        self._holder: ImageSurface = self._FONT.render("|", self._text_color)
        self._holder_index: int = 0
        # display holder
        self._display_holder_timer: BoolTickTimer = BoolTickTimer(500)
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

    def _add_text(self, _content: str) -> None:
        if len(_content) > 0:
            self._text = self._text[: self._holder_index] + _content + self._text[self._holder_index :]
            self._holder_index += len(_content)
            self._reset_inputbox_width()
        elif Debug.get_developer_mode():
            EXCEPTION.inform("The value of event.unicode is empty!")

    def _remove_char(self, action: Locations) -> None:
        if action is Locations.BEGINNING:
            if self._holder_index > 0:
                self._text = self._text[: self._holder_index - 1] + self._text[self._holder_index :]
                self._holder_index -= 1
        elif action is Locations.END:
            if self._holder_index < len(self._text):
                self._text = self._text[: self._holder_index] + self._text[self._holder_index + 1 :]
        elif action is Locations.EVERYWHERE:
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
                self._remove_char(Locations.BEGINNING)
                return True
            case Keys.DELETE:
                self._remove_char(Locations.END)
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
                    self._add_text(Keys.get_clipboard())
                    return True
        return False

    # 画出文字内容
    def _draw_content(self, _surface: ImageSurface, with_holder: bool = True) -> None:
        if self._text is not None and len(self._text) > 0:
            font_t = self._FONT.render(self._text, self._text_color)
            _surface.blit(font_t, (self.x + self._padding, self.y + (self._input_box.height - font_t.get_height()) // 2))
        if with_holder is True:
            self._display_holder_timer.tick()
            if self._display_holder_timer.get_status():
                _surface.blit(self._holder, (self.x + self._padding + self._FONT.estimate_text_width(self._text[: self._holder_index]), self.y + self._padding))

    # 画出内容
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        for event in Controller.get_events():
            match event.type:
                case Events.KEY_DOWN:
                    if self._active is True:
                        if self._check_key_down(event):
                            pass
                        elif event.key == Keys.ESCAPE:
                            self._active = False
                            self.need_save = True
                        else:
                            self._add_text(event.unicode)
                case Events.MOUSE_BUTTON_DOWN:
                    if event.button == 1:
                        if self._active is True:
                            if self.is_hovered(offSet):
                                self._reset_holder_index(Controller.mouse.x)
                            else:
                                self._active = False
                                self.need_save = True
                        elif self.is_hovered(offSet):
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
        # show PySimpleGUI input box button
        self.__show_PySimpleGUI_input_box: Button = Button.load("<&ui>button.png", ORIGIN, (self._FONT.size, self._FONT.size), 150)
        self.__show_PySimpleGUI_input_box.set_text(ButtonComponent.text(Lang.get_text("Editor", "external_inputbox"), font_size // 3))
        self.__show_PySimpleGUI_input_box.set_auto_resize(True)
        # start dictate button
        self.__start_dictating: Button | None = None
        # wether user is using dictation
        self.__is_dictating: bool = False
        if _SPEECH_RECOGNITION_ENABLED and len(sr.Microphone.list_working_microphones()) > 0:
            self.__start_dictating = Button.load("<&ui>button.png", ORIGIN, (self._FONT.size, self._FONT.size), 150)
            self.__start_dictating.set_text(ButtonComponent.text(Lang.get_text("Editor", "dictate"), font_size // 3))
            self.__start_dictating.set_auto_resize(True)
        self.__PySimpleGUIWindow: PySimpleGUI.Window | None = None

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

    def _add_text(self, _content: str) -> None:
        if len(_content) > 0:
            if "\n" not in _content:
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index] + _content + self._text[self.__lineId][self._holder_index :]
                self._holder_index += len(_content)
                self._reset_inputbox_width()
            else:
                theStringAfterHolderIndex = self._text[self.__lineId][self._holder_index :]
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index]
                for i in range(len(_content) - 1):
                    if _content[i] != "\n":
                        self._text[self.__lineId] += _content[i]
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
    def _remove_char(self, action: Locations) -> None:
        if action is Locations.BEGINNING:
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
        elif action is Locations.END:
            if self._holder_index < len(self._text[self.__lineId]):
                self._text[self.__lineId] = self._text[self.__lineId][: self._holder_index] + self._text[self.__lineId][self._holder_index + 1 :]
            elif self.__lineId < len(self._text) - 1:
                # 如果下一行有内容
                if len(self._text[self.__lineId + 1]) > 0:
                    self._text[self.__lineId] += self._text[self.__lineId + 1]
                self._text.pop(self.__lineId + 1)
        elif action is Locations.EVERYWHERE:
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

    # 听写
    def __dictate(self) -> None:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        # Initialize audio
        _audio: sr.AudioData | None = None
        # Capture audio
        try:
            with sr.Microphone() as source:
                _audio = recognizer.listen(source)
        except OSError:
            EXCEPTION.warn("No speaker detected!")
        # try process audio
        if _audio is not None:
            # Recognize speech using Speech API
            try:
                self._add_text(recognizer.recognize_google(_audio, language=Lang.get_current_language_tag()))
            except sr.UnknownValueError:
                EXCEPTION.inform("Speech API could not understand the audio")
            except sr.RequestError as e:
                EXCEPTION.inform(f"Could not request results from Speech API; {e}")
        self.__is_dictating = False

    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if not self.__is_dictating:
            for event in Controller.get_events():
                if self._active:
                    match event.type:
                        case Events.KEY_DOWN:
                            match event.key:
                                case Keys.BACKSPACE:
                                    self._remove_char(Locations.BEGINNING)
                                case Keys.DELETE:
                                    self._remove_char(Locations.END)
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
                                        self._add_text(Keys.get_clipboard())
                                    else:
                                        self._add_text(event.unicode)
                        case Events.MOUSE_BUTTON_DOWN:
                            if event.button == 1:
                                if self.is_hovered(offSet):
                                    self._reset_holder_index(Controller.mouse.x, Controller.mouse.y)
                                # make sure the mouse if outside the box and not press buttons
                                elif not self.__show_PySimpleGUI_input_box.is_hovered() and (
                                    self.__start_dictating is None or not self.__start_dictating.is_hovered()
                                ):
                                    self._active = False
                                    self.need_save = True
                elif event.type == Events.MOUSE_BUTTON_DOWN and event.button == 1 and self.is_hovered(offSet):
                    self._active = True
                    self._reset_holder_index(Controller.mouse.x, Controller.mouse.y)
        # 计算绝对坐标
        abs_pos: Final[tuple[int, int]] = Coordinates.add(self.get_pos(), offSet)
        # 如果有内容
        if self._text is not None:
            for i in range(len(self._text)):
                # 画出文字
                _surface.blit(self._FONT.render(self._text[i], self._text_color), (abs_pos[0] + self._FONT.size // 4, abs_pos[1] + i * self._default_height))
        # 如果输入模式被激活
        if self._active:
            # 画出输入框
            Draw.rect(_surface, self._color, self._input_box.get_rect(), 2)
            if self.__is_dictating:
                Draw.rect(_surface, (0, 0, 0, 150), self._input_box.get_rect())
                Draw.circle(_surface, Colors.RED, self._input_box.center, self._FONT.size // 4)
            # make sure disable button when is dictating
            else:
                # 画出 “|” 符号
                self._display_holder_timer.tick()
                if self._display_holder_timer.get_status():
                    _surface.blit(
                        self._holder,
                        (
                            abs_pos[0] + self._FONT.size // 10 + self._FONT.estimate_text_width(self._text[self.__lineId][: self._holder_index]),
                            abs_pos[1] + self.__lineId * self._default_height,
                        ),
                    )
                # 展示基于PySimpleGUI的外部输入框
                self.__show_PySimpleGUI_input_box.set_right(self._input_box.right)
                self.__show_PySimpleGUI_input_box.set_top(self._input_box.bottom)
                self.__show_PySimpleGUI_input_box.draw(_surface)
                if self.__PySimpleGUIWindow is not None:
                    external_input_event, external_input_values = self.__PySimpleGUIWindow.read()
                    if external_input_event == PySimpleGUI.WIN_CLOSED:
                        self.__PySimpleGUIWindow.close()
                        self.__PySimpleGUIWindow = None
                    else:
                        in_text: str | None = external_input_values.get("CONTENT")
                        if in_text is not None:
                            self._remove_char(Locations.EVERYWHERE)
                            self._add_text(in_text)
                elif self.__show_PySimpleGUI_input_box.is_hovered() and Controller.get_event("confirm"):
                    self.__PySimpleGUIWindow = PySimpleGUI.Window(
                        Lang.get_text("Editor", "external_inputbox"),
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
                # voice to text
                if self.__start_dictating is not None:
                    self.__start_dictating.set_right(self.__show_PySimpleGUI_input_box.left)
                    self.__start_dictating.set_top(self._input_box.bottom)
                    self.__start_dictating.draw(_surface)
                    if self.__start_dictating.is_hovered() and Controller.get_event("confirm"):
                        self.__is_dictating = True
                        threading.Thread(target=self.__dictate).start()
