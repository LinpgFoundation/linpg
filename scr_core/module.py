# cython: language_level=3
import threading
from .controller import *

#游戏对象接口
class GameObject:
    def __init__(self, x:float, y:float) -> None:
        self.x = x
        self.y = y
    def __lt__(self,other) -> bool: return self.y+self.x < other.y+other.x
    #获取坐标
    @property
    def pos(self) -> tuple: return self.get_pos()
    def get_pos(self) -> tuple: return self.x,self.y
    #设置坐标
    def set_pos(self, x:float, y:float) -> None:
        self.x = round(x)
        self.y = round(y)
    #检测是否在给定的位置上
    def on_pos(self, pos) -> bool: return is_same_pos(self.get_pos(),pos)

#3d游戏对象接口
class GameObject3d(GameObject):
    def __init__(self, x:float, y:float, z:float) -> None:
        GameObject.__init__(self,x,y)
        self.z = z
    def __lt__(self,other) -> bool: return self.y+self.x+self.z < other.y+other.x+other.z
    #获取坐标
    def get_pos(self) -> tuple: return self.x,self.y,self.z
    #设置坐标
    def set_pos(self, x:float, y:float, z:float) -> None:
        super().set_pos(x,y)
        self.z = round(z)

#系统模块接口
class SystemObject:
    def __init__(self) -> None:
        #输入事件
        self.__events = None
    #更新输入事件
    def _update_event(self) -> None: self.__events = pygame.event.get()
    #获取输入事件
    @property
    def events(self): return self.__events

#行动点数管理器（塔防模式）
class ApSystem:
    def __init__(self,fontSize):
        self.point = 0
        self.coolDown = 0
        self.FONT = createFont(fontSize)
    def display(self,screen,x,y):
        screen.blit(self.FONT.render(self.point,self.MODE,(255, 255, 255)),(x,y))
        if self.coolDown == 100:
            self.point += 1
            self.coolDown = 0
        else:
            self.coolDown += 1

#音效管理模块
class SoundManagement:
    def __init__(self,channel_id):
        self.channel_id = channel_id
        self.sound_id = 0
        self.__sounds_list = []
    def add(self,path):
        self.__sounds_list.append(pygame.mixer.Sound(path))
    def play(self,sound_id=None):
        if len(self.__sounds_list)>0 and not pygame.mixer.Channel(self.channel_id).get_busy():
            if sound_id == None:
                self.sound_id = randomInt(0,len(self.__sounds_list)-1)
            else:
                self.sound_id = sound_id
            pygame.mixer.Channel(self.channel_id).play(self.__sounds_list[self.sound_id])
    def stop(self):
        pygame.mixer.Channel(self.channel_id).stop()
    def set_volume(self,volume):
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)

#使用多线程保存数据
class SaveDataThread(threading.Thread):
    def __init__(self,config_file_path,data):
        threading.Thread.__init__(self)
        self.config_file_path = config_file_path
        self.data = data
    def run(self):
        saveConfig(self.config_file_path,self.data)
        del self.data,self.config_file_path
