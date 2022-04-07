from .interface import *

# 坐标类
class Coordinate:
    def __init__(self, x: int_f, y: int_f):
        self.x: int = int(x)
        self.y: int = int(y)

    def __lt__(self, other: "Coordinate") -> bool:
        return self.y + self.x < other.y + other.x

    # x轴坐标
    @property
    def left(self) -> int:
        return self.x

    def get_left(self) -> int:
        return self.x

    def set_left(self, value: int_f) -> None:
        self.x = int(value)

    # 向左移动
    def move_left(self, value: int_f) -> None:
        self.set_left(self.x - int(value))

    # 向右移动
    def move_right(self, value: int_f) -> None:
        self.set_left(self.x + int(value))

    # y轴坐标
    @property
    def top(self) -> int:
        return self.y

    def get_top(self) -> int:
        return self.y

    def set_top(self, value: int_f) -> None:
        self.y = int(value)

    # 向上移动
    def move_upward(self, value: int_f) -> None:
        self.set_top(self.y - int(value))

    # 向下移动
    def move_downward(self, value: int_f) -> None:
        self.set_top(self.y + int(value))

    # 坐标信息
    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y

    def get_pos(self) -> tuple[int, int]:
        return self.x, self.y

    # 设置坐标
    def set_pos(self, _x: int_f, _y: int_f) -> None:
        self.set_left(_x)
        self.set_top(_y)

    def move_to(self, pos: tuple) -> None:
        self.set_pos(pos[0], pos[1])

    # 检测是否在给定的位置上
    def on_pos(self, pos: object) -> bool:
        return Coordinates.is_same(self.pos, pos)


# 坐标类 - 更精准坐标
class Position:
    def __init__(self, x: number, y: number):
        # 坐标（注意，与Coordinate不同，Position坐标使用浮点数）
        self.x: number = x
        self.y: number = y

    def __lt__(self, other: "Position") -> bool:
        return self.y + self.x < other.y + other.x

    # 坐标信息
    @property
    def pos(self) -> tuple:
        return self.x, self.y

    def get_pos(self) -> tuple:
        return self.x, self.y

    # 设置坐标
    def set_pos(self, x: number, y: number) -> None:
        self.x = x if isinstance(x, int) else round(x, 5)
        self.y = y if isinstance(y, int) else round(y, 5)

    def move_to(self, pos: tuple) -> None:
        self.set_pos(pos[0], pos[1])


# 2d游戏对象接口
class GameObject2d(Coordinate):
    def __init__(self, x: int_f, y: int_f):
        super().__init__(x, y)
        self.tag: str = ""

    # 宽
    @property
    def width(self) -> int:
        return self.get_width()

    def get_width(self) -> int:
        EXCEPTION.fatal("get_width()", 1)

    # 高
    @property
    def height(self) -> int:
        return self.get_height()

    def get_height(self) -> int:
        EXCEPTION.fatal("get_height()", 1)

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
        self.x = int(centerx - self.get_width() / 2)

    @property
    def centery(self) -> int:
        return self.y + self.get_height() // 2

    def get_centery(self) -> int:
        return self.y + self.get_height() // 2

    def set_centery(self, centery: int_f) -> None:
        self.y = int(centery - self.get_height() / 2)

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
    def is_hovered(self, off_set: tuple[int, int] = NoPos) -> bool:
        mouse_pos: tuple[int, int] = (
            Controller.mouse.pos if off_set is NoPos else Coordinates.subtract(Controller.mouse.pos, off_set)
        )
        return 0 < mouse_pos[0] - self.x < self.get_width() and 0 < mouse_pos[1] - self.y < self.get_height()

    # 检测自身是否覆盖了另一个2d游戏对象
    def is_overlapped_with(self, _rect: "GameObject2d") -> bool:
        return max(self.left, _rect.left) < min(self.right, _rect.right) and max(self.top, _rect.top) < min(
            self.bottom, _rect.bottom
        )

    # 将图片直接画到surface上
    def draw(self, surface: ImageSurface) -> None:
        self.display(surface)

    # 将图片直接画到屏幕上
    def draw_on_screen(self) -> None:
        self.display(Display.get_window())

    # 根据offSet将图片展示到surface的对应位置上 - 子类必须实现
    def display(self, surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        EXCEPTION.fatal("display()", 1)

    # 根据offSet将图片展示到屏幕的对应位置上
    def display_on_screen(self, offSet: tuple[int, int] = ORIGIN) -> None:
        self.display(Display.get_window(), offSet)

    # 忽略现有坐标，将图片画到surface的指定位置上
    def blit(self, surface: ImageSurface, pos: tuple[int, int]) -> None:
        old_pos = self.get_pos()
        self.move_to(pos)
        self.draw(surface)
        self.move_to(old_pos)

    # 忽略现有坐标，将图片画到surface的指定位置上
    def blit_on_screen(self, pos: tuple[int, int]) -> None:
        old_pos = self.get_pos()
        self.move_to(pos)
        self.draw(Display.get_window())
        self.move_to(old_pos)


# 2.5d游戏对象接口 - 使用z轴判断图案的图层
class GameObject2point5d(Coordinate):
    def __init__(self, x: int_f, y: int_f, z: int_f):
        super().__init__(x, y)
        self.z: int = int(z)

    def __lt__(self, other: "GameObject2point5d") -> bool:  # type: ignore[override]
        if self.z != other.z:
            return self.z < other.z
        else:
            return self.y + self.x < other.y + other.x

    # 获取坐标
    @property
    def pos(self) -> tuple[int, int, int]:  # type: ignore[override]
        return self.x, self.y, self.z

    def get_pos(self) -> tuple[int, int, int]:  # type: ignore[override]
        return self.x, self.y, self.z

    # 设置坐标
    def set_pos(self, x: int_f, y: int_f, z: int_f = None) -> None:
        super().set_pos(x, y)
        if z is not None:
            self.z = int(z)
