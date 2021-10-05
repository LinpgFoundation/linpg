from pygame._sdl2 import Renderer, Window, messagebox
from .image import *

# 提示窗口
class Message:
    def __init__(
        self,
        title: str,
        message: str,
        buttons: tuple[str],
        info: bool = False,
        warn: bool = False,
        error: bool = False,
        return_button: int = 0,
        escape_button: int = 0,
    ):
        """Display a message box.
        :param str title: A title string or None.
        :param str message: A message string.
        :param bool info: If ``True``, display an info message.
        :param bool warn: If ``True``, display a warning message.
        :param bool error: If ``True``, display an error message.
        :param tuple buttons: An optional sequence of buttons to show to the user (strings).
        :param int return_button: 按下回车返回的值 (-1 for none).
        :param int escape_button: 点击右上角关闭按钮返回的值 (-1 for none).
        :return: 被按下按钮在self.buttons列表中的index.
        """
        self.title: str = title
        self.message: str = message
        self.buttons: tuple = buttons
        self.info: bool = info
        self.warn: bool = warn
        self.error: bool = error
        self.return_button: int = return_button
        self.escape_button: int = escape_button

    def show(self) -> int:
        return messagebox(
            self.title,
            self.message,
            None,
            self.info,
            self.warn,
            self.error,
            self.buttons,
            self.return_button,
            self.escape_button,
        )


# 窗口
class RenderedWindow(Rect):
    def __init__(self, width: int, height: int, title: str, is_win_always_on_top: bool):
        super().__init__(0, 0, width, height)
        self.title: str = title
        self.always_on_top: bool = is_win_always_on_top
        self.__win = None
        self.__update_window()

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

    def draw_rect(self, rect_pos: Iterable, color: color_liked) -> None:
        self.__win.draw_color = Color.get(color)
        self.__win.draw_rect(convert_to_pygame_rect(rect_pos))

    def fill_rect(self, rect_pos: Iterable, color: color_liked) -> None:
        self.__win.draw_color = Color.get(color)
        self.__win.fill_rect(convert_to_pygame_rect(rect_pos))

    def fill(self, color: color_liked) -> None:
        self.fill_rect((0, 0, self.__size[0], self.__size[1]), color)

    # 清空窗口
    def clear(self) -> None:
        self.__win.clear()

    # 展示
    def present(self) -> None:
        self.__win.present()


# 基于ImageSurface的内部窗口
class SurfaceWindow(AdvancedAbstractImageSurface):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, bar_height: int_f, tag: str = ""):
        super().__init__(None, x, y, width, height, tag=tag)
        self._bar_height: int = int(bar_height)
        self.__content_layer: ImageSurface = None
        self.__mouse_hovered_local_pos: tuple = tuple()
        self._generate_window()

    def get_bar_rect(self) -> Rect:
        return new_rect((0, 0), (self._width, self._bar_height))

    def _generate_window(self):
        self.img = new_surface((self._width, self._height + self._bar_height)).convert()
        self.img.fill(Color.WHITE)
        draw_rect(self.img, Color.LIGHT_GRAY, self.get_bar_rect())
        draw_rect(self.img, Color.GRAY, self.img.get_rect(), 1)

    def present_on(self, surface: ImageSurface) -> None:
        if not self.hidden:
            if Controller.mouse.get_pressed(0):
                if len(self.__mouse_hovered_local_pos) > 0:
                    self.move_to(Pos.subtract(Controller.mouse.get_pos(), self.__mouse_hovered_local_pos))
                elif is_hover(self.get_bar_rect(), off_set_x=self.x, off_set_y=self.y):
                    self.__mouse_hovered_local_pos = Pos.subtract(Controller.mouse.get_pos(), self.pos)
            else:
                self.__mouse_hovered_local_pos = tuple()
            surface.blit(self.img, self.pos)
            if self.__content_layer is not None:
                surface.blit(self.__content_layer, (self.x, self.y + self._bar_height))
