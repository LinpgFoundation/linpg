from .decoration import *

# 方块类
class BlockObject:
    def __init__(self, name: str, canPassThrough: bool):
        self.name: str = name
        self.canPassThrough: bool = canPassThrough

    def update(self, name: str, canPassThrough: bool):
        self.name = name
        self.canPassThrough = canPassThrough


# 点
class Point(GameObject):
    def __eq__(self, other: object) -> bool:
        return self.x == other.x and self.y == other.y


# 描述AStar算法中的节点数据
class Node:
    def __init__(self, point: Point, endPoint: Point, g: number = 0):
        self.point = point  # 自己的坐标
        self.father = None  # 父节点
        self.g = g  # g值，g值在用到的时候会重新算
        self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值


# 天气系统
class WeatherSystem:
    def __init__(self):
        self.__initialized: bool = False
        self.__items: tuple = tuple()
        self.__img_list: list = []
        self.__speed_unit: int = 0

    # 初始化
    def init(self, weather: str, entityNum: int = 50) -> None:
        self.__initialized = True
        self.name = 0
        self.__img_list = [
            IMG.load(imgPath)
            for imgPath in glob(os.path.join(ASSET.get_internal_environment_image_path("weather"), weather, "*.png"))
        ]
        i: int
        self.__items = tuple(
            [
                Snow(
                    imgId=get_random_int(0, len(self.__img_list) - 1),
                    size=get_random_int(5, 10),
                    speed=get_random_int(1, 4),
                    x=get_random_int(1, Display.get_width() * 1.5),
                    y=get_random_int(1, Display.get_height()),
                )
                for i in range(entityNum)
            ]
        )

    # 查看初始化状态
    def get_init(self) -> bool:
        return self.__initialized

    # 画出
    def draw(self, surface: ImageSurface, perBlockWidth: number) -> None:
        try:
            assert self.__initialized is True
        except AssertionError:
            EXCEPTION.fatal("You need to initialize the weather system before using it.")
        self.__speed_unit: int = int(perBlockWidth / 15)
        for item in self.__items:
            if 0 <= item.x < surface.get_width() and 0 <= item.y < surface.get_height():
                surface.blit(
                    IMG.resize(self.__img_list[item.imgId], (perBlockWidth / item.size, perBlockWidth / item.size)), item.pos
                )
            item.move(self.__speed_unit)
            if item.x <= 0 or item.y >= surface.get_height():
                item.y = get_random_int(-50, 0)
                item.x = get_random_int(0, surface.get_width() * 2)


# 雪花片
class Snow(GameObject):
    def __init__(self, imgId: int, size: int, speed: int, x: int, y: int):
        super().__init__(x, y)
        self.imgId: int = imgId
        self.size: int = size
        self.speed: int = speed

    def move(self, speed_unit: int) -> None:
        self.x -= self.speed * speed_unit
        self.y += self.speed * speed_unit
