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
    img_list_or_path: Union[list, tuple, str],
    position: tuple,
    size: tuple,
    updateGap: int = 1
    ) -> GifObject:
    if isinstance(img_list_or_path, str):
        imgList:list = []
        gif_image:object = Image.open(img_list_or_path)
        theFilePath:str = os.path.dirname(img_list_or_path)
        for i in range(gif_image.n_frames):
            gif_image.seek(i)
            pathTmp = os.path.join(theFilePath, "gifTempFileForLoading_{}.png".format(i))
            gif_image.save(pathTmp)
            imgList.append(loadImg(pathTmp))
            os.remove(pathTmp)
        return GifObject(numpy.asarray(imgList), position[0], position[1], size[0], size[1], updateGap)
    else:
        return GifObject(numpy.asarray(img_list_or_path), position[0], position[1], size[0], size[1], updateGap)

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

# 转换pygame的rect类
def convert_rect(rect: pygame.Rect) -> Shape: return Shape(rect.x, rect.y, rect.width, rect.height)

# 是否形状一样
def is_same_shape(rect1: Union[Shape, pygame.Rect], rect2: Union[Shape, pygame.Rect]) -> bool:
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height
