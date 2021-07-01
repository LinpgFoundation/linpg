# cython: language_level=3
from .character import *

#战斗系统接口，请勿实例化
class AbstractBattleSystem(AbstractGameSystem):
    def __init__(self) -> None:
        super().__init__()
        #用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x = -1
        self.__mouse_move_temp_y = -1
        self.screen_to_move_x = None
        self.screen_to_move_y = None
        #是否是死亡的那个
        self.the_dead_one:dict = {}
        #用于检测是否有方向键被按到的字典
        self.__pressKeyToMove:dict = {"up":False,"down":False,"left":False,"right":False}
        #角色数据
        self.alliances_data = None
        self.enemies_data = None
        #地图数据
        self.MAP:object = None
        #视觉小说系统与参数
        self._DIALOG:object = DialogSystem(True)
        self.dialog_parameters:dict = None
        self._is_dialog_updated:bool = False
        self._dialog_dictionary:dict = {}
        self.dialog_key:str = ""
        #方格标准尺寸
        self._standard_block_width:int = int(Display.get_width()/10)
        self._standard_block_height:int = int(Display.get_height()/10)
        #缩进
        self.zoomIn = 100
        self.zoomIntoBe = 100
    def stop(self) -> None:
        self._DIALOG.stop()
        super().stop()
    #获取对话文件所在的具体路径
    def get_map_file_location(self) -> str:
        return os.path.join("Data",self._chapter_type,"chapter{}_map.yaml".format(self._chapter_id)) if self._project_name is None\
            else os.path.join("Data",self._chapter_type,self._project_name,"chapter{}_map.yaml".format(self._chapter_id))
    #初始化地图
    def _create_map(self, map_data:dict) -> None:
        self.MAP = MapObject(map_data,self._standard_block_width,self._standard_block_height)
    #计算光亮区域 并初始化地图
    def _calculate_darkness(self) -> None: self.MAP.calculate_darkness(self.alliances_data)
    #展示地图
    def _display_map(self, screen:ImageSurface) -> None:
        self._check_if_move_screen()
        self._move_screen()
        self.screen_to_move_x,self.screen_to_move_y = self.MAP.display_map(screen,self.screen_to_move_x,self.screen_to_move_y)
    #展示场景装饰物
    def _display_decoration(self, screen:ImageSurface) -> None:
        self.MAP.display_decoration(screen,self.alliances_data,self.enemies_data)
    #展示天气
    def _display_weather(self, screen:ImageSurface) -> None:
        if self.weatherController is not None: self.weatherController.draw(screen,self.MAP.block_width)
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
    #检测按下按键的事件
    def _check_key_down(self, event:object) -> None:
        if event.key == Key.ARROW_UP: self.__pressKeyToMove["up"] = True
        elif event.key == Key.ARROW_DOWN: self.__pressKeyToMove["down"] = True
        elif event.key == Key.ARROW_LEFT: self.__pressKeyToMove["left"] = True
        elif event.key == Key.ARROW_RIGHT: self.__pressKeyToMove["right"] = True
        elif event.unicode == "p": self.MAP.dev_mode()
    #检测按键回弹的事件
    def _check_key_up(self, event:object) -> None:
        if event.key == Key.ARROW_UP: self.__pressKeyToMove["up"] = False
        elif event.key == Key.ARROW_DOWN: self.__pressKeyToMove["down"] = False
        elif event.key == Key.ARROW_LEFT: self.__pressKeyToMove["left"] = False
        elif event.key == Key.ARROW_RIGHT: self.__pressKeyToMove["right"] = False
    #根据鼠标移动屏幕
    def _check_right_click_move(self) -> None:
        if controller.mouse_get_press(2):
            mouse_pos = controller.get_mouse_pos()
            if self.__mouse_move_temp_x == -1 and self.__mouse_move_temp_y == -1:
                self.__mouse_move_temp_x = mouse_pos[0]
                self.__mouse_move_temp_y = mouse_pos[1]
            else:
                if self.__mouse_move_temp_x != mouse_pos[0] or self.__mouse_move_temp_y != mouse_pos[1]:
                    if self.__mouse_move_temp_x != mouse_pos[0]:
                        self.MAP.add_local_x(self.__mouse_move_temp_x-mouse_pos[0])
                    if self.__mouse_move_temp_y != mouse_pos[1]:
                        self.MAP.add_local_y(self.__mouse_move_temp_y-mouse_pos[1])
                    self.__mouse_move_temp_x = mouse_pos[0]
                    self.__mouse_move_temp_y = mouse_pos[1]
        else:
            self.__mouse_move_temp_x = -1
            self.__mouse_move_temp_y = -1
    #检测手柄事件
    def _check_jostick_events(self) -> None:
        if controller.joystick.get_init():
            self.__pressKeyToMove["up"] = True if round(controller.joystick.get_axis(4)) == -1 else False
            self.__pressKeyToMove["down"] = True if round(controller.joystick.get_axis(4)) == 1 else False
            self.__pressKeyToMove["right"] = True if round(controller.joystick.get_axis(3)) == 1 else False
            self.__pressKeyToMove["left"] = True if round(controller.joystick.get_axis(3)) == -1 else False
    #检测并处理屏幕移动事件
    def _check_if_move_screen(self) -> None:
        #根据按键情况设定要移动的数值
        if self.__pressKeyToMove["up"]:
            if self.screen_to_move_y is None:
                self.screen_to_move_y = self.MAP.block_height/4
            else:
                self.screen_to_move_y += self.MAP.block_height/4
        if self.__pressKeyToMove["down"]:
            if self.screen_to_move_y is None:
                self.screen_to_move_y = -self.MAP.block_height/4
            else:
                self.screen_to_move_y -= self.MAP.block_height/4
        if self.__pressKeyToMove["left"]:
            if self.screen_to_move_x is None:
                self.screen_to_move_x = self.MAP.block_width/4
            else:
                self.screen_to_move_x += self.MAP.block_width/4
        if self.__pressKeyToMove["right"]:
            if self.screen_to_move_x is None:
                self.screen_to_move_x = -self.MAP.block_width/4
            else:
                self.screen_to_move_x -= self.MAP.block_width/4
    def _move_screen(self) -> None:
        #如果需要移动屏幕
        if self.screen_to_move_x is not None and self.screen_to_move_x != 0:
            temp_value = int(self.MAP.get_local_x() + self.screen_to_move_x*0.2)
            if Display.get_width()-self.MAP.get_width() <= temp_value <= 0:
                self.MAP.set_local_x(temp_value)
                self.screen_to_move_x *= 0.8
                if round(self.screen_to_move_x) == 0: self.screen_to_move_x = 0
            else:
                self.screen_to_move_x = 0
        if self.screen_to_move_y is not None and self.screen_to_move_y != 0:
            temp_value = int(self.MAP.get_local_y() + self.screen_to_move_y*0.2)
            if Display.get_height()-self.MAP.get_height() <= temp_value <= 0:
                self.MAP.set_local_y(temp_value)
                self.screen_to_move_y *= 0.8
                if round(self.screen_to_move_y) == 0: self.screen_to_move_y = 0
            else:
                self.screen_to_move_y = 0