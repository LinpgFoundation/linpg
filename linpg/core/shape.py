from .system import *


# 2d游戏对象接口
class GameObject2d(Coordinate):
    def __init__(self, x: int_f, y: int_f):
        super().__init__(x, y)
        self.tag: str = ""

    # 宽
    @property
    def width(self) -> int:
        return self.get_width()

    @abstractmethod
    def get_width(self) -> int:
        Exceptions.fatal("get_width()", 1)

    # 高
    @property
    def height(self) -> int:
        return self.get_height()

    @abstractmethod
    def get_height(self) -> int:
        Exceptions.fatal("get_height()", 1)

    # 尺寸
    @property
    def size(self) -> tuple[int, int]:
        return self.get_width(), self.get_height()

    def get_size(self) -> tuple[int, int]:
        return self.get_width(), self.get_height()

    # 右侧位置
    @property
    def right(self) -> int:
        return self.x + self.get_width()

    def get_right(self) -> int:
        return self.x + self.get_width()

    def set_right(self, value: int_f) -> None:
        self.set_left(value - self.get_width())

    # 底部位置
    @property
    def bottom(self) -> int:
        return self.y + self.get_height()

    def get_bottom(self) -> int:
        return self.y + self.get_height()

    def set_bottom(self, value: int_f) -> None:
        self.set_top(value - self.get_height())

    # 中心位置
    @property
    def centerx(self) -> int:
        return self.x + self.get_width() // 2

    def get_centerx(self) -> int:
        return self.x + self.get_width() // 2

    def set_centerx(self, centerx: int_f) -> None:
        self.set_left(centerx - self.get_width() / 2)

    @property
    def centery(self) -> int:
        return self.y + self.get_height() // 2

    def get_centery(self) -> int:
        return self.y + self.get_height() // 2

    def set_centery(self, centery: int_f) -> None:
        self.set_top(centery - self.get_height() / 2)

    @property
    def center(self) -> tuple[int, int]:
        return self.centerx, self.centery

    def get_center(self) -> tuple[int, int]:
        return self.centerx, self.centery

    def set_center(self, centerx: int_f, centery: int_f) -> None:
        self.set_centerx(centerx)
        self.set_centery(centery)

    @property
    def left_center(self) -> tuple[int, int]:
        return self.x, self.centery

    @property
    def right_center(self) -> tuple[int, int]:
        return self.right, self.centery

    @property
    def top_center(self) -> tuple[int, int]:
        return self.centerx, self.y

    @property
    def bottom_center(self) -> tuple[int, int]:
        return self.centerx, self.bottom

    # 是否被鼠标触碰
    def is_hovered(self, off_set: tuple[int, int] | None = None) -> bool:
        if off_set is None:
            return Controller.mouse.is_in_rect(self.x, self.y, self.get_width(), self.get_height())
        else:
            return Controller.mouse.is_in_rect(self.x + off_set[0], self.y + off_set[1], self.get_width(), self.get_height())

    # 检测自身是否覆盖了另一个2d游戏对象
    def is_overlapping_with(self, _rect: "GameObject2d") -> bool:
        return max(self.left, _rect.left) < min(self.right, _rect.right) and max(self.top, _rect.top) < min(
            self.bottom, _rect.bottom
        )

    # 将图片直接画到surface上
    def draw(self, _surface: ImageSurface) -> None:
        self.display(_surface)

    # 根据offSet将图片展示到surface的对应位置上 - 子类必须实现
    @abstractmethod
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        Exceptions.fatal("display()", 1)

    # 忽略现有坐标，将图片画到surface的指定位置上
    def render(self, _surface: ImageSurface, pos: tuple[int, int]) -> None:
        old_pos = self.get_pos()
        self.move_to(pos)
        self.draw(_surface)
        self.move_to(old_pos)


# 正方形类
class Square(GameObject2d):
    def __init__(self, x: int_f, y: int_f, width: int_f):
        super().__init__(x, y)
        self.__width: int = int(width)
        self.__min_width: int = 0
        self.__max_width: int = -1

    # 高度（应与宽度一致），子类如果是Rect必须重写
    def get_height(self) -> int:
        return self.__width

    # 宽度
    def get_width(self) -> int:
        return self.__width

    def set_width(self, value: int_f) -> None:
        new_width: int = int(value)
        if new_width > self.__min_width:
            if self.__max_width <= 0 or new_width < self.__max_width:
                self.__width = new_width
            else:
                self.__width = self.__max_width
        else:
            self.__width = self.__min_width

    # 最短宽度
    @property
    def min_width(self) -> int:
        return self.get_min_width()

    def get_min_width(self) -> int:
        return self.__min_width

    def set_min_width(self, value: int_f) -> None:
        new_width: int = int(value)
        if new_width >= 1:
            if self.__max_width <= 0 or new_width < self.__max_width:
                if self.__min_width != new_width:
                    self.__min_width = new_width
                    # 重置宽度
                    self.set_width(self.get_width())
            else:
                Exceptions.fatal(
                    f"The minimum width has to be smaller than the maximum width, which in this case is {self.__max_width}."
                )
        else:
            Exceptions.fatal("The minimum width has to be greater than 1.")

    # 最长宽度
    @property
    def max_width(self) -> int:
        return self.get_max_width()

    def get_max_width(self) -> int:
        return self.__max_width

    def set_max_width(self, value: int_f = -1) -> None:
        new_width: int = int(value)
        if new_width >= 0:
            if new_width > self.__min_width:
                self.__max_width = new_width
            else:
                Exceptions.fatal(
                    f"The maximum width has to be greater than the minimum width, which in this case is {self.__min_width}."
                )
        else:
            self.__max_width = -1
        # 重置宽度
        self.set_width(self.get_width())

    # 画出轮廓
    def draw_outline(
        self,
        _surface: ImageSurface,
        color: color_liked = "red",
        thickness: int = 2,
        radius: int = -1,
        offSet: tuple[int, int] = ORIGIN,
    ) -> None:
        Draw.rect(_surface, Colors.get(color), (Coordinates.add(self.pos, offSet), self.size), thickness, radius)

    # 画出轮廓 - 实现父类的要求
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        self.draw_outline(_surface, offSet=offSet)


# 用于兼容的长方类
class Rectangle(Square):
    def __init__(self, left: int_f, top: int_f, width: int_f, height: int_f):
        super().__init__(left, top, width)
        self.__height: int = int(height)
        self.__min_height: int = 0
        self.__max_height: int = -1

    # 高度
    def get_height(self) -> int:
        return self.__height

    def set_height(self, value: int_f) -> None:
        new_height: int = int(value)
        if new_height > self.__min_height:
            if self.__max_height <= 0 or new_height < self.__max_height:
                self.__height = new_height
            else:
                self.__height = self.__max_height
        else:
            self.__height = self.__min_height

    # 最短高度
    @property
    def min_height(self) -> int:
        return self.get_min_height()

    def get_min_height(self) -> int:
        return self.__min_height

    def set_min_height(self, value: int_f) -> None:
        new_height: int = int(value)
        if new_height >= 1:
            if self.__max_height <= 0 or new_height < self.__max_height:
                if self.__min_height != new_height:
                    self.__min_height = new_height
                    # 重置高度
                    self.set_height(self.get_height())
            else:
                Exceptions.fatal(
                    f"The minimum height has to be smaller than the maximum height, which in this case is {self.__max_height}."
                )
        else:
            Exceptions.fatal("The minimum height has to be greater than 1.")

    # 最长高度
    @property
    def max_height(self) -> int:
        return self.get_max_height()

    def get_max_height(self) -> int:
        return self.__max_height

    def set_max_height(self, value: int_f = -1) -> None:
        new_height: int = int(value)
        if new_height >= 0:
            if new_height > self.__min_height:
                self.__max_height = new_height
            else:
                Exceptions.fatal(
                    f"The maximum height has to be greater than the minimum height, which in this case is {self.__min_height}."
                )
        else:
            self.__max_height = -1
        # 重置高度
        self.set_height(self.get_height())

    # 尺寸
    def set_size(self, width: int_f, height: int_f) -> None:
        self.set_width(width)
        self.set_height(height)

    # 获取rect
    def get_rect(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.get_width(), self.__height

    def get_rectangle(self) -> "Rectangle":
        return Rectangle(self.x, self.y, self.get_width(), self.__height)


RectObject = Rectangle | Rect
RectLiked = RectObject | tuple


# Rectangle方法管理
class Rectangles:
    # 转换tuple至Rectangle
    @staticmethod
    def from_tuple(tuple_rect: tuple) -> Rectangle:
        match len(tuple_rect):
            case 2:
                return Rectangle(tuple_rect[0][0], tuple_rect[0][1], tuple_rect[1][0], tuple_rect[1][1])
            case 4:
                return Rectangle(tuple_rect[0], tuple_rect[1], tuple_rect[2], tuple_rect[3])
        Exceptions.fatal("Invalid length for forming a rect.")

    # 将tuple转换至RectObject以方便操作
    @classmethod
    def __comply(cls, rect: RectLiked) -> RectObject:
        if isinstance(rect, tuple):
            return cls.from_tuple(rect)
        return rect

    # 是否2个Rectangle形状一样
    @classmethod
    def equal(cls, rect1: RectLiked | None, rect2: RectLiked | None) -> bool:
        if rect1 is not None and rect2 is not None:
            rect1 = cls.__comply(rect1)
            rect2 = cls.__comply(rect2)
            return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height
        return rect1 == rect2

    # 转换2d库的Rect类至linpg引擎的rect类
    @classmethod
    def create(cls, rect: RectLiked) -> Rectangle:
        # 如果是Rect类，则没必要转换
        if isinstance(rect, Rectangle):
            return rect
        # 如果是2d库的Rect类则需转换
        elif isinstance(rect, Rect):
            return Rectangle(rect.x, rect.y, rect.width, rect.height)
        # 如果是tuple类，则需要创建
        elif isinstance(rect, tuple):
            return cls.from_tuple(rect)
        Exceptions.fatal(f'The rect has to be RectLiked object, not "{type(rect)}".')

    # 相加2个rect
    @classmethod
    def add(cls, source_rect: RectLiked, apply_rect: RectLiked) -> Rectangle:
        source_rect = cls.__comply(source_rect)
        apply_rect = cls.__comply(apply_rect)
        return Rectangle(
            source_rect.x + apply_rect.x,
            source_rect.y + apply_rect.y,
            source_rect.width + apply_rect.width,
            source_rect.height + apply_rect.height,
        )
