# cython: language_level=3
from .font import *

"""（即将弃置）"""
# 高级图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_dynamic_image(
    path: Union[str, ImageSurface],
    position: tuple,
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag: str = "default",
    ifConvertAlpha: bool = True
    ) -> DynamicImage:
    return DynamicImage(
        quickly_load_img(path, ifConvertAlpha),
        position[0],
        position[1],
        int(width),
        int(height),
        tag
        )

"""（即将弃置）"""
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

"""（即将弃置）"""
# 高级动态图片加载模块：接收图片路径（或者已经载入的图片）,位置:(x,y),长,高,返回对应的图片class
def load_movable_image(
    path: Union[str, ImageSurface],
    position: tuple,
    target_position: tuple,
    moveSpeed: tuple = (0, 0),
    width: Union[int, float] = -1,
    height: Union[int, float] = -1,
    tag="default",
    ifConvertAlpha: bool = True
    ) -> MovableImage:
    return MovableImage(
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

"""（即将弃置）"""
# 加载GIF格式图片
def load_gif(
    img_list_or_path: Union[str, tuple, list],
    position: tuple,
    size: tuple,
    updateGap: int = 1
    ) -> GifImage:
    imgList: list = []
    from PIL import Image as ImageLoader
    # 如果是gif文件
    if isinstance(img_list_or_path, str) and img_list_or_path.endswith(".gif"):
        gif_image: object = ImageLoader.open(img_list_or_path)
        theFilePath: str = os.path.dirname(img_list_or_path)
        for i in range(gif_image.n_frames):
            gif_image.seek(i)
            pathTmp = os.path.join(
                theFilePath, "gifTempFileForLoading_{}.png".format(i)
            )
            gif_image.save(pathTmp)
            imgList.append(StaticImage(pathTmp, 0, 0, size[0], size[1]))
            os.remove(pathTmp)
    # 如果是一个列表的文件路径
    elif isinstance(img_list_or_path, (tuple, list)):
        for image_path in img_list_or_path:
            imgList.append(StaticImage(image_path, 0, 0, size[0], size[1]))
    else:
        throw_exception(
            "error", 'Invalid input for "img_list_or_path": {}'.format(img_list_or_path)
        )
    return GifImage(
        numpy.asarray(imgList), position[0], position[1], size[0], size[1], updateGap
    )