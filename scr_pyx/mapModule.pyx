# cython: language_level=3
from ..scr_core.function import *

#地图场景模块
class EnvImagesManagement:
    def __init__(self,theMap,decorationData,bgImgName,blockSize,darkMode,darkness=150):
        self.__ENV_IMAGE_DICT = {}
        self.__ENV_IMAGE_DICT_DARK = None if not darkMode else {}
        self.__DECORATION_IMAGE_DICT = {}
        self.__DECORATION_IMAGE_DICT_DARK = None if not darkMode else {}
        self.__BACKGROUND_IMAGE = pygame.image.load("Assets/image/dialog_background/{}".format(bgImgName)).convert() if bgImgName != None else None
        self.__BACKGROUND_SURFACE = None
        self.__MAP_SURFACE = None
        self.__BLOCK_WIDTH = round(blockSize[0])
        self.__BLOCK_HEIGHT =  round(blockSize[1])
        self.__DARKNESS = darkness if darkMode else None
        cdef int x,y
        cdef list all_images_needed = []
        for y in range(len(theMap)):
            for x in range(len(theMap[y])):
                if theMap[y][x].name not in all_images_needed:
                    all_images_needed.append(theMap[y][x].name)
        #加载图片
        for fileName in all_images_needed:
            self.__add_evn_image(fileName)
        for decoration in decorationData:
            self.__add_decoration_image(decoration.type,decoration.image)
    #加载环境图片
    def __add_evn_image(self,fileName):
        self.__ENV_IMAGE_DICT[fileName] = SrcalphaSurface("Assets/image/environment/block/"+fileName+".png",0,0)
        self.__ENV_IMAGE_DICT[fileName].set_width_with_size_locked(self.__BLOCK_WIDTH)
        #如果是夜战模式
        if self.__ENV_IMAGE_DICT_DARK != None:
            self.__ENV_IMAGE_DICT_DARK[fileName] = self.__ENV_IMAGE_DICT[fileName].copy()
            self.__ENV_IMAGE_DICT_DARK[fileName].addDarkness(self.__DARKNESS)
    #加载场景装饰物图片
    def __add_decoration_image(self,decorationType,fileName):
        if decorationType != "campfire":
            if decorationType not in self.__DECORATION_IMAGE_DICT:
                self.__DECORATION_IMAGE_DICT[decorationType] = {}
            self.__DECORATION_IMAGE_DICT[decorationType][fileName] = SrcalphaSurface("Assets/image/environment/decoration/"+fileName+".png",0,0)
            #如果是夜战模式
            if self.__DECORATION_IMAGE_DICT_DARK != None:
                if decorationType not in self.__DECORATION_IMAGE_DICT_DARK:
                    self.__DECORATION_IMAGE_DICT_DARK[decorationType] = {}
                self.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName] = self.__DECORATION_IMAGE_DICT[decorationType][fileName].copy()
                self.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName].addDarkness(self.__DARKNESS)
        #--篝火--
        elif "campfire" not in self.__DECORATION_IMAGE_DICT:
            self.__DECORATION_IMAGE_DICT["campfire"] = [SrcalphaSurface("Assets/image/environment/campfire/{}.png".format(i),0,0) for i in range(1,12)]
            if self.__DECORATION_IMAGE_DICT_DARK != None:
                self.__DECORATION_IMAGE_DICT_DARK["campfire"] = {}
                self.__DECORATION_IMAGE_DICT_DARK["campfire"]["campfire"] = self.__DECORATION_IMAGE_DICT["campfire"][-1].copy()
                self.__DECORATION_IMAGE_DICT_DARK["campfire"]["campfire"].addDarkness(self.__DARKNESS)
    def get_block_width(self):
        return self.__BLOCK_WIDTH
    def get_block_height(self):
        return self.__BLOCK_HEIGHT
    def resize(self,newWidth,newHeight):
        self.__BLOCK_WIDTH = round(newWidth)
        self.__BLOCK_HEIGHT = round(newHeight)
        for key in self.__ENV_IMAGE_DICT:
            self.__ENV_IMAGE_DICT[key].set_width_with_size_locked(self.__BLOCK_WIDTH)
        if self.__ENV_IMAGE_DICT_DARK != None:
            for key in self.__ENV_IMAGE_DICT_DARK:
                self.__ENV_IMAGE_DICT_DARK[key].set_width_with_size_locked(self.__BLOCK_WIDTH)
    def get_env_image(self,key,darkMode):
        try:
            if darkMode:
                return self.__ENV_IMAGE_DICT_DARK[key]
            else:
                return self.__ENV_IMAGE_DICT[key]
        except BaseException:
            print('LinpgEngine-Warning: Cannot find block image "{}", we will try to load it for you right now, but please by aware.'.format(key))
            self.__add_evn_image(key)
    def get_decoration_image(self,decorationType,key,darkMode):
        try:
            if darkMode:
                return self.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
            else:
                return self.__DECORATION_IMAGE_DICT[decorationType][key]
        #如果图片没找到
        except BaseException:
            print('LinpgEngine-Warning: Cannot find decoration image "{0}" in type "{1}", we will try to load it for you right now, but please by aware.'.format(key,decorationType))
            self.__add_decoration_image(decorationType,key)
    #获取当前装饰物种类的数量
    def get_decoration_num(self,decorationType):
        return len(self.__DECORATION_IMAGE_DICT[decorationType])
    def new_surface(self,screen_size,map_size):
        if self.__BACKGROUND_IMAGE != None:
            self.__BACKGROUND_SURFACE = resizeImg(self.__BACKGROUND_IMAGE,screen_size)
        else:
            self.__BACKGROUND_SURFACE = pygame.Surface(screen_size).convert()
        if self.__MAP_SURFACE != None:
            self.__MAP_SURFACE.fill((0,0,0,0))
        else:
            self.__MAP_SURFACE = pygame.Surface(map_size,flags=pygame.SRCALPHA).convert_alpha()
    def get_surface(self):
        return self.__MAP_SURFACE
    def display_background_surface(self,screen,pos):
        screen.blit(self.__BACKGROUND_SURFACE,(0,0))
        screen.blit(self.__MAP_SURFACE,pos)

#方块类
class BlockObject:
    def __init__(self,name,canPassThrough):
        self.name = name
        self.canPassThrough = canPassThrough
    def update(self,name,canPassThrough):
        self.name = name
        self.canPassThrough = canPassThrough

#点
class Point(GameObject):
    def __init__(self,x,y):
        GameObject.__init__(self,x,y)
        self.x = x
        self.y = y
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

#管理场景装饰物的类
class DecorationObject(GameObject):
    def  __init__(self,x,y,itemType,image):
        GameObject.__init__(self,x,y)
        self.type = itemType
        self.image = image
        self.alpha = None
        self.triggered = True
    def is_on_pos(self,pos):
        return is_same_pos(self.get_pos(),pos)
    def switch(self):
        self.triggered = not self.triggered

#描述AStar算法中的节点数据
class Node:
    def __init__(self,point,endPoint,g=0):
        self.point = point  # 自己的坐标
        self.father = None  # 父节点
        self.g = g  # g值，g值在用到的时候会重新算
        self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值