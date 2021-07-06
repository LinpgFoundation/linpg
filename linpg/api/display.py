# cython: language_level=3
from pygame._sdl2 import Renderer, Window, messagebox
from .controller import *

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
    def show(self): return messagebox(self.title,self.message,None,self.info,self.warn,self.error,self.buttons,self.return_button,self.escape_button)

#窗口
class RenderedWindow:
    def __init__(self, title:str, size:tuple, is_win_always_on_top:bool):
        self.title = title
        self.always_on_top = is_win_always_on_top
        self.set_size(size)
    @property
    def size(self) -> tuple: return self.__size
    def set_size(self, size:tuple) -> None:
        win = Window(self.title,size,always_on_top=self.always_on_top)
        self.__win = Renderer(win)
        self.__size = size
    def clear(self) -> None: self.__win.clear()
    def present(self) -> None: self.__win.present()
    def draw_rect(self, rect_pos:pos_liked, color:color_liked) -> None:
        self.__win.draw_color = Color.get(color)
        self.__win.draw_rect(pygame.Rect(rect_pos))
    def fill_rect(self, rect_pos:pos_liked, color:color_liked) -> None:
        self.__win.draw_color = Color.get(color)
        self.__win.fill_rect(pygame.Rect(rect_pos))
    def fill(self, color:color_liked) -> None:
        self.fill_rect((0,0,self.__size[0],self.__size[1]),color)

#画面更新控制器
class DisplayController:
    def __init__(self):
        self.__fps:int = max(int(Setting.get("FPS")), 1)
        self.__clock:object = get_clock()
        self.__standard_fps:int = 60
        #默认尺寸
        self.__screen_scale:int = max(int(Setting.get("ScreenScale")), 0)
        self.__standard_width:int = round(1920*self.__screen_scale/100)
        self.__standard_height:int = round(1080*self.__screen_scale/100)
        #主要的窗口
        self.__SCREEN_WINDOW:object = None
    #帧数
    @property
    def fps(self) -> int: return self.__fps
    def get_fps(self) -> int: return self.__fps
    #标准帧数校准器
    @property
    def sfpsp(self) -> float: return self.__standard_fps/self.__fps
    #更新
    def flip(self) -> None:
        self.__clock.tick(self.fps)
        pygame.display.flip()
        Controller.update()
        Controller.mouse.draw_custom_icon(self.__SCREEN_WINDOW)
    #设置窗口标题
    def set_caption(self, title:str) -> None:
        if is_using_pygame():
            pygame.display.set_caption(title)
        else:
            self.__SCREEN_WINDOW.set_caption(title)
    #设置窗口图标
    def set_icon(self, path:str) -> None:
        if is_using_pygame():
            pygame.display.set_icon(quickly_load_img(path, False))
        else:
            self.__SCREEN_WINDOW.set_icon(quickly_load_img(path, False))
    #窗口尺寸
    @property
    def width(self) -> int: return self.__standard_width
    def get_width(self) -> int: return self.__standard_width
    @property
    def height(self) -> int: return self.__standard_height
    def get_height(self) -> int: return self.__standard_height
    @property
    def size(self) -> tuple: return self.__standard_width, self.__standard_height
    def get_size(self) -> tuple: return self.__standard_width, self.__standard_height
    #分辨率 - str
    @property
    def resolution(self) -> str: return "{0}x{1}".format(self.__standard_width, self.__standard_height)
    #初始化屏幕
    def init(self) -> object:
        if is_using_pygame():
            flags = pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN if self.__screen_scale == 100 else pygame.SCALED
            self.__SCREEN_WINDOW = pygame.display.set_mode(self.get_size(), flags)
            self.__SCREEN_WINDOW.set_alpha(None)
        else:
            self.__SCREEN_WINDOW = pyglet.window.Window(self.get_width(), self.get_height())
        return self.__SCREEN_WINDOW
    #获取屏幕
    @property
    def window(self) -> object: return self.__SCREEN_WINDOW
    #退出
    def quit(self) -> None:
        from sys import exit
        #退出游戏
        exit()

#帧率控制器
Display:DisplayController = DisplayController()

# 直接画到屏幕上
def draw_on_screen(surface_to_draw: ImageSurface, pos:pos_liked) -> None:
    Display.window.blit(surface_to_draw, convert_pos(pos))