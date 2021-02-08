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

#2d游戏对象接口
class GameObject2d(GameObject):
    def __init__(self, x:float, y:float) -> None:
        GameObject.__init__(self,x,y)
    #宽
    @property
    def width(self) -> int: return self.get_width()
    #高
    @property
    def height(self) -> int: return self.get_height()
    #尺寸
    @property
    def size(self) -> tuple: return self.get_size()
    def get_size(self) -> tuple: return self.get_width(),self.get_height()
    #将图片直接画到surface上
    def draw(self,surface) -> None: self.display(surface)
    #根据offSet将图片展示到surface的对应位置上 - 子类必须实现
    def display(self,surface,offSet:tuple=(0,0)) -> None:
        raise Exception("LinpgEngine-Error: This child class doesn't implement display() function!")
    #忽略现有坐标，将图片画到surface的指定位置上，不推荐使用
    def blit(self,surface,pos:tuple) -> None: 
        old_pos = self.get_pos()
        self.set_pos(pos)
        self.display(surface)
        self.set_pos(old_pos)

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
        #判定用于判定是否还在播放的参数
        self._isPlaying = True
    #是否正在播放
    def is_playing(self) -> bool:  return self._isPlaying
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
    def display(self,surface,x,y):
        surface.blit(self.FONT.render(self.point,self.MODE,(255, 255, 255)),(x,y))
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
    def add(self,path:str) -> None: self.__sounds_list.append(pygame.mixer.Sound(path))
    def play(self,sound_id=None):
        if len(self.__sounds_list)>0 and not pygame.mixer.Channel(self.channel_id).get_busy():
            if sound_id == None:
                self.sound_id = randomInt(0,len(self.__sounds_list)-1)
            else:
                self.sound_id = sound_id
            pygame.mixer.Channel(self.channel_id).play(self.__sounds_list[self.sound_id])
    #停止音乐
    def stop(self): pygame.mixer.Channel(self.channel_id).stop()
    #获取音量
    def get_volume(self) -> float: return self.__sounds_list[0].get_volume()
    #设置音量
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

class ItemNeedBlit:
    def __init__(self,image,weight,pos,offSet):
        self.image = image
        self.weight = weight
        self.pos = pos
        self.offSet = offSet
    def __lt__(self,o) -> bool: return self.weight < o.weight
    def blit(self,screen):
        if isinstance(self.image,pygame.Surface):
            if self.offSet == None:
                screen.blit(self.image,self.pos)
            else:
                screen.blit(self.image,(self.pos[0]+self.offSet[0],self.pos[1]+self.offSet[1]))
        else:
            if self.offSet != None:
                self.image.display(screen,self.offSet)
            else:
                try:
                    self.image.draw(screen)
                except:
                    self.image.display(screen)
