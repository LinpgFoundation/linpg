from PIL import Image as ImageLoader
from ..battle import *


class Loader:

    # 原始图片
    @staticmethod
    def img(path: str, size: tuple = tuple(), alpha: int = 255, ifConvertAlpha: bool = True) -> ImageSurface:
        return IMG.load(path, size, alpha, ifConvertAlpha)

    # 静态图片
    @staticmethod
    def static_image(path: str, position: tuple, size: tuple = NoSize, tag: str = "") -> StaticImage:
        return StaticImage(path, position[0], position[1], size[0], size[1], tag)

    # 动态图片
    @staticmethod
    def dynamic_image(path: str, position: tuple, size: tuple = NoSize, tag: str = "") -> DynamicImage:
        return DynamicImage(path, position[0], position[1], size[0], size[1], tag)

    # 可自行移动的图片
    @staticmethod
    def movable_image(
        path: str, position: tuple, target_position: tuple, move_speed: tuple = (0, 0), size: tuple = NoSize, tag=""
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
    @staticmethod
    def progress_bar_surface(
        img_on_top_path: str, img_on_bottom_path: str, position: tuple, size: tuple, mode: str = "horizontal", tag: str = ""
    ) -> ProgressBarSurface:
        return ProgressBarSurface(img_on_top_path, img_on_bottom_path, position[0], position[1], size[0], size[1], mode, tag)

    # gif图片
    @staticmethod
    def gif(gif_path_or_img_list: Union[str, tuple, list], position: tuple, size: tuple, updateGap: int = 1) -> GifImage:
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
        return GifImage(tuple(imgList), position[0], position[1], size[0], size[1], updateGap)

    @staticmethod
    def button(path: str, position: tuple, size: tuple, alpha_when_not_hover: int = 255) -> Button:
        return load_button(path, position, size, alpha_when_not_hover)

    @staticmethod
    def button_with_text_in_center(
        path: str, txt: any, font_color: color_liked, font_size: int, position: tuple, alpha_when_not_hover: int = 255
    ) -> Button:
        return load_button_with_text_in_center(path, txt, font_color, font_size, position, alpha_when_not_hover)

    # 普通文字模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class
    @staticmethod
    def text(
        txt: any, color: color_liked, pos: tuple, size: int, ifBold: bool = False, ifItalic: bool = False
    ) -> TextSurface:
        return TextSurface(Font.render(txt, color, size, ifBold, ifItalic), pos[0], pos[1])

    # 高级文字模块：接受文字，颜色，位置，文字大小，文字样式，模式，返回制作完的文字Class，该Class具有一大一普通的字号
    @staticmethod
    def dynamic_text(
        txt: any, color: color_liked, pos: tuple, size: int, ifBold: bool = False, ifItalic: bool = False
    ) -> DynamicTextSurface:
        return DynamicTextSurface(
            Font.render(txt, color, size, ifBold, ifItalic),
            Font.render(txt, color, size * 1.5, ifBold, ifItalic),
            pos[0],
            pos[1],
        )


load: Loader = Loader()
