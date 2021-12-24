from .decoration import *

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
        self.__img_list = [
            IMG.load(imgPath)
            for imgPath in glob(os.path.join(ASSET.get_internal_environment_image_path("weather"), weather, "*.png"))
        ]
        self.__items = tuple(
            [
                Snow(
                    imgId=get_random_int(0, len(self.__img_list) - 1),
                    size=get_random_int(5, 10),
                    speed=get_random_int(1, 4),
                    x=get_random_int(1, int(Display.get_width() * 1.5)),
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
        if not self.__initialized:
            EXCEPTION.fatal("You need to initialize the weather system before using it.")
        self.__speed_unit = int(perBlockWidth / 15)
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
