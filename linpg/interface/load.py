from PIL import Image as ImageLoader
from ..battle import *


class Loader:
    def __init__(self) -> None:
        pass

    # 原始图片
    def img(
        self,
        path: str,
        size: tuple = tuple(),
        alpha: int = 255,
        ifConvertAlpha: bool = True,
    ) -> ImageSurface:
        return IMG.load(path, size, alpha, ifConvertAlpha)

    # 静态图片
    def static_image(self, path: str, position: tuple, size: tuple = NoSize, tag: str = "deafult") -> StaticImage:
        return StaticImage(path, position[0], position[1], size[0], size[1], tag)

    # 动态图片
    def dynamic_image(self, path: str, position: tuple, size: tuple = NoSize, tag: str = "deafult") -> DynamicImage:
        return DynamicImage(path, position[0], position[1], size[0], size[1], tag)

    # 可自行移动的图片
    def movable_image(
        self,
        path: str,
        position: tuple,
        target_position: tuple,
        move_speed: tuple = (0, 0),
        size: tuple = NoSize,
        tag="default",
    ) -> MovableImage:
        return MovableImage(
            path,
            position[0],
            position[1],
            target_position[0],
            target_position[1],
            move_speed[0],
            move_speed[1],
            size[0],
            size[1],
            tag,
        )

    # 进度条Surface
    def progress_bar_surface(
        self,
        img_on_top_path: str,
        img_on_bottom_path: str,
        position: tuple,
        size: tuple,
        mode: str = "horizontal",
        tag: str = "",
    ) -> ProgressBarSurface:
        return ProgressBarSurface(
            img_on_top_path,
            img_on_bottom_path,
            position[0],
            position[1],
            size[0],
            size[1],
            mode,
            tag,
        )

    # gif图片
    def gif(
        self,
        gif_path_or_img_list: Union[str, tuple, list],
        position: tuple,
        size: tuple,
        updateGap: int = 1,
    ) -> GifImage:
        imgList: list = []
        # 如果是gif文件
        if isinstance(gif_path_or_img_list, str) and gif_path_or_img_list.endswith(".gif"):
            gif_image: object = ImageLoader.open(gif_path_or_img_list)
            theFilePath: str = os.path.dirname(gif_path_or_img_list)
            for i in range(gif_image.n_frames):
                gif_image.seek(i)
                pathTmp = os.path.join(theFilePath, "gifTempFileForLoading_{}.png".format(i))
                gif_image.save(pathTmp)
                imgList.append(StaticImage(pathTmp, 0, 0, size[0], size[1]))
                os.remove(pathTmp)
        # 如果是一个列表的文件路径
        elif isinstance(gif_path_or_img_list, (tuple, list)):
            for image_path in gif_path_or_img_list:
                imgList.append(StaticImage(image_path, 0, 0, size[0], size[1]))
        else:
            EXCEPTION.fatal('Invalid input for "gif_path_or_img_list": {}'.format(gif_path_or_img_list))
        return GifImage(
            numpy.asarray(imgList),
            position[0],
            position[1],
            size[0],
            size[1],
            updateGap,
        )

    def button(self, path: str, position: tuple, size: tuple, alpha_when_not_hover: int = 255) -> Button:
        return load_button(path, position, size, alpha_when_not_hover)

    def button_with_text_in_center(
        self,
        path: str,
        txt: any,
        font_color: color_liked,
        font_size: int,
        position: tuple,
        alpha_when_not_hover: int = 255,
    ) -> Button:
        return load_button_with_text_in_center(path, txt, font_color, font_size, position, alpha_when_not_hover)


load: Loader = Loader()
