from .inputbox import *


# 控制台
class Console(SingleLineInputBox, HidableSurface, threading.Thread):

    _COMMAND_INDICATOR: str = "/"

    def __init__(self, x: int_f, y: int_f, font_size: int = 32, default_width: int = 150):
        HidableSurface.__init__(self, False)
        self.color_active = Colors.get("dodgerblue2")
        SingleLineInputBox.__init__(self, x, y, font_size, self.color_active, default_width)
        self.color_inactive = Colors.get("lightskyblue3")
        self._color = self.color_active
        self._active: bool = True
        self._text_history: list[str] = []
        self.__backward_id: int = 1
        self._txt_output: list[str] = []
        # 初始化多线程模块
        threading.Thread.__init__(self)
        # 多线程锁
        self.__THREADING_LOCK: threading.Lock = threading.Lock()
        self.daemon = True

    # 安全地设置文字（主要用于确保多线程运行）
    def safely_set_text(self, new_txt: str) -> None:
        self.__THREADING_LOCK.acquire()
        super().set_text(new_txt)
        self.__THREADING_LOCK.release()

    # 启用基于命令行的多线程模式
    def run(self) -> None:
        self.__is_using_threading = True
        while self.__is_using_threading:
            txt: str = self._COMMAND_INDICATOR + input("> ")
            self.__THREADING_LOCK.acquire()
            self._text = txt
            self.__execute_command()
            print(self._txt_output[len(self._txt_output) - 1])
            self.__THREADING_LOCK.release()

    def _check_key_down(self, event: PG_Event) -> bool:
        if super()._check_key_down(event):
            return True
        # 向上-过去历史
        elif event.key == Keys.ARROW_UP and self.__backward_id < len(self._text_history):
            self.__backward_id += 1
            self.safely_set_text(self._text_history[-self.__backward_id])
            return True
        # 向下-过去历史，最近的一个
        elif event.key == Keys.ARROW_DOWN and self.__backward_id > 1:
            self.__backward_id -= 1
            self.safely_set_text(self._text_history[-self.__backward_id])
            return True
        # 回车
        elif event.key == Keys.RETURN:
            self.__THREADING_LOCK.acquire()
            if len(self._text) > 0:
                self.__execute_command()
            else:
                EXCEPTION.inform("The input box is empty!")
            self.__THREADING_LOCK.release()
            return True
        # ESC，关闭
        elif event.key == Keys.ESCAPE:
            self._active = False
            # Change the current color of the input box.
            self._color = self.color_active if self._active else self.color_inactive
            return True
        return False

    # 处理命令
    def __execute_command(self) -> None:
        if self._text.startswith(self._COMMAND_INDICATOR):
            self._check_command(self._text.removeprefix(self._COMMAND_INDICATOR).split())
        else:
            self._txt_output.append(self._text)
        self._text_history.append(self._text)
        self.__backward_id = 0
        self.set_text()

    # 根据参数处理命令
    def _check_command(self, command_blocks: list[str]) -> None:
        if command_blocks[0] == "cheat":
            if len(command_blocks) < 2:
                self._txt_output.append("Unknown status for cheat command.")
            elif command_blocks[1] == "on":
                if Debug.get_cheat_mode() is True:
                    self._txt_output.append("Cheat mode has already been activated!")
                else:
                    Debug.set_cheat_mode(True)
                    self._txt_output.append("Cheat mode is activated.")
            elif command_blocks[1] == "off":
                if not Debug.get_cheat_mode():
                    self._txt_output.append("Cheat mode has already been deactivated!")
                else:
                    Debug.set_cheat_mode(False)
                    self._txt_output.append("Cheat mode is deactivated.")
            else:
                self._txt_output.append("Unknown status for cheat command.")
        elif command_blocks[0] == "show":
            if len(command_blocks) >= 3:
                if command_blocks[1] == "fps":
                    if command_blocks[2] == "on":
                        Debug.set_show_fps(True)
                    elif command_blocks[2] == "off":
                        Debug.set_show_fps(False)
                    else:
                        self._txt_output.append("Unknown status for show command.")
                else:
                    self._txt_output.append("Unknown status for show command.")
            else:
                self._txt_output.append("Unknown status for show command.")
        elif command_blocks[0] == "say":
            self._txt_output.append(self._text[len(self._COMMAND_INDICATOR) + 4 :])
        elif command_blocks[0] == "set":
            Setting.set(*command_blocks[1 : len(command_blocks) - 1], value=command_blocks[len(command_blocks) - 1])
        elif command_blocks[0] == "dev":
            if len(command_blocks) < 2:
                self._txt_output.append("Unknown status for dev command.")
            elif command_blocks[1] == "on":
                if Debug.get_developer_mode() is True:
                    self._txt_output.append("Developer mode has been activated!")
                else:
                    Debug.set_developer_mode(True)
                    self._txt_output.append("Developer mode is activated.")
            elif command_blocks[1] == "off":
                if not Debug.get_developer_mode():
                    self._txt_output.append("Developer mode has been deactivated!")
                else:
                    Debug.set_developer_mode(False)
                    self._txt_output.append("Developer mode is deactivated.")
            else:
                self._txt_output.append("Unknown status for dev command.")
        elif command_blocks[0] == "linpg" and len(command_blocks) > 1 and command_blocks[1] == "info":
            self._txt_output.append("Linpg Version: {}".format(Info.get_current_version()))
        elif command_blocks[0] == "quit":
            Display.quit()
        elif command_blocks[0] == "clear":
            self._txt_output.clear()
        else:
            self._txt_output.append("The command is unknown!")

    def draw(self, _surface: ImageSurface) -> None:
        if self.is_hidden():
            for event in Controller.get_events():
                if event.type == Keys.DOWN and event.unicode == self._COMMAND_INDICATOR:
                    self.set_visible(True)
                    break
        else:
            for event in Controller.get_events():
                if event.type == MOUSE_BUTTON_DOWN:
                    if self.x <= Controller.mouse.x <= self.x + self._input_box.width and self.y <= Controller.mouse.y <= self.y + self._input_box.height:
                        self._active = not self._active
                        # Change the current color of the input box.
                        self._color = self.color_active if self._active else self.color_inactive
                    else:
                        self._active = False
                        self._color = self.color_inactive
                elif event.type == Keys.DOWN:
                    if self._active is True:
                        if self._check_key_down(event):
                            pass
                        else:
                            self._add_chars(event.unicode)
                    else:
                        if event.key == Keys.BACKQUOTE or event.key == Keys.ESCAPE:
                            self.set_visible(False)
                            self.set_text()
            # 画出输出信息
            for i in range(len(self._txt_output)):
                _surface.blit(
                    self._FONT.render(self._txt_output[i], self._color),
                    (self.x + self._FONT.size // 4, self.y - (len(self._txt_output) - i) * self._FONT.size * 3 / 2),
                )
            # 画出输入框
            Draw.rect(_surface, self._color, self._input_box.get_rect(), 2)
            # 画出文字
            self._draw_content(_surface)
