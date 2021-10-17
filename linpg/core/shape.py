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
    def get_rect(self) -> tuple[int]:
        return self.left, self.top, self.__width, self.__width

    # 画出轮廓
    def draw_outline(
        self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN, color: str = "red", thickness: int = 2
    ) -> None:
        draw_rect(surface, color, (Pos.add(self.pos, offSet), self.size), thickness)


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
    def get_rect(self) -> tuple[int]:
        return self.x, self.y, self.get_width(), self.__height


# 新建一个形状类
def new_rect(pos: tuple, size: tuple) -> Rect:
    return Rect(pos[0], pos[1], size[0], size[1])


# 画正方形（的方块）
def draw_rect(surface: ImageSurface, color: color_liked, rect: RectLiked, thickness: int = 0) -> None:
    if isinstance(rect, (pygame.Rect, tuple)):
        pygame.draw.rect(surface, Color.get(color), rect, thickness)
    elif isinstance(rect, Rect):
        pygame.draw.rect(surface, Color.get(color), rect.get_rect(), thickness)
    else:
        EXCEPTION.fatal('You need to put in a rect liked object, and "{0}" is a "{1}".'.format(rect, type(rect)))


# 转换pygame的rect类至linpg引擎的rect类
def convert_rect(rect: RectLiked) -> Rect:
    # 确认是pygame.Rect类再转换
    if isinstance(rect, pygame.Rect):
        return Rect(rect.x, rect.y, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return new_rect(rect[0], rect[1])
        elif len(rect) == 4:
            return Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.fatal("Invalid length for forming a rect.")
    # 如果是Rect类，则没必要转换
    elif isinstance(rect, Rect):
        return rect
    else:
        EXCEPTION.fatal('The rect has to be RectLiked object, not "{}".'.format(type(rect)))


# 转换linpg.Rect至pygame.Rect
def convert_to_pygame_rect(rect: RectLiked) -> pygame.Rect:
    # 如果是pygame.Rect类，则没必要转换
    if isinstance(rect, pygame.Rect):
        return rect
    # 确认是linpg.Rect类再转换
    elif isinstance(rect, Rect):
        return pygame.Rect(rect.left, rect.top, rect.width, rect.height)
    # 如果是tuple类，则需要创建
    elif isinstance(rect, tuple):
        if len(rect) == 2:
            return pygame.Rect(rect[0], rect[1])
        elif len(rect) == 4:
            return pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            EXCEPTION.fatal("Invalid length for forming a rect.")
    else:
        EXCEPTION.fatal('The rect has to be RectLiked object, not "{}".'.format(type(rect)))


# 是否形状一样
def is_same_rect(rect1: RectLiked, rect2: RectLiked) -> bool:
    # 确保两个输入的类rect的物品都不是tuple
    if isinstance(rect1, tuple):
        convert_rect(rect1)
    if isinstance(rect2, tuple):
        convert_rect(rect2)
    # 比较并返回结果
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height


# 检测图片是否被点击
def is_hover(imgObject: object, objectPos: Iterable = Pos.ORIGIN, off_set_x: number = 0, off_set_y: number = 0) -> bool:
    # 如果是Linpg引擎的GameObject2d类(所有2d物品的父类)
    if isinstance(imgObject, GameObject2d):
        return imgObject.is_hover(Pos.subtract(Controller.mouse.pos, (off_set_x, off_set_y)))
    # 如果是pygame类
    else:
        mouse_pos: tuple[number]
        # 如果是Surface类
        if isinstance(imgObject, ImageSurface):
            mouse_pos = Pos.subtract(Controller.mouse.pos, (off_set_x, off_set_y), objectPos)
        # 如果是Rect类
        elif isinstance(imgObject, pygame.Rect):
            mouse_pos = Pos.subtract(Controller.mouse.pos, (off_set_x, off_set_y), (imgObject.x, imgObject.y))
        else:
            EXCEPTION.fatal("Unable to check current object: {0} (type:{1})".format(imgObject, type(imgObject)))
        # 返回结果
        return 0 < mouse_pos[0] < imgObject.get_width() and 0 < mouse_pos[1] < imgObject.get_height()


# 获取图片的subsurface
def get_img_subsurface(img: ImageSurface, rect: RectLiked) -> ImageSurface:
    return img.subsurface(rect if isinstance(rect, pygame.Rect) else convert_to_pygame_rect(rect))


# 圆形类
class Circle(Square):
    def __init__(self, x: int_f, y: int_f, diameter: int):
        super().__init__(x, y, diameter)

    @property
    def radius(self) -> number:
        return self.get_width() / 2

    # 画出轮廓
    def draw_outline(
        self, surface: ImageSurface, offSet: Iterable = Pos.ORIGIN, color: str = "red", thickness: int = 2
    ) -> None:
        draw_circle(surface, color, Pos.add(self.center, offSet), self.radius, thickness)


# 画圆形
def draw_circle(surface: ImageSurface, color: color_liked, center_pos: tuple, radius: int, thickness: int = 0):
    pygame.draw.circle(surface, Color.get(color), center_pos, radius, thickness)
