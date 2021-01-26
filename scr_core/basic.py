# cython: language_level=3
from __future__ import annotations
#python本体库
import glob, os, random
#额外库
import numpy, pygame
from pygame.locals import *

#初始化pygame
pygame.init()

"""加载"""
#识别图片模块，用于引擎内加载图片，十分不建议在本文件外调用
def imgLoadFunction(path:str, ifConvertAlpha:bool) -> pygame.Surface:
    if isinstance(path,str):
        if not ifConvertAlpha:
            try:
                return pygame.image.load(os.path.join(path))
            except BaseException:
                raise Exception('LinpgEngine-Error: Cannot load image! Path:',path)
        else:
            try:
                return pygame.image.load(os.path.join(path)).convert_alpha()
            except BaseException:
                raise Exception('LinpgEngine-Error: Cannot load image! Path:',path)
    elif isinstance(path,pygame.Surface):
        return path
    else:
        raise Exception('LinpgEngine-Error: The path has to be a string or pygame.Surface! Path:',path)

#图片加载模块：接收图片路径,长,高,返回对应图片
def loadImg(path:str, size:str=None, setAlpha:int=None, ifConvertAlpha:bool=True) -> pygame.Surface:
    #加载图片
    img = imgLoadFunction(path,ifConvertAlpha)
    #根据参数编辑图片
    if setAlpha != None:
        img.set_alpha(setAlpha)
    #如果没有给size,则直接返回Surface
    if size == None or len(size) == 0:
        return img
    else:
        return resizeImg(img,size)

#加载音效
def loadSound(path:str, volume:float) -> pygame.mixer.Sound:
    soundTmp = pygame.mixer.Sound(path)
    soundTmp.set_volume(volume)
    return soundTmp

#加载路径下的所有图片，储存到一个list当中，然后返回
def loadAllImgInFile(pathRule:str, width=None, height=None) -> list[pygame.Surface]:
    return [loadImg(imgPath,(width,height)) for imgPath in glob.glob(pathRule)]

"""处理"""
#重新编辑尺寸
def resizeImg(img:pygame.Surface, size=(None,None)) -> pygame.Surface:
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
        raise Exception('LinpgEngine-Error: size "{}" is not acceptable'.format(size))
    #编辑图片
    if height!= None and height >= 0 and width == None:
        img = pygame.transform.scale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height == None and width!= None and width >= 0:
        img = pygame.transform.scale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.scale(img, (round(width), round(height)))
    elif width < 0 or height < 0:
        raise Exception('LinpgEngine-Error: Both width and height must be positive interger!')
    return img

#增加图片暗度
def addDarkness(img:pygame.Surface, value:int) -> pygame.Surface:
    newImg = img.copy()
    newImg.fill((value, value, value),special_flags=pygame.BLEND_RGB_SUB) 
    return newImg

#减少图片暗度
def removeDarkness(img:pygame.Surface, value:int) -> pygame.Surface:
    newImg = img.copy()
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
def cropImg(img:pygame.Surface, pos=(0,0),size=(0,0)) -> pygame.Surface:
    if isinstance(pos,pygame.Rect):
        cropped = pygame.Surface((pos.width,pos.height),flags=pygame.SRCALPHA).convert_alpha()
        cropped.blit(img,(-pos.x,-pos.y))
    else:
        cropped = pygame.Surface((round(size[0]), round(size[1])),flags=pygame.SRCALPHA).convert_alpha()
        cropped.blit(img,(-pos[0],-pos[1]))
    return cropped

#移除掉图片周围的透明像素
def copeBounding(img:pygame.Surface) -> pygame.Surface: return cropImg(img,img.get_bounding_rect())

"""展示"""
#图片blit模块：接受图片，位置（列表格式），屏幕，如果不是UI层需要local_x和local_y
def drawImg(img:pygame.Surface, position:tuple, screen:pygame.Surface, local_x:int=0, local_y:int=0) -> None:
    screen.blit(img,(position[0]+local_x,position[1]+local_y))

#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def displayInCenter(item1:pygame.Surface,item2:pygame.Surface,x,y,screen,local_x=0,local_y=0) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def displayWithInCenter(item1:pygame.Surface,item2:pygame.Surface,x,y,screen,local_x=0,local_y=0) -> None:
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
def convert_pos(pos:any) -> tuple:
    #检测坐标
    if isinstance(pos,(list,tuple,numpy.ndarray)):
        x = pos[0]
        y = pos[1]
    elif isinstance(pos,dict):
        x = pos["x"]
        y = pos["y"]
    else:
        x = pos.x
        y = pos.y
    return x,y

#判断2个坐标是否相同
def is_same_pos(pos1,pos2) -> bool: return convert_pos(pos1) == convert_pos(pos2)
