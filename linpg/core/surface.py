from .shape import *

# 图形接口
class AbstractImageSurface(Rect):
    def __init__(self, img: any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str):
        super().__init__(x, y, width, height)
        self.img: any = img
        self.hidden: bool = False
        self.tag: str = str(tag)
        # 确保长宽均已输入且为正整数
        if self._width < 0 and self._height < 0:
            self._width, self._height = self.img.get_size()
        elif self._width < 0 and self._height >= 0:
            self.set_width(self._height / self.img.get_height() * self.img.get_width())
        elif self._width >= 0 and self._height < 0:
            self.set_height(self._width / self.img.get_width() * self.img.get_height())

    """透明度"""

    @property
    def alpha(self) -> int:
        return self.get_alpha()

    def get_alpha(self) -> int:
        return self.img.get_alpha()

    def set_alpha(self, value: int) -> None:
        self.img.set_alpha(keep_in_range(int(value), 0, 255))

    def add_alpha(self, value: int) -> None:
        self.set_alpha(self.get_alpha() + value)

    def subtract_alpha(self, value: int) -> None:
        self.set_alpha(self.get_alpha() - value)

    # 获取图片复制品
    def get_image_copy(self) -> any:
        return self.img.copy()

    # 更新图片
    def update_image(self, img_path: PoI, ifConvertAlpha: bool = True) -> None:
        self.img = IMG.quickly_load(img_path, ifConvertAlpha)

    # 旋转
    def rotate(self, angle: int) -> None:
        self.img = IMG.rotate(self.img, angle)


# 有本地坐标的图形接口
class AdvancedAbstractImageSurface(AbstractImageSurface):
    def __init__(self, img: any, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = ""):
        super().__init__(img, x, y, width, height, tag)
        self._local_x: int = 0
        self._local_y: int = 0
        self._alpha: int = 255

    # 透明度
    def get_alpha(self) -> int:
        return self._alpha

    def set_alpha(self, value: int, update_original: bool = True) -> None:
        self._alpha = keep_in_range(int(value), 0, 255)
        if update_original is True and isinstance(self.img, ImageSurface):
            super().set_alpha(self._alpha)

    # 获取本地坐标
    @property
    def local_x(self) -> int:
        return self._local_x

    def get_local_x(self) -> int:
        return self._local_x

    @property
    def local_y(self) -> int:
        return self._local_y

    def get_local_y(self) -> int:
        return self._local_y

    @property
    def local_pos(self) -> tuple[int]:
        return self._local_x, self._local_y

    def get_local_pos(self) -> tuple[int]:
        return self._local_x, self._local_y

    # 设置本地坐标
    def set_local_x(self, value: int_f) -> None:
        self._local_x = int(value)

    def set_local_y(self, value: int_f) -> None:
        self._local_y = int(value)

    def set_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.set_local_x(local_x)
        self.set_local_y(local_y)

    # 增加本地坐标
    def add_local_x(self, value: int_f) -> None:
        self.set_local_x(self._local_x + value)

    def add_local_y(self, value: int_f) -> None:
        self.set_local_y(self._local_y + value)

    def add_local_pos(self, local_x: int_f, local_y: int_f) -> None:
        self.add_local_x(local_x)
        self.add_local_y(local_y)

    # 绝对的本地坐标
    @property
    def abs_x(self) -> int:
        return int(self.x + self._local_x)

    @property
    def abs_y(self) -> int:
        return int(self.y + self._local_y)

    @property
    def abs_pos(self) -> tuple[int]:
        return self.abs_x, self.abs_y

    def get_abs_pos(self) -> tuple[int]:
        return self.abs_x, self.abs_y


# 基础文字类
class TextSurface(AbstractImageSurface):
    def __init__(self, font_surface: ImageSurface, x: int_f, y: int_f, tag: str = ""):
        super().__init__(font_surface, x, y, -1, -1, tag)

    # 画出
    def display(self, surface: ImageSurface, offSet: tuple = Pos.ORIGIN) -> None:
        if not self.hidden:
            surface.blit(self.img, Pos.add(self.pos, offSet))


# 动态文字类
class DynamicTextSurface(TextSurface):
    def __init__(self, n: ImageSurface, b: ImageSurface, x: int_f, y: int_f):
        super().__init__(n, x, y)
        self.__big_font_surface: ImageSurface = b
        self.__is_hovered: bool = False

    # 设置透明度
    def set_alpha(self, value: int) -> None:
        super().set_alpha(value)
        self.__big_font_surface.set_alpha(value)

    # 用于检测触碰的快捷
    def has_been_hovered(self) -> bool:
        return self.__is_hovered

    # 画出
    def display(self, surface: ImageSurface, offSet: tuple = Pos.ORIGIN) -> None:
        if not self.hidden:
            self.__is_hovered = self.is_hover(Pos.subtract(Controller.mouse.pos, offSet))
            if not self.__is_hovered:
                surface.blit(self.img, Pos.add(self.pos, offSet))
            else:
                surface.blit(
                    self.__big_font_surface,
                    (
                        int(self.x - (self.__big_font_surface.get_width() - self.img.get_width()) / 2 + offSet[0]),
                        int(self.y - (self.__big_font_surface.get_height() - self.img.get_height()) / 2 + offSet[1]),
                    ),
                )
        else:
            self.__is_hovered = False
