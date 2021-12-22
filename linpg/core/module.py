from .interface import *

# 坐标类
class Coordinate:
    def __init__(self, x: int_f, y: int_f):
        self.x: int = int(x)
        self.y: int = int(y)

    def __lt__(self, other: "Coordinate") -> bool:
        return self.y + self.x < other.y + other.x

    # 坐标信息
    @property
    def pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def get_pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    # 设置坐标
    def set_pos(self, x: int_f, y: int_f) -> None:
        self.x = int(x)
        self.y = int(y)

    def move_to(self, pos: tuple) -> None:
        self.set_pos(pos[0], pos[1])

    # 检测是否在给定的位置上
    def on_pos(self, pos: Any) -> bool:
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


# 游戏对象接口
class GameObject(Coordinate):
    # 左侧位置
    @property
    def left(self) -> int:
        return int(self.x)

    def get_left(self) -> int:
        return int(self.x)

    def set_left(self, value: int_f) -> None:
        self.x = int(value)

    def move_left(self, value: int_f) -> None:
        self.x -= int(value)

    def move_right(self, value: int_f) -> None:
        self.x += int(value)

    # 上方位置
    @property
    def top(self) -> int:
        return int(self.y)

    def get_top(self) -> int:
        return int(self.y)

    def set_top(self, value: int_f) -> None:
        self.y = int(value)

    def move_upward(self, value: int_f) -> None:
        self.y -= int(value)

    def move_downward(self, value: int_f) -> None:
        self.y += int(value)


# 2d游戏对象接口
class GameObject2d(GameObject):
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
        return int(self.x + self.get_width())

    def get_right(self) -> int:
        return int(self.x + self.get_width())

    def set_right(self, value: number) -> None:
        self.x = int(value - self.get_width())

    # 底部位置
    @property
    def bottom(self) -> int:
        return int(self.y + self.get_height())

    def get_bottom(self) -> int:
        return int(self.y + self.get_height())

    def set_bottom(self, value: number) -> None:
        self.y = int(value - self.get_height())

    # 中心位置
    @property
    def centerx(self) -> int:
        return int(self.x + self.get_width() / 2)

    def get_centerx(self) -> int:
        return int(self.x + self.get_width() / 2)

    def set_centerx(self, centerx: number) -> None:
        self.x = int(centerx - self.get_width() / 2)

    @property
    def centery(self) -> int:
        return int(self.y + self.get_height() / 2)

    def get_centery(self) -> int:
        return int(self.y + self.get_height() / 2)

    def set_centery(self, centery: number) -> None:
        self.y = int(centery - self.get_height() / 2)

    @property
    def center(self) -> tuple[int, int]:
        return self.centerx, self.centery

    def get_center(self) -> tuple[int, int]:
        return self.centerx, self.centery

    def set_center(self, centerx: number, centery: number) -> None:
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
    def is_hovered(self, off_set: tuple = NoPos) -> bool:
        mouse_pos: tuple[int, int] = (
            Controller.mouse.pos if off_set is NoPos else Coordinates.subtract(Controller.mouse.pos, off_set)
        )
        return 0 < mouse_pos[0] - self.x < self.get_width() and 0 < mouse_pos[1] - self.y < self.get_height()

    # 将图片直接画到surface上
    def draw(self, surface: ImageSurface) -> None:
        self.display(surface)

    # 将图片直接画到屏幕上
    def draw_on_screen(self) -> None:
        self.display(Display.window)

    # 根据offSet将图片展示到surface的对应位置上 - 子类必须实现
    def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
        EXCEPTION.fatal("display()", 1)

    # 根据offSet将图片展示到屏幕的对应位置上
    def display_on_screen(self, offSet: tuple = ORIGIN) -> None:
        self.display(Display.window, offSet)

    # 忽略现有坐标，将图片画到surface的指定位置上
    def blit(self, surface: ImageSurface, pos: tuple) -> None:
        old_pos = self.get_pos()
        self.move_to(pos)
        self.draw(surface)
        self.move_to(old_pos)

    # 忽略现有坐标，将图片画到surface的指定位置上
    def blit_on_screen(self, pos: tuple) -> None:
        old_pos = self.get_pos()
        self.move_to(pos)
        self.draw(Display.window)
        self.move_to(old_pos)


# 2.5d游戏对象接口 - 使用z轴判断图案的图层
class GameObject2point5d(GameObject):
    def __init__(self, x: int_f, y: int_f, z: int_f):
        super().__init__(x, y)
        self.z: int = int(z)

    def __lt__(self, other: "GameObject2point5d") -> bool:
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


# 需要被打印的物品
class ItemNeedBlit(GameObject2point5d):
    def __init__(self, image: object, weight: number, pos: tuple, offSet: tuple):
        super().__init__(pos[0], pos[1], weight)
        self.image = image
        self.offSet = offSet

    def draw(self, surface: ImageSurface) -> None:
        if isinstance(self.image, ImageSurface):
            surface.blit(self.image, Coordinates.add(self.pos, self.offSet))
        else:
            try:
                self.image.display(surface, self.offSet)
            except Exception:
                self.image.draw(surface)
