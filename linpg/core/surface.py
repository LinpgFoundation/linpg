from .shape import *

# 可隐藏的Surface
class HiddenableSurface:
    def __init__(self, visible: bool = True) -> None:
        self.__hidden: bool = not visible

    def set_visible(self, visible: bool) -> None:
        self.__hidden = not visible

    def is_visible(self) -> bool:
        return not self.__hidden

    def is_hidden(self) -> bool:
        return self.__hidden


# 图形接口
class AbstractImageSurface(Rectangle, HiddenableSurface):
    def __init__(self, img: Any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str) -> None:
        Rectangle.__init__(self, x, y, width, height)
        HiddenableSurface.__init__(self)
        self.img: Any = img
        # 确保长宽均已输入且为正整数
        if self.get_width() < 0 and self.get_height() < 0:
            self.set_size(self.img.get_width(), self.img.get_height())
        elif self.get_width() < 0 and self.get_height() >= 0:
            self.set_width(self.get_height() / self.img.get_height() * self.img.get_width())
        elif self.get_width() >= 0 and self.get_height() < 0:
            self.set_height(self.get_width() / self.img.get_width() * self.img.get_height())

    """透明度"""

    @property
    def alpha(self) -> int:
        return self.get_alpha()

    def get_alpha(self) -> int:
        return int(self.img.get_alpha())

    def set_alpha(self, value: int) -> None:
        self.img.set_alpha(Numbers.keep_int_in_range(value, 0, 255))

    def add_alpha(self, value: int) -> None:
        self.set_alpha(self.get_alpha() + value)

    def subtract_alpha(self, value: int) -> None:
        self.set_alpha(self.get_alpha() - value)

    # 获取图片复制品
    def get_image_copy(self) -> Any:
        return self.img.copy()

    # 更新图片
    def update_image(self, img_path: PoI, ifConvertAlpha: bool = True) -> None:
        self.img = Images.quickly_load(img_path, ifConvertAlpha)

    # 在尺寸比例不变的情况下改变尺寸
    def set_width_with_original_image_size_locked(self, width: int_f) -> None:
        self.set_size(width, width / self.img.get_width() * self.img.get_height())

    def set_height_with_original_image_size_locked(self, height: int_f) -> None:
        self.set_size(height / self.img.get_height() * self.img.get_width(), height)

    # 自动放大2倍
    def scale_n_times(self, times: float) -> None:
        self.set_width(self.get_width() * times)
        self.set_height(self.get_height() * times)

    # 旋转
    def rotate(self, angle: int) -> None:
        self.img = Images.rotate(self.img, angle)


# 有本地坐标的Surface (警告，子类必须实现get_left()和get_top()方法)
class SurfaceWithLocalPos:
    def __init__(self) -> None:
        self.__local_x: int = 0
        self.__local_y: int = 0

    # 获取x坐标（子类需实现）
    def get_left(self) -> int:
        EXCEPTION.fatal("get_left()", 1)

    # 获取y坐标（子类需实现）
    def get_top(self) -> int:
        EXCEPTION.fatal("get_top()", 1)

    # 获取本地坐标
    @property
    def local_x(self) -> int:
        return self.__local_x

    def get_local_x(self) -> int:
        return self.__local_x

    @property
    def local_y(self) -> int:
        return self.__local_y

    def get_local_y(self) -> int:
        return self.__local_y

    @property
    def local_pos(self) -> tuple[int, int]:
        return self.__local_x, self.__local_y

    def get_local_pos(self) -> tuple[int, int]:
        return self.__local_x, self.__local_y

    # 设置本地坐标
    def set_local_x(self, value: int_f) -> None:
        self.__local_x = int(value)

    def set_local_y(self, value: int_f) -> None:
        self.__local_y = int(value)

    def set_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.set_local_x(local_x)
        self.set_local_y(local_y)

    def locally_move_to(self, local_pos: tuple) -> None:
        self.set_local_pos(local_pos[0], local_pos[1])

    # 增加本地坐标
    def add_local_x(self, value: int_f) -> None:
        self.set_local_x(self.__local_x + value)

    def add_local_y(self, value: int_f) -> None:
        self.set_local_y(self.__local_y + value)

    def add_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.add_local_x(local_x)
        self.add_local_y(local_y)

    # 减少本地坐标
    def subtract_local_x(self, value: int_f) -> None:
        self.set_local_x(self.__local_x - value)

    def subtract_local_y(self, value: int_f) -> None:
        self.set_local_y(self.__local_y - value)

    def subtract_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.subtract_local_x(local_x)
        self.subtract_local_y(local_y)

    # 绝对的本地坐标
    @property
    def abs_x(self) -> int:
        return self.get_left() + self.__local_x

    @property
    def abs_y(self) -> int:
        return self.get_top() + self.__local_y

    @property
    def abs_pos(self) -> tuple[int, int]:
        return self.abs_x, self.abs_y

    def get_abs_pos(self) -> tuple[int, int]:
        return self.abs_x, self.abs_y


# 有本地坐标的图形接口
class AdvancedAbstractImageSurface(AbstractImageSurface, SurfaceWithLocalPos):
    def __init__(self, img: Any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = "") -> None:
        AbstractImageSurface.__init__(self, img, x, y, width, height, tag)
        SurfaceWithLocalPos.__init__(self)
        self._alpha: int = 255

    # 获取透明度
    def get_alpha(self) -> int:
        return self._alpha

    # 设置透明度
    def set_alpha(self, value: int) -> None:
        self._set_alpha(value)

    def _set_alpha(self, value: int, update_original: bool = True) -> None:
        self._alpha = Numbers.keep_int_in_range(value, 0, 255)
        if update_original is True and isinstance(self.img, ImageSurface):
            super().set_alpha(self._alpha)


# 带缓存的高级图片拟态类
class AdvancedAbstractCachingImageSurface(AdvancedAbstractImageSurface):
    def __init__(self, img: Any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = "") -> None:
        super().__init__(img, x, y, width, height, tag=tag)
        self._processed_img: Optional[ImageSurface] = None
        self._need_update: bool = True if self.get_width() >= 0 and self.get_height() >= 0 else False

    # 处理图片（子类必须实现）
    def _update_img(self) -> None:
        EXCEPTION.fatal("_update_img()", 1)

    # 更新图片
    def update_image(self, img_path: PoI, ifConvertAlpha: bool = True) -> None:
        super().update_image(img_path, ifConvertAlpha)
        self._need_update = True

    # 设置透明度
    def set_alpha(self, value: int) -> None:
        self._set_alpha(value, False)
        if self._processed_img is not None:
            self._processed_img.set_alpha(self.get_alpha())

    # 宽度
    def set_width(self, value: int_f) -> None:
        _value: int = int(value)
        if _value != self.get_width():
            super().set_width(value)
            self._need_update = True

    # 高度
    def set_height(self, value: int_f) -> None:
        _value: int = int(value)
        if _value != self.get_height():
            super().set_height(value)
            self._need_update = True

    # 是否被鼠标触碰
    def is_hovered(self, off_set: Optional[tuple[int, int]] = None) -> bool:
        if self._processed_img is not None:
            _x: int = self.x + self.local_x
            _y: int = self.y + self.local_y
            if off_set is not None:
                _x += off_set[0]
                _y += off_set[1]
            return Controller.mouse.is_in_rect(_x, _y, self._processed_img.get_width(), self._processed_img.get_height())
        else:
            return False

    # 加暗度
    def add_darkness(self, value: int) -> None:
        self.img = Images.add_darkness(self.img, value)
        self._need_update = True

    # 减暗度
    def subtract_darkness(self, value: int) -> None:
        self.img = Images.subtract_darkness(self.img, value)
        self._need_update = True

    # 旋转
    def rotate(self, angle: int) -> None:
        # 旋转图片
        super().rotate(angle)
        self._need_update = True

    # 反转原图
    def flip_original_img(self, horizontal: bool = True, vertical: bool = False) -> None:
        self.img = Images.flip(self.img, horizontal, vertical)
        self._need_update = True

    # 画出轮廓
    def draw_outline(
        self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN, color: color_liked = "red", line_width: int = 2
    ) -> None:
        if self._need_update is True:
            self._update_img()
        if self._processed_img is not None:
            Draw.rect(
                _surface, Colors.get(color), (Coordinates.add(self.abs_pos, offSet), self._processed_img.get_size()), line_width
            )
        else:
            EXCEPTION.fatal("The image has not been correctly processed.")

    # 展示
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        if self.is_visible():
            # 如果图片需要更新，则先更新
            if self._need_update is True:
                self._update_img()
            # 将已经处理好的图片画在给定的图层上
            if self._processed_img is not None:
                _surface.blit(self._processed_img, Coordinates.add(self.abs_pos, offSet))
            else:
                EXCEPTION.fatal("The image has not been correctly processed.")
