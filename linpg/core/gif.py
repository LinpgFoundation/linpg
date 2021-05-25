# cython: language_level=3
from PIL import Image as ImageLoader
from .surface import *

# gif图片管理
class GifImage(AdvancedAbstractImage):
    def __init__(
        self,
        imgList: numpy.ndarray,
        x: Union[int, float],
        y: Union[int, float],
        width: int_f,
        height: int_f,
        updateGap: int_f,
        tag: str = "default"
        ):
        super().__init__(imgList, x, y, width, height, tag)
        self.imgId: int = 0
        self.updateGap: int = max(int(updateGap), 0)
        self.countDown: int = 0
    # 返回一个复制
    def copy(self):
        return GifImage(
            self.get_image_copy(),
            self.x,
            self.y,
            self._width,
            self._height,
            self.updateGap,
        )
    # 返回一个浅复制品
    def light_copy(self):
        return GifImage(
            self.get_image_pointer(),
            self.x,
            self.y,
            self._width,
            self._height,
            self.updateGap,
        )
    # 当前图片
    @property
    def current_image(self) -> StaticImage:
        return self.img[self.imgId]
    # 展示
    def display(self, surface: ImageSurface, offSet: Union[tuple, list] = (0, 0)):
        if not self.hidden:
            self.current_image.set_size(self.get_width(), self.get_height())
            self.current_image.set_alpha(self._alpha)
            self.current_image.display(surface, add_pos(self.pos, offSet))
            if self.countDown >= self.updateGap:
                self.countDown = 0
                self.imgId += 1
                if self.imgId >= len(self.img):
                    self.imgId = 0
            else:
                self.countDown += 1

# 加载GIF格式图片
def load_gif(
    img_list_or_path: Union[str, tuple, list],
    position: tuple,
    size: tuple,
    updateGap: int = 1
    ) -> GifImage:
    imgList: list = []
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
