# cython: language_level=3
from pygame.draw import rect
import pygame.freetype
from pygame.colordict import THECOLORS
from .config import *

#文字渲染器管理模块
class FontGenerator:
    def __init__(self):
        self.__SIZE = None
        self.__FONT = None
    @property
    def bold(self):
        return self.__FONT.bold
    @property
    def italic(self):
        return self.__FONT.italic
    def update(self,size:int,ifBold:bool=False,ifItalic:bool=False) -> None:
        self.__SIZE = size
        self.__FONT = createFont(size,ifBold,ifItalic)
    def render(self,txt,color):
        if self.__SIZE != None:
            if isinstance(color,str):
                return self.__FONT.render(txt, LINPG_MODE, findColorRGBA(color))
            else:
                return self.__FONT.render(txt, LINPG_MODE, color)
        else:
            raise Exception('LinpgEngine-Error: Standard font is not initialized!')
    def get_size(self) -> int:
        if self.__SIZE != None:
            return self.__SIZE
        else:
            raise Exception('LinpgEngine-Error: Standard font is not initialized!')
    def get_font(self):
        if self.__FONT != None:
            return self.__FONT
        else:
            raise Exception('LinpgEngine-Error: Standard font is not initialized!')
    def check_for_update(self,size:int,ifBold:bool=False,ifItalic:bool=False) -> None:
        if self.__FONT == None or self.__SIZE != size or self.bold != ifBold or self.italic != ifItalic: self.update(size)

#初始化字体的配置文件
LINPG_FONT = get_setting("Font")
LINPG_FONTTYPE = get_setting("FontType")
LINPG_MODE = get_setting("Antialias")
#引擎标准文件渲染器
LINPG_STANDARD_SMALL_FONT = FontGenerator()
LINPG_STANDARD_MEDIUM_FONT = FontGenerator()
LINPG_STANDARD_BIG_FONT = FontGenerator()
#上一次render的字体
LINPG_LAST_FONT = FontGenerator()

#获取文字信息
def get_font():
    return LINPG_FONT
def get_fontType():
    return LINPG_FONTTYPE
def get_fontMode():
    return LINPG_MODE
def get_fontDetails():
    return LINPG_FONT,LINPG_FONTTYPE,LINPG_MODE
#设置和获取标准文字大小
def set_standard_font_size(size,fonType="medium"):
    if isinstance (size,int) and size > 0:
        if fonType == "medium":
            LINPG_STANDARD_MEDIUM_FONT.update(size)
        elif fonType == "small":
            LINPG_STANDARD_SMALL_FONT.update(size)
        elif fonType == "big":
            LINPG_STANDARD_BIG_FONT.update(size)
        else:
            raise Exception('LinpgEngine-Error: Standard font type must be "small","medium", or "big"!')
    else:
        raise Exception('LinpgEngine-Error: Standard font size must be positive interger not {}!'.format(size))
def get_standard_font_size(fonType):
    if fonType == "medium":
        return LINPG_STANDARD_MEDIUM_FONT.get_size()
    elif fonType == "small":
        return LINPG_STANDARD_SMALL_FONT.get_size()
    elif fonType == "big":
        return LINPG_STANDARD_BIG_FONT.get_size()
    else:
        raise Exception('LinpgEngine-Error: Standard font type must be "small","medium", or "big"!')
#标准文字快速渲染
def standard_font_render(fonType,txt,color):
    if fonType == "medium":
        return LINPG_STANDARD_MEDIUM_FONT.render(txt,color)
    elif fonType == "small":
        return LINPG_STANDARD_SMALL_FONT.render(txt,color)
    elif fonType == "big":
        return LINPG_STANDARD_BIG_FONT.render(txt,color)
    else:
        raise Exception('LinpgEngine-Error: Standard font type must be "small","medium", or "big"!')

#重新获取设置信息
def reload_setting():
    reload_DATA()
    global LINPG_FONT
    global LINPG_FONTTYPE
    global LINPG_MODE
    LINPG_FONT = get_setting("Font")
    LINPG_FONTTYPE = get_setting("FontType")
    LINPG_MODE = get_setting("Antialias")

#创建字体
def createFont(size,ifBold=False,ifItalic=False):
    if LINPG_FONTTYPE == "default":
        try:
            return pygame.font.SysFont(LINPG_FONT,int(size),ifBold,ifItalic)
        except BaseException:
            pygame.font.init()
            normal_font = pygame.font.SysFont(LINPG_FONT,int(size),ifBold,ifItalic)
    elif LINPG_FONTTYPE == "custom":
        try:
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(LINPG_FONT),int(size))
        #如果文字没有初始化
        except BaseException:
            pygame.font.init()
            normal_font = pygame.font.Font("Assets/font/{}.ttf".format(LINPG_FONT),int(size))
        if ifBold:
            normal_font.set_bold(ifBold)
        if ifItalic:
            normal_font.set_italic(ifItalic)
        return normal_font
    else:
        raise Exception('LinpgEngine-Error: FontType option in setting file is incorrect!')

#创建FreeType字体
def createFreeTypeFont(size,ifBold=False,ifItalic=False):
    if LINPG_FONTTYPE == "default":
        try:
            return pygame.freetype.SysFont(LINPG_FONT,int(size),ifBold,ifItalic)
        except BaseException:
            pygame.freetype.init()
            return pygame.freetype.SysFont(LINPG_FONT,int(size),ifBold,ifItalic)
    elif LINPG_FONTTYPE == "custom":
        try:
            normal_font = pygame.freetype.Font("Assets/font/{}.ttf".format(LINPG_FONT),int(size))
        #如果文字没有初始化
        except BaseException:
            pygame.freetype.init()
            normal_font = pygame.freetype.Font("Assets/font/{}.ttf".format(LINPG_FONT),int(size))
        if ifBold:
            normal_font.set_bold(ifBold)
        if ifItalic:
            normal_font.set_italic(ifItalic)
        return normal_font
    else:
        raise Exception('LinpgEngine-Error: FontType option in setting file is incorrect!')

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRender(txt,color,size:int,ifBold:bool=False,ifItalic:bool=False) -> pygame.Surface:
    LINPG_LAST_FONT.check_for_update(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = LINPG_LAST_FONT.render(txt, findColorRGBA(color))
    else:
        text_out = LINPG_LAST_FONT.render(txt, color)
    return text_out

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def freeTypeRender(txt,color,size:int,ifBold:bool=False,ifItalic:bool=False) -> pygame.Surface:
    normal_font = createFreeTypeFont(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = normal_font.render(txt, LINPG_MODE, findColorRGBA(color))
    else:
        text_out = normal_font.render(txt, LINPG_MODE, color)
    return text_out

#文字画面类
class TextSurface:
    def __init__(self,n,b,x,y):
        self.n = n
        self.b = b
        self.n_x = x
        self.n_y = y
        self.b_x = x - (self.b.get_width()-self.n.get_width())/2
        self.b_y = y - (self.b.get_height()-self.n.get_height())/2
        self.__isHover = False
    def display(self,screen):
        mouse_x,mouse_y = pygame.mouse.get_pos()
        if self.n_x<=mouse_x<=self.n_x+self.n.get_width() and self.n_y<=mouse_y<=self.n_y+self.n.get_height():
            screen.blit(self.b,(self.b_x,self.b_y))
            self.__isHover = True
        else:
            screen.blit(self.n,(self.n_x,self.n_y))
            self.__isHover = False
        return self.__isHover
    def draw(self,screen):
        self.display(screen)
    def isHover(self):
        return self.__isHover
    def get_pos(self):
        return self.n_x,self.n_y

#高级文字制作模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt,color,pos,size=50,ifBold=False,ifItalic=False):
    return TextSurface(fontRender(txt,color,size,ifBold,ifItalic),fontRender(txt,color,size*1.5,ifBold,ifItalic),pos[0],pos[1])

#给定一个颜色的名字，返回对应的RGB列表
def findColorRGBA(color):
    if isinstance(color,(tuple,list)):
        return color
    elif isinstance(color,(str)):
        if color == "gray" or color == "grey" or color == "disable":
            return (105, 105, 105, 255)
        elif color == "white" or color == "enable":
            return (255, 255, 255, 255)
        else:
            try:
                return THECOLORS[color]
            except BaseException:
                raise Exception('LinpgEngine-Error: This color is currently not available!')
    else:
        raise Exception('LinpgEngine-Error: The color has to be a string, tuple or list!')