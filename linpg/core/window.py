import PySimpleGUI  # type: ignore
from pygame._sdl2 import Renderer, Window

from .frame import *

# 设置PySimpleGUI主题
PySimpleGUI.theme(Specification.get("PySimpleGUITheme"))


# 确认窗口
class ConfirmMessageWindow:
    def __init__(self, title: str, message: str, keep_on_top: bool = True) -> None:
        self.__title: str = title
        self.__message: str = message
        self.__keep_on_top: bool = keep_on_top

    @staticmethod
    def YES() -> str:
        return Lang.get_text("Global", "yes")

    @staticmethod
    def NO() -> str:
        return Lang.get_text("Global", "no")

    # 更新信息
    def update_message(self, message: str) -> None:
        self.__message = message

    # 展示窗口
    def show(self) -> str:
        return str(
            PySimpleGUI.Window(
                self.__title,
                [[PySimpleGUI.Text(self.__message)], [PySimpleGUI.Submit(self.YES()), PySimpleGUI.Cancel(self.NO())]],
                keep_on_top=self.__keep_on_top,
            ).read(close=True)[0]
        )


# 警告窗口
class LinpgVersionChecker:
    def __init__(self, action: str, recommended_revision: int, recommended_patch: int, recommended_version: int = 3) -> None:
        if not Info.ensure_linpg_version(action, recommended_revision, recommended_patch, recommended_version):
            _quit_text: str = Lang.get_text("LinpgVersionIncorrect", "exit_button")
            if (
                PySimpleGUI.Window(
                    Lang.get_text("Global", "warning"),
                    [
                        [
                            PySimpleGUI.Text(
                                Lang.get_text("LinpgVersionIncorrect", "message").format(
                                    "3.{0}.{1}".format(recommended_revision, recommended_patch), Info.get_current_version()
                                )
                            )
                        ],
                        [
                            PySimpleGUI.Submit(Lang.get_text("LinpgVersionIncorrect", "continue_button")),
                            PySimpleGUI.Cancel(_quit_text),
                        ],
                    ],
                    keep_on_top=True,
                ).read(close=True)[0]
                == _quit_text
            ):
                from sys import exit
                exit()


# 窗口
class RenderedWindow(Rectangle):
    def __init__(self, width: int, height: int, title: str, is_win_always_on_top: bool) -> None:
        super().__init__(0, 0, width, height)
        self.title: str = title
        self.always_on_top: bool = is_win_always_on_top
        self.__win: Renderer = Renderer(Window(self.title, self.size, always_on_top=self.always_on_top))

    # 设置尺寸
    def set_width(self, value: int_f) -> None:
        super().set_width(value)
        self.__update_window()

    def set_height(self, value: int_f) -> None:
        super().set_height(value)
        self.__update_window()

    # 更新窗口
    def __update_window(self) -> None:
        self.__win = Renderer(Window(self.title, self.size, always_on_top=self.always_on_top))

    def draw_rect(self, rect_pos: RectLiked, color: color_liked) -> None:
        _color: tuple[int, int, int, int] = Colors.get(color)
        self.__win.draw_color = pygame.Color(_color[0], _color[1], _color[2], _color[3])
        self.__win.draw_rect(convert_to_pygame_rect(rect_pos))

    def fill_rect(self, rect_pos: RectLiked, color: color_liked) -> None:
        _color: tuple[int, int, int, int] = Colors.get(color)
        self.__win.draw_color = pygame.Color(_color[0], _color[1], _color[2], _color[3])
        self.__win.fill_rect(convert_to_pygame_rect(rect_pos))

    def fill(self, color: color_liked) -> None:
        self.fill_rect(((0, 0), self.get_size()), color)

    # 清空窗口
    def clear(self) -> None:
        self.__win.clear()

    # 展示
    def present(self) -> None:
        self.__win.present()
