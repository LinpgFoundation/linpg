# cython: language_level=3
from PIL import Image as ImageLoader
from .inputbox import *

# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int,float] = -1,
    height: Union[int,float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> Image:
    return Image(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag,
    )

# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_static_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int,float] = -1,
    height: Union[int,float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> StaticImage:
    return StaticImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag,
    )

# 高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_dynamic_image(
    path: Union[str, ImageSurface],
    position: tuple,
    target_position: tuple,
    moveSpeed: tuple = (0, 0),
    width: Union[int,float] = -1,
    height: Union[int,float] = -1,
    tag="default",
    ifConvertAlpha: bool = True
    ) -> DynamicImage:
    return DynamicImage(
        quickly_load_img(path,ifConvertAlpha),
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
    imgList:list = []
    #如果是gif文件
    if isinstance(img_list_or_path, str) and img_list_or_path.endswith(".gif"):
        gif_image:object = ImageLoader.open(img_list_or_path)
        theFilePath:str = os.path.dirname(img_list_or_path)
        for i in range(gif_image.n_frames):
            gif_image.seek(i)
            pathTmp = os.path.join(theFilePath, "gifTempFileForLoading_{}.png".format(i))
            gif_image.save(pathTmp)
            imgList.append(StaticImage(pathTmp,0,0,size[0], size[1]))
            os.remove(pathTmp)
    #如果是一个列表的文件路径
    elif isinstance(img_list_or_path, (tuple, list)):
        for image_path in img_list_or_path: imgList.append(StaticImage(image_path,0,0,size[0], size[1]))
    else:
        throw_exception("error", 'Invalid input for "img_list_or_path": {}'.format(img_list_or_path))
    return GifSurface(numpy.asarray(imgList), position[0], position[1], size[0], size[1], updateGap)

# 加载按钮
def load_button(
    path: Union[str, ImageSurface],
    position: tuple,
    size: tuple,
    alpha_when_not_hover: int = 255
    ) -> Button:
    if alpha_when_not_hover < 255:
        fading_button = Button(
            load_img(path, alpha=alpha_when_not_hover),
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
        return Button(load_img(path), position[0], position[1], size[0], size[1])

# 加载按钮
def load_button_with_des(
    path: Union[str, ImageSurface],
    tag: str,
    position: tuple,
    size: tuple,
    alpha_when_not_hover: int = 255) -> ButtonWithDes:
    if alpha_when_not_hover < 255:
        fading_button = ButtonWithDes(
            load_img(path, alpha=alpha_when_not_hover),
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
            load_img(path), tag, position[0], position[1], size[0], size[1]
        )

# 加载中间有文字按钮
def load_button_with_text_in_center(
    path: Union[str, ImageSurface],
    txt: any,
    font_color: any,
    font_size: int,
    position: tuple,
    alpha_when_not_hover: int = 255
    ) -> Button:
    txt_surface = render_font_without_bounding(txt, get_color_rbga(font_color), font_size)
    panding: int = int(font_size * 0.3)
    img = load_img(path,size=(txt_surface.get_width()+panding*2,txt_surface.get_height()+panding*2))
    img.blit(txt_surface,(panding,panding))
    return load_button(img, position, img.get_size(), alpha_when_not_hover)

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
        return is_hover_pygame_object(imgObject, objectPos, local_x, local_y)
