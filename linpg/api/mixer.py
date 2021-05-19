# cython: language_level=3
from .module import *

#音效管理模块接口
class AbstractSoundManager:
    def __init__(self, channel_id:int):
        self._channel_id:int = int(channel_id)
    @property
    def channel_id(self) -> int: return self._channel_id
    def get_channel_id(self) -> int: return self._channel_id
    def set_channel_id(self, channel_id:int) -> None: self.channel_id = int(channel_id)

#音效管理模块-列表
class SoundManagement(AbstractSoundManager):
    def __init__(self, channel_id:int):
        super().__init__(channel_id)
        self.sound_id = 0
        self.__sounds_list = []
    #添加音乐
    def add(self, path:str) -> None: self.__sounds_list.append(load_sound(path))
    #播放音乐
    def play(self, sound_id:int=-1) -> None:
        if len(self.__sounds_list) > 0 and not pygame.mixer.Channel(self._channel_id).get_busy():
            self.sound_id = get_random_int(0,len(self.__sounds_list)-1) if sound_id < 0 else sound_id
            pygame.mixer.Channel(self._channel_id).play(self.__sounds_list[self.sound_id])
    #停止播放
    def stop(self) -> None: pygame.mixer.Channel(self._channel_id).stop()
    #获取音量
    @property
    def volume(self) -> float: return self.get_volume()
    def get_volume(self) -> float: return self.__sounds_list[0].get_volume()
    #设置音量
    def set_volume(self, volume:Union[float,int]) -> None:
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)

#寻找一个可用的频道
def find_channel(force:bool=False) -> int: return pygame.mixer.find_channel(force)

"""音效"""
#加载音效
def load_sound(path:str, volume:float=1.0) -> pygame.mixer.Sound:
    soundTmp:object = pygame.mixer.Sound(path)
    if volume != 1.0: soundTmp.set_volume(volume)
    return soundTmp
#播放音效
def play_sound(sound:pygame.mixer.Sound, channel_id:int) -> None:
    pygame.mixer.Channel(channel_id).play(sound)
#淡出音效
def fade_out_sound(time:int) -> None: pygame.mixer.fadeout(time)

"""背景音乐"""
#卸载背景音乐
def unload_music() -> None: pygame.mixer.music.unload()
#加载背景音乐（但不播放）
def load_music(path:str) -> None: pygame.mixer.music.load(path)
#播放背景音乐
def play_music() -> None: pygame.mixer.music.play()
#淡出背景音乐
def fade_out_music(time:int) -> None: pygame.mixer.music.fadeout(time)
#获取背景音乐播放的位置
def get_music_pos() -> any: return pygame.mixer.music.get_pos()
#获取背景音乐的音量
def get_music_volume() -> float: return pygame.mixer.music.get_volume()
#调整背景音乐的音量
def set_music_volume(volume:float) -> None: pygame.mixer.music.set_volume(volume)

#是否有任何音乐在播放
def is_any_sound_playing() -> bool: return pygame.mixer.get_busy()

#卸载所有音乐
def unload_all_music() -> None:
    unload_music()
    pygame.mixer.stop()