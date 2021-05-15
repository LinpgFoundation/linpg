# cython: language_level=3
from PIL import Image
from .inputbox import *

# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def loadImage(
    path: Union[str, pygame.Surface],
    position: tuple,
    width: int = -1,
    height: int = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> ImageSurface:
    return ImageSurface(
        imgLoadFunction(path, ifConvertAlpha),
        position[0],
        position[1],
        width,
        height,
        tag,
    )

# 高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def loadDynamicImage(
    path: Union[str, pygame.Surface],
    position: tuple,
    target_position: tuple,
    moveSpeed: tuple = (0, 0),
    width: int = -1,
    height: int = -1,
    tag="default",
    ifConvertAlpha: bool = True
    ) -> DynamicImageSurface:
    return DynamicImageSurface(imgLoadFunction(path,ifConvertAlpha),position[0],position[1],target_position[0],target_position[1],\
        moveSpeed[0],moveSpeed[1],width,height,tag)

# 加载GIF格式图片
def loadGif(
    img_list_or_path: Union[str, tuple, list],
    position: tuple,
    size: tuple,
    updateGap: int = 1
    ) -> GifSurface:
    imgList:list = []
    #如果是gif文件
    if isinstance(img_list_or_path, str) and img_list_or_path.endswith(".gif"):
        gif_image:object = Image.open(img_list_or_path)
        theFilePath:str = os.path.dirname(img_list_or_path)
        for i in range(gif_image.n_frames):
            gif_image.seek(i)
            pathTmp = os.path.join(theFilePath, "gifTempFileForLoading_{}.png".format(i))
            gif_image.save(pathTmp)
            imgList.append(StaticImageSurface(pathTmp,0,0,size[0], size[1]))
            os.remove(pathTmp)
    #如果是一个列表的文件路径
    elif isinstance(img_list_or_path, (tuple, list)):
        for image_path in img_list_or_path: imgList.append(StaticImageSurface(image_path,0,0,size[0], size[1]))
    else:
        throwException("error", 'Invalid input for "img_list_or_path": {}'.format(img_list_or_path))
    return GifSurface(numpy.asarray(imgList), position[0], position[1], size[0], size[1], updateGap)

# 加载按钮
def loadButton(
    path: Union[str, pygame.Surface],
    position: tuple,
    size: tuple,
    alpha_when_not_hover: int = 255
    ) -> Button:
    if alpha_when_not_hover < 255:
        fading_button = Button(
            loadImg(path, alpha=alpha_when_not_hover),
            position[0],
            position[1],
            size[0],
            size[1],
        )
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return Button(loadImg(path), position[0], position[1], size[0], size[1])

# 加载按钮
def loadButtonWithDes(
    path: Union[str, pygame.Surface],
    tag: str,
    position: tuple,
    size: tuple,
    alpha_when_not_hover: int = 255) -> ButtonWithDes:
    if alpha_when_not_hover < 255:
        fading_button = ButtonWithDes(
            loadImg(path, alpha=alpha_when_not_hover),
            tag,
            position[0],
            position[1],
            size[0],
            size[1],
        )
        img2 = fading_button.get_image_copy()
        img2.set_alpha(255)
        fading_button.set_hover_img(img2)
        return fading_button
    else:
        return ButtonWithDes(
            loadImg(path), tag, position[0], position[1], size[0], size[1]
        )

# 加载中间有文字按钮
def loadButtonWithTextInCenter(
    path: Union[str, pygame.Surface],
    txt: any,
    font_color: any,
    font_size: int,
    position: tuple,
    alpha_when_not_hover: int = 255
    ) -> Button:
    txt_surface = fontRenderWithoutBound(txt, findColorRGBA(font_color), font_size)
    panding: int = int(font_size * 0.3)
    img = loadImg(path,size=(txt_surface.get_width()+panding*2,txt_surface.get_height()+panding*2))
    img.blit(txt_surface,(panding,panding))
    return loadButton(img, position, img.get_size(), alpha_when_not_hover)

#获取特定颜色的表面
def getSingleColorSurface(color, size=None) -> ImageSurface:
    # 如果size是none，则使用屏幕的尺寸
    if size is None: size = display.get_size()
    # 获取surface
    surfaceTmp = getSurface(size).convert()
    surfaceTmp.fill(color)
    return ImageSurface(surfaceTmp, 0, 0, size[0], size[1])

# 检测图片是否被点击
def isHover(
    imgObject: object,
    objectPos: Union[tuple, list] = (0, 0),
    local_x: Union[int, float] = 0,
    local_y: Union[int, float] = 0
    ) -> bool:
    mouse_x, mouse_y = controller.get_mouse_pos()
    # 如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    if isinstance(imgObject, GameObject2d):
        return imgObject.is_hover((mouse_x - local_x, mouse_y - local_y))
    else:
        return isHoverPygameObject(imgObject, objectPos, local_x, local_y)

# 转换pygame的rect类至linpg引擎的shape类
def convert_to_shape(rect: Union[Shape, pygame.Rect]) -> Shape:
    #确认是pygame.Rect类再转换
    if isinstance(rect, pygame.Rect):
        return Shape(rect.x, rect.y, rect.width, rect.height)
    #如果是Shape类，则没必要转换
    elif isinstance(rect, Shape):
        return rect
    else:
        throwException("error", 'The rect has to be "pygame.Rect" or at least "linpg.Shape", not "{}".'.format(type(rect)))

# 转换linpg引擎的shape类至pygame的rect类
def convert_to_rect(shape: Union[Shape, pygame.Rect]) -> pygame.Rect:
    #确认是pygame.Rect类再转换
    if isinstance(shape, pygame.Rect):
        return shape
    #如果是Shape类，则没必要转换
    elif isinstance(shape, Shape):
        return pygame.Rect(shape.left, shape.top, shape.width, shape.height)
    else:
        throwException("error", 'The shape has to be "linpg.Shape" or at least "pygame.Rect", not "{}".'.format(type(shape)))

# 是否形状一样
def is_same_shape(rect1: Union[Shape, pygame.Rect], rect2: Union[Shape, pygame.Rect]) -> bool:
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height

# 画正方形（的方块）
def draw_rect(surface:pygame.Surface, color:any, rect:Union[pygame.Rect, Shape], width:int=0) -> None:
    pygame.draw.rect(surface, color, convert_to_rect(rect), width)
