# cython: language_level=3
from .characterDataManager import *
from ..scr_pyd.map import MapObject
from .entity_ai import *

#战斗系统接口，请勿实例化
class BattleSystemInterface:
    def __init__(self,chapterType,chapterId,collection_name):
        #用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x = -1
        self.__mouse_move_temp_y = -1
        self.screen_to_move_x = None
        self.screen_to_move_y = None
        #是否是死亡的那个
        self.the_dead_one = {}
        #用于检测是否有方向键被按到的字典
        self.__pressKeyToMove = {"up":False,"down":False,"left":False,"right":False}
        #战斗系统主循环判定参数
        self.isPlaying = True
        #战斗系统进行时的输入事件
        self.__events = None
        #角色数据
        self.characters_data = None
        self.sangvisFerris_data = None
        #地图数据
        self.MAP = None
        #对话数据
        self.dialogData = None
        #是否从存档中加载的数据-默认否
        self.loadFromSave = False
        #章节名和种类
        self.chapterId = chapterId
        self.chapterType = chapterType
        self.collection_name = collection_name
    def _create_map(self,MapData,darkMode=None):
        self.MAP = MapObject(MapData,round(self.window_x/10),round(self.window_y/10),darkMode)
    #检测手柄事件
    def _check_jostick_events(self):
        if controller.joystick.get_init() == True:
            if round(controller.joystick.get_axis(4)) == -1:
                self.__pressKeyToMove["up"]=True
            else:
                self.__pressKeyToMove["up"]=False
            if round(controller.joystick.get_axis(4)) == 1:
                self.__pressKeyToMove["down"]=True
            else:
                self.__pressKeyToMove["down"]=False
            if round(controller.joystick.get_axis(3)) == 1:
                self.__pressKeyToMove["right"]=True
            else:
                self.__pressKeyToMove["right"]=False
            if round(controller.joystick.get_axis(3)) == -1:
                self.__pressKeyToMove["left"]=True
            else:
                self.__pressKeyToMove["left"]=False
    def _check_key_down(self,event):
        if event.key == pygame.K_w:
            self.__pressKeyToMove["up"]=True
        if event.key == pygame.K_s:
            self.__pressKeyToMove["down"]=True
        if event.key == pygame.K_a:
            self.__pressKeyToMove["left"]=True
        if event.key == pygame.K_d:
            self.__pressKeyToMove["right"]=True
    def _check_key_up(self,event):
        if event.key == pygame.K_w:
            self.__pressKeyToMove["up"]=False
        if event.key == pygame.K_s:
            self.__pressKeyToMove["down"]=False
        if event.key == pygame.K_a:
            self.__pressKeyToMove["left"]=False
        if event.key == pygame.K_d:
            self.__pressKeyToMove["right"]=False
    def _check_right_click_move(self,mouse_x,mouse_y):
        #移动屏幕
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
    def __check_if_move_screen(self):
        #根据按键情况设定要移动的数值
        if self.__pressKeyToMove["up"] == True:
            if self.screen_to_move_y == None:
                self.screen_to_move_y = self.MAP.block_height/4
            else:
                self.screen_to_move_y += self.MAP.block_height/4
        if self.__pressKeyToMove["down"] == True:
            if self.screen_to_move_y == None:
                self.screen_to_move_y = -self.MAP.block_height/4
            else:
                self.screen_to_move_y -= self.MAP.block_height/4
        if self.__pressKeyToMove["left"] == True:
            if self.screen_to_move_x == None:
                self.screen_to_move_x = self.MAP.block_width/4
            else:
                self.screen_to_move_x += self.MAP.block_width/4
        if self.__pressKeyToMove["right"] == True:
            if self.screen_to_move_x == None:
                self.screen_to_move_x = -self.MAP.block_width/4
            else:
                self.screen_to_move_x -= self.MAP.block_width/4
    def _move_screen(self):
        #如果需要移动屏幕
        if self.screen_to_move_x != None and self.screen_to_move_x != 0:
            temp_value = int(self.MAP.getPos_x() + self.screen_to_move_x*0.2)
            if self.window_x-self.MAP.surface_width<=temp_value<=0:
                self.MAP.setPos_x(temp_value)
                self.screen_to_move_x*=0.8
                if int(self.screen_to_move_x) == 0:
                    self.screen_to_move_x = 0
            else:
                self.screen_to_move_x = 0
        if self.screen_to_move_y != None and self.screen_to_move_y !=0:
            temp_value = int(self.MAP.getPos_y() + self.screen_to_move_y*0.2)
            if self.window_y-self.MAP.surface_height<=temp_value<=0:
                self.MAP.setPos_y(temp_value)
                self.screen_to_move_y*=0.8
                if int(self.screen_to_move_y) == 0:
                    self.screen_to_move_y = 0
            else:
                self.screen_to_move_y = 0
    def _display_map(self,screen):
        self.__check_if_move_screen()
        self._move_screen()
        self.screen_to_move_x,self.screen_to_move_y = self.MAP.display_map(screen,self.screen_to_move_x,self.screen_to_move_y)
    def _display_weather(self,screen):
        if self.weatherController != None:
            self.weatherController.display(screen,self.MAP.block_width)
    def _get_event(self):
        return self.__events
    def _update_event(self):
        #更新游戏事件
        self.__events = pygame.event.get()