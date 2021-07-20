from .system import *

# 坐标类
class Coordinate:
    def __init__(self, x: int_f, y: int_f):
        self.x = int(x)
        self.y = int(y)

    def __lt__(self, other: object) -> bool:
        return self.y + self.x < other.y + other.x

    # 坐标信息
    @property
    def pos(self) -> tuple[int]:
        return int(self.x), int(self.y)

    def get_pos(self) -> tuple[int]:
        return int(self.x), int(self.y)

    def set_pos(self, x: int_f, y: int_f) -> None:
        self.x = int(x)
        self.y = int(y)

    # 检测是否在给定的位置上
    def on_pos(self, pos: any) -> bool:
        return Pos.is_same(self.pos, pos)


# 游戏对象接口
class GameObject(Coordinate):
    def __init__(self, x: int_f, y: int_f):
        super().__init__(x, y)

    # 左侧位置
    @property
    def left(self) -> int:
        return int(self.x)

    def get_left(self) -> int:
        return int(self.x)

    def set_left(self, value: int_f) -> None:
        self.x = int(value)

    # 上方位置
    @property
    def top(self) -> int:
        return int(self.y)

    def get_top(self) -> int:
        return int(self.y)

    def set_top(self, value: int_f) -> None:
        self.y = int(value)


# 2d游戏对象接口
class GameObject2d(GameObject):
    def __init__(self, x: int_f, y: int_f):
        super().__init__(x, y)

    # 宽
    @property
    def width(self) -> int:
        return self.get_width()

    def get_width(self) -> int:
        EXCEPTION.fatal("The child class has to implement get_width() function!")

    # 高
    @property
    def height(self) -> int:
        return self.get_height()

    def get_height(self) -> int:
        EXCEPTION.fatal("The child class has to implement get_height() function!")

    # 尺寸
    @property
    def size(self) -> tuple[int]:
        return self.get_width(), self.get_height()

    def get_size(self) -> tuple[int]:
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
    def center(self) -> tuple[int]:
        return self.centerx, self.centery

    def get_center(self) -> tuple[int]:
        return self.centerx, self.centery

    def set_center(self, centerx: number, centery: number) -> None:
        self.set_centerx(centerx)
        self.set_centery(centery)

    # 是否被鼠标触碰
    def is_hover(self, mouse_pos: pos_liked = NoPos) -> bool:
        if mouse_pos is NoPos:
            mouse_pos = Controller.mouse.pos
        return 0 < mouse_pos[0] - self.x < self.get_width() and 0 < mouse_pos[1] - self.y < self.get_height()

    # 将图片直接画到surface上
    def draw(self, surface: ImageSurface) -> None:
        self.display(surface)

    # 将图片直接画到屏幕上
    def draw_on_screen(self) -> None:
        self.display(Display.window)

    # 根据offSet将图片展示到surface的对应位置上 - 子类必须实现
    def display(self, surface: ImageSurface, offSet: pos_liked = Pos.ORIGIN) -> None:
        EXCEPTION.fatal("The child class does not implement display() function!")

    # 根据offSet将图片展示到屏幕的对应位置上
    def display_on_screen(self, offSet: pos_liked = Pos.ORIGIN) -> None:
        self.display(Display.window, offSet)

    # 忽略现有坐标，将图片画到surface的指定位置上
    def blit(self, surface: ImageSurface, pos: pos_liked) -> None:
        old_pos = self.get_pos()
        self.set_pos(pos[0], pos[1])
        self.draw(surface)
        self.set_pos(old_pos[0], old_pos[1])

    # 忽略现有坐标，将图片画到surface的指定位置上
    def blit_on_screen(self, pos: pos_liked) -> None:
        old_pos = self.get_pos()
        self.set_pos(pos[0], pos[1])
        self.draw(Display.window)
        self.set_pos(old_pos[0], old_pos[1])


# 2.5d游戏对象接口 - 使用z轴判断图案的图层
class GameObject2point5d(GameObject):
    def __init__(self, x: int_f, y: int_f, z: int_f):
        super().__init__(x, y)
        self.z = int(z)

    def __lt__(self, other: object) -> bool:
        if self.z != other.z:
            return self.z < other.z
        else:
            return self.y + self.x < other.y + other.x

    # 获取坐标
    @property
    def pos(self) -> tuple:
        return self.x, self.y, self.z

    def get_pos(self) -> tuple:
        return self.x, self.y, self.z

    # 设置坐标
    def set_pos(self, x: int_f, y: int_f, z: int_f = None) -> None:
        super().set_pos(x, y)
        if z is not None:
            self.z = int(z)


# 需要被打印的物品
class ItemNeedBlit(GameObject2point5d):
    def __init__(self, image: object, weight: number, pos: pos_liked, offSet: pos_liked):
        super().__init__(pos[0], pos[1], weight)
        self.image = image
        self.offSet = offSet

    def draw(self, surface: ImageSurface) -> None:
        if isinstance(self.image, pygame.Surface):
            surface.blit(self.image, Pos.add(self.pos, self.offSet))
        else:
            try:
                self.image.display(surface, self.offSet)
            except Exception:
                self.image.draw(surface)
