# cython: language_level=3
from __future__ import annotations
#python本体库
import glob, os, random
from typing import Union
#额外库
import numpy, pygame
from pygame.locals import *

"""
结构:
basic -> config -> controller -> lang -> module -> font -> surface -> ui -> inputbox -> function
"""

#初始化pygame
pygame.init()

"""加载"""
#识别图片模块，用于引擎内加载图片，十分不建议在本文件外调用
def imgLoadFunction(path:Union[str,pygame.Surface], ifConvertAlpha:bool) -> pygame.Surface:
    if isinstance(path,pygame.Surface):
        return path
    elif isinstance(path,str):
        if not ifConvertAlpha:
            try:
                return pygame.image.load(os.path.join(path))
            except:
                throwException("error",'Cannot load image from path: {}'.format(path))
        else:
            try:
                return pygame.image.load(os.path.join(path)).convert_alpha()
            except:
                throwException("error",'Cannot load image from path: {}'.format(path))
    else:
        throwException("error","The path '{}' has to be a string or at least a pygame.Surface!".format(path))

#图片加载模块：接收图片路径,长,高,返回对应图片
def loadImg(path:Union[str,pygame.Surface], size:Union[tuple,list]=[], setAlpha:int=255, ifConvertAlpha:bool=True) -> pygame.Surface:
    #加载图片
    img = imgLoadFunction(path,ifConvertAlpha)
    #根据参数编辑图片
    if setAlpha != 255: img.set_alpha(setAlpha)
    #如果没有给size,则直接返回Surface
    return img if len(size) == 0 else resizeImg(img,size)

#加载音效
def loadSound(path:str, volume:float) -> pygame.mixer.Sound:
    soundTmp:object = pygame.mixer.Sound(path)
    soundTmp.set_volume(volume)
    return soundTmp

#加载路径下的所有图片，储存到一个list当中，然后返回
def loadAllImgInFile(pathRule:str, width:any=None, height:any=None) -> list[pygame.Surface]:
    return [loadImg(imgPath,(width,height)) for imgPath in glob.glob(pathRule)]

#获取Surface
def getSurface(size:Union[tuple,list], surface_flags:any=None) -> pygame.Surface:
    if surface_flags != None:
        return pygame.Surface(size,flags=surface_flags)
    else:
        return pygame.Surface(size)

"""处理"""
#重新编辑尺寸
def resizeImg(img:pygame.Surface, size:Union[tuple,list]=(None,None)) -> pygame.Surface:
    #转换尺寸
    if isinstance(size,(list,tuple,numpy.ndarray)):
        if len(size) == 1:
            width = size[0]
            height = None
        else:
            width = size[0]
            height = size[1]
    elif isinstance(size,(int,float)):
        width = size
        height = None
    else:
        throwException("error","The size '{}' is not acceptable.".format(size))
    #编辑图片
    if height!= None and height >= 0 and width == None:
        img = pygame.transform.scale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height == None and width!= None and width >= 0:
        img = pygame.transform.scale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.scale(img, (round(width), round(height)))
    elif width < 0 or height < 0:
        throwException("error","Both width and height must be positive interger!")
    return img

#增加图片暗度
def addDarkness(img:pygame.Surface, value:int) -> pygame.Surface:
    newImg:pygame.Surface = img.copy()
    newImg.fill((value, value, value),special_flags=pygame.BLEND_RGB_SUB) 
    return newImg

#减少图片暗度
def removeDarkness(img:pygame.Surface, value:int) -> pygame.Surface:
    newImg:pygame.Surface = img.copy()
    newImg.fill((value, value, value), special_flags=pygame.BLEND_RGB_ADD)
    return newImg

#调整图片亮度
def changeDarkness(surface:pygame.Surface, value:int) -> pygame.Surface:
    if value == 0:
        return surface
    if value > 0:
        return addDarkness(surface,value)
    else:
        return removeDarkness(surface,abs(value))

#按照给定的位置对图片进行剪裁
def cropImg(img:pygame.Surface, pos:Union[tuple,list]=(0,0),size:Union[tuple,list]=(0,0)) -> pygame.Surface:
    if isinstance(pos,pygame.Rect):
        cropped = getSurface(pos.size,pygame.SRCALPHA).convert_alpha()
        cropped.blit(img,(-pos.x,-pos.y))
    else:
        cropped = getSurface((round(size[0]),round(size[1])),pygame.SRCALPHA).convert_alpha()
        cropped.blit(img,(-pos[0],-pos[1]))
    return cropped

#移除掉图片周围的透明像素
def copeBounding(img:pygame.Surface) -> pygame.Surface: return cropImg(img,img.get_bounding_rect())

"""展示"""
#图片blit模块：接受图片，位置（列表格式），屏幕，如果不是UI层需要local_x和local_y
def drawImg(img:pygame.Surface, position:Union[tuple,list], screen:pygame.Surface,
    local_x:Union[int,float] = 0, local_y:Union[int,float] = 0) -> None:
    screen.blit(img,(position[0]+local_x,position[1]+local_y))

#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def displayInCenter(item1:pygame.Surface, item2:pygame.Surface, x:Union[int,float], y:Union[int,float], screen:pygame.Surface,
    local_x:Union[int,float] = 0, local_y:Union[int,float] = 0) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def displayWithInCenter(item1:pygame.Surface, item2:pygame.Surface, x:Union[int,float], y:Union[int,float], screen:pygame.Surface,
    local_x:Union[int,float] = 0, local_y:Union[int,float] = 0) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+local_x,y+local_y))
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

"""其他"""
#字典合并
def dicMerge(dict1:dict, dict2:dict) -> dict: return {**dict1, **dict2}

#关闭背景音乐
def unloadBackgroundMusic() -> None:
    pygame.mixer.music.unload()
    pygame.mixer.stop()

#随机数
def randomInt(start:int, end:int) -> int: return random.randint(start,end)

#转换坐标
def convert_pos(pos:Union[list,tuple,dict,object,numpy.ndarray]) -> tuple:
    #检测坐标
    if isinstance(pos,(list,tuple,numpy.ndarray)):
        return pos[0],pos[1]
    elif isinstance(pos,dict):
        return pos["x"],pos["y"]
    else:
        return pos.x,pos.y

#判断2个坐标是否相同
def is_same_pos(pos1:any, pos2:any) -> bool: return convert_pos(pos1) == convert_pos(pos2)

#抛出引擎内的异常
def throwException(exception_type:str, info:str) -> None:
    if exception_type == "error":
        raise Exception('LinpgEngine-Error: {}'.format(info))
    elif exception_type == "warning":
        print("LinpgEngine-Warning: {}".format(info))
    elif exception_type == "info":
        print('LinpgEngine-Info: {}'.format(info))
    else:
        throwException("error","Hey, the exception_type '{}' is not acceptable!".format(exception_type))
