# cython: language_level=3
import pygame.freetype
from pygame.colordict import THECOLORS
from .system import *

#初始化字体的配置文件
_LINPG_FONT:str = get_setting("Font")
_LINPG_FONTTYPE:str = get_setting("FontType")
_LINPG_MODE:bool = get_setting("Antialias")

#文字渲染器管理模块
class FontGenerator:
    def __init__(self):
        self.__SIZE = None
        self.__FONT = None
    #是否加粗
    @property
    def bold(self) -> bool: return self.__FONT.bold
    #是否斜体
    @property
    def italic(self) -> bool: return self.__FONT.italic
    def update(self, size:int, ifBold:bool=False, ifItalic:bool=False) -> None:
        self.__SIZE = size
        self.__FONT = createFont(size,ifBold,ifItalic)
    def render(self, txt:any, color:Union[tuple,str,list]):
        global _LINPG_MODE
        if self.__SIZE is not None:
            return self.__FONT.render(txt, _LINPG_MODE, findColorRGBA(color))
        else:
            throwException("error","Standard font is not initialized!")
    def get_size(self) -> int:
        if self.__SIZE is not None:
            return self.__SIZE
        else:
            throwException("error","Standard font is not initialized!")
    def get_font(self):
        if self.__FONT is not None:
            return self.__FONT
        else:
            throwException("error","Standard font is not initialized!")
    def check_for_update(self, size:int, ifBold:bool=False, ifItalic:bool=False) -> None:
        if self.__FONT is None or self.__SIZE != size or self.bold != ifBold or self.italic != ifItalic: self.update(size)

#引擎标准文件渲染器
_LINPG_STANDARD_SMALL_FONT:object = FontGenerator()
_LINPG_STANDARD_MEDIUM_FONT:object = FontGenerator()
_LINPG_STANDARD_BIG_FONT:object = FontGenerator()
#上一次render的字体
_LINPG_LAST_FONT:object = FontGenerator()

#获取文字信息
def get_font() -> str: return _LINPG_FONT
def get_fontType() -> str: return _LINPG_FONTTYPE
def get_fontMode() -> bool: return _LINPG_MODE
def get_fontDetails() -> tuple: return _LINPG_FONT,_LINPG_FONTTYPE,_LINPG_MODE
#设置和获取标准文字大小
def set_standard_font_size(size:int, fonType:str="medium") -> None:
    if isinstance(size,int) and size > 0:
        if fonType == "medium":
            _LINPG_STANDARD_MEDIUM_FONT.update(size)
        elif fonType == "small":
            _LINPG_STANDARD_SMALL_FONT.update(size)
        elif fonType == "big":
            _LINPG_STANDARD_BIG_FONT.update(size)
        else:
            throwException("error", "Standard font type must be 'small', 'medium', or 'big'!")
    else:
        throwException("error","Standard font size must be positive interger not {}!".format(size))
def get_standard_font_size(fonType:str) -> int:
    if fonType == "medium":
        return _LINPG_STANDARD_MEDIUM_FONT.get_size()
    elif fonType == "small":
        return _LINPG_STANDARD_SMALL_FONT.get_size()
    elif fonType == "big":
        return _LINPG_STANDARD_BIG_FONT.get_size()
    else:
        throwException("error","Standard font type must be 'small', 'medium', or 'big'!")
#标准文字快速渲染
def standard_font_render(fonType:str, txt:str, color:str) -> pygame.Surface:
    if fonType == "medium":
        return _LINPG_STANDARD_MEDIUM_FONT.render(txt,color)
    elif fonType == "small":
        return _LINPG_STANDARD_SMALL_FONT.render(txt,color)
    elif fonType == "big":
        return _LINPG_STANDARD_BIG_FONT.render(txt,color)
    else:
        throwException("error","Standard font type must be 'small', 'medium', or 'big'!")

#重新获取文字信息
def reload_font_setting() -> None:
    global _LINPG_FONT
    global _LINPG_FONTTYPE
    global _LINPG_MODE
    _LINPG_FONT = get_setting("Font")
    _LINPG_FONTTYPE = get_setting("FontType")
    _LINPG_MODE = get_setting("Antialias")

#创建字体
def createFont(size:Union[int,float], ifBold:bool=False, ifItalic:bool=False) -> object:
    global _LINPG_FONT
    global _LINPG_FONTTYPE
    #int化文字尺寸
    font_size:int = max(int(size),1)
    #检测pygame的font模块是否已经初始化
    if not pygame.font.get_init(): pygame.font.init()
    #根据类型处理
    if _LINPG_FONTTYPE == "default":
        return pygame.font.SysFont(_LINPG_FONT,font_size,ifBold,ifItalic)
    elif _LINPG_FONTTYPE == "custom":
        font_path:str = os.path.join("Assets","font","{}.ttf".format(_LINPG_FONT))
        if os.path.exists(font_path):
            normal_font = pygame.font.Font(font_path,font_size)
        else:
            throwException("warning", "Cannot find the {}.ttf file, the engine's font has been change to default.".format(_LINPG_FONT))
            _LINPG_FONT = "arial"
            _LINPG_FONTTYPE = "default"
            return pygame.font.SysFont(_LINPG_FONT,font_size,ifBold,ifItalic)
        if ifBold is True: normal_font.set_bold(ifBold)
        if ifItalic is True: normal_font.set_italic(ifItalic)
        return normal_font
    else:
        throwException("error","FontType option in setting file is incorrect!")

#创建FreeType字体
def createFreeTypeFont(size:Union[float,int], ifBold:bool=False, ifItalic:bool=False) -> any:
    global _LINPG_FONT
    global _LINPG_FONTTYPE
    #int化文字尺寸
    font_size:int = max(int(size),1)
    #检测pygame的font模块是否已经初始化
    if not pygame.freetype.get_init(): pygame.freetype.init()
    #根据类型处理
    if _LINPG_FONTTYPE == "default":
        return pygame.freetype.SysFont(_LINPG_FONT,font_size,ifBold,ifItalic)
    elif _LINPG_FONTTYPE == "custom":
        font_path:str = os.path.join("Assets","font","{}.ttf".format(_LINPG_FONT))
        if os.path.exists(font_path):
            normal_font = pygame.freetype.Font(font_path,font_size)
        else:
            throwException("warning", "Cannot find the {}.ttf file, the engine's font has been change to default.".format(_LINPG_FONT))
            _LINPG_FONT = "arial"
            _LINPG_FONTTYPE = "default"
            return pygame.freetype.SysFont(_LINPG_FONT,font_size,ifBold,ifItalic)
        if ifBold is True: normal_font.set_bold(True)
        if ifItalic is True: normal_font.set_italic(True)
        return normal_font
    else:
        throwException("error","FontType option in setting file is incorrect!")

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRender(txt:any, color:Union[tuple,str,list], size:int, ifBold:bool=False, ifItalic:bool=False) -> pygame.Surface:
    _LINPG_LAST_FONT.check_for_update(size, ifBold, ifItalic)
    return _LINPG_LAST_FONT.render(txt, findColorRGBA(color)) if isinstance(color,str) else _LINPG_LAST_FONT.render(txt, color)

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def fontRenderWithoutBound(txt:any, color:Union[tuple,str,list], size:int, ifBold:bool=False, ifItalic:bool=False) -> pygame.Surface:
    return copeBounding(fontRender(txt,color,size,ifBold,ifItalic))

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def freeTypeRender(txt:any, color:Union[tuple,str,list], size:int, ifBold:bool=False, ifItalic:bool=False) -> pygame.Surface:
    normal_font = createFreeTypeFont(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = normal_font.render(txt, _LINPG_MODE, findColorRGBA(color))
    else:
        text_out = normal_font.render(txt, _LINPG_MODE, color)
    return text_out

#基础文字类
class TextSurface(GameObject2d):
    def __init__(self, font_surface:pygame.Surface, x:Union[int,float], y:Union[int,float]):
        super().__init__(x,y)
        self.font_surface = font_surface
    def get_width(self) -> int:
        return self.font_surface.get_width()
    def get_height(self) -> int:
        return self.font_surface.get_height()
    #透明度
    @property
    def alpha(self) -> int: return self.get_alpha()
    def get_alpha(self) -> int: return self.font_surface.get_alpha()
    def set_alpha(self, value:int) -> None: self.font_surface.set_alpha(value)
    #画出
    def display(self, surface:pygame.Surface, offSet:tuple=(0,0)) -> None:
        surface.blit(self.font_surface,add_pos(self.pos,offSet))

#动态文字类
class DynamicTextSurface(TextSurface):
    def __init__(self, n:pygame.Surface, b:pygame.Surface, x:Union[int,float], y:Union[int,float]):
        super().__init__(n,x,y)
        self.big_font_surface = b
    #设置透明度
    def set_alpha(self, value:int) -> None:
        super().set_alpha(value)
        self.big_font_surface.set_alpha(value)
    #画出
    def display(self, surface:pygame.Surface, offSet:tuple=(0,0)) -> None:
        mouse_pos = controller.get_mouse_pos()
        if self.is_hover(subtract_pos(mouse_pos,offSet)):
            surface.blit(
                self.big_font_surface,
                (int(self.x-(self.big_font_surface.get_width()-self.font_surface.get_width())/2+offSet[0]),
                int(self.y-(self.big_font_surface.get_height()-self.font_surface.get_height())/2+offSet[1]))
                )
        else:
            surface.blit(self.font_surface,add_pos(self.pos,offSet))

#高级文字制作模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def fontRenderPro(txt:any, color:Union[tuple,str,list], pos:tuple, size:int=50, ifBold:bool=False, ifItalic:bool=False) -> DynamicTextSurface:
    return DynamicTextSurface(fontRender(txt,color,size,ifBold,ifItalic),fontRender(txt,color,size*1.5,ifBold,ifItalic),pos[0],pos[1])

#给定一个颜色的名字，返回对应的RGB列表
def findColorRGBA(color:Union[tuple,str,list]) -> tuple:
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
                throwException("error","This color is currently not available!")
    else:
        throwException(
            "error",
            "The color has to be a string, tuple or list! As a result, {0} (type:{1}) is not acceptable!".format(color,type(color))
            )
