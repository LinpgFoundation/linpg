from .text import *


# 用于静态图片的surface
class StaticImage(AdvancedAbstractCachingImageSurface):
    def __init__(
        self,
        img: PoI,
        x: int_f = 0,
        y: int_f = 0,
        width: int_f = -1,
        height: int_f = -1,
        enable_cropping: bool = False,
        is_pixelated: bool = False,
        tag: str = "",
    ) -> None:
        super().__init__(Images.quickly_load(img), x, y, width, height, tag)
        self.__is_flipped_horizontally: bool = False
        self.__is_flipped_vertically: bool = False
        self.__crop_rect: Rectangle | None = None
        self.__bounding_rect: Rectangle = Rectangle(0, 0, 0, 0)
        self.__enable_cropping: bool = enable_cropping
        self.__is_pixelated: bool = is_pixelated

    # 截图的范围
    @property
    def crop_rect(self) -> Rectangle | None:
        return self.__crop_rect

    def get_crop_rect(self) -> Rectangle | None:
        return self.__crop_rect

    def set_crop_rect(self, rect: Rectangle | None) -> None:
        if not Rectangles.equal(self.__crop_rect, rect):
            self.__crop_rect = rect
            self._need_update = True

    # 反转原图，并打上已反转的标记
    def flip(self, horizontal: bool = True, vertical: bool = False) -> None:
        if horizontal is True:
            self.__is_flipped_horizontally = not self.__is_flipped_horizontally
            self._need_update = True
        if vertical is True:
            self.__is_flipped_vertically = not self.__is_flipped_vertically
            self._need_update = True

    # 如果不处于反转状态，则反转
    def flip_if_not(self, horizontal: bool = True, vertical: bool = False) -> None:
        if horizontal is True and not self.__is_flipped_horizontally:
            self.__is_flipped_horizontally = True
            self._need_update = True
        if vertical is True and not self.__is_flipped_vertically:
            self.__is_flipped_vertically = True
            self._need_update = True

    # 反转回正常状态
    def flip_back_to_normal(self) -> None:
        if self.__is_flipped_horizontally is True:
            self.__is_flipped_horizontally = False
            self._need_update = True
        if self.__is_flipped_vertically is True:
            self.__is_flipped_vertically = False
            self._need_update = True

    # 返回一个复制品
    def copy(self, deep_copy: bool = True) -> "StaticImage":
        return StaticImage(
            self.get_image_copy() if deep_copy else self._get_image_reference(),
            self.x,
            self.y,
            self.get_width(),
            self.get_height(),
            self.__enable_cropping,
            self.__is_pixelated,
            self.tag,
        )

    # 获取切割后的图片的rect
    def get_bounding_rect(self) -> Rectangle:
        # 如果图片需要更新，则先更新
        if self._need_update is True:
            self._update_img()
        return self.__bounding_rect

    def get_buffer(self) -> ImageSurface:
        # 如果图片需要更新，则先更新
        if self._need_update is True:
            self._update_img()
        return self._processed_img  # type: ignore

    # 更新图片
    def _update_img(self) -> None:
        # 改变尺寸
        imgTmp = (
            Images.smoothly_resize(self._get_image_reference(), self.size)
            if not self.__is_pixelated and Settings.get_antialias()
            else Images.resize(self._get_image_reference(), self.size)
        )
        # 翻转图片
        if self.__is_flipped_horizontally is True or self.__is_flipped_vertically is True:
            imgTmp = Images.flip(imgTmp, self.__is_flipped_horizontally, self.__is_flipped_vertically)
        if self.__enable_cropping:
            # 获取切割rect
            rect: Rectangle = Rectangles.create(imgTmp.get_bounding_rect())
            if self.width != rect.width or self.height != rect.height or self.__crop_rect is not None:
                if self.__crop_rect is not None:
                    new_x: int = max(rect.x, self.__crop_rect.x)
                    new_y: int = max(rect.y, self.__crop_rect.y)
                    rect.move_to((new_x, new_y))
                    rect.set_size(
                        min(rect.right, self.__crop_rect.right) - new_x, min(rect.bottom, self.__crop_rect.bottom) - new_y
                    )
                self.set_local_pos(rect.x, rect.y)
                self.__bounding_rect.move_to(rect.get_pos())
                self.__bounding_rect.set_size(rect.get_width(), rect.get_height())
                self._processed_img = imgTmp.subsurface(self.__bounding_rect.get_rect())
            else:
                self._processed_img = imgTmp
                self.__bounding_rect = Rectangles.create(self._processed_img.get_bounding_rect())
        else:
            self._processed_img = imgTmp
            self.__bounding_rect = Rectangles.create(self._processed_img.get_bounding_rect())
        if self._alpha < 255:
            self._processed_img.set_alpha(self._alpha)
        self._need_update = False


# gif图片管理
class AnimatedImage(AdvancedAbstractImageSurface):
    def __init__(
        self, imgList: tuple[StaticImage, ...], x: int_f, y: int_f, width: int_f, height: int_f, fps: int_f, tag: str = ""
    ) -> None:
        super().__init__(imgList, x, y, width, height, tag)
        self.__imgId: int = 0
        self.__fps: int = max(int(fps), 0)
        self.__countDown: int = 0

    # get frame per second of
    def get_fps(self) -> int:
        return self.__fps

    # set frame per second of
    def set_fps(self, value: int_f) -> None:
        self.__fps = max(int(value), 0)

    # 返回一个复制
    def copy(self, deep_copy: bool = True) -> "AnimatedImage":
        return AnimatedImage(
            self.get_image_copy() if deep_copy else self._get_image_reference(),
            self.x,
            self.y,
            self.get_width(),
            self.get_height(),
            self.__fps,
            self.tag,
        )

    # 当前图片
    def _get_image_reference(self) -> tuple[StaticImage, ...]:
        return super()._get_image_reference()  # type: ignore

    @property
    def current_image(self) -> StaticImage:
        self._get_image_reference()[self.__imgId].set_size(self.get_width(), self.get_height())
        self._get_image_reference()[self.__imgId].set_alpha(self._alpha)
        return self._get_image_reference()[self.__imgId]

    # 获取图片非透明部分的rect
    def get_bounding_rect(self) -> Rectangle:
        return self.current_image.get_bounding_rect()

    # 展示
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_hidden():
            return
        self.current_image.display(_surface, Coordinates.add(self.pos, offSet))
        if self.__countDown >= 1000 // self.__fps:
            self.__countDown = 0
            self.__imgId += 1
            if self.__imgId >= len(self._get_image_reference()):
                self.__imgId = 0
        else:
            self.__countDown += Display.get_delta_time()
