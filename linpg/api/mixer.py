# cython: language_level=3
import av
import linpgtoolkit
from .display import *

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
    def add(self, path:str) -> None: self.__sounds_list.append(Sound.load(path))
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
    def set_volume(self, volume:number) -> None:
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)

#获取视频的音频 （返回路径）
def _split_audio_from_video(input_path:str) -> str:
    output_folder:str = os.path.dirname(input_path)
    #产生不重名的output文件名称
    output_file_name_t:str = os.path.basename(input_path).replace(".","_") + "{}.ogg"
    output_file_name:str
    index = 0
    while True:
        output_file_name = output_file_name_t.format(index)
        if not os.path.exists(output_file_name):
            break
        else:
            index += 1
    #生成output路径
    output_path:str = os.path.join(output_folder, output_file_name)
    #让linpgtoolkit生成视频文件
    convert_status:str = linpgtoolkit.ffmpeg.convert_from_vedio_to_audio(input_path, output_path)
    #如果一切正常，返回output路径
    if len(convert_status) < 1:
        return output_path
    #如果不正常...
    elif convert_status == "FILE_NOT_EXIST":
        EXCEPTION.fatal('Cannot find media file on path "{}".'.format(input_path))
    elif convert_status == "FFMPEG_MISSING":
        EXCEPTION.fatal('LinpgToolKit cannot find its "ffmpeg.exe" file. You may need to reinstall the toolkit.')
    else:
        EXCEPTION.fatal("Unexpected convert status, you need to report this issue to the developers.")

#音效管理
class SoundController:
    def __init__(self) -> None:
        pass
    #加载音效
    def load(self, path:str, volume:float=1.0) -> pygame.mixer.Sound:
        soundTmp:object = pygame.mixer.Sound(path)
        if volume != 1.0: soundTmp.set_volume(volume)
        return soundTmp
    #从一个视频中加载音效
    def load_from_video(self, path:str, volume:float=1.0) -> pygame.mixer.Sound:
        path_of_sound:str = _split_audio_from_video(path)
        sound_audio = self.load(path_of_sound, volume)
        os.remove(path_of_sound)
        return sound_audio
    #播放音效
    def play(self, sound:pygame.mixer.Sound, channel_id:int) -> None:
        pygame.mixer.Channel(channel_id).play(sound)
    #淡出音效
    def fade_out(self, time:float) -> None: pygame.mixer.fadeout(int(time))
    #寻找一个可用的频道
    def find_channel(self, force:bool=False) -> int: return pygame.mixer.find_channel(force)

Sound:SoundController = SoundController()

#音乐管理
class MusicController:
    def __init__(self) -> None:
        pass
    #加载背景音乐（但不播放）
    def load(self, path:str) -> None: pygame.mixer.music.load(path)
    #从一个视频中加载音乐
    def load_from_video(self, path:str) -> bool:
        self.unload()
        try:
            path_of_music:str = _split_audio_from_video(path)
            self.load(path_of_music)
            os.remove(path_of_music)
            return True
        except Exception:
            EXCEPTION.warn("Cannot load music from {}!\nIf this vedio has no sound, then just ignore this warning.".format(path))
            return False
    #卸载背景音乐
    def unload(self) -> None: pygame.mixer.music.unload()
    #播放背景音乐
    def play(self, loops:int=0, start:float=0.0, fade_ms:int = 0) -> None: pygame.mixer.music.play(loops, start, fade_ms)
    #停止播放
    def stop(self) -> None: pygame.mixer.music.stop()
    #淡出背景音乐
    def fade_out(self, time:float) -> None: pygame.mixer.music.fadeout(int(time))
    #获取背景音乐播放的位置
    def get_pos(self) -> any: return pygame.mixer.music.get_pos()
    #设置背景音乐播放的位置
    def set_pos(self, time:float) -> any: return pygame.mixer.music.set_pos(time)
    #获取背景音乐的音量
    def get_volume(self) -> float: return pygame.mixer.music.get_volume()
    #调整背景音乐的音量
    def set_volume(self, volume:float) -> None: pygame.mixer.music.set_volume(volume)
    #是否忙碌
    def get_busy(self) -> bool: return pygame.mixer.music.get_busy()

Music:MusicController = MusicController()

#音量管理
class SoundVolumeManger:
    def __init__(self) -> None:
        self.__sound_unit:int = 100
    @property
    def global_value(self) -> int:
        return round(keep_in_range(Setting.get("Sound", "global_value"), 0, self.__sound_unit) * self.global_value / self.__sound_unit)
    @property
    def background_music(self) -> int:
        return round(keep_in_range(Setting.get("Sound", "background_music"), 0, self.__sound_unit) * self.global_value / self.__sound_unit)
    @property
    def effects(self) -> int:
        return round(keep_in_range(Setting.get("Sound", "effects"), 0, self.__sound_unit) * self.global_value / self.__sound_unit)
    @property
    def environment(self) -> int:
        return round(keep_in_range(Setting.get("Sound", "environment"), 0, self.__sound_unit) * self.global_value / self.__sound_unit)

#多媒体全局管理
class MediaController:
    def __init__(self) -> None:
        self.__volume:SoundVolumeManger = SoundVolumeManger()
    @property
    def volume(self) -> SoundVolumeManger: return self.__volume
    #是否有任何音乐在播放
    def get_busy(self) -> bool: return pygame.mixer.get_busy()
    #卸载所有音乐
    def unload(self) -> None:
        Music.unload()
        pygame.mixer.stop()
    def fade_out(self, time:float) -> None:
        Sound.fade_out(time)
        Music.fade_out(time)

Media:MediaController = MediaController()
