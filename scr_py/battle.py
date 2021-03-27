# cython: language_level=3
from ..scr_pyd.map import MapObject
from .character import *

#战斗系统接口，请勿实例化
class AbstractBattleSystem(SystemWithBackgroundMusic):
    def __init__(self, chapterType:str, chapterId:int, collection_name:str) -> None:
        SystemWithBackgroundMusic.__init__(self)
        #用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x = -1
        self.__mouse_move_temp_y = -1
        self.screen_to_move_x = None
        self.screen_to_move_y = None
        #是否是死亡的那个
        self.the_dead_one = {}
        #用于检测是否有方向键被按到的字典
        self.__pressKeyToMove = {"up":False,"down":False,"left":False,"right":False}
        #角色数据
        self.alliances_data = None
        self.enemies_data = None
        #地图数据
        self.MAP = None
        #对话数据
        self.dialogData = None
        #章节名和种类
        self.chapterId = chapterId
        self.chapterType = chapterType
        self.collection_name = collection_name
        #方格标准尺寸
        self.standard_block_width = round(display.get_width()/10)
        self.standard_block_height = round(display.get_height()/10)
        #缩进
        self.zoomIn = 100
        self.zoomIntoBe = 100
    #初始化地图
    def _create_map(self, MapData:dict) -> None:
        self.MAP = MapObject(MapData,self.standard_block_width,self.standard_block_height)
    #计算光亮区域 并初始化地图
    def _calculate_darkness(self) -> None: self.MAP.calculate_darkness(self.alliances_data)
    #展示地图
    def _display_map(self, screen:pygame.Surface) -> None:
        self._check_if_move_screen()
        self._move_screen()
        self.screen_to_move_x,self.screen_to_move_y = self.MAP.display_map(screen,self.screen_to_move_x,self.screen_to_move_y)
    #展示场景装饰物
    def _display_decoration(self, screen:pygame.Surface) -> None:
        self.MAP.display_decoration(screen,self.alliances_data,self.enemies_data)
    #展示天气
    def _display_weather(self, screen:pygame.Surface) -> None:
        if self.weatherController != None: self.weatherController.display(screen,self.MAP.block_width)
    #初始化角色加载器
    def _initial_characters_loader(self, alliancesData:dict, enemiesData:dict, mode:str="default") -> None:
        self.__characterDataLoaderThread = CharacterDataLoader(alliancesData,enemiesData,mode)
    #启动角色加载器
    def _start_characters_loader(self) -> None: self.__characterDataLoaderThread.start()
    #是否角色加载器还在运行
    def _is_characters_loader_alive(self) -> bool:
        if self.__characterDataLoaderThread.is_alive():
            return True
        else:
            self.alliances_data,self.enemies_data = self.__characterDataLoaderThread.getResult()
            if self.__characterDataLoaderThread.mode == "dev":
                #如果是开发模式，则保存数据库
                self.DATABASE = self.__characterDataLoaderThread.DATABASE
            del self.__characterDataLoaderThread
            return False
    @property
    def characters_loaded(self) -> int: return self.__characterDataLoaderThread.currentID
    @property
    def characters_total(self) -> int: return self.__characterDataLoaderThread.totalNum
    #检测手柄事件
    def _check_jostick_events(self) -> None:
        if controller.joystick.get_init():
            self.__pressKeyToMove["up"] = True if round(controller.joystick.get_axis(4)) == -1 else False
            self.__pressKeyToMove["down"] = True if round(controller.joystick.get_axis(4)) == 1 else False
            self.__pressKeyToMove["right"] = True if round(controller.joystick.get_axis(3)) == 1 else False
            self.__pressKeyToMove["left"] = True if round(controller.joystick.get_axis(3)) == -1 else False
    def _check_key_down(self, event:object) -> None:
        if event.key == pygame.K_UP: self.__pressKeyToMove["up"] = True
        if event.key == pygame.K_DOWN: self.__pressKeyToMove["down"] = True
        if event.key == pygame.K_LEFT: self.__pressKeyToMove["left"] = True
        if event.key == pygame.K_RIGHT: self.__pressKeyToMove["right"] = True
        if event.key == pygame.K_p: self.MAP.dev_mode()
    def _check_key_up(self, event:object) -> None:
        if event.key == pygame.K_UP: self.__pressKeyToMove["up"] = False
        if event.key == pygame.K_DOWN: self.__pressKeyToMove["down"] = False
        if event.key == pygame.K_LEFT: self.__pressKeyToMove["left"] = False
        if event.key == pygame.K_RIGHT: self.__pressKeyToMove["right"] = False
    #根据鼠标移动屏幕
    def _check_right_click_move(self, mouse_x:int, mouse_y:int) -> None:
        if pygame.mouse.get_pressed()[2]:
            if self.__mouse_move_temp_x == -1 and self.__mouse_move_temp_y == -1:
                self.__mouse_move_temp_x = mouse_x
                self.__mouse_move_temp_y = mouse_y
            else:
                if self.__mouse_move_temp_x != mouse_x or self.__mouse_move_temp_y != mouse_y:
                    if self.__mouse_move_temp_x != mouse_x:
                        self.MAP.addPos_x(self.__mouse_move_temp_x-mouse_x)
                    if self.__mouse_move_temp_y != mouse_y:
                        self.MAP.addPos_y(self.__mouse_move_temp_y-mouse_y)
                    self.__mouse_move_temp_x = mouse_x
                    self.__mouse_move_temp_y = mouse_y
        else:
            self.__mouse_move_temp_x = -1
            self.__mouse_move_temp_y = -1
    def _check_if_move_screen(self) -> None:
        #根据按键情况设定要移动的数值
        if self.__pressKeyToMove["up"]:
            if self.screen_to_move_y == None:
                self.screen_to_move_y = self.MAP.block_height/4
            else:
                self.screen_to_move_y += self.MAP.block_height/4
        if self.__pressKeyToMove["down"]:
            if self.screen_to_move_y == None:
                self.screen_to_move_y = -self.MAP.block_height/4
            else:
                self.screen_to_move_y -= self.MAP.block_height/4
        if self.__pressKeyToMove["left"]:
            if self.screen_to_move_x == None:
                self.screen_to_move_x = self.MAP.block_width/4
            else:
                self.screen_to_move_x += self.MAP.block_width/4
        if self.__pressKeyToMove["right"]:
            if self.screen_to_move_x == None:
                self.screen_to_move_x = -self.MAP.block_width/4
            else:
                self.screen_to_move_x -= self.MAP.block_width/4
    def _move_screen(self) -> None:
        #如果需要移动屏幕
        if self.screen_to_move_x != None and self.screen_to_move_x != 0:
            temp_value = int(self.MAP.getPos_x() + self.screen_to_move_x*0.2)
            if display.get_width()-self.MAP.surface_width<=temp_value<=0:
                self.MAP.setPos_x(temp_value)
                self.screen_to_move_x*=0.8
                if round(self.screen_to_move_x) == 0: self.screen_to_move_x = 0
            else:
                self.screen_to_move_x = 0
        if self.screen_to_move_y != None and self.screen_to_move_y !=0:
            temp_value = int(self.MAP.getPos_y() + self.screen_to_move_y*0.2)
            if display.get_height()-self.MAP.surface_height<=temp_value<=0:
                self.MAP.setPos_y(temp_value)
                self.screen_to_move_y*=0.8
                if round(self.screen_to_move_y) == 0: self.screen_to_move_y = 0
            else:
                self.screen_to_move_y = 0