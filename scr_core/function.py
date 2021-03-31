# cython: language_level=3
from PIL import Image
from .inputbox import *

#高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:[x,y],长,高,返回对应的图片class
def loadImage(path:Union[str,pygame.Surface], position, width=None, height=None, description="Default" ,ifConvertAlpha:bool=True) -> ImageSurface:
    return ImageSurface(imgLoadFunction(path,ifConvertAlpha),position[0],position[1],width,height,description)

#高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:[x,y],长,高,返回对应的图片class
def loadDynamicImage(path:Union[str,pygame.Surface], position, target_position, moveSpeed=(0,0),
    width:Union[int,float]=None, height:Union[int,float]=None, description="Default", ifConvertAlpha:bool=True) -> DynamicImageSurface:
    return DynamicImageSurface(imgLoadFunction(path,ifConvertAlpha),position[0],position[1],target_position[0],target_position[1],\
        moveSpeed[0],moveSpeed[1],width,height,description)

#加载GIF格式图片
def loadGif(img_list_or_path,position,size,updateGap=1) -> GifObject:
    if isinstance(img_list_or_path,str):
        imgList = []
        gif_img = Image.open(img_list_or_path)
        theFilePath = os.path.dirname(img_list_or_path)
        try:
            i = 0
            while True:
                gif_img.seek(i)
                pathTmp = theFilePath+'/gifTempFileForLoading__'+str(i)+'.png'
                gif_img.save(pathTmp)
                imgList.append(loadImg(pathTmp))
                os.remove(pathTmp)
                i += 1
        except:
            pass
    else:
        imgList = img_list_or_path
    return GifObject(numpy.asarray(imgList),position[0],position[1],size[0],size[1],updateGap)

#获取特定颜色的表面
def get_SingleColorSurface(color,size=None) -> ImageSurface:
    #如果size是none，则使用屏幕的尺寸
    if size == None: size = display.get_size()
    #获取surface
    surfaceTmp = getSurface(size).convert()
    surfaceTmp.fill(color)
    return ImageSurface(surfaceTmp,0,0,size[0],size[1])

#检测图片是否被点击
def is_hover(imgObject:object, objectPos:Union[tuple,list]=(0,0), local_x:Union[int,float]=0, local_y:Union[int,float]=0) -> bool:
    mouse_x,mouse_y = pygame.mouse.get_pos()
    #如果是pygame的面
    if isinstance(imgObject,pygame.Surface):
        if 0<mouse_x-local_x-objectPos[0]<imgObject.get_width() and 0<mouse_y-local_y-objectPos[1]<imgObject.get_height():
            return True
        else:
            return False
    #如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    elif isinstance(imgObject,GameObject2d):
        return imgObject.is_hover((mouse_x-local_x,mouse_y-local_y))
    else:
        throwException("error","Unable to check current object: {}".format(imgObject))

