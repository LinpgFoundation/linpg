from .surface import *

# 动态图形类
class DynamicImage(AbstractImageSurface):
    def __init__(self, img: PoI, x: int_f, y: int_f, width: int_f = -1, height: int_f = -1, tag: str = ""):
        super().__init__(IMG.quickly_load(img), x, y, width, height, tag)
        self.__processed_img: ImageSurface = None

    # 返回一个复制
    def copy(self) -> AbstractImageSurface:
        replica = DynamicImage(self.get_image_copy(), self.x, self.y, self.get_width(), self.get_height(), self.tag)
        replica.set_alpha(255)
        return replica

    # 返回一个浅复制品
    def light_copy(self) -> AbstractImageSurface:
        return DynamicImage(self.img, self.x, self.y, self.get_width(), self.get_height(), self.tag)

    # 反转
    def flip(self, vertical: bool = False, horizontal: bool = False) -> None:
        self.img = IMG.flip(self.img, vertical, horizontal)

    # 设置透明度
    def set_alpha(self, value: int) -> None:
        super().set_alpha(value)
        if self.__processed_img is not None:
            self.__processed_img.set_alpha(self.get_alpha())

    # 更新图片
    def update_image(self, img_path: PoI, ifConvertAlpha: bool) -> None:
        super().update_image(img_path, ifConvertAlpha=ifConvertAlpha)
        self.__processed_img = None

    # 旋转
    def rotate(self, angle: int) -> None:
        super().rotate(angle)
        self.__processed_img = None

    # 展示
    def display(self, surface: ImageSurface, offSet: Iterable = Coordinates.ORIGIN) -> None:
        if not self.hidden:
            if not Setting.low_memory_mode:
                if self.__processed_img is None or self.__processed_img.get_size() != self.size:
                    self.__processed_img = IMG.smoothly_resize(self.img, self.size)
                surface.blit(self.__processed_img, Coordinates.add(self.pos, offSet))
            else:
                surface.blit(IMG.resize(self.img, self.size), Coordinates.add(self.pos, offSet))


# 用于静态图片的surface
class StaticImage(AdvancedAbstractCachingImageSurface):
    def __init__(self, img: PoI, x: int_f, y: int_f, width: int_f = -1, height: int_f = -1, tag: str = ""):
        super().__init__(IMG.quickly_load(img), x, y, width, height, tag)
        self.__is_flipped_horizontally: bool = False
        self.__is_flipped_vertically: bool = False
        self.__crop_rect: object = None

    # 截图的范围
    @property
    def crop_rect(self) -> object:
        return self.__crop_rect

    def get_crop_rect(self) -> object:
        return self.__crop_rect

    def set_crop_rect(self, rect: Rect) -> None:
        if rect is None or isinstance(rect, Rect):
            if self.__crop_rect != rect:
                self.__crop_rect = rect
                self._need_update = True
            else:
                pass
        else:
            EXCEPTION.fatal("You have to input either a None or a Rect, not {}".format(type(rect)))

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
    def copy(self) -> AdvancedAbstractImageSurface:
        return StaticImage(self.img.copy(), self.x, self.y, self.get_width(), self.get_height())

    # 返回一个浅复制品
    def light_copy(self) -> AdvancedAbstractImageSurface:
        return StaticImage(self.img, self.x, self.y, self.get_width(), self.get_height())

    # 更新图片
    def _update_img(self) -> None:
        # 改变尺寸
        imgTmp = IMG.smoothly_resize(self.img, self.size) if Setting.antialias is True else IMG.resize(self.img, self.size)
        # 翻转图片
        if self.__is_flipped_horizontally is True or self.__is_flipped_vertically is True:
            imgTmp = IMG.flip(imgTmp, self.__is_flipped_horizontally, self.__is_flipped_vertically)
        # 获取切割rect
        rect = imgTmp.get_bounding_rect()
        if self.width != rect.width or self.height != rect.height or self.__crop_rect is not None:
            if self.__crop_rect is not None:
                new_x: int = max(rect.x, self.__crop_rect.x)
                new_y: int = max(rect.y, self.__crop_rect.y)
                rect = Rect(
                    new_x,
                    new_y,
                    min(rect.right, self.__crop_rect.right) - new_x,
                    min(rect.bottom, self.__crop_rect.bottom) - new_y,
                )
            self._processed_img = new_transparent_surface(rect.size)
            self.set_local_pos(rect.x, rect.y)
            self._processed_img.blit(imgTmp, (-self.local_x, -self.local_y))
        else:
            self._processed_img = imgTmp
        if self._alpha < 255:
            self._processed_img.set_alpha(self._alpha)
        self._need_update = False


# 需要移动的动态图片
class MovableImage(StaticImage):
    def __init__(
        self,
        img: PoI,
        x: int_f,
        y: int_f,
        target_x: int_f,
        target_y: int_f,
        move_speed_x: number,
        move_speed_y: number,
        width: int_f = -1,
        height: int_f = -1,
        tag: str = "",
    ):
        super().__init__(img, x, y, width, height, tag)
        self.__default_x: int = int(self.x)
        self.__default_y: int = int(self.y)
        self.__target_x: int = int(target_x)
        self.__target_y: int = int(target_y)
        self.__move_speed_x: number = move_speed_x
        self.__move_speed_y: number = move_speed_y
        self.__is_moving_toward_target: bool = False

    # 返回一个复制
    def copy(self) -> StaticImage:
        return MovableImage(
            self.get_image_copy(),
            self.x,
            self.y,
            self.__target_x,
            self.__target_y,
            self.__move_speed_x,
            self.__move_speed_y,
            self.get_width(),
            self.get_height(),
            self.tag,
        )

    # 返回一个浅复制品
    def light_copy(self) -> StaticImage:
        return MovableImage(
            self.img,
            self.x,
            self.y,
            self.__target_x,
            self.__target_y,
            self.__move_speed_x,
            self.__move_speed_y,
            self.get_width(),
            self.get_height(),
            self.tag,
        )

    # 设置初始坐标
    def set_pos(self, x: int_f, y: int_f) -> None:
        self.__default_x = int(x)
        self.__default_y = int(y)

    # 设置当前的所在坐标
    def set_real_pos(self, x: int_f, y: int_f) -> None:
        super().set_pos(x, y)

    # 设置目标坐标
    def set_target(self, target_x: int_f, target_y: int_f, move_speed_x: number, move_speed_y: number) -> None:
        self.__target_x = int(target_x)
        self.__target_y = int(target_y)
        self.__move_speed_x = move_speed_x
        self.__move_speed_y = move_speed_y

    # 控制
    def switch(self) -> None:
        self.__is_moving_toward_target = not self.__is_moving_toward_target

    def move_toward(self) -> None:
        self.__is_moving_toward_target = True

    def move_back(self) -> None:
        self.__is_moving_toward_target = False

    # 移动状态
    def is_moving_toward_target(self) -> bool:
        return self.__is_moving_toward_target

    def has_reached_target(self) -> bool:
        return (
            self.x == self.__target_x and self.y == self.__target_y
            if self.__is_moving_toward_target is True
            else self.x == self.__default_x and self.y == self.__default_y
        )

    # 画出
    def display(self, surface: ImageSurface, offSet: Iterable = Coordinates.ORIGIN) -> None:
        if not self.hidden:
            super().display(surface, offSet)
            if self.__is_moving_toward_target is True:
                if self.__default_x < self.__target_x:
                    if self.x < self.__target_x:
                        self.x += self.__move_speed_x
                    if self.x > self.__target_x:
                        self.set_left(self.__target_x)
                elif self.__default_x > self.__target_x:
                    if self.x > self.__target_x:
                        self.x -= self.__move_speed_x
                    if self.x < self.__target_x:
                        self.set_left(self.__target_x)
                if self.__default_y < self.__target_y:
                    if self.y < self.__target_y:
                        self.y += self.__move_speed_y
                    if self.y > self.__target_y:
                        self.set_top(self.__target_y)
                elif self.__default_y > self.__target_y:
                    if self.y > self.__target_y:
                        self.y -= self.__move_speed_y
                    if self.y < self.__target_y:
                        self.set_top(self.__target_y)
            else:
                if self.__default_x < self.__target_x:
                    if self.x > self.__default_x:
                        self.x -= self.__move_speed_x
                    if self.x < self.__default_x:
                        self.set_left(self.__default_x)
                elif self.__default_x > self.__target_x:
                    if self.x < self.__default_x:
                        self.x += self.__move_speed_x
                    if self.x > self.__default_x:
                        self.set_left(self.__default_x)
                if self.__default_y < self.__target_y:
                    if self.y > self.__default_y:
                        self.y -= self.__move_speed_y
                    if self.y < self.__default_y:
                        self.set_top(self.__default_y)
                elif self.__default_y > self.__target_y:
                    if self.y < self.__default_y:
                        self.y += self.__move_speed_y
                    if self.y > self.__default_y:
                        self.set_top(self.__default_y)


# gif图片管理
class GifImage(AdvancedAbstractImageSurface):
    def __init__(
        self, imgList: tuple, x: int_f, y: int_f, width: int_f, height: int_f, updateGap: int_f, tag: str = ""
    ) -> None:
        super().__init__(imgList, x, y, width, height, tag)
        self.imgId: int = 0
        self.updateGap: int = max(int(updateGap), 0)
        self.countDown: int = 0

    # 返回一个复制
    def copy(self) -> AdvancedAbstractImageSurface:
        return GifImage(self.get_image_copy(), self.x, self.y, self.get_width(), self.get_height(), self.updateGap)

    # 返回一个浅复制品
    def light_copy(self) -> AdvancedAbstractImageSurface:
        return GifImage(self.img, self.x, self.y, self.get_width(), self.get_height(), self.updateGap)

    # 当前图片
    @property
    def current_image(self) -> StaticImage:
        return self.img[self.imgId]

    # 展示
    def display(self, surface: ImageSurface, offSet: Iterable = Coordinates.ORIGIN) -> None:
        if not self.hidden:
            self.current_image.set_size(self.get_width(), self.get_height())
            self.current_image.set_alpha(self._alpha)
            self.current_image.display(surface, Coordinates.add(self.pos, offSet))
            if self.countDown >= self.updateGap:
                self.countDown = 0
                self.imgId += 1
                if self.imgId >= len(self.img):
                    self.imgId = 0
            else:
                self.countDown += 1
