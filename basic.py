# cython: language_level=3
from .module import *
from PIL import Image
import numpy

#图片加载模块：接收图片路径,长,高,返回对应图片
def loadImg(path,width=None,height=None,setAlpha=None,ifConvertAlpha=True):
    img = imgLoadFunction(path,ifConvertAlpha)
    if setAlpha != None:
        img.set_alpha(setAlpha)
    if width == None and height == None:
        pass
    elif height!= None and height >= 0 and width == None:
        img = pygame.transform.scale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height == None and width!= None and width >= 0:
        img = pygame.transform.scale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.scale(img, (int(width), int(height)))
    elif width < 0 or height < 0:
        raise Exception('LinpgEngine-Error: Both width and height must be positive interger!')
    return img

#图片blit模块：接受图片，位置（列表格式），屏幕，如果不是UI层需要local_x和local_y
def drawImg(img,position,screen,local_x=0,local_y=0):
    screen.blit(img,(position[0]+local_x,position[1]+local_y))

#重新编辑尺寸
def resizeImg(img,imgSize=(None,None)):
    if imgSize[1]!= None and imgSize[1] >= 0 and imgSize[0] == None:
        img = pygame.transform.scale(img,(round(imgSize[1]/img.get_height()*img.get_width()), round(imgSize[1])))
    elif imgSize[1] == None and imgSize[0]!= None and imgSize[0] >= 0:
        img = pygame.transform.scale(img,(round(imgSize[0]), round(imgSize[0]/img.get_width()*img.get_height())))
    elif imgSize[0] >= 0 and imgSize[1] >= 0:
        img = pygame.transform.scale(img, (round(imgSize[0]), round(imgSize[1])))
    elif imgSize[0] < 0 or imgSize[1] < 0:
        raise Exception('LinpgEngine-Error: Both width and height must be positive interger!')
    return img

#高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:[x,y],长,高,返回对应的图片class
def loadImage(path,position,width=None,height=None,description="Default",ifConvertAlpha=True):
    return ImageSurface(imgLoadFunction(path,ifConvertAlpha),position[0],position[1],width,height,description)

#高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:[x,y],长,高,返回对应的图片class
def loadDynamicImage(path,position,target_position,moveSpeed=(0,0),width=None,height=None,description="Default",ifConvertAlpha=True):
    return DynamicImageSurface(imgLoadFunction(path,ifConvertAlpha),position[0],position[1],target_position[0],target_position[1],moveSpeed[0],moveSpeed[1],width,height,description)

#加载GIF格式图片
def loadGif(imgList,position,size,updateGap=1):
    return GifObject(imgList,position[0],position[1],size[0],size[1],updateGap)

def loadRealGif(path,position,size,updateGap=1):
    gif_img = Image.open(path)
    theFilePath = os.path.dirname(path)
    imgList = []
    try:
        i = 0
        while True:
            gif_img.seek(i)
            pathTmp = theFilePath+'/gifTempFileForLoading__'+str(i)+'.png'
            gif_img.save(pathTmp)
            imgList.append(pygame.image.load(os.path.join(pathTmp)).convert_alpha())
            os.remove(pathTmp)
            i += 1
    except:
        pass
    return GifObject(imgList,position[0],position[1],size[0],size[1],updateGap)

#加载音效
def loadSound(path,volume):
    soundTmp = pygame.mixer.Sound(path)
    soundTmp.set_volume(volume)
    return soundTmp

#识别图片模块，用于引擎内加载图片，十分不建议在本文件外调用
def imgLoadFunction(path,ifConvertAlpha):
    if isinstance(path,str):
        if ifConvertAlpha == False:
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
        raise Exception('LinpgEngine-Error: The path has to be a string or pygame.Surface (even though this is not recommended)! Path:',path)

#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def displayInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def displayWithInCenter(item1,item2,x,y,screen,local_x=0,local_y=0):
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+local_x,y+local_y))
    screen.blit(item1,(x+added_x+local_x,y+added_y+local_y))

#字典合并
def dicMerge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res

#加载路径下的所有图片，储存到一个list当中，然后返回
def loadAllImgInFile(pathRule,width=None,height=None):
    allImg = glob.glob(pathRule)
    for i in range(len(allImg)):
        allImg[i] = loadImg(allImg[i],width,height)
    return allImg

#增加图片暗度
def addDarkness(img,value):
    newImg = img.copy()
    newImg.fill((value, value, value),special_flags=pygame.BLEND_RGB_SUB) 
    return newImg

#减少图片暗度
def removeDarkness(img,value):
    newImg = img.copy()
    newImg.fill((value, value, value), special_flags=pygame.BLEND_RGB_ADD)
    return newImg

#调整图片亮度
def changeDarkness(surface,value):
    if value == 0:
        return surface
    if value > 0:
        return addDarkness(surface,value)
    else:
        return removeDarkness(surface,abs(value))

#按照给定的位置对图片进行剪裁
def cropImg(img,pos=(0,0),size=(0,0)):
    cropped = pygame.Surface((round(size[0]), round(size[1])),flags=pygame.SRCALPHA).convert_alpha()
    cropped.blit(img,(-pos[0],-pos[1]))
    return cropped

#检测图片是否被点击
def ifHover(imgObject,objectPos=(0,0),local_x=0,local_y=0):
    mouse_x,mouse_y = pygame.mouse.get_pos()
    #如果是pygame的面
    if isinstance(imgObject,pygame.Surface):
        if objectPos[0]<mouse_x-local_x<objectPos[0]+imgObject.get_width() and objectPos[1]<mouse_y-local_y<objectPos[1]+imgObject.get_height():
            return True
        else:
            return False
    #如果是Linpg引擎的Image类
    elif isinstance(imgObject,ImageSurface):
        return imgObject.ifHover(mouse_x-local_x,mouse_y-local_y)
    #如果是Linpg引擎的Button类
    elif isinstance(imgObject,Button):
        if imgObject.x<=mouse_x-local_x<=imgObject.x+imgObject.img.get_width() and imgObject.y<=mouse_y-local_y<=imgObject.y+imgObject.img.get_height():
            imgObject.hoverEventOn()
            return True
        else:
            imgObject.hoverEventOff()
            return False
    #如果是Linpg引擎的TextSurface类
    elif isinstance(imgObject,TextSurface):
        return imgObject.ifHover()
    else:
        raise Exception('LinpgEngine-Error: Unable to check current object:',imgObject)

#关闭背景音乐
def unloadBackgroundMusic():
    pygame.mixer.music.unload()
    pygame.mixer.stop()

#获取特定颜色的表面
def get_SingleColorSurface(color,size=None):
    if size == None:
        width,height = display.get_size()
    else:
        width = size[0]
        height = size[1]
    surfaceTmp = pygame.Surface((width,height),flags=pygame.SRCALPHA).convert()
    surfaceTmp.fill(color)
    return ImageSurface(surfaceTmp,0,0,width,height)

#随机数
def randomInt(start,end):
    return random.randint(start,end)

#获取pygame的输入事件
def get_pygame_events():
    return pygame.event.get()

#转换路径
def convert_pos(pos):
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

def is_same_pos(pos1,pos2):
    return convert_pos(pos1) == convert_pos(pos2)