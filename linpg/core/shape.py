from .module import *

RectLiked = Union[Rect, pygame.Rect, tuple]

# 正方形类
class Square(GameObject2d):
    def __init__(self, x: int_f, y: int_f, width: int):
        super().__init__(x, y)
        self.__width: int = int(width)
        self.__min_width: int = 1
        self.__max_width: int = -1

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
                EXCEPTION.fatal(
                    "The minimum width has to be smaller than the maximum width, which in this case is {}.".format(
                        self.__max_width
                    )
                )
        else:
            EXCEPTION.fatal("The minimum width has to be greater than 1.")

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
                EXCEPTION.fatal(
                    "The maximum width has to be greater than the minimum width, which in this case is {}.".format(
                        self.__min_width
                    )
                )
        else:
            self.__max_width = -1
        # 重置宽度
        self.set_width(self.get_width())

    # 获取rect
    def get_rect(self) -> tuple[int, int, int, int]:
        return self.left, self.top, self.__width, self.__width

    # 根据给与的rect画出轮廓（static method）
    @staticmethod
    def draw_(surface: ImageSurface, color: tuple, rect: tuple, thickness: int) -> None:
        pygame.draw.rect(surface, color, rect, thickness)

    # 画出轮廓
    def draw_outline(self, surface: ImageSurface, offSet: Iterable = ORIGIN, color: str = "red", thickness: int = 2) -> None:
        self.draw_(surface, Color.get(color), (Coordinates.add(self.pos, offSet), self.size), thickness)


# 用于兼容的长方类
class Rect(Square):
    def __init__(self, left: int_f, top: int_f, width: int, height: int):
        super().__init__(left, top, width)
        self.__height: int = int(height)
        self.__min_height: int = 1
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
                EXCEPTION.fatal(
                    "The minimum height has to be smaller than the maximum height, which in this case is {}.".format(
                        self.__max_height
                    )
                )
        else:
            EXCEPTION.fatal("The minimum height has to be greater than 1.")

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
                EXCEPTION.fatal(
                    "The maximum height has to be greater than the minimum height, which in this case is {}.".format(
                        self.__min_height
                    )
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


# 圆形类
class Circle(Square):
    def __init__(self, x: int_f, y: int_f, diameter: int):
        super().__init__(x, y, diameter)

    @property
    def radius(self) -> number:
        return self.get_width() / 2

    # 根据给与的中心点画出一个圆（static method）
    @staticmethod
    def draw_(surface: ImageSurface, color: tuple, center_pos: tuple, radius: int, thickness: int) -> None:
        pygame.draw.circle(surface, color, center_pos, radius, thickness)

    # 画出轮廓
    def draw_outline(self, surface: ImageSurface, offSet: Iterable = ORIGIN, color: str = "red", thickness: int = 2) -> None:
        self.draw_(surface, Color.get(color), Coordinates.add(self.center, offSet), self.radius, thickness)
