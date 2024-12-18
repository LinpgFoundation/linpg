from .module import *


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


RectLiked = Rectangle | pygame.Rect | tuple
RectObject = Rectangle | pygame.Rect


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

    # 转换pygame的rect类至linpg引擎的rect类
    @classmethod
    def create(cls, rect: RectLiked) -> Rectangle:
        # 如果是Rect类，则没必要转换
        if isinstance(rect, Rectangle):
            return rect
        # 如果是pygame.Rect类则需转换
        elif isinstance(rect, pygame.Rect):
            return Rectangle(rect.x, rect.y, rect.width, rect.height)
        # 如果是tuple类，则需要创建
        elif isinstance(rect, tuple):
            return cls.from_tuple(rect)
        Exceptions.fatal(f'The rect has to be RectLiked object, not "{type(rect)}".')

    # 相加2个rect
    @classmethod
    def apply(cls, source_rect: RectLiked, apply_rect: RectLiked) -> Rectangle:
        source_rect = cls.__comply(source_rect)
        apply_rect = cls.__comply(apply_rect)
        return Rectangle(
            source_rect.x + apply_rect.x,
            source_rect.y + apply_rect.y,
            source_rect.width + apply_rect.width,
            source_rect.height + apply_rect.height,
        )


# 转换linpg.Rect至pygame.Rect
def convert_to_pygame_rect(rect: RectLiked) -> pygame.Rect:
    # 如果是pygame.Rect类，则没必要转换
    if isinstance(rect, pygame.Rect):
        return rect
    # 确认是linpg.Rect类再转换
    elif isinstance(rect, Rectangle):
        return pygame.Rect(rect.left, rect.top, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        match len(rect):
            case 2:
                return pygame.Rect(rect[0], rect[1])
            case 4:
                return pygame.Rect(rect[0], rect[1], rect[2], rect[3])
            case _:
                Exceptions.fatal("Invalid length for forming a rect.")
    else:
        Exceptions.fatal(f'The rect has to be RectLiked object, not "{type(rect)}".')


# 检测pygame类2d模型是否被点击
def is_hovering(imgObject: ImageSurface, objectPos: tuple[int, int] = ORIGIN) -> bool:
    return Controller.mouse.is_in_rect(objectPos[0], objectPos[1], imgObject.get_width(), imgObject.get_height())


# 获取图片的subsurface
def get_img_subsurface(img: ImageSurface, rect: RectLiked) -> ImageSurface:
    return img.subsurface(rect if isinstance(rect, pygame.Rect) else convert_to_pygame_rect(rect))
