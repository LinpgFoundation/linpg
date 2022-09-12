from .display import *

# 声音 type alias
PG_Sound = pygame.mixer.Sound
# 频道 type alias
PG_Channel = pygame.mixer.Channel

# 根据设置参数改变声道数量
__MIXER_CHANNEL_NUM: Final[int] = max(int(Setting.get("NumberOfChannels")), 8) + 3
"""
linpg引擎保留的频道
"""
# 背景音乐
__RESERVED_BACKGROUND_MUSIC_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 3
LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL: Optional[PG_Channel] = None
# 音效
__RESERVED_SOUND_EFFECTS_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 2
LINPG_RESERVED_SOUND_EFFECTS_CHANNEL: Optional[PG_Channel] = None
# 环境
__RESERVED_ENVIRONMENTAL_SOUND_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 1
LINPG_RESERVED_ENVIRONMENTAL_SOUND_CHANNEL: Optional[PG_Channel] = None
"""
初始化对应频道
"""
if pygame.mixer.get_init() is not None:
    pygame.mixer.set_num_channels(__MIXER_CHANNEL_NUM)
    LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL = pygame.mixer.Channel(__RESERVED_BACKGROUND_MUSIC_CHANNEL_ID)
    LINPG_RESERVED_SOUND_EFFECTS_CHANNEL = pygame.mixer.Channel(__RESERVED_SOUND_EFFECTS_CHANNEL_ID)
    LINPG_RESERVED_ENVIRONMENTAL_SOUND_CHANNEL = pygame.mixer.Channel(__RESERVED_ENVIRONMENTAL_SOUND_CHANNEL_ID)
else:
    EXCEPTION.warn("Mixer has not been initialized correctly!")
    print("One possible cause could be no output device, anyway, please double check your output device(s)!")


# 音效管理模块接口
class AbstractSoundManager(ABC):
    def __init__(self, channel_id: int):
        self._channel_id: int = channel_id

    @property
    def channel_id(self) -> int:
        return self._channel_id

    def get_channel_id(self) -> int:
        return self._channel_id


# 音效管理模块-列表
class SoundManagement(AbstractSoundManager):
    def __init__(self, channel_id: int):
        super().__init__(channel_id)
        self.__sound_id: int = 0
        self.__sounds_list: list[PG_Sound] = []

    # 添加音乐
    def add(self, path: str) -> None:
        self.__sounds_list.append(Sound.load(path))

    # 清空列表释放内存
    def clear(self) -> None:
        self.__sounds_list.clear()

    # 播放音乐
    def play(self, sound_id: int = -1) -> None:
        if len(self.__sounds_list) > 0 and not pygame.mixer.Channel(self._channel_id).get_busy():
            self.__sound_id = Numbers.get_random_int(0, len(self.__sounds_list) - 1) if sound_id < 0 else sound_id
            pygame.mixer.Channel(self._channel_id).play(self.__sounds_list[self.__sound_id])

    # 停止播放
    def stop(self) -> None:
        pygame.mixer.Channel(self._channel_id).stop()

    # 获取音量
    @property
    def volume(self) -> float:
        return self.get_volume()

    def get_volume(self) -> float:
        return self.__sounds_list[0].get_volume()

    # 设置音量
    def set_volume(self, volume: number) -> None:
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)


# 获取视频的音频 （返回路径）
def _split_audio_from_video(input_path: str, audio_type: str = "ogg") -> str:
    # 产生不重名的output文件名称
    output_file_name_t: str = os.path.basename(input_path).replace(".", "_") + "{0}.{1}"
    output_file_name: str
    index: int = 0
    while True:
        output_file_name = output_file_name_t.format(index, audio_type)
        if not os.path.exists(output_file_name):
            break
        else:
            index += 1
    # 生成output路径
    output_path: str = os.path.join(Cache.get_directory(), output_file_name)
    try:
        # 生成视频文件
        VideoConverter.convert_from_video_to_audio(input_path, output_path)
        # 如果一切正常，返回output路径
        return output_path
    # 如果不正常...
    except EXCEPTION.FileNotExists:
        EXCEPTION.fatal('Cannot find media file on path "{}".'.format(input_path))
    except EXCEPTION.ToolIsMissing:
        EXCEPTION.fatal(
            'To split audio from video, "ffmpeg.exe" needs to be placed under directory "{}" inside your project. FFmpeg is never a part of Linpg Engine.'.format(
                os.path.dirname(VideoConverter.get_tool_path())
            )
        )


# 音效管理
class Sound:

    # 加载音效
    @staticmethod
    def load(path: str, volume: Optional[float] = None) -> PG_Sound:
        soundTmp: PG_Sound = pygame.mixer.Sound(path)
        if volume is not None:
            soundTmp.set_volume(volume)
        return soundTmp

    # 从一个视频中加载音效
    @classmethod
    def load_from_video(cls, path: str, volume: Optional[float] = None, cache_key: Optional[str] = None) -> PG_Sound:
        # 如果给定了cache_key，则先尝试从缓存中读取音乐文件
        if cache_key is not None and len(cache_key) > 0 and Cache.match(cache_key, path) is True:
            try:
                return cls.load(Cache.get_cache_path(cache_key), volume)
            except Exception:
                pass
        # 如果读取失败或者没有缓存key或者match失败，则应根据给定的路径生成音乐文件并返回
        path_of_sound: str = _split_audio_from_video(path)
        sound_audio: PG_Sound = cls.load(path_of_sound, volume)
        # 如果给了缓存key，则应该生成缓存联系并保留缓存文件
        if cache_key is not None and len(cache_key) > 0:
            Cache.new(cache_key, path, path_of_sound)
        # 如果没有缓存key，则删除缓存文件
        else:
            os.remove(path_of_sound)
        return sound_audio

    # 从一个文件夹中加载音效
    @classmethod
    def load_from_directory(cls, folder_path: str) -> tuple[PG_Sound, ...]:
        if not os.path.isdir(folder_path):
            EXCEPTION.fatal("The path is not a valid directory!")
        return tuple(cls.load(_path) for _path in glob(os.path.join(folder_path, "*")))

    # 播放音效
    @staticmethod
    def play(sound: PG_Sound, channel_id: int) -> None:
        pygame.mixer.Channel(channel_id).play(sound)

    # 淡出音效
    @staticmethod
    def fade_out(time: int) -> None:
        pygame.mixer.fadeout(time)

    # 寻找一个可用的频道
    @staticmethod
    def find_channel(force: bool = False) -> PG_Channel:
        return pygame.mixer.find_channel(force)

    # 获取频道的数量
    @staticmethod
    def get_num_channels() -> int:
        return pygame.mixer.get_num_channels() - 3

    # 获取对应id的频道
    @classmethod
    def get_channel(cls, channel_id: int) -> PG_Channel:
        if channel_id < cls.get_num_channels():
            return pygame.mixer.Channel(channel_id)
        else:
            EXCEPTION.fatal('The channel_id "{0}" is out of bound of {1}'.format(channel_id, cls.get_num_channels()))


# 音乐管理
class Music:

    # 加载背景音乐（但不播放）
    @staticmethod
    def load(path: str) -> None:
        pygame.mixer.music.load(path)

    # 从一个视频中加载音乐
    @staticmethod
    def load_from_video(path: str) -> str:
        Music.unload()
        path_of_music: str = _split_audio_from_video(path, "mp3")
        Music.load(path_of_music)
        return path_of_music

    # 卸载背景音乐
    @staticmethod
    def unload() -> None:
        pygame.mixer.music.unload()

    # 重新开始播放背景音乐
    @staticmethod
    def restart() -> None:
        pygame.mixer.music.rewind()

    # 播放背景音乐
    @staticmethod
    def play(loops: int = 0, start: float = 0.0, fade_ms: int = 0) -> None:
        pygame.mixer.music.play(loops, start, fade_ms)

    # 停止播放
    @staticmethod
    def stop() -> None:
        pygame.mixer.music.stop()

    # 淡出背景音乐
    @staticmethod
    def fade_out(time: int) -> None:
        pygame.mixer.music.fadeout(time)

    # 获取背景音乐播放的位置
    @staticmethod
    def get_pos() -> int:
        return pygame.mixer.music.get_pos()

    # 设置背景音乐播放的位置
    @staticmethod
    def set_pos(time: float) -> None:
        pygame.mixer.music.set_pos(time)

    # 获取背景音乐的音量
    @staticmethod
    def get_volume() -> float:
        return pygame.mixer.music.get_volume()

    # 调整背景音乐的音量
    @staticmethod
    def set_volume(volume: float) -> None:
        pygame.mixer.music.set_volume(volume)

    # 是否忙碌
    @staticmethod
    def get_busy() -> bool:
        return pygame.mixer.music.get_busy()


# 音量管理
class Volume:

    __sound_unit: Final[int] = 100

    @classmethod
    def get_global_value(cls) -> int:
        return Numbers.keep_int_in_range(round(Setting.get("Sound", "global_value")), 0, cls.__sound_unit)

    @classmethod
    def get_background_music(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Setting.get("Sound", "background_music"), 2), 0, cls.__sound_unit) * cls.get_global_value() / cls.__sound_unit
        )

    @classmethod
    def get_effects(cls) -> int:
        return round(Numbers.keep_number_in_range(round(Setting.get("Sound", "effects"), 2), 0, cls.__sound_unit) * cls.get_global_value() / cls.__sound_unit)

    @classmethod
    def get_environment(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Setting.get("Sound", "environment"), 2), 0, cls.__sound_unit) * cls.get_global_value() / cls.__sound_unit
        )


# 多媒体全局管理
class Media:

    # 是否有任何音乐在播放
    @staticmethod
    def get_busy() -> bool:
        return pygame.mixer.get_busy()

    # 暂停正在播放的音乐
    @staticmethod
    def pause() -> None:
        pygame.mixer.pause()

    # 继续播放暂停的音乐
    @staticmethod
    def unpause() -> None:
        pygame.mixer.unpause()

    # 卸载所有音乐
    @staticmethod
    def unload() -> None:
        Music.unload()
        pygame.mixer.stop()

    # 淡出所有音乐
    @staticmethod
    def fade_out(time: int) -> None:
        Sound.fade_out(time)
        Music.fade_out(time)
