# cython: language_level=3
from ..basic import addDarkness, loadImg, resizeImg, GameObject, convert_pos, is_same_pos
import pygame

#地图场景模块
class EnvImagesManagement:
    def __init__(self,theMap,decorationData,bgImgName,blockSize,darkMode,darkness=150):
        self.__ENV_IMAGE_DICT_ORIGINAL = {}
        self.__ENV_IMAGE_DICT_ORIGINAL_DARK = None
        self.__ENV_IMAGE_DICT = {}
        self.__ENV_IMAGE_DICT_DARK = None
        self.__DECORATION_IMAGE_DICT = {}
        self.__DECORATION_IMAGE_DICT_DARK = None
        self.__BACKGROUND_IMAGE = loadImg("Assets/image/dialog_background/{}".format(bgImgName),ifConvertAlpha=False).convert() if bgImgName != None else None
        self.__BACKGROUND_SURFACE = None
        self.__MAP_SURFACE = None
        self.__BLOCK_WIDTH = round(blockSize[0])
        self.__BLOCK_HEIGHT =  round(blockSize[1])
        cdef list all_images_needed = []
        for y in range(len(theMap)):
            for x in range(len(theMap[y])):
                if theMap[y][x].name not in all_images_needed:
                    all_images_needed.append(theMap[y][x].name)
        #加载背景图片
        for fileName in all_images_needed:
            try:
                self.__ENV_IMAGE_DICT_ORIGINAL[fileName] = loadImg("Assets/image/environment/block/"+fileName+".png")
                self.__ENV_IMAGE_DICT[fileName] = resizeImg(self.__ENV_IMAGE_DICT_ORIGINAL[fileName],(self.__BLOCK_WIDTH,None))
            except BaseException:
                raise Exception('LinpgEngine-Error: An map-block called '+fileName+' cannot find its image in the folder.')
        #加载场地设施的图片
        for decoration in decorationData:
            #--篝火--
            if decoration.type == "campfire":
                if "campfire" not in self.__DECORATION_IMAGE_DICT:
                    self.__DECORATION_IMAGE_DICT["campfire"] = [loadImg("Assets/image/environment/campfire/{}.png".format(i)) for i in range(1,12)]
            elif decoration.type not in self.__DECORATION_IMAGE_DICT:
                self.__DECORATION_IMAGE_DICT[decoration.type] = {}
                self.__DECORATION_IMAGE_DICT[decoration.type][decoration.image] = loadImg("Assets/image/environment/decoration/"+decoration.image+".png")
            elif decoration.image not in self.__DECORATION_IMAGE_DICT[decoration.type]:
                self.__DECORATION_IMAGE_DICT[decoration.type][decoration.image] = loadImg("Assets/image/environment/decoration/"+decoration.image+".png")
        #如果是夜战模式
        if darkMode:
            self.__ENV_IMAGE_DICT_ORIGINAL_DARK = {}
            for img,value in self.__ENV_IMAGE_DICT_ORIGINAL.items():
                self.__ENV_IMAGE_DICT_ORIGINAL_DARK[img] = addDarkness(value,darkness)
            self.__ENV_IMAGE_DICT_DARK = {}
            for img,value in self.__ENV_IMAGE_DICT.items():
                self.__ENV_IMAGE_DICT_DARK[img] = addDarkness(value,darkness)
            self.__DECORATION_IMAGE_DICT_DARK = {}
            for key,value in self.__DECORATION_IMAGE_DICT.items():
                if key != "campfire":
                    self.__DECORATION_IMAGE_DICT_DARK[key] = {}
                    for key2,value2 in value.items():
                        self.__DECORATION_IMAGE_DICT_DARK[key][key2] = addDarkness(value2,darkness)
                elif "campfire" not in self.__DECORATION_IMAGE_DICT_DARK:
                    self.__DECORATION_IMAGE_DICT_DARK["campfire"] = {}
                    self.__DECORATION_IMAGE_DICT_DARK["campfire"]["campfire"] = (addDarkness(self.__DECORATION_IMAGE_DICT["campfire"][-1],darkness))
    def get_block_width(self):
        return self.__BLOCK_WIDTH
    def get_block_height(self):
        return self.__BLOCK_HEIGHT
    def resize(self,newWidth,newHeight):
        self.__BLOCK_WIDTH = round(newWidth)
        self.__BLOCK_HEIGHT = round(newHeight)
        for key in self.__ENV_IMAGE_DICT:
            self.__ENV_IMAGE_DICT[key] = resizeImg(self.__ENV_IMAGE_DICT_ORIGINAL[key],(self.__BLOCK_WIDTH, None))
        if self.__ENV_IMAGE_DICT_ORIGINAL_DARK != None:
            for key in self.__ENV_IMAGE_DICT_DARK:
                self.__ENV_IMAGE_DICT_DARK[key] = resizeImg(self.__ENV_IMAGE_DICT_ORIGINAL_DARK[key],(self.__BLOCK_WIDTH,None))
    def get_env_image(self,key,darkMode):
        try:
            if darkMode:
                return self.__ENV_IMAGE_DICT_DARK[key]
            else:
                return self.__ENV_IMAGE_DICT[key]
        except BaseException:
            print('LinpgEngine-Warning: Cannot find block image "{}", we will try to load it for you right now, but please by aware.'.format(key))
            imgTmp = loadImg("Assets/image/environment/block/"+key+".png")
            self.__ENV_IMAGE_DICT_ORIGINAL[key] = imgTmp
            self.__ENV_IMAGE_DICT[key] = resizeImg(imgTmp,(self.__BLOCK_WIDTH,None))
            if self.__ENV_IMAGE_DICT_ORIGINAL_DARK != None:
                imgTmp = addDarkness(imgTmp,150)
                self.__ENV_IMAGE_DICT_ORIGINAL_DARK[key] = imgTmp
                self.__ENV_IMAGE_DICT_DARK[key] = resizeImg(imgTmp,(self.__BLOCK_WIDTH,None))
    def get_decoration_image(self,decorationType,key,darkMode,darkness=150):
        try:
            if darkMode:
                return self.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
            else:
                return self.__DECORATION_IMAGE_DICT[decorationType][key]
        #如果图片没找到
        except BaseException:
            print('LinpgEngine-Warning: Cannot find decoration image "{0}" in type "{1}", we will try to load it for you right now, but please by aware.'.format(key,decorationType))
            imgTmp = loadImg("Assets/image/environment/decoration/"+key+".png")
            self.__DECORATION_IMAGE_DICT[decorationType][key] = imgTmp
            if self.__DECORATION_IMAGE_DICT_DARK != None:
                self.__DECORATION_IMAGE_DICT_DARK[decorationType][key] = addDarkness(imgTmp,darkness)
    #获取当前装饰物种类的数量
    def get_decoration_num(self,decorationType):
        return len(self.__DECORATION_IMAGE_DICT[decorationType])
    def new_surface(self,screen_size,map_size):
        if self.__BACKGROUND_IMAGE != None:
            self.__BACKGROUND_SURFACE = resizeImg(self.__BACKGROUND_IMAGE,screen_size)
        else:
            self.__BACKGROUND_SURFACE = pygame.Surface(screen_size).convert()
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