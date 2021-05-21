# cython: language_level=3
from PIL import Image as ImageLoader
from .font import *

# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> Image:
    return Image(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag
        )

# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_static_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> StaticImage:
    return StaticImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag
        )

# 高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_dynamic_image(
    path: Union[str, ImageSurface],
    position: tuple,
    target_position: tuple,
    moveSpeed: tuple = (0, 0),
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag="default",
    ifConvertAlpha: bool = True
    ) -> DynamicImage:
    return DynamicImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        target_position[0],
        target_position[1],
        moveSpeed[0],
        moveSpeed[1],
        int(width),
        int(height),
        tag
        )

# 加载GIF格式图片
def load_gif(
    img_list_or_path: Union[str, tuple, list],
    position: tuple,
    size: tuple,
    updateGap: int = 1
    ) -> GifSurface:
    imgList: list = []
    # 如果是gif文件
    if isinstance(img_list_or_path, str) and img_list_or_path.endswith(".gif"):
        gif_image: object = ImageLoader.open(img_list_or_path)
        theFilePath: str = os.path.dirname(img_list_or_path)
        for i in range(gif_image.n_frames):
            gif_image.seek(i)
            pathTmp = os.path.join(theFilePath, "gifTempFileForLoading_{}.png".format(i))
            gif_image.save(pathTmp)
            imgList.append(StaticImage(pathTmp, 0, 0, size[0], size[1]))
            os.remove(pathTmp)
    # 如果是一个列表的文件路径
    elif isinstance(img_list_or_path, (tuple, list)):
        for image_path in img_list_or_path:
            imgList.append(StaticImage(image_path, 0, 0, size[0], size[1]))
    else:
        throw_exception("error", 'Invalid input for "img_list_or_path": {}'.format(img_list_or_path))
    return GifSurface(numpy.asarray(imgList), position[0], position[1], size[0], size[1], updateGap)

#转换linpg.Rect至pygame.Rect
def convert_to_pygame_rect(rect:RectLiked) -> pygame.Rect:
    # 如果是pygame.Rect类，则没必要转换
    if isinstance(rect, pygame.Rect):
        return rect
    # 确认是linpg.Rect类再转换
    elif isinstance(rect, Rect):
        return pygame.Rect(rect.left, rect.top, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return pygame.Rect(rect[0], rect[1])
        elif len(rect) == 4:
            return pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            throw_exception("error", 'Invalid length for forming a rect.')
    else:
        throw_exception("error", 'The rect has to be RectLiked object, not "{}".'.format(type(rect)))

#获取图片的subsurface
def get_img_subsurface(img:ImageSurface, rect:RectLiked) -> ImageSurface:
    if isinstance(rect, pygame.Rect):
        return img.subsurface(rect)
    else:
        return img.subsurface(convert_to_pygame_rect(rect))

#获取特定颜色的表面
def get_single_color_surface(color, size=None) -> Image:
    # 如果size是none，则使用屏幕的尺寸
    if size is None: size = display.get_size()
    # 获取surface
    surfaceTmp = new_surface(size).convert()
    surfaceTmp.fill(color)
    return Image(surfaceTmp, 0, 0, size[0], size[1])

# 检测图片是否被点击
def is_hover(
    imgObject: object, objectPos: Union[tuple, list] = (0, 0), off_set_x: Union[int, float] = 0, off_set_y: Union[int, float] = 0
    ) -> bool:
    mouse_x, mouse_y = controller.get_mouse_pos()
    # 如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    if isinstance(imgObject, GameObject2d):
        return imgObject.is_hover((mouse_x - off_set_x, mouse_y - off_set_y))
    else:
        return is_hover_pygame_object(imgObject, objectPos, off_set_x, off_set_y)