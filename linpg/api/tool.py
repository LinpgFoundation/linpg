# cython: language_level=3
from pygame._sdl2 import Renderer, Window, messagebox
from .system import *

#提示窗口
class Message:
    def __init__(self, title:str, message:str, buttons:tuple, info:bool=False, warn:bool=False, error:bool=False, return_button:int=0, escape_button:int=0):
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
    def draw(self): return messagebox(self.title,self.message,None,self.info,self.warn,self.error,self.buttons,self.return_button,self.escape_button)

#窗口
class RenderedWindow:
    def __init__(self, title:str, size:tuple, is_win_always_on_top:bool):
        self.title = title
        self.always_on_top = is_win_always_on_top
        self.set_size(size)
    @property
    def size(self) -> tuple: return self.__size
    def set_size(self,size:tuple) -> None:
        win = Window(self.title,size,always_on_top=self.always_on_top)
        self.__win = Renderer(win)
        self.__size = size
    def clear(self) -> None: self.__win.clear()
    def present(self) -> None: self.__win.present()
    def draw_rect(self,rect_pos,color) -> None:
        self.__win.draw_color = Color.get(color)
        self.__win.draw_rect(pygame.Rect(rect_pos))
    def fill_rect(self,rect_pos,color) -> None:
        self.__win.draw_color = Color.get(color)
        self.__win.fill_rect(pygame.Rect(rect_pos))
    def fill(self,color) -> None:
        self.fill_rect((0,0,self.__size[0],self.__size[1]),color)

#优化中文文档
def optimize_cn_content(filePath:str) -> None:
    #读取原文件的数据
    with open(filePath, "r", encoding='utf-8') as f:
        file_lines = f.readlines()
    #优化字符串
    for i in range(len(file_lines)):
        #如果字符串不为空
        if len(file_lines[i]) > 1:
            #替换字符
            file_lines[i] = file_lines[i]\
                .replace("。。。","... ")\
                .replace("。",". ")\
                .replace("？？：","??: ")\
                .replace("？？","?? ")\
                .replace("？","? ")\
                .replace("！！","!! ")\
                .replace("！","! ")\
                .replace("：",": ")\
                .replace("，",", ")\
                .replace("“",'"')\
                .replace("”",'"')\
                .replace("‘","'")\
                .replace("’","'")\
                .replace("（"," (")\
                .replace("）",") ")\
                .replace("  "," ")
            #移除末尾的空格
            try:
                while file_lines[i][-2] == " ":
                    file_lines[i] = file_lines[i][:-2]+"\n"
            except Exception:
                pass
    #删除原始文件
    os.remove(filePath)
    #创建并写入新数据
    with open(filePath, "w", encoding='utf-8') as f:
        f.writelines(file_lines)

#优化文件夹中特定文件的中文字符串
def optimize_cn_content_in_folder(pathname:str) -> None:
    for configFilePath in glob(pathname):
        optimize_cn_content(configFilePath)