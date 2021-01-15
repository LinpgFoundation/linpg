from pygame._sdl2 import messagebox,Window,Renderer
from .font import findColorRGBA
from pygame import Rect

#提示窗口
class Message:
    def __init__(self,title,message,buttons,info=False,warn=False,error=False,return_button=0,escape_button=0):
        """ Display a message box.
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
        self.title = title
        self.message = message
        self.buttons = buttons
        self.info = info
        self.warn = warn
        self.error = error
        self.return_button = return_button
        self.escape_button = escape_button
    def draw(self):
        return messagebox(self.title,self.message,None,self.info,self.warn,self.error,self.buttons,self.return_button,self.escape_button)

#窗口
class RenderedWindow:
    def __init__(self,title,size,is_win_always_on_top):
        self.title = title
        self.always_on_top = is_win_always_on_top
        self.set_size(size)
    @property
    def size(self):
        return self.__size
    def set_size(self,size):
        win = Window(self.title,size,always_on_top=self.always_on_top)
        self.__win = Renderer(win)
        self.__size = size
    def clear(self):
        self.__win.clear()
    def present(self):
        self.__win.present()
    def draw_rect(self,rect_pos,color):
        self.__win.draw_color = findColorRGBA(color)
        self.__win.draw_rect(Rect(rect_pos))
    def fill_rect(self,rect_pos,color):
        self.__win.draw_color = findColorRGBA(color)
        self.__win.fill_rect(Rect(rect_pos))
    def fill(self,color):
        self.fill_rect((0,0,self.__size[0],self.__size[1]),color)