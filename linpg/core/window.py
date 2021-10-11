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
class AbstractSurfaceWindow(AdvancedAbstractImageSurface):
    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, bar_height: int_f, tag: str = ""):
        super().__init__(None, x, y, width, height, tag=tag)
        self.__bar_height: int = int(bar_height)
        self.__mouse_hovered_offset_pos: tuple = tuple()
        self.__outline_thickness: int = 2
        self.__rescale_icon = StaticImage("<!ui>rescale.png", 0, 0, self.__bar_height, self.__bar_height)
        self.__rescale_directions: dict[str, bool] = {"left": False, "right": False, "top": False, "bottom": False}
        self.__if_regenerate_window: bool = True

    # 更新窗口
    def __update_window_frame(self) -> None:
        if self.__if_regenerate_window is True:
            self.img = new_surface(self.size)
            self.img.fill(Color.WHITE)
            draw_rect(self.img, Color.LIGHT_GRAY, ((0, 0), (self._width, self.__bar_height)))
            draw_rect(self.img, Color.GRAY, self.img.get_rect(), self.__outline_thickness)
            self.__if_regenerate_window = False

    # 展示内容（子类必须实现该功能）
    def _present_content(self, surface: ImageSurface) -> None:
        EXCEPTION.fatal("_present_content()", 1)

    # 设置宽度
    def set_width(self, value: int_f) -> None:
        super().set_width(value)
        self.__if_regenerate_window = True

    # 设置高度
    def set_height(self, value: int_f) -> None:
        super().set_height(value)
        self.__if_regenerate_window = True

    # 角落是否被触碰
    def __is_corner_hovered(self, side1: str, side2: str = None) -> bool:
        if side2 is None:
            return bool(self.__rescale_directions[side1])
        else:
            return self.__rescale_directions[side1] is True and self.__rescale_directions[side2] is True

    # 展示
    def present_on(self, surface: ImageSurface) -> None:
        if not self.hidden:
            # 如果鼠标之前没有被按下
            if not Controller.mouse.get_pressed_previously(0):
                # 查看鼠标是否触碰窗口的边缘
                self.__rescale_directions["left"] = bool(
                    -self.__outline_thickness <= Controller.mouse.x - self.x < self.__outline_thickness * 2
                )
                self.__rescale_directions["right"] = bool(
                    -self.__outline_thickness * 2 < Controller.mouse.x - self.right <= self.__outline_thickness
                )
                self.__rescale_directions["top"] = bool(
                    -self.__outline_thickness <= Controller.mouse.y - self.y < self.__outline_thickness * 2
                )
                self.__rescale_directions["bottom"] = bool(
                    -self.__outline_thickness * 2 < Controller.mouse.y - self.bottom <= self.__outline_thickness
                )
                # 如果鼠标按住bar
                if True not in self.__rescale_directions.values() and is_hover(
                    new_rect((self.x, self.y), (self._width, self.__bar_height))
                ):
                    self.__mouse_hovered_offset_pos = Pos.subtract(Controller.mouse.get_pos(), self.pos)
                else:
                    self.__mouse_hovered_offset_pos = tuple()
                # 如果鼠标触碰了边框，则旋转放大icon至对应角度
                if self.__is_corner_hovered("top", "right") or self.__is_corner_hovered("bottom", "left"):
                    self.__rescale_icon.rotate_to(45)
                elif self.__is_corner_hovered("top", "left") or self.__is_corner_hovered("bottom", "right"):
                    self.__rescale_icon.rotate_to(135)
                elif self.__is_corner_hovered("top") or self.__is_corner_hovered("bottom"):
                    self.__rescale_icon.rotate_to(90)
                else:
                    self.__rescale_icon.rotate_to(0)
            elif Controller.mouse.get_pressed(0):
                # 移动窗口
                if len(self.__mouse_hovered_offset_pos) > 0:
                    self.move_to(Pos.subtract(Controller.mouse.get_pos(), self.__mouse_hovered_offset_pos))
                else:
                    # 向左放大
                    if self.__rescale_directions["left"] is True:
                        if Controller.mouse.x < self.right:
                            self.set_width(self.right - Controller.mouse.x)
                            self.set_left(Controller.mouse.x)
                        else:
                            self.__rescale_directions["left"] = False
                            self.__rescale_directions["right"] = True
                    # 向右放大
                    if self.__rescale_directions["right"] is True:
                        if Controller.mouse.x > self.left:
                            self.set_width(Controller.mouse.x - self.left)
                        else:
                            self.__rescale_directions["right"] = False
                            self.__rescale_directions["left"] = True
                    # 向上放大
                    if self.__rescale_directions["top"] is True:
                        if Controller.mouse.y < self.bottom - self.__bar_height:
                            self.set_height(self.bottom - Controller.mouse.y)
                            self.set_top(Controller.mouse.y)
                        else:
                            self.__rescale_directions["top"] = False
                            self.__rescale_directions["bottom"] = True
                    # 向下放大
                    if self.__rescale_directions["bottom"] is True:
                        if Controller.mouse.y > self.top:
                            self.set_height(Controller.mouse.y - self.top)
                        else:
                            self.__rescale_directions["bottom"] = False
                            self.__rescale_directions["top"] = True
            else:
                for key in self.__rescale_directions:
                    self.__rescale_directions[key] = False
                self.__mouse_hovered_offset_pos = tuple()
            # 更新窗口
            self.__update_window_frame()
            # 画出窗口
            surface.blit(self.img, self.pos)
            # 画出内容
            self._present_content(surface)
            # 画出放大icon
            if True in self.__rescale_directions.values():
                self.__rescale_icon.set_center(Controller.mouse.x, Controller.mouse.y)
                self.__rescale_icon.draw(surface)
