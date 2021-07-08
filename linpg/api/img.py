# cython: language_level=3
from .color import *

# 源库自带的图形类
ImageSurface = pygame.Surface if is_using_pygame() else pyglet.image

"""加载"""
#识快速加载图片
def quickly_load_img(path:Union[str,ImageSurface], ifConvertAlpha:bool=True) -> ImageSurface:
    if isinstance(path, ImageSurface):
        return path
    elif isinstance(path, str):
        path = os.path.join(path)
        if ifConvertAlpha is True:
            try:
                return pygame.image.load(path).convert_alpha() if is_using_pygame() else pyglet.image.load(path)
            except Exception:
                if Setting.developer_mode is True: 
                    EXCEPTION.fatal('Cannot load image from path: {}'.format(path))
                else:
                    return get_texture_missing_surface((192,108))
        else:
            try:
                return pygame.image.load(path) if is_using_pygame() else pyglet.image.load(path)
            except Exception:
                if Setting.developer_mode is True:
                    EXCEPTION.fatal('Cannot load image from path: {}'.format(path))
                else:
                    return get_texture_missing_surface((192,108))
    else:
        EXCEPTION.fatal("The path '{}' has to be a string or at least a ImageSurface!".format(path))

#图片加载模块：接收图片路径,长,高,返回对应图片
def load_img(path:Union[str,ImageSurface], size:size_liked=tuple(), alpha:int=255, ifConvertAlpha:bool=True) -> ImageSurface:
    #加载图片
    img = quickly_load_img(path,ifConvertAlpha)
    #根据参数编辑图片
    if alpha < 255: img.set_alpha(alpha)
    #如果没有给size,则直接返回Surface
    if len(size) == 0:
        return img
    else:
        return smoothly_resize_img(img, size) if Setting.antialias is True else resize_img(img, size)

#加载路径下的所有图片，储存到一个list当中，然后返回
def load_img_in_folder(pathRule:str, size:size_liked=tuple()) -> list:
    return [load_img(imgPath, size) for imgPath in glob(pathRule)]

#获取Surface
def new_surface(size:size_liked, surface_flags:any=None) -> ImageSurface:
    return pygame.Surface(size, flags=surface_flags) if surface_flags is not None else pygame.Surface(size)

#获取透明的Surface
def new_transparent_surface(size:size_liked) -> ImageSurface:
    return new_surface(size, pygame.SRCALPHA).convert_alpha()

#获取材质缺失的临时警示材质
def get_texture_missing_surface(size:size_liked) -> ImageSurface:
    texture_missing_surface:ImageSurface = new_surface(size).convert()
    texture_missing_surface.fill(Color.BLACK)
    half_width:int = int(size[0]/2)
    half_height:int = int(size[1]/2)
    purple_color_rbga:tuple = Color.VIOLET
    pygame.draw.rect(
        texture_missing_surface, purple_color_rbga, pygame.Rect(half_width, 0, texture_missing_surface.get_width()-half_width, half_height)
        )
    pygame.draw.rect(
        texture_missing_surface, purple_color_rbga, pygame.Rect(0, half_height, half_width, texture_missing_surface.get_height()-half_height)
        )
    return texture_missing_surface

"""处理"""
#重新编辑尺寸
def resize_img(img:ImageSurface, size:size_liked=(None,None)) -> ImageSurface:
    #转换尺寸
    if isinstance(size,(list,tuple)):
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
        EXCEPTION.fatal("The size '{}' is not acceptable.".format(size))
    #编辑图片
    if height is not None and height >= 0 and width is None:
        img = pygame.transform.scale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height is None and width is not None and width >= 0:
        img = pygame.transform.scale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.scale(img, (round(width), round(height)))
    elif width < 0 or height < 0:
        EXCEPTION.fatal("Both width and height must be positive interger!")
    return img

#精准地缩放尺寸
def smoothly_resize_img(img:ImageSurface, size:size_liked=(None,None)):
    #转换尺寸
    if isinstance(size,(list,tuple)):
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
        EXCEPTION.fatal("The size '{}' is not acceptable.".format(size))
    #编辑图片
    if height is not None and height >= 0 and width is None:
        img = pygame.transform.smoothscale(img,(round(height/img.get_height()*img.get_width()), round(height)))
    elif height is None and width is not None and width >= 0:
        img = pygame.transform.smoothscale(img,(round(width), round(width/img.get_width()*img.get_height())))
    elif width >= 0 and height >= 0:
        img = pygame.transform.smoothscale(img, (round(width), round(height)))
    elif width < 0 or height < 0:
        EXCEPTION.fatal("Both width and height must be positive interger!")
    return img

#翻转图片
def flip_img(img:ImageSurface, horizontal:bool, vertical:bool) -> ImageSurface: return pygame.transform.flip(img, horizontal, vertical)

#旋转图片
def rotate_img(img:ImageSurface, angle:int) -> ImageSurface: return pygame.transform.rotate(img, angle)

#增加图片暗度
def add_darkness(img:ImageSurface, value:int) -> ImageSurface:
    newImg:ImageSurface = img.copy()
    newImg.fill((value, value, value),special_flags=pygame.BLEND_RGB_SUB) 
    return newImg

#减少图片暗度
def subtract_darkness(img:ImageSurface, value:int) -> ImageSurface:
    newImg:ImageSurface = img.copy()
    newImg.fill((value, value, value),special_flags=pygame.BLEND_RGB_ADD)
    return newImg

#调整图片亮度
def change_darkness(surface:ImageSurface, value:int) -> ImageSurface:
    if value == 0:
        return surface
    if value > 0:
        return add_darkness(surface,value)
    else:
        return subtract_darkness(surface,abs(value))

#按照给定的位置对图片进行剪裁
def crop_img(img:ImageSurface, pos:pos_liked=Origin, size:size_liked=(1,1)) -> ImageSurface:
    if isinstance(pos,pygame.Rect):
        cropped = new_transparent_surface(pos.size)
        cropped.blit(img,(-pos.x,-pos.y))
    else:
        cropped = new_transparent_surface((round(size[0]),round(size[1])))
        cropped.blit(img,(-pos[0],-pos[1]))
    return cropped

#移除掉图片周围的透明像素
def cope_bounding(img:ImageSurface) -> ImageSurface: return crop_img(img,img.get_bounding_rect())

"""展示"""
#中心展示模块1：接受两个item和item2的x和y，将item1展示在item2的中心位置,但不展示item2：
def display_in_center(
    item1:ImageSurface, item2:ImageSurface, x:number, y:number, screen:ImageSurface, off_set_x:number = 0, off_set_y:number = 0
    ) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item1,(x+added_x+off_set_x,y+added_y+off_set_y))

#中心展示模块2：接受两个item和item2的x和y，展示item2后，将item1展示在item2的中心位置：
def display_within_center(
    item1:ImageSurface, item2:ImageSurface, x:number, y:number, screen:ImageSurface, off_set_x:number = 0, off_set_y:number = 0
    ) -> None:
    added_x = (item2.get_width()-item1.get_width())/2
    added_y = (item2.get_height()-item1.get_height())/2
    screen.blit(item2,(x+off_set_x,y+off_set_y))
    screen.blit(item1,(x+added_x+off_set_x,y+added_y+off_set_y))

# 将array转换并画到surface上
def draw_array(surface: ImageSurface, array: any) -> None:
    pygame.surfarray.blit_array(surface, array)

#是否触碰pygame类
def is_hover_pygame_object(imgObject:object, objectPos:pos_liked=Origin, off_set_x:number=0, off_set_y:number=0) -> bool:
    mouse_x,mouse_y = pygame.mouse.get_pos()
    #如果是pygame的Surface类
    if isinstance(imgObject, ImageSurface):
        return True if 0 < mouse_x-off_set_x-objectPos[0] < imgObject.get_width() and 0 < mouse_y-off_set_y-objectPos[1] < imgObject.get_height()\
            else False
    #如果是Rect类
    elif isinstance(imgObject,pygame.Rect):
        return True if 0 < mouse_x-off_set_x-imgObject.x < imgObject.width and 0 < mouse_y-off_set_y-imgObject.y < imgObject.height\
            else False
    else:
        EXCEPTION.fatal("Unable to check current object: {0} (type:{1})".format(imgObject,type(imgObject)))