# cython: language_level=3
import pygame.freetype
from pygame.colordict import THECOLORS
from .system import *

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
        self.__FONT = create_font(size,ifBold,ifItalic)
    def render(self, txt:any, color:Union[str,tuple,list]):
        if self.__SIZE is not None:
            return self.__FONT.render(txt, get_antialias(), get_color_rbga(color))
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
def standard_font_render(fonType:str, txt:str, color:str) -> ImageSurface:
    if fonType == "medium":
        return _LINPG_STANDARD_MEDIUM_FONT.render(txt,color)
    elif fonType == "small":
        return _LINPG_STANDARD_SMALL_FONT.render(txt,color)
    elif fonType == "big":
        return _LINPG_STANDARD_BIG_FONT.render(txt,color)
    else:
        throwException("error","Standard font type must be 'small', 'medium', or 'big'!")

#创建字体
def create_font(size:Union[int,float], ifBold:bool=False, ifItalic:bool=False) -> object:
    #int化文字尺寸
    font_size:int = max(int(size),1)
    #检测pygame的font模块是否已经初始化
    if not pygame.font.get_init(): pygame.font.init()
    #根据类型处理
    if get_font_type() == "default":
        return pygame.font.SysFont(get_font(),font_size,ifBold,ifItalic)
    elif get_font_type() == "custom":
        font_path:str = os.path.join("Assets","font","{}.ttf".format(get_font()))
        if os.path.exists(font_path):
            normal_font = pygame.font.Font(font_path,font_size)
        else:
            throwException("warning", "Cannot find the {}.ttf file, the engine's font has been change to default.".format(get_font()))
            set_font("arial")
            set_font_type("default")
            return pygame.font.SysFont(get_font(),font_size,ifBold,ifItalic)
        if ifBold is True: normal_font.set_bold(ifBold)
        if ifItalic is True: normal_font.set_italic(ifItalic)
        return normal_font
    else:
        throwException("error","FontType option in setting file is incorrect!")

#创建FreeType字体
def create_freetype_font(size:Union[float,int], ifBold:bool=False, ifItalic:bool=False) -> any:
    #int化文字尺寸
    font_size:int = max(int(size),1)
    #检测pygame的font模块是否已经初始化
    if not pygame.freetype.get_init(): pygame.freetype.init()
    #根据类型处理
    if get_font_type() == "default":
        return pygame.freetype.SysFont(get_font(),font_size,ifBold,ifItalic)
    elif get_font_type() == "custom":
        font_path:str = os.path.join("Assets","font","{}.ttf".format(get_font()))
        if os.path.exists(font_path):
            normal_font = pygame.freetype.Font(font_path,font_size)
        else:
            throwException("warning", "Cannot find the {}.ttf file, the engine's font has been change to default.".format(get_font()))
            set_font("arial")
            set_font_type("default")
            return pygame.freetype.SysFont(get_font(),font_size,ifBold,ifItalic)
        if ifBold is True: normal_font.set_bold(True)
        if ifItalic is True: normal_font.set_italic(True)
        return normal_font
    else:
        throwException("error","FontType option in setting file is incorrect!")

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def render_font(txt:any, color:Union[str,tuple,list], size:int, ifBold:bool=False, ifItalic:bool=False) -> ImageSurface:
    _LINPG_LAST_FONT.check_for_update(size, ifBold, ifItalic)
    return _LINPG_LAST_FONT.render(txt, get_color_rbga(color)) if isinstance(color,str) else _LINPG_LAST_FONT.render(txt, color)

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def render_font_without_bounding(txt:any, color:Union[str,tuple,list], size:int, ifBold:bool=False, ifItalic:bool=False) -> ImageSurface:
    return cope_bounding(render_font(txt,color,size,ifBold,ifItalic))

#文字制作模块：接受文字，颜色，文字大小，文字样式，模式，返回制作完的文字
def render_freetype(txt:any, color:Union[str,tuple,list], size:int, ifBold:bool=False, ifItalic:bool=False) -> ImageSurface:
    normal_font = create_freetype_font(size,ifBold,ifItalic)
    if isinstance(color,str):
        text_out = normal_font.render(txt, get_antialias(), get_color_rbga(color))
    else:
        text_out = normal_font.render(txt, get_antialias(), color)
    return text_out

#基础文字类
class TextSurface(GameObject2d):
    def __init__(self, font_surface:ImageSurface, x:Union[int,float], y:Union[int,float]):
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
    def display(self, surface:ImageSurface, offSet:tuple=(0,0)) -> None:
        surface.blit(self.font_surface,add_pos(self.pos,offSet))

#动态文字类
class DynamicTextSurface(TextSurface):
    def __init__(self, n:ImageSurface, b:ImageSurface, x:Union[int,float], y:Union[int,float]):
        super().__init__(n,x,y)
        self.big_font_surface = b
        self.__is_hovered:bool = False
    #设置透明度
    def set_alpha(self, value:int) -> None:
        super().set_alpha(value)
        self.big_font_surface.set_alpha(value)
    #用于检测触碰的快捷
    def has_been_hovered(self) -> bool: return self.__is_hovered
    #画出
    def display(self, surface:ImageSurface, offSet:tuple=(0,0)) -> None:
        mouse_pos = controller.get_mouse_pos()
        self.__is_hovered = self.is_hover(subtract_pos(mouse_pos,offSet))
        if self.__is_hovered:
            surface.blit(
                self.big_font_surface,
                (int(self.x-(self.big_font_surface.get_width()-self.font_surface.get_width())/2+offSet[0]),
                int(self.y-(self.big_font_surface.get_height()-self.font_surface.get_height())/2+offSet[1]))
                )
        else:
            surface.blit(self.font_surface,add_pos(self.pos,offSet))

#高级文字制作模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
def load_dynamic_text(txt:any, color:Union[str,tuple,list], pos:tuple, size:int=50, ifBold:bool=False, ifItalic:bool=False) -> DynamicTextSurface:
    return DynamicTextSurface(render_font(txt,color,size,ifBold,ifItalic),render_font(txt,color,size*1.5,ifBold,ifItalic),pos[0],pos[1])

#给定一个颜色的名字，返回对应的RGB列表
def get_color_rbga(color:Union[str,tuple,list]) -> tuple:
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
            except KeyError:
                throwException("error","This color is currently not available!")
    else:
        throwException(
            "error",
            "The color has to be a string, tuple or list! As a result, {0} (type:{1}) is not acceptable!".format(color,type(color))
            )
