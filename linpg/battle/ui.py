# cython: language_level=3
from .character import *

#环境系统
class WeatherSystem:
    def  __init__(self, weather:str, window_x:int, window_y:int, entityNum:int=50):
        self.name = 0
        self.img_list = [load_img(imgPath) for imgPath in glob(os.path.join("Assets/image/environment",weather,"*.png"))]
        self.__items:tuple = tuple([Snow(
                imgId = get_random_int(0,len(self.img_list)-1),
                size = get_random_int(5,10),
                speed = get_random_int(1,4),
                x = get_random_int(1,window_x*1.5),
                y = get_random_int(1,window_y)
                ) for i in range(entityNum)])
    def draw(self, surface:ImageSurface, perBlockWidth:Union[int,float]) -> None:
        speed_unit:int = int(perBlockWidth/15)
        for item in self.__items:
            if 0 <= item.x < surface.get_width() and 0 <= item.y < surface.get_height():
                surface.blit(resize_img(self.img_list[item.imgId],(perBlockWidth/item.size,perBlockWidth/item.size)),item.pos)
            item.move(speed_unit)
            if item.x <= 0 or item.y >= surface.get_height():
                item.y = get_random_int(-50,0)
                item.x = get_random_int(0,surface.get_width()*2)

#雪花片
class Snow(GameObject):
    def  __init__(self, imgId:int, size:int, speed:int, x:int, y:int):
        super().__init__(x,y)
        self.imgId:int = imgId
        self.size:int = size
        self.speed:int = speed
    def move(self, speed_unit:int) -> None:
        self.x -= self.speed*speed_unit
        self.y += self.speed*speed_unit